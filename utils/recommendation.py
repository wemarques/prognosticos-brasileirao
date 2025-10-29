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
    
    # 6. Analisar Cartões
    # Usar estatísticas de cartões se disponíveis
    cards_prob_over_35 = prognosis.get('cards', {}).get('over_35', 0)
    cards_prob_over_45 = prognosis.get('cards', {}).get('over_45', 0)
    
    if cards_prob_over_35 > 0.55:
        recommendations.append({
            'market': 'Cartões',
            'recommendation': 'Over 3.5 cartões',
            'confidence': 'MÉDIA' if cards_prob_over_35 > 0.60 else 'MÉDIA-BAIXA',
            'confidence_score': cards_prob_over_35 * 100,
            'reason': f"Jogo com tendência a muitas faltas. "
                     f"Probabilidade de Over 3.5 cartões: {cards_prob_over_35*100:.1f}%.",
            'stake': "1% do bankroll",
            'expected_roi': f"{(cards_prob_over_35 - 0.5) * 100:.1f}%",
            'priority': 5
        })
    
    if cards_prob_over_45 > 0.60:
        recommendations.append({
            'market': 'Cartões',
            'recommendation': 'Over 4.5 cartões',
            'confidence': 'MÉDIA-ALTA',
            'confidence_score': cards_prob_over_45 * 100,
            'reason': f"Jogo muito disputado com muitas faltas esperadas. "
                     f"Probabilidade de Over 4.5 cartões: {cards_prob_over_45*100:.1f}%.",
            'stake': "1-2% do bankroll",
            'expected_roi': f"{(cards_prob_over_45 - 0.5) * 100:.1f}%",
            'priority': 4
        })
    
    # 7. Analisar Escanteios
    corners_prob_over_85 = prognosis.get('corners', {}).get('over_85', 0)
    corners_prob_over_95 = prognosis.get('corners', {}).get('over_95', 0)
    
    if corners_prob_over_85 > 0.55:
        recommendations.append({
            'market': 'Escanteios',
            'recommendation': 'Over 8.5 escanteios',
            'confidence': 'MÉDIA' if corners_prob_over_85 > 0.60 else 'MÉDIA-BAIXA',
            'confidence_score': corners_prob_over_85 * 100,
            'reason': f"Times com jogo ofensivo. "
                     f"Probabilidade de Over 8.5 escanteios: {corners_prob_over_85*100:.1f}%.",
            'stake': "1% do bankroll",
            'expected_roi': f"{(corners_prob_over_85 - 0.5) * 100:.1f}%",
            'priority': 5
        })
    
    if corners_prob_over_95 > 0.60:
        recommendations.append({
            'market': 'Escanteios',
            'recommendation': 'Over 9.5 escanteios',
            'confidence': 'MÉDIA-ALTA',
            'confidence_score': corners_prob_over_95 * 100,
            'reason': f"Jogo muito ofensivo com muitos ataques esperados. "
                     f"Probabilidade de Over 9.5 escanteios: {corners_prob_over_95*100:.1f}%.",
            'stake': "1-2% do bankroll",
            'expected_roi': f"{(corners_prob_over_95 - 0.5) * 100:.1f}%",
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
    
    # Se não há recomendações, criar uma baseada no mercado mais provável
    if not recommendations:
        # Encontrar maior probabilidade entre todos os mercados
        all_probs = [
            ('home_win', probs.get('home_win', 0), f"Vitória {home_team}"),
            ('draw', probs.get('draw', 0), "Empate"),
            ('away_win', probs.get('away_win', 0), f"Vitória {away_team}"),
            ('over_25', probs.get('over_25', 0), "Over 2.5 gols"),
            ('btts', probs.get('btts', 0), "Ambos Marcam - SIM"),
        ]
        
        best_market = max(all_probs, key=lambda x: x[1])
        
        recommendations.append({
            'market': '1X2' if best_market[0] in ['home_win', 'draw', 'away_win'] else best_market[0].upper(),
            'recommendation': best_market[2],
            'confidence': 'MÉDIA' if best_market[1] > 0.40 else 'BAIXA',
            'confidence_score': best_market[1] * 100,
            'reason': f"Mercado com maior probabilidade ({best_market[1]*100:.1f}%). "
                     f"Apesar de não haver edge significativo, esta é a opção mais provável "
                     f"segundo os modelos estatísticos.",
            'stake': "1% do bankroll (conservador)" if best_market[1] > 0.40 else "0.5% do bankroll (muito conservador)",
            'expected_roi': f"{(best_market[1] - 0.33) * 100:.1f}%" if best_market[0] in ['home_win', 'draw', 'away_win'] else f"{(best_market[1] - 0.5) * 100:.1f}%",
            'priority': 10
        })
    
    # Ordenar por prioridade e confiança
    recommendations.sort(key=lambda x: (x['priority'], -x['confidence_score']))
    
    # Retornar melhor recomendação
    best = recommendations[0]
    
    # Adicionar alternativas
    alternatives = recommendations[1:3] if len(recommendations) > 1 else []
    
    return {
        'main': best,
        'alternatives': alternatives,
        'total_recommendations': len(recommendations)
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

