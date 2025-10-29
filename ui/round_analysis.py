"""
Interface de Análise de Rodadas
Integra todos os módulos para análise completa por rodada
"""

import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime

try:
    from data.round_manager import RoundManager
    from data.odds_collector import OddsCollector
    from analysis.comparison import PrognosisComparator
    from models.auto_calibration import ModelCalibrator
    from analysis.calculator import PrognosisCalculator
    from data.processor import DataProcessor
    from data.collector import FootballDataCollector
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")


def show_round_analysis(rodada: int):
    """
    Exibe análise completa de uma rodada
    
    Args:
        rodada: Número da rodada (1-38)
    """
    
    st.header(f"🏆 Análise da Rodada {rodada}")
    
    try:
        # Inicializar gerenciador de rodadas
        round_mgr = RoundManager()
        
        # Buscar jogos da rodada
        with st.spinner(f"Buscando jogos da rodada {rodada}..."):
            round_status = round_mgr.get_round_status(rodada)
        
        if not round_status['matches']:
            st.warning(f"⚠️ Nenhum jogo encontrado para a rodada {rodada}")
            return
        
        # Exibir status da rodada
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Jogos", round_status['total_matches'])
        
        with col2:
            st.metric("Finalizados", round_status['finished'], 
                     delta=None if round_status['finished'] == 0 else "✅")
        
        with col3:
            st.metric("Agendados", round_status['scheduled'],
                     delta=None if round_status['scheduled'] == 0 else "📅")
        
        with col4:
            st.metric("Em Andamento", round_status['in_play'],
                     delta=None if round_status['in_play'] == 0 else "⚽")
        
        st.markdown("---")
        
        # Determinar tipo de análise
        if round_status['is_complete']:
            # RODADA PASSADA: Comparação prognóstico vs realidade
            show_past_round_analysis(rodada, round_status['matches'])
        elif round_status['scheduled'] > 0:
            # RODADA FUTURA: Prognósticos
            show_future_round_analysis(rodada, round_status['matches'])
        else:
            # RODADA EM ANDAMENTO
            st.info("⚽ Rodada em andamento! Aguarde finalização para análise completa.")
            show_live_round_status(round_status['matches'])
    
    except Exception as e:
        st.error(f"❌ Erro ao analisar rodada: {e}")
        with st.expander("🐛 Detalhes do Erro"):
            import traceback
            st.code(traceback.format_exc())


def show_past_round_analysis(rodada: int, matches: List[Dict]):
    """
    Análise de rodada passada: Comparação prognóstico vs realidade
    
    Args:
        rodada: Número da rodada
        matches: Lista de jogos finalizados
    """
    
    st.subheader("📊 Análise Retrospectiva: Prognóstico vs Realidade")
    
    st.info(f"✅ Rodada {rodada} finalizada! Comparando prognósticos com resultados reais...")
    
    # Inicializar comparador e calibrador
    comparator = PrognosisComparator()
    calibrator = ModelCalibrator()
    
    # Processar cada jogo
    all_comparisons = []
    
    for match in matches:
        with st.expander(f"⚽ {match['home_team']['name']} {match['score']['home']}-{match['score']['away']} {match['away_team']['name']}"):
            
            # Gerar prognóstico (como teria sido)
            try:
                prognosis = generate_prognosis_for_match(match)
                
                # Comparar com resultado real
                real_result = {
                    'home_score': match['score']['home'],
                    'away_score': match['score']['away']
                }
                
                match_info = {
                    'home_team': match['home_team']['name'],
                    'away_team': match['away_team']['name'],
                    'date': match['date'],
                    'round': rodada,
                    'referee': match.get('referee', 'N/A')
                }
                
                comparison = comparator.compare_match(prognosis, real_result, match_info)
                all_comparisons.append(comparison)
                
                # Exibir comparação
                display_match_comparison(comparison)
            
            except Exception as e:
                st.error(f"Erro ao processar jogo: {e}")
    
    # Relatório de acurácia geral
    if all_comparisons:
        st.markdown("---")
        st.subheader("📈 Relatório de Acurácia da Rodada")
        
        accuracy_report = comparator.get_accuracy_report()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Acurácia 1X2", f"{accuracy_report['accuracy_1x2']:.1f}%")
        
        with col2:
            st.metric("Acurácia Over/Under", f"{accuracy_report['accuracy_over_under']:.1f}%")
        
        with col3:
            st.metric("Acurácia BTTS", f"{accuracy_report['accuracy_btts']:.1f}%")
        
        with col4:
            st.metric("Acurácia Geral", f"{accuracy_report['overall_accuracy']:.1f}%")
        
        # Sugestões de ajuste
        st.markdown("---")
        st.subheader("🔧 Sugestões de Ajuste do Modelo")
        
        suggestions = comparator.suggest_model_adjustments(all_comparisons)
        
        if suggestions:
            for sug in suggestions:
                priority_color = {
                    'HIGH': '🔴',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }.get(sug['priority'], '⚪')
                
                st.markdown(f"""
                **{priority_color} {sug['parameter']}**
                - Razão: {sug['reason']}
                - Valor atual: {sug.get('current_value', sug.get('current_multiplier', 'N/A'))}
                - Valor sugerido: {sug.get('suggested_value', sug.get('suggested_multiplier', 'N/A'))}
                """)
            
            # Botão para aplicar ajustes
            if st.button("✅ Aplicar Ajustes Automaticamente"):
                result = calibrator.apply_adjustments(suggestions)
                
                if result['adjustments_made']:
                    st.success(f"✅ {result['total_adjustments']} ajustes aplicados!")
                    
                    for adj in result['adjustments_made']:
                        st.info(f"**{adj['parameter']}:** {adj['old_value']} → {adj['new_value']}")
                else:
                    st.warning("⚠️ Nenhum ajuste foi aplicado")
        else:
            st.success("✅ Modelo está bem calibrado! Nenhum ajuste necessário.")


