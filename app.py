"""
Sistema de Prognósticos - Campeonato Brasileiro
VERSÃO COMPLETA com Integração Real dos Módulos
"""

import streamlit as st

# IMPORTANTE: st.set_page_config() DEVE ser a PRIMEIRA chamada
st.set_page_config(
    page_title="Prognósticos Brasileirão",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports padrão
import sys
import os
from pathlib import Path

# Adicionar raiz ao path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Imports científicos
try:
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px
    SCIENTIFIC_IMPORTS_OK = True
except ImportError as e:
    st.error(f"❌ Erro ao importar bibliotecas científicas: {e}")
    SCIENTIFIC_IMPORTS_OK = False

# Imports dos módulos do sistema
MODULES_AVAILABLE = {
    'collector': False,
    'processor': False,
    'calculator': False,
    'value_detector': False,
}

try:
    from data.collector import FootballDataCollector
    MODULES_AVAILABLE['collector'] = True
except Exception:
    pass

try:
    from data.processor import DataProcessor
    MODULES_AVAILABLE['processor'] = True
except Exception:
    pass

try:
    from analysis.calculator import PrognosisCalculator
    MODULES_AVAILABLE['calculator'] = True
except Exception:
    pass

try:
    from analysis.value_detector import ValueBetDetector
    MODULES_AVAILABLE['value_detector'] = True
except Exception:
    pass

try:
    from analysis.stake_optimizer import StakeOptimizer
    from analysis.outcome_checker import OutcomeChecker
except Exception:
    pass

# Mapeamento de times
BRASILEIRAO_TEAMS = {
    'Flamengo': 127,
    'Palmeiras': 128,
    'São Paulo': 126,
    'Corinthians': 131,
    'Santos': 124,
    'Grêmio': 136,
    'Internacional': 134,
    'Atlético-MG': 133,
    'Fluminense': 125,
    'Botafogo': 129,
    'Athletico-PR': 149,
    'Cruzeiro': 132,
    'Vasco': 130,
    'Bahia': 159,
    'Fortaleza': 160,
    'Bragantino': 1371,
    'Cuiabá': 1193,
    'Criciúma': 1207,
    'Vitória': 154,
    'Juventude': 1188,
}

# CSS Customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        padding: 1rem 0;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .value-bet-high {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .value-bet-medium {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def show_system_status():
    """Mostra status do sistema na sidebar"""
    with st.sidebar:
        st.header("🔧 Status do Sistema")
        
        # Imports científicos
        if SCIENTIFIC_IMPORTS_OK:
            st.success("✅ Bibliotecas científicas OK")
        else:
            st.error("❌ Bibliotecas científicas com erro")
        
        # Módulos internos
        st.subheader("📦 Módulos")
        for module, available in MODULES_AVAILABLE.items():
            if available:
                st.success(f"✅ {module}")
            else:
                st.error(f"❌ {module}")
        
        # Modo de operação
        st.markdown("---")
        if all(MODULES_AVAILABLE.values()):
            st.info("🚀 **Modo:** Produção Completa")
        else:
            st.warning("🧪 **Modo:** Demonstração")


def generate_prognosis_real(home_team, away_team, context):
    """Gera prognóstico usando módulos reais"""
    
    # Inicializar módulos
    collector = FootballDataCollector()
    processor = DataProcessor()
    calculator = PrognosisCalculator()
    value_detector = ValueBetDetector()
    
    # 1. Coletar dados da API
    home_id = BRASILEIRAO_TEAMS.get(home_team)
    away_id = BRASILEIRAO_TEAMS.get(away_team)
    
    if not home_id or not away_id:
        raise ValueError("Time não encontrado no mapeamento")
    
    # Buscar estatísticas
    home_api_stats = collector.get_team_stats(home_id)
    away_api_stats = collector.get_team_stats(away_id)
    
    # Buscar H2H
    h2h_matches = collector.get_h2h(home_id, away_id, last=5)
    
    # 2. Processar dados
    home_stats = processor.process_team_stats(home_api_stats, is_home=True)
    away_stats = processor.process_team_stats(away_api_stats, is_home=False)
    h2h_stats = processor.process_h2h(h2h_matches, home_team, away_team)
    
    # Mesclar com H2H
    home_stats_merged = processor.merge_stats(home_stats, h2h_stats, is_home=True)
    away_stats_merged = processor.merge_stats(away_stats, h2h_stats, is_home=False)
    
    # Ajustes contextuais
    context_adj = processor.calculate_context_adjustments(
        home_team, away_team,
        venue_altitude=context.get('altitude', 0),
        is_classic=context.get('is_classic', False),
        is_derby=context.get('is_derby', False)
    )
    
    # 3. Calcular prognóstico
    prognosis = calculator.calculate_full_prognosis(
        home_stats_merged,
        away_stats_merged,
        context_adj
    )
    
    # 4. Buscar odds e detectar value bets
    # (Simplificado - em produção buscar odds reais)
    mock_odds = {
        'home': 1 / prognosis['probabilities']['home_win'] * 0.9,
        'draw': 1 / prognosis['probabilities']['draw'] * 0.9,
        'away': 1 / prognosis['probabilities']['away_win'] * 0.9,
        'over_25': 1 / prognosis['probabilities']['over_25'] * 0.9,
        'btts_yes': 1 / prognosis['probabilities']['btts'] * 0.9,
    }
    
    value_bets = value_detector.find_value_bets(
        prognosis['probabilities'],
        mock_odds
    )
    
    return prognosis, value_bets, h2h_stats


def generate_prognosis_mock(home_team, away_team):
    """Gera prognóstico simulado"""
    return {
        'probabilities': {
            'home_win': 0.452,
            'draw': 0.285,
            'away_win': 0.263,
            'btts': 0.523,
            'over_15': 0.715,
            'over_25': 0.458,
            'over_35': 0.213,
        },
        'cards': {
            'p_over_25': 0.685,
            'p_over_35': 0.523,
            'p_over_45': 0.357,
            'p_over_55': 0.182,
        },
        'corners': {
            'p_over_65': 0.612,
            'p_over_75': 0.458,
            'p_over_85': 0.321,
            'p_over_95': 0.215,
        },
        'top_scores': [
            {'score': '2-1', 'probability': 0.125},
            {'score': '1-1', 'probability': 0.118},
            {'score': '2-0', 'probability': 0.102},
            {'score': '1-0', 'probability': 0.095},
            {'score': '2-2', 'probability': 0.081},
        ],
        'expected_goals': {
            'home': 1.85,
            'away': 1.42,
            'total': 3.27,
        }
    }, [], {}


def display_roi_simulation(value_bets, investment_value, match_details):
    """Exibe simulação de ROI com stakes otimizados pelo Critério de Kelly"""
    st.markdown("## 💰 Retorno e ROI Simulado (singles)")
    if not value_bets:
        st.warning("Nenhuma aposta de valor encontrada para esta simulação.")
        return

    optimizer = StakeOptimizer()
    bets_with_stakes = optimizer.calculate_kelly_stakes(value_bets, investment_value)
    if not bets_with_stakes:
        st.info("O modelo não recomendou alocação de stake.")
        return

    simulation_data = []
    brier_scores = []
    match_status = match_details.get("status", "SCHEDULED")

    for bet in bets_with_stakes:
        result_icon, retorno, outcome = ("⏳", 0, None)
        if match_status == "FINISHED":
            is_win = OutcomeChecker.check_bet_outcome(bet, match_details)
            outcome = 1 if is_win else 0
            result_icon = "✅" if is_win else "❌"
            retorno = (bet["stake"] * bet["suggested_odd"]) - bet["stake"] if is_win else -bet["stake"]
            brier_scores.append((outcome - bet["probability"]) ** 2)

        simulation_data.append({
            "Aposta": f"{bet['market']} - {bet['selection']}",
            "Odd": f"{bet['suggested_odd']:.2f}",
            "Stake (R$)": f"{bet['stake']:.2f}",
            "Resultado": result_icon,
            "Retorno (R$)": f"{retorno:+.2f}"
        })

    st.dataframe(pd.DataFrame(simulation_data), use_container_width=True)

    total_investido = sum(b["stake"] for b in bets_with_stakes)
    total_retorno_valor = sum(float(row["Retorno (R$)"]) for row in simulation_data)
    lucro = total_retorno_valor
    roi = (lucro / total_investido) * 100 if total_investido > 0 else 0
    avg_brier = sum(brier_scores) / len(brier_scores) if brier_scores else 0

    st.markdown("### Totais:")
    st.markdown(f"- **Investimento:** R$ {total_investido:.2f}")
    st.markdown(f"- **Retorno (Lucro/Prejuízo):** R$ {lucro:+.2f}")
    st.markdown(f"- **ROI (singles):** {roi:+.2f}%")
    if avg_brier > 0:
        st.markdown(f"- **Brier Score médio:** {avg_brier:.2f}")


def display_results(prognosis, value_bets, home_team, away_team, h2h_stats=None):
    """Exibe resultados completos"""
    
    st.success(f"✅ Análise: **{home_team}** vs **{away_team}**")
    
    # Métricas principais
    st.subheader("📊 Resultado Final (1X2)")
    col1, col2, col3 = st.columns(3)
    
    probs = prognosis['probabilities']
    
    with col1:
        st.metric(
            f"🏠 {home_team}",
            f"{probs['home_win']*100:.1f}%",
            help="Probabilidade de vitória do mandante"
        )
    
    with col2:
        st.metric(
            "🤝 Empate",
            f"{probs['draw']*100:.1f}%",
            help="Probabilidade de empate"
        )
    
    with col3:
        st.metric(
            f"✈️ {away_team}",
            f"{probs['away_win']*100:.1f}%",
            help="Probabilidade de vitória do visitante"
        )
    
    # Gráfico 1X2
    fig_1x2 = go.Figure(data=[
        go.Bar(
            x=[home_team, 'Empate', away_team],
            y=[probs['home_win']*100, probs['draw']*100, probs['away_win']*100],
            marker_color=['#1f77b4', '#ff7f0e', '#d62728'],
            text=[f"{probs['home_win']*100:.1f}%", 
                  f"{probs['draw']*100:.1f}%", 
                  f"{probs['away_win']*100:.1f}%"],
            textposition='auto'
        )
    ])
    
    fig_1x2.update_layout(
        title="Probabilidades do Resultado",
        yaxis_title="Probabilidade (%)",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_1x2, use_container_width=True)
    
    # Gols Esperados
    st.subheader("📈 Gols Esperados")
    col1, col2, col3 = st.columns(3)
    
    exp_goals = prognosis['expected_goals']
    
    with col1:
        st.metric(f"🏠 {home_team}", f"{exp_goals['home']:.2f} gols")
    with col2:
        st.metric("⚽ Total", f"{exp_goals['total']:.2f} gols")
    with col3:
        st.metric(f"✈️ {away_team}", f"{exp_goals['away']:.2f} gols")
    
    # Over/Under
    st.subheader("⚽ Total de Gols (Over/Under)")
    
    over_under_data = {
        'Mercado': ['Over 1.5', 'Over 2.5', 'Over 3.5'],
        'Probabilidade (%)': [
            probs['over_15']*100,
            probs['over_25']*100,
            probs['over_35']*100
        ]
    }
    
    df_over = pd.DataFrame(over_under_data)
    
    fig_over = go.Figure(data=[
        go.Bar(
            x=df_over['Mercado'],
            y=df_over['Probabilidade (%)'],
            marker_color='#2ecc71',
            text=[f"{v:.1f}%" for v in df_over['Probabilidade (%)']],
            textposition='auto'
        )
    ])
    
    fig_over.update_layout(
        yaxis_title="Probabilidade (%)",
        showlegend=False,
        height=350
    )
    
    st.plotly_chart(fig_over, use_container_width=True)
    
    # BTTS
    st.subheader("🎯 Ambos Marcam (BTTS)")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("✅ Sim", f"{probs['btts']*100:.1f}%")
    with col2:
        st.metric("❌ Não", f"{(1-probs['btts'])*100:.1f}%")
    
    # Placares Prováveis
    st.subheader("🎲 Placares Mais Prováveis")
    
    scores_data = {
        'Placar': [s['score'] for s in prognosis['top_scores']],
        'Probabilidade (%)': [s['probability']*100 for s in prognosis['top_scores']]
    }
    
    df_scores = pd.DataFrame(scores_data)
    st.dataframe(df_scores, use_container_width=True)
    
    # Cartões
    st.subheader("🟨 Cartões")
    cards = prognosis.get('cards', {})
    
    if cards:
        cards_data = {
            'Mercado': ['Over 2.5', 'Over 3.5', 'Over 4.5', 'Over 5.5'],
            'Probabilidade (%)': [
                cards.get('p_over_25', 0)*100,
                cards.get('p_over_35', 0)*100,
                cards.get('p_over_45', 0)*100,
                cards.get('p_over_55', 0)*100,
            ]
        }
        
        df_cards = pd.DataFrame(cards_data)
        st.dataframe(df_cards, use_container_width=True)
    
    # Escanteios
    st.subheader("⚐ Escanteios")
    corners = prognosis.get('corners', {})
    
    if corners:
        corners_data = {
            'Mercado': ['Over 6.5', 'Over 7.5', 'Over 8.5', 'Over 9.5'],
            'Probabilidade (%)': [
                corners.get('p_over_65', 0)*100,
                corners.get('p_over_75', 0)*100,
                corners.get('p_over_85', 0)*100,
                corners.get('p_over_95', 0)*100,
            ]
        }
        
        df_corners = pd.DataFrame(corners_data)
        st.dataframe(df_corners, use_container_width=True)
    
    # Value Bets
    if value_bets:
        st.subheader("💎 Value Bets Detectados")
        
        for vb in value_bets[:3]:  # Top 3
            confidence = vb['confidence']
            
            if confidence == "ALTA":
                st.markdown(f"""
                <div class="value-bet-high">
                    <h4>🔥 {vb['market'].upper()} - Confiança ALTA</h4>
                    <p><strong>Edge:</strong> {vb['edge']*100:.1f}% | 
                       <strong>Stake Recomendado:</strong> {vb['stake_pct']:.1f}% | 
                       <strong>ROI Esperado:</strong> {vb['expected_roi']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="value-bet-medium">
                    <h4>⚡ {vb['market'].upper()} - Confiança {confidence}</h4>
                    <p><strong>Edge:</strong> {vb['edge']*100:.1f}% | 
                       <strong>Stake Recomendado:</strong> {vb['stake_pct']:.1f}% | 
                       <strong>ROI Esperado:</strong> {vb['expected_roi']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
    
    # H2H Stats (se disponível)
    if h2h_stats and h2h_stats.get('total_matches', 0) > 0:
        with st.expander("📊 Histórico de Confrontos (H2H)"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(f"Vitórias {home_team}", h2h_stats['team1_wins'])
            with col2:
                st.metric("Empates", h2h_stats['draws'])
            with col3:
                st.metric(f"Vitórias {away_team}", h2h_stats['team2_wins'])
            
            st.write(f"**Média de gols {home_team}:** {h2h_stats['avg_goals_team1']:.2f}")
            st.write(f"**Média de gols {away_team}:** {h2h_stats['avg_goals_team2']:.2f}")
            st.write(f"**Taxa BTTS:** {h2h_stats['btts_rate']*100:.1f}%")


def main():
    """Função principal"""
    
    # Header
    st.markdown('<h1 class="main-header">⚽ Prognósticos Brasileirão</h1>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # Status na sidebar
    show_system_status()
    
    # Sidebar - Configurações
    with st.sidebar:
        st.markdown("---")
        st.header("⚙️ Configurações")
        
        use_real_data = st.checkbox(
            "🌐 Usar dados reais da API",
            value=False,
            help="Requer API-Football configurada",
            disabled=not all(MODULES_AVAILABLE.values())
        )
        
        if not all(MODULES_AVAILABLE.values()):
            st.warning("⚠️ Módulos faltando - apenas modo simulado disponível")
    
    # Conteúdo principal
    if not SCIENTIFIC_IMPORTS_OK:
        st.error("❌ Sistema indisponível - bibliotecas científicas não carregadas")
        return
    
    # Seleção de times
    col1, col2 = st.columns(2)
    
    teams_list = sorted(BRASILEIRAO_TEAMS.keys())
    
    with col1:
        st.subheader("🏠 Time Mandante")
        home_team = st.selectbox(
            "Selecione o time da casa",
            teams_list,
            key="home"
        )
    
    with col2:
        st.subheader("✈️ Time Visitante")
        away_team = st.selectbox(
            "Selecione o time visitante",
            teams_list,
            index=1 if len(teams_list) > 1 else 0,
            key="away"
        )
    
    st.markdown("---")
    
    # Configurações avançadas
    with st.expander("⚙️ Configurações Avançadas"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            altitude = st.slider("⛰️ Altitude (m)", 0, 1000, 0)
        with col2:
            is_classic = st.checkbox("🏆 É um clássico?")
        with col3:
            is_derby = st.checkbox("⚔️ É um derby?")
    
    investment_value = st.number_input(
        "💰 Valor do Investimento para Simulação (R$)",
        min_value=1.0, value=100.0, step=10.0
    )
    
    # Botão de análise
    if st.button("🔮 GERAR PROGNÓSTICO", type="primary", use_container_width=True):
        
        if home_team == away_team:
            st.error("❌ Selecione times diferentes!")
            return
        
        context = {
            'altitude': altitude,
            'is_classic': is_classic,
            'is_derby': is_derby,
        }
        
        with st.spinner("🔄 Processando análise..."):
            try:
                match_details = {
                    "status": "SCHEDULED",
                    "score": {"fullTime": {"home": 0, "away": 0}}
                }
                
                if use_real_data and all(MODULES_AVAILABLE.values()):
                    # Usar dados reais
                    prognosis, value_bets, h2h_stats = generate_prognosis_real(
                        home_team, away_team, context
                    )
                    display_results(prognosis, value_bets, home_team, away_team, h2h_stats)
                    display_roi_simulation(value_bets, investment_value, match_details)
                else:
                    # Usar dados simulados
                    prognosis, value_bets, h2h_stats = generate_prognosis_mock(
                        home_team, away_team
                    )
                    display_results(prognosis, value_bets, home_team, away_team)
                    display_roi_simulation(value_bets, investment_value, match_details)
                    
                    if not use_real_data:
                        st.info("💡 Usando dados simulados. Ative 'Usar dados reais da API' para análise real.")
            
            except Exception as e:
                st.error(f"❌ Erro ao gerar prognóstico: {e}")
                
                with st.expander("🐛 Detalhes do Erro"):
                    import traceback
                    st.code(traceback.format_exc())
                
                # Fallback para dados simulados
                st.info("💡 Usando dados simulados como fallback")
                match_details = {
                    "status": "SCHEDULED",
                    "score": {"fullTime": {"home": 0, "away": 0}}
                }
                prognosis, value_bets, h2h_stats = generate_prognosis_mock(
                    home_team, away_team
                )
                display_results(prognosis, value_bets, home_team, away_team)
                display_roi_simulation(value_bets, investment_value, match_details)
    
    # Informações adicionais
    with st.expander("ℹ️ Sobre o Sistema"):
        st.markdown("""
        ### 📊 Sistema de Prognósticos Brasileirão
        
        **Modelos Utilizados:**
        - **Dixon-Coles:** Modelo Poisson bivariado para cálculo de probabilidades
        - **Monte Carlo:** 50.000 simulações para distribuição de resultados
        - **Calibração Brasileirão:** Ajustes específicos para o campeonato brasileiro
        
        **Parâmetros:**
        - HFA (Home Field Advantage): 1.53
        - Média de gols por time: 1.82
        - Correlação entre gols: -0.11
        
        **Mercados Disponíveis:**
        - ✅ 1X2 (Vitória/Empate/Derrota)
        - ✅ Over/Under Gols (1.5, 2.5, 3.5)
        - ✅ BTTS (Ambos Marcam)
        - ✅ Placares Exatos (Top 5)
        - ✅ Cartões (Over 2.5, 3.5, 4.5, 5.5)
        - ✅ Escanteios (Over 6.5, 7.5, 8.5, 9.5)
        - ✅ Value Bets (Detecção automática)
        
        **Ajustes Contextuais:**
        - Distância de viagem
        - Altitude do estádio
        - Tipo de confronto (clássico/derby)
        - Histórico H2H
        
        ⚠️ **Aviso:** Sistema para fins educacionais e de pesquisa.
        """)
    
    # Rodapé
    st.markdown("---")
    st.caption("Sistema de Prognósticos Brasileirão - v3.0 (Completo) | Desenvolvido com Streamlit")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Erro crítico: {e}")
        
        with st.expander("🐛 Detalhes do Erro"):
            import traceback
            st.code(traceback.format_exc())

