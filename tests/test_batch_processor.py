"""
Testes para BatchMatchProcessor
"""
import pytest
import time
from analysis.batch_processor import BatchMatchProcessor


class TestBatchMatchProcessor:
    """Testes para o processador em lote"""
    
    @pytest.fixture
    def processor(self):
        """Fixture para criar um processador"""
        return BatchMatchProcessor(max_workers=2, max_retries=2)
    
    @pytest.fixture
    def sample_matches(self):
        """Fixture com matches de exemplo"""
        return [
            {
                'home_team': 'Flamengo',
                'away_team': 'Vasco',
                'home_stats': {'cards_for': 15, 'cards_against': 12},
                'away_stats': {'cards_for': 14, 'cards_against': 13},
                'h2h_data': {},
                'referee_key': 'anderson_daronco',
                'utc_timestamp': int(time.time()) + 86400,
                'competition': 'brasileirao'
            },
            {
                'home_team': 'Botafogo',
                'away_team': 'Palmeiras',
                'home_stats': {'cards_for': 12, 'cards_against': 14},
                'away_stats': {'cards_for': 16, 'cards_against': 11},
                'h2h_data': {},
                'referee_key': 'raphael_claus',
                'utc_timestamp': int(time.time()) + 86400 + 7200,
                'competition': 'brasileirao'
            }
        ]
    
    def test_processor_initialization(self, processor):
        """Testa inicialização do processador"""
        assert processor.max_workers == 2
        assert processor.max_retries == 2
        assert processor.processor is not None
    
    def test_validate_match_data_valid(self, processor):
        """Testa validação com dados válidos"""
        match = {
            'home_team': 'Flamengo',
            'away_team': 'Vasco',
            'home_stats': {},
            'away_stats': {}
        }
        # Não deve lançar exceção
        processor._validate_match_data(match)
    
    def test_validate_match_data_missing_home_team(self, processor):
        """Testa validação com home_team faltando"""
        match = {
            'away_team': 'Vasco',
            'home_stats': {},
            'away_stats': {}
        }
        with pytest.raises(ValueError):
            processor._validate_match_data(match)
    
    def test_validate_match_data_missing_away_team(self, processor):
        """Testa validação com away_team faltando"""
        match = {
            'home_team': 'Flamengo',
            'home_stats': {},
            'away_stats': {}
        }
        with pytest.raises(ValueError):
            processor._validate_match_data(match)
    
    def test_validate_match_data_invalid_stats(self, processor):
        """Testa validação com stats inválido"""
        match = {
            'home_team': 'Flamengo',
            'away_team': 'Vasco',
            'home_stats': 'invalid',  # Deve ser dict
            'away_stats': {}
        }
        with pytest.raises(ValueError):
            processor._validate_match_data(match)
    
    def test_create_mock_match(self, processor):
        """Testa criação de match mock"""
        match = {
            'home_team': 'Flamengo',
            'away_team': 'Vasco'
        }
        mock_match = processor._create_mock_match(match)
        
        assert mock_match['home_team'] == 'Flamengo'
        assert mock_match['away_team'] == 'Vasco'
        assert 'home_stats' in mock_match
        assert 'away_stats' in mock_match
        assert isinstance(mock_match['home_stats'], dict)
        assert isinstance(mock_match['away_stats'], dict)
    
    def test_process_round_structure(self, processor, sample_matches):
        """Testa estrutura de resultados do processamento"""
        results = processor.process_round(sample_matches, show_progress=False)
        
        # Verificar estrutura
        assert 'successful' in results
        assert 'failed' in results
        assert 'total' in results
        assert 'matches' in results
        assert 'errors' in results
        assert 'processing_time' in results
        assert 'avg_time_per_match' in results
        assert 'start_time' in results
        assert 'end_time' in results
        
        # Verificar valores
        assert results['total'] == len(sample_matches)
        assert results['successful'] + results['failed'] == results['total']
        assert results['processing_time'] > 0
    
    def test_process_round_with_empty_list(self, processor):
        """Testa processamento com lista vazia"""
        results = processor.process_round([], show_progress=False)
        
        assert results['total'] == 0
        assert results['successful'] == 0
        assert results['failed'] == 0
        assert len(results['matches']) == 0
    
    def test_get_processing_summary(self, processor, sample_matches):
        """Testa geração de resumo"""
        results = processor.process_round(sample_matches, show_progress=False)
        summary = processor.get_processing_summary(results)
        
        assert 'RESUMO DO PROCESSAMENTO' in summary
        assert 'Total de Matches' in summary
        assert 'Processados com Sucesso' in summary
        assert 'Tempo Total' in summary
    
    def test_export_results_to_json(self, processor, sample_matches, tmp_path):
        """Testa exportação para JSON"""
        results = processor.process_round(sample_matches, show_progress=False)
        
        filepath = tmp_path / "results.json"
        processor.export_results_to_json(results, str(filepath))
        
        assert filepath.exists()
        
        # Verificar conteúdo
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert 'successful' in data
        assert 'failed' in data
        assert 'total' in data
    
    def test_export_results_to_csv(self, processor, sample_matches, tmp_path):
        """Testa exportação para CSV"""
        results = processor.process_round(sample_matches, show_progress=False)
        
        filepath = tmp_path / "results.csv"
        processor.export_results_to_csv(results, str(filepath))
        
        assert filepath.exists()
        
        # Verificar conteúdo
        import csv
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) > 0
        assert 'home_team' in rows[0]
        assert 'away_team' in rows[0]
    
    def test_process_round_performance(self, processor):
        """Testa performance do processamento"""
        # Criar 10 matches
        matches = []
        for i in range(10):
            matches.append({
                'home_team': f'Time{i}A',
                'away_team': f'Time{i}B',
                'home_stats': {'cards_for': 15, 'cards_against': 12},
                'away_stats': {'cards_for': 14, 'cards_against': 13},
                'h2h_data': {},
                'referee_key': 'anderson_daronco',
                'utc_timestamp': int(time.time()) + 86400 + (i * 3600),
                'competition': 'brasileirao'
            })
        
        results = processor.process_round(matches, show_progress=False)
        
        # Verificar que processou todos
        assert results['total'] == 10
        
        # Verificar performance (deve ser rápido com parallelização)
        # Esperamos menos de 30 segundos para 10 matches
        assert results['processing_time'] < 30
        
        # Verificar velocidade
        velocity = results['total'] / results['processing_time']
        assert velocity > 0.1  # Pelo menos 0.1 matches/segundo