def show_future_round_analysis(rodada: int, matches: List[Dict]):
    """
    Análise de rodada futura: Prognósticos com odds
    
    Args:
        rodada: Número da rodada
        matches: Lista de jogos agendados
    """
    
    st.subheader("🔮 Prognósticos da Próxima Rodada")
    
    st.info(f"📅 Rodada {rodada} ainda não começou. Gerando prognósticos...")
    
    # Inicializar coletor de odds
    try:
        odds_collector = OddsCollector()
        odds_available = True
    except:
        odds_available = False
        st.warning("⚠️ Odds API não disponível. Usando apenas modelos estatísticos.")
    
    # Processar cada jogo
    for match in matches:
        with st.expander(f"⚽ {match['home_team']['name']} vs {match['away_team']['name']} - {format_match_date(match['date'])}"):
            
            # Árbitro (se disponível)
            if match.get('referee') and match['referee'] != 'N/A':
                st.markdown(f"**⚖️ Árbitro:** {match['referee']}")
                # TODO: Adicionar estatísticas do árbitro quando implementado
            
            # Gerar prognóstico
            try:
                prognosis = generate_prognosis_for_match(match)
                
                # Buscar odds reais
                if odds_available:
                    odds_data = odds_collector.get_match_odds(
                        match['home_team']['name'],
                        match['away_team']['name']
                    )
                    
                    if odds_data:
                        display_odds_comparison(prognosis, odds_data)
                
                # Exibir prognóstico
                display_prognosis_summary(prognosis, match['home_team']['name'], match['away_team']['name'])
            
            except Exception as e:
                st.error(f"Erro ao gerar prognóstico: {e}")


def show_live_round_status(matches: List[Dict]):
    """
    Exibe status de rodada em andamento
    
    Args:
        matches: Lista de jogos
    """
    
    for match in matches:
        status_emoji = {
            'FINISHED': '✅',
            'IN_PLAY': '⚽',
            'PAUSED': '⏸️',
            'SCHEDULED': '📅',
            'TIMED': '⏰'
        }.get(match['status'], '❓')
        
        if match['status'] == 'FINISHED':
            st.markdown(f"{status_emoji} **{match['home_team']['name']} {match['score']['home']}-{match['score']['away']} {match['away_team']['name']}**")
        else:
            st.markdown(f"{status_emoji} **{match['home_team']['name']} vs {match['away_team']['name']}** - {format_match_date(match['date'])}")


def generate_prognosis_for_match(match: Dict) -> Dict:
    """
    Gera prognóstico para um jogo específico
    
    Args:
        match: Dados do jogo
        
    Returns:
        Dict com prognóstico completo
    """
    
    # Inicializar módulos
    collector = FootballDataCollector()
    processor = DataProcessor()
    calculator = PrognosisCalculator()
    
    # Buscar estatísticas dos times
    home_stats = collector.calculate_team_stats(match['home_team']['id'], venue='HOME')
    away_stats = collector.calculate_team_stats(match['away_team']['id'], venue='AWAY')
    
    # Processar dados
    processed_data = processor.process_match_data(
        home_stats,
        away_stats,
        {},  # H2H vazio por enquanto
        match['home_team']['name'],
        match['away_team']['name']
    )
    
    # Calcular prognóstico
    prognosis = calculator.calculate_full_prognosis(
        processed_data['xG_home'],
        processed_data['xG_away'],
        match['home_team']['name'],
        match['away_team']['name']
    )
    
    return prognosis


