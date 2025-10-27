from typing import Dict

class BrasileiraoCalibrator:
    """Aplica calibrações específicas do Brasileirão"""
    
    @staticmethod
    def calibrate_btts(p_btts: float) -> float:
        """
        Calibra BTTS (ambos marcam)
        
        Brasileirão tem apenas 36% BTTS real, modelos superestimam
        """
        if p_btts > 0.50:
            return p_btts * 0.85
        return p_btts
    
    @staticmethod
    def calibrate_over25(p_over25: float) -> float:
        """Calibra Over 2.5 gols"""
        if p_over25 > 0.60:
            return p_over25 * 0.88
        return p_over25
    
    @staticmethod
    def calibrate_cards(p_cards: Dict[str, float]) -> Dict[str, float]:
        """
        Calibra probabilidades de cartões
        
        Aplica redução de 10% (modelos superestimam)
        """
        calibrated = {}
        for key, value in p_cards.items():
            if key.startswith('p_over'):
                calibrated[key] = value * 0.90
            else:
                calibrated[key] = value
        return calibrated
    
    @staticmethod
    def calibrate_corners(p_corners: Dict[str, float]) -> Dict[str, float]:
        """
        Calibra escanteios
        
        Brasileirão tem MUITO menos escanteios, redução de 20%
        """
        calibrated = {}
        for key, value in p_corners.items():
            if key.startswith('p_over'):
                calibrated[key] = value * 0.80
            else:
                calibrated[key] = value
        return calibrated
    
    @staticmethod
    def get_travel_factor(distance_km: float) -> float:
        """
        Calcula fator de viagem baseado em distância
        
        Args:
            distance_km: Distância entre cidades
            
        Returns:
            Fator multiplicativo para λ_away
        """
        if distance_km < 500:
            return 1.00
        elif distance_km < 1500:
            return 0.95
        elif distance_km < 2500:
            return 0.88
        else:
            return 0.82
    
    @staticmethod
    def get_altitude_factor(altitude_m: float) -> float:
        """
        Calcula fator de altitude
        
        Args:
            altitude_m: Altitude do estádio em metros
            
        Returns:
            Fator multiplicativo para λ_away
        """
        if altitude_m < 500:
            return 1.00
        elif altitude_m < 1000:
            return 0.97
        else:
            return 0.90
    
    @staticmethod
    def get_classic_bonus(match_type: str) -> float:
        """
        Bônus para clássicos e derbies
        
        Args:
            match_type: 'normal', 'classic', 'derby'
            
        Returns:
            Valor a ADICIONAR no λ_home
        """
        bonuses = {
            'normal': 0.0,
            'classic': 0.4,  # Ex: Fla-Flu, Gre-Nal
            'derby': 0.5,    # Ex: Ba-Vi
        }
        return bonuses.get(match_type, 0.0)
    
    @staticmethod
    def get_cards_bonus_classic(match_type: str) -> float:
        """
        Cartões extras em clássicos
        
        Returns:
            Valor a ADICIONAR no λ_cards_total
        """
        bonuses = {
            'normal': 0.0,
            'classic': 1.2,
            'derby': 1.5,
        }
        return bonuses.get(match_type, 0.0)