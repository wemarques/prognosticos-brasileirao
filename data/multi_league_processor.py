"""
Processador multi-liga para Brasileirão e Premier League
Integra análise de árbitros, timezone e processamento em lote
"""
from typing import Dict, List, Any
from data.processor_with_referee import DataProcessorWithReferee
from utils.multi_league_config import (
    get_league_config,
    get_league_stats,
    get_timezone,
    get_available_leagues
)
from utils.timezone_utils import TimezoneConverter
from analysis.batch_processor import BatchMatchProcessor


class MultiLeagueProcessor:
    """Processador que suporta múltiplas ligas"""
    
    def __init__(self):
        """Inicializa o processador multi-liga"""
        self.processors = {}
        self.batch_processors = {}
        self.timezone_converter = TimezoneConverter()
        
        # Inicializar processadores para cada liga
        for league_key in get_available_leagues():
            self.processors[league_key] = DataProcessorWithReferee()
            self.batch_processors[league_key] = BatchMatchProcessor(max_workers=4)
    
    def process_match(
        self,
        league: str,
        home_stats: Dict,
        away_stats: Dict,
        h2h_data: Dict,
        home_team_name: str,
        away_team_name: str,
        referee_key: str = None,
        utc_timestamp: int = None,
        competition: str = None
    ) -> Dict[str, Any]:
        """
        Processa um match de qualquer liga
        
        Args:
            league: 'brasileirao' ou 'premier_league'
            home_stats: Estatísticas do time mandante
            away_stats: Estatísticas do time visitante
            h2h_data: Dados de confrontos diretos
            home_team_name: Nome do time mandante
            away_team_name: Nome do time visitante
            referee_key: Chave do árbitro
            utc_timestamp: Timestamp UTC do match
            competition: Competição (se None, usa a padrão da liga)
            
        Returns:
            Dados processados do match
        """
        # Usar competição padrão se não especificada
        if competition is None:
            league_config = get_league_config(league)
            competition = league_config.get('code', league)
        
        # Obter processador da liga
        processor = self.processors.get(league)
        if not processor:
            raise ValueError(f"Liga não suportada: {league}")
        
        # Processar match
        processed = processor.process_match_with_referee_and_timezone(
            home_stats=home_stats,
            away_stats=away_stats,
            h2h_data=h2h_data,
            home_team_name=home_team_name,
            away_team_name=away_team_name,
            referee_key=referee_key,
            utc_timestamp=utc_timestamp,
            competition=competition
        )
        
        # Adicionar informações da liga
        processed['league'] = league
        processed['league_config'] = get_league_config(league)
        
        return processed
    
    def process_round(
        self,
        league: str,
        matches: List[Dict[str, Any]],
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Processa uma rodada completa de uma liga
        
        Args:
            league: 'brasileirao' ou 'premier_league'
            matches: Lista de matches
            show_progress: Mostrar progresso
            
        Returns:
            Resultados do processamento
        """
        # Obter processador em lote da liga
        batch_processor = self.batch_processors.get(league)
        if not batch_processor:
            raise ValueError(f"Liga não suportada: {league}")
        
        # Processar rodada
        results = batch_processor.process_round(
            matches,
            competition=league,
            show_progress=show_progress
        )
        
        # Adicionar informações da liga
        results['league'] = league
        results['league_config'] = get_league_config(league)
        
        return results
    
    def process_multiple_leagues(
        self,
        matches_by_league: Dict[str, List[Dict[str, Any]]],
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Processa matches de múltiplas ligas simultaneamente
        
        Args:
            matches_by_league: Dict com liga -> lista de matches
            show_progress: Mostrar progresso
            
        Returns:
            Resultados por liga
        """
        results = {}
        
        for league, matches in matches_by_league.items():
            results[league] = self.process_round(
                league,
                matches,
                show_progress=show_progress
            )
        
        return results
    
    def get_league_comparison(self) -> Dict[str, Any]:
        """
        Obter comparação de estatísticas entre ligas
        
        Returns:
            Comparação de estatísticas
        """
        comparison = {}
        
        for league in get_available_leagues():
            config = get_league_config(league)
            stats = get_league_stats(league)
            
            comparison[league] = {
                'name': config['name'],
                'icon': config['icon'],
                'country': config['country'],
                'timezone': config['timezone'],
                'stats': stats,
                'api': config['api']
            }
        
        return comparison
    
    def convert_time_to_league_timezone(
        self,
        league: str,
        utc_timestamp: int
    ) -> str:
        """
        Converte timestamp UTC para timezone da liga
        
        Args:
            league: 'brasileirao' ou 'premier_league'
            utc_timestamp: Timestamp UTC
            
        Returns:
            Horário formatado no timezone da liga
        """
        timezone = get_timezone(league)
        
        # Converter para timezone específico
        import pytz
        from datetime import datetime
        
        utc_dt = datetime.fromtimestamp(utc_timestamp, tz=pytz.UTC)
        league_tz = pytz.timezone(timezone)
        league_dt = utc_dt.astimezone(league_tz)
        
        return league_dt.strftime("%d/%m/%Y %H:%M")
    
    def get_league_stats_summary(self, league: str) -> str:
        """
        Obter resumo de estatísticas de uma liga
        
        Args:
            league: 'brasileirao' ou 'premier_league'
            
        Returns:
            String com resumo formatado
        """
        config = get_league_config(league)
        stats = get_league_stats(league)
        
        summary = f"""
╔════════════════════════════════════════════════════════════╗
║           ESTATÍSTICAS DA LIGA - {config['name'].upper()}                ║
╠════════════════════════════════════════════════════════════╣
║ País:                    {config['country']:<35} ║
║ Timezone:                {config['timezone']:<35} ║
║ Temporada:               {config['season']:<35} ║
╠════════════════════════════════════════════════════════════╣
║ Gols/Jogo:               {stats.get('league_avg_goals', 0):<35.2f} ║
║ xG/Jogo:                 {stats.get('league_avg_xg', 0):<35.2f} ║
║ Vantagem Casa:           {stats.get('home_advantage', 0):<35.2f} ║
║ Taxa BTTS:               {stats.get('btts_rate', 0):<35.0%} ║
║ Cartões/Jogo:            {stats.get('avg_cards_per_match', 0):<35.1f} ║
║ Cartões Amarelos:        {stats.get('avg_yellow_cards', 0):<35.1f} ║
║ Cartões Vermelhos:       {stats.get('avg_red_cards', 0):<35.1f} ║
╚════════════════════════════════════════════════════════════╝
"""
        return summary
    
    def export_league_comparison(self, filepath: str) -> None:
        """
        Exporta comparação de ligas para arquivo
        
        Args:
            filepath: Caminho do arquivo
        """
        import json
        
        comparison = self.get_league_comparison()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)