class TestBatchProcessorIntegration:
    """Testes de integração"""
    
    def test_process_round_with_fallback(self):
        """Testa processamento com fallback para mock"""
        processor = BatchMatchProcessor(max_workers=2)
        
        matches = [
            {
                'home_team': 'Flamengo',
                'away_team': 'Vasco',
                # Dados incompletos para forçar erro
                'h2h_data': {},
                'referee_key': 'anderson_daronco',
                'utc_timestamp': int(time.time()) + 86400,
                'competition': 'brasileirao'
            }
        ]
        
        results = processor.process_round_with_fallback(matches, show_progress=False)
        
        # Deve ter processado com fallback
        assert results['total'] == 1
        assert results['successful'] + results['failed'] == 1
    
    def test_multiple_competitions(self):
        """Testa processamento de múltiplas competições"""
        processor = BatchMatchProcessor(max_workers=2)
        
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
                'competition': 'brasileirao'
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
                'referee_key': 'andre_marriner',
                'utc_timestamp': int(time.time()) + 86400,
                'competition': 'premier_league'
            }
        ]
        
        # Processar ambas
        br_results = processor.process_round(br_matches, competition='brasileirao', show_progress=False)
        pl_results = processor.process_round(pl_matches, competition='premier_league', show_progress=False)
        
        assert br_results['total'] == 1
        assert pl_results['total'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])