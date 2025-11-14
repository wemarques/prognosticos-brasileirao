#!/usr/bin/env python3
"""
Script para atualizar CSV com dados da API
Rodar 1x por dia via cron ou manualmente

Uso:
    python scripts/update_csv_from_api.py --league brasileirao
    python scripts/update_csv_from_api.py --league premier_league --season 2024

Autor: Sistema de Prognósticos
Data: 2025-11-14
"""

import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import os
import logging

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.collectors.football_data_collector_v2 import FootballDataCollectorV2
from utils.leagues_config import get_api_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_matches_csv(collector, csv_dir: Path, season: str):
    """Atualiza CSV de matches"""
    logger.info("📥 Coletando matches da API...")

    try:
        matches = collector.get_matches(status=None)  # Todos os status

        if not matches:
            logger.warning("⚠️ Nenhum match retornado da API")
            return False

        # Converter para DataFrame
        df = pd.DataFrame(matches)

        # Garantir colunas esperadas
        expected_cols = [
            'id', 'round', 'date', 'home_team', 'away_team',
            'home_score', 'away_score', 'status', 'referee',
            'home_xg', 'away_xg', 'home_shots', 'away_shots',
            'home_corners', 'away_corners', 'home_cards', 'away_cards'
        ]

        # Adicionar colunas faltantes com valores padrão
        for col in expected_cols:
            if col not in df.columns:
                if col in ['home_score', 'away_score', 'home_shots', 'away_shots',
                           'home_corners', 'away_corners', 'home_cards', 'away_cards']:
                    df[col] = None
                elif col in ['home_xg', 'away_xg']:
                    df[col] = None
                elif col == 'round':
                    df[col] = 1  # Padrão
                elif col == 'referee':
                    df[col] = ''
                else:
                    df[col] = ''

        # Reordenar colunas
        df = df[expected_cols]

        # Salvar CSV
        csv_file = csv_dir / f'{season}_matches.csv'
        df.to_csv(csv_file, index=False)

        logger.info(f"✅ Matches salvos: {len(matches)} jogos em {csv_file}")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao atualizar matches: {e}")
        return False


def update_teams_csv(collector, csv_dir: Path, season: str):
    """Atualiza CSV de times"""
    logger.info("📥 Coletando times da API...")

    try:
        teams = collector.get_teams()

        if not teams:
            logger.warning("⚠️ Nenhum time retornado da API")
            return False

        # Converter para DataFrame
        df = pd.DataFrame(teams)

        # Garantir colunas esperadas
        expected_cols = ['id', 'name', 'code', 'stadium', 'city', 'founded', 'crest_url']

        for col in expected_cols:
            if col not in df.columns:
                if col in ['stadium', 'city', 'founded']:
                    df[col] = ''
                elif col == 'crest_url':
                    df[col] = ''
                elif col == 'code':
                    # Gerar código a partir do nome
                    df[col] = df['name'].str[:3].str.upper()

        # Reordenar colunas
        df = df[[c for c in expected_cols if c in df.columns]]

        # Salvar CSV
        csv_file = csv_dir / f'{season}_teams.csv'
        df.to_csv(csv_file, index=False)

        logger.info(f"✅ Times salvos: {len(teams)} times em {csv_file}")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao atualizar times: {e}")
        return False