# Exemplo de uso
if __name__ == "__main__":
    import time
    
    # Criar processador multi-liga
    processor = MultiLeagueProcessor()
    
    # Matches do Brasileirão
    br_matches = [
        {
            'home_team': 'Flamengo',
            'away_team': 'Vasco',
            'home_stats': {'cards_for': 15, 'cards_against': 12},
            'away_stats': {'cards_for': 14, 'cards_against': 13},
            'h2h_data': {},
            'referee_key': 'anderson_daronco',
            'utc_timestamp': int(time.time()) + 86400,
        }
    ]
    
    # Matches da Premier League
    pl_matches = [
        {
            'home_team': 'Manchester United',
            'away_team': 'Liverpool',
            'home_stats': {'cards_for': 16, 'cards_against': 11},
            'away_stats': {'cards_for': 13, 'cards_against': 14},
            'h2h_data': {},
            'referee_key': 'anthony_taylor',
            'utc_timestamp': int(time.time()) + 86400,
        }
    ]
    
    # Processar ambas as ligas
    print("Processando Brasileirão...")
    br_results = processor.process_round('brasileirao', br_matches, show_progress=True)
    
    print("\nProcessando Premier League...")
    pl_results = processor.process_round('premier_league', pl_matches, show_progress=True)
    
    # Exibir resumos
    print(processor.get_league_stats_summary('brasileirao'))
    print(processor.get_league_stats_summary('premier_league'))
    
    # Exibir comparação
    print("\nComparação de Ligas:")
    comparison = processor.get_league_comparison()
    for league, data in comparison.items():
        print(f"\n{data['icon']} {data['name']}:")
        print(f"  Gols/Jogo: {data['stats']['league_avg_goals']}")
        print(f"  Cartões/Jogo: {data['stats']['avg_cards_per_match']}")