def display_match_comparison(comparison: Dict):
    """Exibe comparação de um jogo"""
    
    # Árbitro
    if comparison['match'].get('referee') and comparison['match']['referee'] != 'N/A':
        st.markdown(f"**⚖️ Árbitro:** {comparison['match']['referee']}")
    
    # Resultado 1X2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Prognóstico:**")
        acc = comparison['accuracy']['1x2']
        result_map = {'home': comparison['match']['home_team'], 'away': comparison['match']['away_team'], 'draw': 'Empate'}
        st.write(f"Resultado: {result_map.get(acc['predicted'], 'N/A')} ({acc['probability']*100:.1f}%)")
    
    with col2:
        st.markdown("**Realidade:**")
        st.write(f"Resultado: {result_map.get(acc['actual'], 'N/A')}")
        st.write("✅ ACERTOU!" if acc['correct'] else "❌ ERROU")
    
    # Gols
    st.markdown("**Gols:**")
    goals = comparison['accuracy']['goals']
    st.write(f"Previsto: {goals['predicted']} | Real: {goals['actual']} | Erro: {goals['error']}")
    
    # Discrepâncias
    if comparison['discrepancies']:
        st.warning(f"⚠️ {len(comparison['discrepancies'])} discrepâncias detectadas")
        for disc in comparison['discrepancies']:
            st.markdown(f"- **{disc['market']}:** {disc['severity']}")


def display_odds_comparison(prognosis: Dict, odds_data: Dict):
    """Exibe comparação entre prognóstico e odds"""
    
    st.markdown("### 💰 Comparação com Odds Reais")
    
    # Converter odds para probabilidades
    from data.odds_collector import OddsCollector
    odds_collector = OddsCollector()
    market_probs = odds_collector.get_market_probabilities(odds_data)
    
    # Comparar probabilidades
    col1, col2, col3 = st.columns(3)
    
    probs = prognosis['probabilities']
    
    with col1:
        st.metric("Mandante", 
                 f"Modelo: {probs['home_win']*100:.1f}%",
                 f"Odds: {market_probs['home_win']*100:.1f}%")
    
    with col2:
        st.metric("Empate",
                 f"Modelo: {probs['draw']*100:.1f}%",
                 f"Odds: {market_probs['draw']*100:.1f}%")
    
    with col3:
        st.metric("Visitante",
                 f"Modelo: {probs['away_win']*100:.1f}%",
                 f"Odds: {market_probs['away_win']*100:.1f}%")
    
    # Detectar value bets
    edges = {
        'home_win': probs['home_win'] - market_probs['home_win'],
        'draw': probs['draw'] - market_probs['draw'],
        'away_win': probs['away_win'] - market_probs['away_win']
    }
    
    max_edge = max(edges.values())
    
    if max_edge > 0.05:  # Edge > 5%
        best_market = max(edges, key=edges.get)
        st.success(f"🔥 VALUE BET DETECTADO: {best_market.replace('_', ' ').title()} (Edge: {max_edge*100:.1f}%)")


def display_prognosis_summary(prognosis: Dict, home_team: str, away_team: str):
    """Exibe resumo do prognóstico"""
    
    probs = prognosis['probabilities']
    exp_goals = prognosis['expected_goals']
    
    # Resultado mais provável
    max_prob = max(probs['home_win'], probs['draw'], probs['away_win'])
    
    if probs['home_win'] == max_prob:
        result = f"Vitória {home_team}"
    elif probs['away_win'] == max_prob:
        result = f"Vitória {away_team}"
    else:
        result = "Empate"
    
    st.markdown(f"**🎯 Resultado Mais Provável:** {result} ({max_prob*100:.1f}%)")
    st.markdown(f"**⚽ Gols Esperados:** {home_team} {exp_goals['home']:.2f} x {exp_goals['away']:.2f} {away_team}")
    
    # Outros mercados
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Over 2.5:** {probs.get('over_25', 0)*100:.1f}%")
    
    with col2:
        st.markdown(f"**BTTS:** {probs.get('btts', 0)*100:.1f}%")


def format_match_date(date_str: str) -> str:
    """Formata data do jogo"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return date_str