def update_standings_csv(collector, csv_dir: Path, season: str):
    """Atualiza CSV de classificação"""
    logger.info("📥 Coletando classificação da API...")

    try:
        standings_data = collector.get_standings()

        if not standings_data:
            logger.warning("⚠️ Nenhuma classificação retornada da API")
            return False

        # Verificar estrutura dos dados
        if isinstance(standings_data, list) and len(standings_data) > 0:
            # Se já é lista de dicionários
            df = pd.DataFrame(standings_data)
        elif isinstance(standings_data, dict) and 'standings' in standings_data:
            # Se é dict com key 'standings'
            df = pd.DataFrame(standings_data['standings'])
        else:
            logger.warning("⚠️ Formato de standings não reconhecido")
            return False

        # Garantir colunas esperadas
        expected_cols = [
            'round', 'position', 'team', 'matches_played',
            'wins', 'draws', 'losses', 'goals_for', 'goals_against',
            'goal_difference', 'points'
        ]

        # Mapear colunas da API para nomes esperados
        column_mapping = {
            'playedGames': 'matches_played',
            'won': 'wins',
            'draw': 'draws',
            'lost': 'losses',
            'goalsFor': 'goals_for',
            'goalsAgainst': 'goals_against',
            'goalDifference': 'goal_difference',
            'team_name': 'team'
        }

        df = df.rename(columns=column_mapping)

        # Adicionar rodada (rodada atual)
        if 'round' not in df.columns:
            # Calcular rodada baseado em matches_played
            if 'matches_played' in df.columns:
                df['round'] = df['matches_played'].max()
            else:
                df['round'] = 1

        # Adicionar colunas faltantes
        for col in expected_cols:
            if col not in df.columns:
                if col in ['wins', 'draws', 'losses', 'goals_for', 'goals_against', 'points']:
                    df[col] = 0
                elif col == 'goal_difference':
                    df[col] = 0
                elif col == 'position':
                    df[col] = range(1, len(df) + 1)

        # Reordenar colunas
        df = df[[c for c in expected_cols if c in df.columns]]

        # Salvar CSV
        csv_file = csv_dir / f'{season}_standings.csv'

        # Se já existe, append (múltiplas rodadas)
        if csv_file.exists():
            existing_df = pd.read_csv(csv_file)
            # Remover rodada atual se já existe (update)
            current_round = df['round'].iloc[0] if 'round' in df.columns else 1
            existing_df = existing_df[existing_df['round'] != current_round]
            # Concatenar
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_csv(csv_file, index=False)

        logger.info(f"✅ Classificação salva em {csv_file}")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao atualizar standings: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def update_league_csv(league_key: str, season: str = '2025'):
    """
    Atualiza todos os CSVs de uma liga

    Args:
        league_key: Chave da liga ('brasileirao', 'premier_league', etc)
        season: Temporada (default: 2025)
    """
    logger.info(f"🚀 Iniciando atualização de CSV para {league_key} - Temporada {season}")

    # Criar diretório se não existir
    csv_dir = Path(__file__).parent.parent / 'data' / 'csv' / league_key
    csv_dir.mkdir(parents=True, exist_ok=True)

    # Obter configuração da API
    try:
        api_config = get_api_config(league_key)
    except Exception as e:
        logger.error(f"❌ Erro ao obter configuração da API: {e}")
        return False

    # Criar collector
    try:
        collector = FootballDataCollectorV2(league_key, api_config)
    except Exception as e:
        logger.error(f"❌ Erro ao criar collector: {e}")
        return False

    # Atualizar cada CSV
    results = {
        'matches': update_matches_csv(collector, csv_dir, season),
        'teams': update_teams_csv(collector, csv_dir, season),
        'standings': update_standings_csv(collector, csv_dir, season)
    }

    # Salvar timestamp da última atualização
    timestamp_file = csv_dir / 'last_update.txt'
    with open(timestamp_file, 'w') as f:
        f.write(f"Last update: {datetime.now().isoformat()}\n")
        f.write(f"League: {league_key}\n")
        f.write(f"Season: {season}\n")
        f.write(f"Results: {results}\n")

    # Resumo
    success_count = sum(results.values())
    total_count = len(results)

    logger.info(f"\n{'='*50}")
    logger.info(f"📊 RESUMO DA ATUALIZAÇÃO")
    logger.info(f"{'='*50}")
    logger.info(f"Liga: {league_key}")
    logger.info(f"Temporada: {season}")
    logger.info(f"Sucesso: {success_count}/{total_count}")
    logger.info(f"Matches: {'✅' if results['matches'] else '❌'}")
    logger.info(f"Teams: {'✅' if results['teams'] else '❌'}")
    logger.info(f"Standings: {'✅' if results['standings'] else '❌'}")
    logger.info(f"{'='*50}\n")

    return success_count == total_count


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Atualizar CSV com dados da API')
    parser.add_argument(
        '--league',
        type=str,
        default='brasileirao',
        help='Liga a atualizar (brasileirao, premier_league, etc)'
    )
    parser.add_argument(
        '--season',
        type=str,
        default='2025',
        help='Temporada (default: 2025)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Atualizar todas as ligas configuradas'
    )

    args = parser.parse_args()

    if args.all:
        # Atualizar todas as ligas
        leagues = ['brasileirao', 'premier_league', 'la_liga']
        for league in leagues:
            logger.info(f"\n{'#'*60}")
            logger.info(f"# Atualizando {league.upper()}")
            logger.info(f"{'#'*60}\n")
            update_league_csv(league, args.season)
    else:
        # Atualizar liga específica
        update_league_csv(args.league, args.season)


if __name__ == '__main__':
    main()
