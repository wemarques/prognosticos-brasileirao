"""
Coletor de Odds usando The Odds API
Busca odds reais de casas de apostas
"""

import requests
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
from datetime import datetime

load_dotenv()

class OddsCollector:
    """Coleta odds reais de casas de apostas"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        self.base_url = "https://api.the-odds-api.com/v4"
        self.sport_key = "soccer_brazil_campeonato"  # Brasileirão
        self.regions = "us,uk,eu"  # Múltiplas regiões
        self.odds_format = "decimal"  # Formato decimal (ex: 2.50)
    
    def get_upcoming_matches(self) -> List[Dict]:
        """
        Busca próximos jogos com odds
        
        Returns:
            Lista de jogos com odds
        """
        endpoint = f"{self.base_url}/sports/{self.sport_key}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': self.regions,
            'oddsFormat': self.odds_format,
            'markets': 'h2h,totals'  # 1X2 e Over/Under
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro ao buscar odds: {e}")
            return []
    
    def get_match_odds(
        self, 
        home_team: str, 
        away_team: str
    ) -> Optional[Dict]:
        """
        Busca odds de um jogo específico
        
        Args:
            home_team: Nome do time mandante
            away_team: Nome do time visitante
            
        Returns:
            Dict com odds do jogo ou None
        """
        matches = self.get_upcoming_matches()
        
        for match in matches:
            if (self._normalize_team_name(match['home_team']) == self._normalize_team_name(home_team) and
                self._normalize_team_name(match['away_team']) == self._normalize_team_name(away_team)):
                return self._process_match_odds(match)
        
        return None
    
    def _normalize_team_name(self, name: str) -> str:
        """Normaliza nome do time para comparação"""
        # Remover acentos e converter para minúsculas
        import unicodedata
        normalized = unicodedata.normalize('NFKD', name)
        normalized = normalized.encode('ASCII', 'ignore').decode('ASCII')
        return normalized.lower().strip()
    
    def _process_match_odds(self, match: Dict) -> Dict:
        """
        Processa odds de um jogo
        
        Args:
            match: Dados brutos do jogo
            
        Returns:
            Dict com odds processadas
        """
        result = {
            'match_id': match['id'],
            'home_team': match['home_team'],
            'away_team': match['away_team'],
            'commence_time': match['commence_time'],
            'bookmakers': [],
            'best_odds': {
                'home_win': 0,
                'draw': 0,
                'away_win': 0,
                'over_25': 0,
                'under_25': 0
            },
            'average_odds': {
                'home_win': 0,
                'draw': 0,
                'away_win': 0,
                'over_25': 0,
                'under_25': 0
            }
        }
        
        # Coletar odds de todas as casas
        home_odds_list = []
        draw_odds_list = []
        away_odds_list = []
        over_25_list = []
        under_25_list = []
        
        for bookmaker in match.get('bookmakers', []):
            bookmaker_data = {
                'name': bookmaker['title'],
                'last_update': bookmaker['last_update'],
                'odds': {}
            }
            
            # Processar mercado H2H (1X2)
            for market in bookmaker.get('markets', []):
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == match['home_team']:
                            bookmaker_data['odds']['home_win'] = outcome['price']
                            home_odds_list.append(outcome['price'])
                        elif outcome['name'] == match['away_team']:
                            bookmaker_data['odds']['away_win'] = outcome['price']
                            away_odds_list.append(outcome['price'])
                        else:  # Draw
                            bookmaker_data['odds']['draw'] = outcome['price']
                            draw_odds_list.append(outcome['price'])
                
                # Processar mercado Totals (Over/Under)
                elif market['key'] == 'totals':
                    for outcome in market['outcomes']:
                        # Procurar Over/Under 2.5
                        if outcome.get('point') == 2.5:
                            if outcome['name'] == 'Over':
                                bookmaker_data['odds']['over_25'] = outcome['price']
                                over_25_list.append(outcome['price'])
                            elif outcome['name'] == 'Under':
                                bookmaker_data['odds']['under_25'] = outcome['price']
                                under_25_list.append(outcome['price'])
            
            result['bookmakers'].append(bookmaker_data)
        
        # Calcular melhores odds (maiores valores)
        if home_odds_list:
            result['best_odds']['home_win'] = max(home_odds_list)
            result['average_odds']['home_win'] = sum(home_odds_list) / len(home_odds_list)
        
        if draw_odds_list:
            result['best_odds']['draw'] = max(draw_odds_list)
            result['average_odds']['draw'] = sum(draw_odds_list) / len(draw_odds_list)
        
        if away_odds_list:
            result['best_odds']['away_win'] = max(away_odds_list)
            result['average_odds']['away_win'] = sum(away_odds_list) / len(away_odds_list)
        
        if over_25_list:
            result['best_odds']['over_25'] = max(over_25_list)
            result['average_odds']['over_25'] = sum(over_25_list) / len(over_25_list)
        
        if under_25_list:
            result['best_odds']['under_25'] = max(under_25_list)
            result['average_odds']['under_25'] = sum(under_25_list) / len(under_25_list)
        
        return result
    
    def convert_odds_to_probability(self, odds: float) -> float:
        """
        Converte odds decimal para probabilidade implícita
        
        Args:
            odds: Odds em formato decimal (ex: 2.50)
            
        Returns:
            Probabilidade implícita (0-1)
        """
        if odds <= 0:
            return 0
        
        return 1 / odds
    
    def get_market_probabilities(self, odds_data: Dict) -> Dict:
        """
        Converte odds em probabilidades implícitas
        
        Args:
            odds_data: Dict com odds processadas
            
        Returns:
            Dict com probabilidades
        """
        avg_odds = odds_data['average_odds']
        
        # Converter odds para probabilidades
        probs = {
            'home_win': self.convert_odds_to_probability(avg_odds['home_win']) if avg_odds['home_win'] > 0 else 0,
            'draw': self.convert_odds_to_probability(avg_odds['draw']) if avg_odds['draw'] > 0 else 0,
            'away_win': self.convert_odds_to_probability(avg_odds['away_win']) if avg_odds['away_win'] > 0 else 0,
            'over_25': self.convert_odds_to_probability(avg_odds['over_25']) if avg_odds['over_25'] > 0 else 0,
            'under_25': self.convert_odds_to_probability(avg_odds['under_25']) if avg_odds['under_25'] > 0 else 0
        }
        
        # Normalizar probabilidades 1X2 (remover margem da casa)
        total_1x2 = probs['home_win'] + probs['draw'] + probs['away_win']
        if total_1x2 > 0:
            probs['home_win'] /= total_1x2
            probs['draw'] /= total_1x2
            probs['away_win'] /= total_1x2
        
        # Normalizar Over/Under
        total_ou = probs['over_25'] + probs['under_25']
        if total_ou > 0:
            probs['over_25'] /= total_ou
            probs['under_25'] /= total_ou
        
        return probs
    
    def get_usage_quota(self) -> Dict:
        """
        Verifica quota de uso da API
        
        Returns:
            Dict com informações de uso
        """
        # The Odds API retorna info de quota nos headers
        # Fazer uma requisição simples para pegar headers
        endpoint = f"{self.base_url}/sports"
        params = {'apiKey': self.api_key}
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            
            return {
                'requests_remaining': response.headers.get('x-requests-remaining', 'N/A'),
                'requests_used': response.headers.get('x-requests-used', 'N/A'),
                'requests_last': response.headers.get('x-requests-last', 'N/A')
            }
        except Exception as e:
            print(f"Erro ao verificar quota: {e}")
            return {}


# Exemplo de uso
if __name__ == "__main__":
    collector = OddsCollector()
    
    # Buscar próximos jogos
    print("🔍 Buscando próximos jogos com odds...")
    matches = collector.get_upcoming_matches()
    
    if matches:
        print(f"\n✅ {len(matches)} jogos encontrados:")
        for match in matches[:3]:
            print(f"\n  {match['home_team']} vs {match['away_team']}")
            print(f"  Data: {match['commence_time']}")
            print(f"  Casas: {len(match.get('bookmakers', []))} bookmakers")
    
    # Verificar quota
    quota = collector.get_usage_quota()
    print(f"\n📊 Quota API:")
    print(f"  Restantes: {quota.get('requests_remaining', 'N/A')}")
    print(f"  Usadas: {quota.get('requests_used', 'N/A')}")

