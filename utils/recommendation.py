"""
Gerador de Recomendação Oficial
Analisa todos os mercados e sugere a melhor aposta
"""

from typing import Dict, List, Tuple

def generate_official_recommendation(
    prognosis: Dict,
    value_bets: List[Dict],
    home_team: str,
    away_team: str
) -> Dict:
    """
    Gera recomendação oficial do sistema
    
    Args:
        prognosis: Dicionário com todas as probabilidades
        value_bets: Lista de value bets detectados
        home_team: Nome do time mandante
        away_team: Nome do time visitante
    
    Returns:
        Dict com recomendação, confiança e justificativa
    """
    
    probs = prognosis['probabilities']
    exp_goals = prognosis['expected_goals']
    
    recommendations = []
    
    # 1. Analisar Value Bets (prioridade máxima)
    if value_bets:
        best_value = value_bets[0]  # Já vem ordenado por edge
        
        recommendations.append({
            'market': best_value['market'],
            'recommendation': _format_market_name(best_value['market'], home_team, away_team),
            'confidence': 'MUITO ALTA' if best_value['edge'] > 0.10 else 'ALTA',
            'confidence_score': min(95, 70 + best_value['edge'] * 100),
            'reason': f"Value bet detectado com edge de {best_value['edge']*100:.1f}%. "
                     f"Probabilidade real ({best_value['true_prob']*100:.1f}%) "
                     f"significativamente maior que odds sugerem.",
            'stake': f"{best_value['stake_pct']:.1f}% do bankroll",
            'expected_roi': f"{best_value['expected_roi']:.1f}%",
            'priority': 1
        })
    
    # 2. Analisar Resultado Final (1X2)
    max_prob_1x2 = max(probs['home_win'], probs['draw'], probs['away_win'])
    
    if max_prob_1x2 > 0.50:  # Alta probabilidade
        if probs['home_win'] == max_prob_1x2:
            market_name = f"Vitória {home_team}"
            reason = f"{home_team} tem {probs['home_win']*100:.1f}% de probabilidade de vencer. "
        elif probs['away_win'] == max_prob_1x2:
            market_name = f"Vitória {away_team}"
            reason = f"{away_team} tem {probs['away_win']*100:.1f}% de probabilidade de vencer. "
        else:
            market_name = "Empate"
            reason = f"Empate tem {probs['draw']*100:.1f}% de probabilidade. "
        
        reason += f"Gols esperados: {home_team} {exp_goals['home']:.2f} x {exp_goals['away']:.2f} {away_team}."
        
        recommendations.append({
            'market': '1X2',
            'recommendation': market_name,
            'confidence': 'ALTA' if max_prob_1x2 > 0.55 else 'MÉDIA-ALTA',
            'confidence_score': max_prob_1x2 * 100,
            'reason': reason,
            'stake': "2-3% do bankroll",
            'expected_roi': f"{(max_prob_1x2 - 0.5) * 100:.1f}%",
            'priority': 2 if value_bets else 1
        })
    
    # 3. Analisar Over/Under
    total_expected = exp_goals['total']
    
    if total_expected > 2.7:  # Jogo com muitos gols esperados
        if probs.get('over_25', 0) > 0.60:
            recommendations.append({
                'market': 'Over/Under',
                'recommendation': 'Over 2.5 gols',
                'confidence': 'ALTA' if probs['over_25'] > 0.65 else 'MÉDIA',
                'confidence_score': probs['over_25'] * 100,
                'reason': f"Expectativa de {total_expected:.2f} gols totais. "
                         f"Probabilidade de Over 2.5: {probs['over_25']*100:.1f}%.",
                'stake': "2% do bankroll",
                'expected_roi': f"{(probs['over_25'] - 0.5) * 100:.1f}%",
                'priority': 3
            })
    elif total_expected < 2.2:  # Jogo com poucos gols
        under_25_prob = 1 - probs.get('over_25', 0.5)
        if under_25_prob > 0.55:
            recommendations.append({
                'market': 'Over/Under',
                'recommendation': 'Under 2.5 gols',
                'confidence': 'MÉDIA',
                'confidence_score': under_25_prob * 100,
                'reason': f"Expectativa de apenas {total_expected:.2f} gols totais. "
                         f"Probabilidade de Under 2.5: {under_25_prob*100:.1f}%.",
                'stake': "1-2% do bankroll",
                'expected_roi': f"{(under_25_prob - 0.5) * 100:.1f}%",
                'priority': 3
            })
    
    # 4. Analisar BTTS
    btts_prob = probs.get('btts', 0.5)
    
    if btts_prob > 0.60:
        recommendations.append({
            'market': 'BTTS',
            'recommendation': 'Ambos Marcam - SIM',
            'confidence': 'MÉDIA-ALTA' if btts_prob > 0.65 else 'MÉDIA',
            'confidence_score': btts_prob * 100,
            'reason': f"Ambos times têm ataque forte. "
                     f"Probabilidade de BTTS: {btts_prob*100:.1f}%. "
                     f"{home_team} espera {exp_goals['home']:.2f} gols, "
                     f"{away_team} espera {exp_goals['away']:.2f} gols.",
            'stake': "1-2% do bankroll",
            'expected_roi': f"{(btts_prob - 0.5) * 100:.1f}%",
            'priority': 4
        })
    elif btts_prob < 0.40:
        recommendations.append({
            'market': 'BTTS',
            'recommendation': 'Ambos Marcam - NÃO',
            'confidence': 'MÉDIA',
            'confidence_score': (1 - btts_prob) * 100,
            'reason': f"Pelo menos um time tem defesa sólida ou ataque fraco. "
                     f"Probabilidade de BTTS NÃO: {(1-btts_prob)*100:.1f}%.",
            'stake': "1% do bankroll",
            'expected_roi': f"{(0.6 - btts_prob) * 100:.1f}%",
            'priority': 4
        })
    
    # 5. Placar Exato (se houver placar muito provável)
    if prognosis.get('top_scores'):
        top_score = prognosis['top_scores'][0]
        if top_score['probability'] > 0.15:  # Placar com >15% de chance
            recommendations.append({
                'market': 'Placar Exato',
                'recommendation': f"Placar {top_score['score']}",
                'confidence': 'MÉDIA',
                'confidence_score': top_score['probability'] * 100,
                'reason': f"Placar mais provável: {top_score['score']} "
                         f"com {top_score['probability']*100:.1f}% de chance.",
                'stake': "0.5-1% do bankroll (risco alto)",
                'expected_roi': "Alto (odds geralmente >6.0)",
                'priority': 5
            })
    
    # Ordenar por prioridade e confiança
    recommendations.sort(key=lambda x: (x['priority'], -x['confidence_score']))
    
    # Retornar melhor recomendação
    if recommendations:
        best = recommendations[0]
        
        # Adicionar alternativas
        alternatives = recommendations[1:3] if len(recommendations) > 1 else []
        
        return {
            'main': best,
            'alternatives': alternatives,
            'total_recommendations': len(recommendations)
        }
    else:
        # Fallback: sem recomendação forte
        return {
            'main': {
                'market': 'Nenhum',
                'recommendation': 'Aguardar melhores oportunidades',
                'confidence': 'BAIXA',
                'confidence_score': 0,
                'reason': 'Nenhum mercado apresenta edge significativo neste momento. '
                         'Recomenda-se aguardar por jogos com probabilidades mais claras.',
                'stake': '0% do bankroll',
                'expected_roi': '0%',
                'priority': 99
            },
            'alternatives': [],
            'total_recommendations': 0
        }


def _format_market_name(market: str, home_team: str, away_team: str) -> str:
    """Formata nome do mercado para exibição"""
    
    market_lower = market.lower()
    
    if 'home' in market_lower or 'mandante' in market_lower:
        return f"Vitória {home_team}"
    elif 'away' in market_lower or 'visitante' in market_lower:
        return f"Vitória {away_team}"
    elif 'draw' in market_lower or 'empate' in market_lower:
        return "Empate"
    elif 'over' in market_lower:
        return market.replace('_', ' ').title()
    elif 'btts' in market_lower:
        return "Ambos Marcam - SIM"
    else:
        return market.replace('_', ' ').title()


def get_confidence_color(confidence: str) -> str:
    """Retorna cor para o nível de confiança"""
    
    if confidence in ['MUITO ALTA', 'ALTA']:
        return '#28a745'  # Verde
    elif confidence in ['MÉDIA-ALTA', 'MÉDIA']:
        return '#ffc107'  # Amarelo
    else:
        return '#dc3545'  # Vermelho

