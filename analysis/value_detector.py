from typing import Dict, List

class ValueBetDetector:
    """Identifica apostas com valor positivo (edge)"""
    
    def __init__(self):
        # Thresholds de edge mínimo (Brasileirão)
        self.min_edge = {
            'goals': 0.05,      # 5%
            'cards': 0.06,      # 6%
            'corners': 0.07,    # 7%
        }
        
        # Stakes máximos
        self.max_stake = {
            'goals': 0.04,      # 4% bankroll
            'cards': 0.03,      # 3%
            'corners': 0.025,   # 2.5%
        }
    
    def calculate_edge(
        self,
        p_model: float,
        odd_market: float
    ) -> float:
        """
        Calcula edge (vantagem sobre o mercado)
        
        Args:
            p_model: Probabilidade do nosso modelo
            odd_market: Odd oferecida pelo mercado
            
        Returns:
            Edge (positivo = value bet)
        """
        p_implied = 1 / odd_market
        edge = p_model - p_implied
        return edge
    
    def calculate_kelly(
        self,
        p_model: float,
        odd_market: float,
        kelly_fraction: float = 0.25
    ) -> float:
        """
        Calcula stake usando Kelly Criterion
        
        Args:
            p_model: Probabilidade do modelo
            odd_market: Odd do mercado
            kelly_fraction: Fração conservadora (0.25 = 25% Kelly)
            
        Returns:
            Stake recomendado (% do bankroll)
        """
        b = odd_market - 1  # Lucro líquido
        q = 1 - p_model     # Probabilidade de perder
        
        if p_model * b > q:
            kelly = (p_model * b - q) / b
            return kelly * kelly_fraction
        else:
            return 0.0
    
    def find_value_bets(
        self,
        probs: Dict,
        odds: Dict
    ) -> List[Dict]:
        """
        Encontra todos value bets em um jogo
        
        Args:
            probs: Probabilidades do modelo
            odds: Odds do mercado
            
        Returns:
            Lista de value bets encontrados
        """
        value_bets = []
        
        # Mapear mercados
        markets = {
            'home_win': ('goals', probs.get('home_win'), odds.get('home')),
            'away_win': ('goals', probs.get('away_win'), odds.get('away')),
            'btts': ('goals', probs.get('btts'), odds.get('btts_yes')),
            'over_25': ('goals', probs.get('over_25'), odds.get('over_25')),
            'over_35': ('goals', probs.get('over_35'), odds.get('over_35')),
            'over_cards_45': ('cards', probs.get('cards', {}).get('p_over_45'), 
                              odds.get('cards_over_45')),
            'over_corners_75': ('corners', probs.get('corners', {}).get('p_over_75'),
                                odds.get('corners_over_75')),
        }
        
        for market_name, (category, p_model, odd) in markets.items():
            if p_model is None or odd is None:
                continue
            
            edge = self.calculate_edge(p_model, odd)
            
            # Verificar se atende threshold
            if edge >= self.min_edge[category]:
                stake = self.calculate_kelly(p_model, odd)
                
                # Aplicar stake máximo
                stake = min(stake, self.max_stake[category])
                
                # Calcular ROI esperado
                roi = edge * 100
                
                value_bets.append({
                    'market': market_name,
                    'category': category,
                    'p_model': p_model,
                    'odd': odd,
                    'edge': edge,
                    'stake_pct': stake * 100,
                    'expected_roi': roi,
                    'confidence': self._calculate_confidence(edge, category),
                })
        
        # Ordenar por edge
        value_bets.sort(key=lambda x: x['edge'], reverse=True)
        
        return value_bets
    
    def _calculate_confidence(self, edge: float, category: str) -> str:
        """Calcula nível de confiança"""
        threshold = self.min_edge[category]
        
        if edge >= threshold * 2.5:
            return "ALTA"
        elif edge >= threshold * 1.5:
            return "MÉDIA-ALTA"
        elif edge >= threshold:
            return "MÉDIA"
        else:
            return "BAIXA"