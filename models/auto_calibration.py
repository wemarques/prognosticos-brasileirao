"""
Sistema de Auto-Calibração do Modelo
Ajusta parâmetros automaticamente baseado em resultados reais
"""

import json
import os
from typing import Dict, List
from datetime import datetime

class ModelCalibrator:
    """Calibra modelo automaticamente baseado em feedback"""
    
    def __init__(self, config_path: str = "models/calibration_config.json"):
        self.config_path = config_path
        self.parameters = self._load_parameters()
        self.adjustment_history = []
    
    def _load_parameters(self) -> Dict:
        """Carrega parâmetros atuais do modelo"""
        default_params = {
            'hfa': 1.53,  # Home Field Advantage
            'xg_home_multiplier': 1.0,
            'xg_away_multiplier': 1.0,
            'correlation': -0.11,
            'avg_goals_per_team': 1.82,
            'btts_threshold': 0.5,
            'over_under_threshold': 0.5,
            'calibration_factor': 1.0,
            'last_updated': datetime.now().isoformat(),
            'total_adjustments': 0
        }
        
        # Tentar carregar de arquivo
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    default_params.update(loaded)
            except Exception as e:
                print(f"Erro ao carregar config: {e}")
        
        return default_params
    
    def _save_parameters(self):
        """Salva parâmetros atualizados"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.parameters, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar config: {e}")
    
    def apply_adjustments(self, suggestions: List[Dict]) -> Dict:
        """
        Aplica ajustes sugeridos ao modelo
        
        Args:
            suggestions: Lista de sugestões de ajuste
            
        Returns:
            Dict com parâmetros atualizados
        """
        if not suggestions:
            return self.parameters
        
        adjustments_made = []
        
        for suggestion in suggestions:
            param = suggestion['parameter']
            priority = suggestion.get('priority', 'LOW')
            
            # Aplicar apenas ajustes de prioridade MEDIUM ou HIGH
            if priority not in ['MEDIUM', 'HIGH']:
                continue
            
            # Ajustar HFA
            if param == 'HFA':
                old_value = self.parameters['hfa']
                new_value = suggestion['suggested_value']
                
                # Limitar mudanças drásticas
                max_change = 0.1
                if abs(new_value - old_value) > max_change:
                    new_value = old_value + (max_change if new_value > old_value else -max_change)
                
                self.parameters['hfa'] = round(new_value, 3)
                
                adjustments_made.append({
                    'parameter': 'HFA',
                    'old_value': old_value,
                    'new_value': self.parameters['hfa'],
                    'reason': suggestion['reason'],
                    'timestamp': datetime.now().isoformat()
                })
            
            # Ajustar xG multipliers
            elif param == 'xG_home':
                old_value = self.parameters['xg_home_multiplier']
                new_value = suggestion['suggested_multiplier']
                
                # Limitar entre 0.8 e 1.2
                new_value = max(0.8, min(1.2, new_value))
                
                self.parameters['xg_home_multiplier'] = round(new_value, 3)
                
                adjustments_made.append({
                    'parameter': 'xG_home_multiplier',
                    'old_value': old_value,
                    'new_value': self.parameters['xg_home_multiplier'],
                    'reason': suggestion['reason'],
                    'timestamp': datetime.now().isoformat()
                })
            
            elif param == 'xG_away':
                old_value = self.parameters['xg_away_multiplier']
                new_value = suggestion['suggested_multiplier']
                
                # Limitar entre 0.8 e 1.2
                new_value = max(0.8, min(1.2, new_value))
                
                self.parameters['xg_away_multiplier'] = round(new_value, 3)
                
                adjustments_made.append({
                    'parameter': 'xG_away_multiplier',
                    'old_value': old_value,
                    'new_value': self.parameters['xg_away_multiplier'],
                    'reason': suggestion['reason'],
                    'timestamp': datetime.now().isoformat()
                })
            
            # Ajustar calibração geral
            elif param == 'calibration':
                action = suggestion.get('action', '')
                
                if action == 'increase_uncertainty':
                    old_value = self.parameters['calibration_factor']
                    # Reduzir confiança em 5%
                    new_value = old_value * 0.95
                    new_value = max(0.7, min(1.3, new_value))
                    
                    self.parameters['calibration_factor'] = round(new_value, 3)
                    
                    adjustments_made.append({
                        'parameter': 'calibration_factor',
                        'old_value': old_value,
                        'new_value': self.parameters['calibration_factor'],
                        'reason': suggestion['reason'],
                        'timestamp': datetime.now().isoformat()
                    })
        
        # Atualizar metadados
        if adjustments_made:
            self.parameters['last_updated'] = datetime.now().isoformat()
            self.parameters['total_adjustments'] = self.parameters.get('total_adjustments', 0) + len(adjustments_made)
            
            # Salvar histórico
            self.adjustment_history.extend(adjustments_made)
            
            # Salvar parâmetros
            self._save_parameters()
        
        return {
            'parameters': self.parameters,
            'adjustments_made': adjustments_made,
            'total_adjustments': len(adjustments_made)
        }
    
    def get_current_parameters(self) -> Dict:
        """Retorna parâmetros atuais"""
        return self.parameters.copy()
    
    def reset_to_defaults(self):
        """Reseta parâmetros para valores padrão"""
        self.parameters = {
            'hfa': 1.53,
            'xg_home_multiplier': 1.0,
            'xg_away_multiplier': 1.0,
            'correlation': -0.11,
            'avg_goals_per_team': 1.82,
            'btts_threshold': 0.5,
            'over_under_threshold': 0.5,
            'calibration_factor': 1.0,
            'last_updated': datetime.now().isoformat(),
            'total_adjustments': 0
        }
        self._save_parameters()
    
    def get_adjustment_history(self, limit: int = 10) -> List[Dict]:
        """
        Retorna histórico de ajustes
        
        Args:
            limit: Número máximo de ajustes a retornar
            
        Returns:
            Lista de ajustes recentes
        """
        return self.adjustment_history[-limit:]
    
    def apply_parameters_to_model(self, base_xg_home: float, base_xg_away: float) -> Dict:
        """
        Aplica parâmetros calibrados aos xG base
        
        Args:
            base_xg_home: xG base do mandante
            base_xg_away: xG base do visitante
            
        Returns:
            Dict com xG ajustados
        """
        adjusted_xg_home = base_xg_home * self.parameters['xg_home_multiplier'] * self.parameters['hfa']
        adjusted_xg_away = base_xg_away * self.parameters['xg_away_multiplier']
        
        return {
            'xg_home': round(adjusted_xg_home, 3),
            'xg_away': round(adjusted_xg_away, 3),
            'hfa_applied': self.parameters['hfa'],
            'multipliers': {
                'home': self.parameters['xg_home_multiplier'],
                'away': self.parameters['xg_away_multiplier']
            }
        }
    
    def get_calibration_report(self) -> Dict:
        """
        Gera relatório de calibração
        
        Returns:
            Dict com status da calibração
        """
        return {
            'current_parameters': self.parameters,
            'total_adjustments': self.parameters.get('total_adjustments', 0),
            'last_updated': self.parameters.get('last_updated', 'Never'),
            'recent_adjustments': self.get_adjustment_history(5),
            'status': 'CALIBRATED' if self.parameters.get('total_adjustments', 0) > 0 else 'DEFAULT'
        }


# Exemplo de uso
if __name__ == "__main__":
    calibrator = ModelCalibrator()
    
    # Exemplo de sugestões
    suggestions = [
        {
            'parameter': 'HFA',
            'current_value': 1.53,
            'suggested_value': 1.48,
            'reason': 'Modelo superestima vantagem do mandante',
            'priority': 'HIGH'
        },
        {
            'parameter': 'xG_home',
            'current_multiplier': 1.0,
            'suggested_multiplier': 0.95,
            'reason': 'Modelo superestima gols do mandante em 0.6 gols',
            'priority': 'MEDIUM'
        }
    ]
    
    # Aplicar ajustes
    result = calibrator.apply_adjustments(suggestions)
    
    print("🔧 Ajustes Aplicados:")
    for adj in result['adjustments_made']:
        print(f"  {adj['parameter']}: {adj['old_value']} → {adj['new_value']}")
        print(f"  Razão: {adj['reason']}")
    
    # Ver parâmetros atuais
    print("\n📊 Parâmetros Atuais:")
    params = calibrator.get_current_parameters()
    print(f"  HFA: {params['hfa']}")
    print(f"  xG Home Mult: {params['xg_home_multiplier']}")
    print(f"  xG Away Mult: {params['xg_away_multiplier']}")

