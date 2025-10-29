"""
Processador em lote para múltiplos matches
Permite processar rodadas completas com tratamento robusto de erros
"""
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from datetime import datetime
import time

from data.processor_with_referee import DataProcessorWithReferee


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchMatchProcessor:
    """Processador em lote para múltiplos matches"""
    
    def __init__(self, max_workers: int = 4, max_retries: int = 3):
        """
        Inicializa o processador em lote
        
        Args:
            max_workers: Número máximo de workers paralelos
            max_retries: Número máximo de tentativas por match
        """
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.processor = DataProcessorWithReferee()
        self.logger = logger
    
    def process_round(
        self,
        matches: List[Dict[str, Any]],
        competition: str = 'brasileirao',
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Processa todos os matches de uma rodada
        
        Args:
            matches: Lista de matches com dados completos
            competition: Competição (brasileirao, premier_league)
            show_progress: Mostrar progresso em tempo real
            
        Returns:
            Dict com resultados processados
        """
        start_time = time.time()
        
        results = {
            'successful': 0,
            'failed': 0,
            'total': len(matches),
            'matches': [],
            'errors': [],
            'processing_time': 0,
            'avg_time_per_match': 0,
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }
        
        self.logger.info(f"Iniciando processamento de {len(matches)} matches")
        
        # Processar matches em paralelo
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submeter todas as tarefas
            future_to_match = {
                executor.submit(
                    self._process_match_with_retry,
                    match,
                    competition
                ): match for match in matches
            }
            
            # Processar resultados conforme completam
            completed = 0
            for future in as_completed(future_to_match):
                completed += 1
                match = future_to_match[future]
                
                try:
                    processed_data = future.result()
                    results['matches'].append(processed_data)
                    results['successful'] += 1
                    
                    if show_progress:
                        self.logger.info(
                            f"✅ [{completed}/{len(matches)}] "
                            f"{match.get('home_team')} vs {match.get('away_team')}"
                        )
                
                except Exception as e:
                    results['failed'] += 1
                    error_info = {
                        'match': f"{match.get('home_team')} vs {match.get('away_team')}",
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    results['errors'].append(error_info)
                    
                    if show_progress:
                        self.logger.error(
                            f"❌ [{completed}/{len(matches)}] "
                            f"{match.get('home_team')} vs {match.get('away_team')}: {str(e)}"
                        )
        
        # Calcular estatísticas
        elapsed_time = time.time() - start_time
        results['processing_time'] = round(elapsed_time, 2)
        results['avg_time_per_match'] = round(elapsed_time / len(matches), 2) if matches else 0
        results['end_time'] = datetime.now().isoformat()
        
        # Log final
        self.logger.info(
            f"Processamento concluído: "
            f"{results['successful']} sucesso, "
            f"{results['failed']} falhas, "
            f"Tempo total: {results['processing_time']}s"
        )
        
        return results
    
    def _process_match_with_retry(
        self,
        match: Dict[str, Any],
        competition: str
    ) -> Dict[str, Any]:
        """
        Processa um match com retry automático
        
        Args:
            match: Dados do match
            competition: Competição
            
        Returns:
            Dados processados
            
        Raises:
            Exception: Se falhar após todas as tentativas
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Validar dados antes de processar
                self._validate_match_data(match)
                
                # Processar match
                processed = self.processor.process_match_with_referee_and_timezone(
                    home_stats=match.get('home_stats', {}),
                    away_stats=match.get('away_stats', {}),
                    h2h_data=match.get('h2h_data', {}),
                    home_team_name=match.get('home_team', ''),
                    away_team_name=match.get('away_team', ''),
                    referee_key=match.get('referee_key'),
                    utc_timestamp=match.get('utc_timestamp'),
                    competition=competition
                )
                
                return processed
            
            except Exception as e:
                last_error = e
                
                if attempt < self.max_retries:
                    wait_time = 2 ** (attempt - 1)  # Exponential backoff
                    self.logger.warning(
                        f"Tentativa {attempt}/{self.max_retries} falhou para "
                        f"{match.get('home_team')} vs {match.get('away_team')}. "
                        f"Aguardando {wait_time}s antes de retry..."
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(
                        f"Todas as {self.max_retries} tentativas falharam para "
                        f"{match.get('home_team')} vs {match.get('away_team')}"
                    )
        
        raise last_error
    
    def _validate_match_data(self, match: Dict[str, Any]) -> None:
        """
        Valida dados do match antes de processar
        
        Args:
            match: Dados do match
            
        Raises:
            ValueError: Se dados inválidos
        """
        required_fields = ['home_team', 'away_team']
        
        for field in required_fields:
            if field not in match or not match[field]:
                raise ValueError(f"Campo obrigatório faltando: {field}")
        
        # Validar estrutura de stats se presente
        if 'home_stats' in match and match['home_stats']:
            if not isinstance(match['home_stats'], dict):
                raise ValueError("home_stats deve ser um dicionário")
        
        if 'away_stats' in match and match['away_stats']:
            if not isinstance(match['away_stats'], dict):
                raise ValueError("away_stats deve ser um dicionário")
    
    def process_round_with_fallback(
        self,
        matches: List[Dict[str, Any]],
        competition: str = 'brasileirao',
        use_mock_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Processa rodada com fallback para dados mock em caso de erro
        
        Args:
            matches: Lista de matches
            competition: Competição
            use_mock_on_error: Usar dados mock se falhar
            
        Returns:
            Resultados processados
        """
        results = self.process_round(matches, competition, show_progress=True)
        
        # Se houver falhas e usar_mock_on_error, tentar com dados mock
        if results['failed'] > 0 and use_mock_on_error:
            self.logger.info(f"Tentando processar {results['failed']} matches com dados mock...")
            
            for error_info in results['errors']:
                # Encontrar o match original
                match_name = error_info['match']
                original_match = next(
                    (m for m in matches 
                     if f"{m.get('home_team')} vs {m.get('away_team')}" == match_name),
                    None
                )
                
                if original_match:
                    try:
                        # Criar dados mock
                        mock_match = self._create_mock_match(original_match)
                        processed = self.processor.process_match_with_referee_and_timezone(
                            home_stats=mock_match.get('home_stats', {}),
                            away_stats=mock_match.get('away_stats', {}),
                            h2h_data=mock_match.get('h2h_data', {}),
                            home_team_name=mock_match.get('home_team', ''),
                            away_team_name=mock_match.get('away_team', ''),
                            referee_key=mock_match.get('referee_key'),
                            utc_timestamp=mock_match.get('utc_timestamp'),
                            competition=competition
                        )
                        
                        results['matches'].append(processed)
                        results['successful'] += 1
                        results['failed'] -= 1
                        results['errors'].remove(error_info)
                        
                        self.logger.info(f"✅ Recuperado com dados mock: {match_name}")
                    
                    except Exception as e:
                        self.logger.error(f"Falha ao usar dados mock para {match_name}: {e}")
        
        return results
    
    def _create_mock_match(self, match: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria dados mock para um match
        
        Args:
            match: Dados originais do match
            
        Returns:
            Match com dados mock
        """
        mock_match = match.copy()
        
        # Criar stats mock se não existirem
        if not mock_match.get('home_stats'):
            mock_match['home_stats'] = {
                'cards_for': 15,
                'cards_against': 12,
                'goals_for': 25,
                'goals_against': 18
            }
        
        if not mock_match.get('away_stats'):
            mock_match['away_stats'] = {
                'cards_for': 14,
                'cards_against': 13,
                'goals_for': 22,
                'goals_against': 20
            }
        
        return mock_match
    
    def get_processing_summary(self, results: Dict[str, Any]) -> str:
        """
        Gera resumo do processamento
        
        Args:
            results: Resultados do processamento
            
        Returns:
            String com resumo formatado
        """
        summary = f"""
╔════════════════════════════════════════════════════════════╗
║           RESUMO DO PROCESSAMENTO EM LOTE                 ║
╠════════════════════════════════════════════════════════════╣
║ Total de Matches:        {results['total']:>3}                        ║
║ Processados com Sucesso: {results['successful']:>3} ✅                      ║
║ Falhados:               {results['failed']:>3} ❌                      ║
║ Taxa de Sucesso:        {(results['successful']/results['total']*100):>5.1f}%                    ║
╠════════════════════════════════════════════════════════════╣
║ Tempo Total:            {results['processing_time']:>6.2f}s                  ║
║ Tempo Médio/Match:      {results['avg_time_per_match']:>6.2f}s                  ║
║ Velocidade:             {results['total']/results['processing_time']:>6.1f} matches/s          ║
╠════════════════════════════════════════════════════════════╣
║ Início:  {results['start_time'][:19]}                    ║
║ Fim:     {results['end_time'][:19]}                    ║
╚════════════════════════════════════════════════════════════╝
"""
        return summary
    
    def export_results_to_json(
        self,
        results: Dict[str, Any],
        filepath: str
    ) -> None:
        """
        Exporta resultados para JSON
        
        Args:
            results: Resultados do processamento
            filepath: Caminho do arquivo
        """
        import json
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Resultados exportados para {filepath}")
    
    def export_results_to_csv(
        self,
        results: Dict[str, Any],
        filepath: str
    ) -> None:
        """
        Exporta resultados para CSV
        
        Args:
            results: Resultados do processamento
            filepath: Caminho do arquivo
        """
        import csv
        
        if not results['matches']:
            self.logger.warning("Nenhum match para exportar")
            return
        
        # Extrair campos
        fieldnames = ['home_team', 'away_team', 'xg_home', 'xg_away', 'status', 'brasilia_time']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for match in results['matches']:
                row = {
                    'home_team': match.get('home_team', ''),
                    'away_team': match.get('away_team', ''),
                    'xg_home': match.get('xG_home', ''),
                    'xg_away': match.get('xG_away', ''),
                    'status': match.get('match_time', {}).get('status', ''),
                    'brasilia_time': match.get('match_time', {}).get('brasilia_time', '')
                }
                writer.writerow(row)
        
        self.logger.info(f"Resultados exportados para {filepath}")


# Exemplo de uso
if __name__ == "__main__":
    import json
    
    # Dados de exemplo
    sample_matches = [
        {
            'home_team': 'Flamengo',
            'away_team': 'Vasco',
            'home_stats': {'cards_for': 15, 'cards_against': 12, 'goals_for': 25, 'goals_against': 18},
            'away_stats': {'cards_for': 14, 'cards_against': 13, 'goals_for': 22, 'goals_against': 20},
            'h2h_data': {},
            'referee_key': 'anderson_daronco',
            'utc_timestamp': int(time.time()) + 86400,
            'competition': 'brasileirao'
        },
        {
            'home_team': 'Botafogo',
            'away_team': 'Palmeiras',
            'home_stats': {'cards_for': 12, 'cards_against': 14, 'goals_for': 20, 'goals_against': 22},
            'away_stats': {'cards_for': 16, 'cards_against': 11, 'goals_for': 28, 'goals_against': 16},
            'h2h_data': {},
            'referee_key': 'raphael_claus',
            'utc_timestamp': int(time.time()) + 86400 + 7200,
            'competition': 'brasileirao'
        },
        {
            'home_team': 'São Paulo',
            'away_team': 'Corinthians',
            'home_stats': {'cards_for': 14, 'cards_against': 13, 'goals_for': 23, 'goals_against': 19},
            'away_stats': {'cards_for': 13, 'cards_against': 14, 'goals_for': 21, 'goals_against': 21},
            'h2h_data': {},
            'referee_key': 'wilton_pereira_sampaio',
            'utc_timestamp': int(time.time()) + 86400 + 14400,
            'competition': 'brasileirao'
        }
    ]
    
    # Processar rodada
    processor = BatchMatchProcessor(max_workers=2)
    results = processor.process_round(sample_matches, competition='brasileirao')
    
    # Exibir resumo
    print(processor.get_processing_summary(results))
    
    # Exibir erros se houver
    if results['errors']:
        print("\n❌ ERROS:")
        for error in results['errors']:
            print(f"  - {error['match']}: {error['error']}")