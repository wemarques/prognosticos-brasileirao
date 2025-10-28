"""
Sistema de Prognósticos - Campeonato Brasileiro
Aplicação Principal com Tratamento Robusto de Erros
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

# Verificar quais módulos internos existem
MODULES_AVAILABLE = {
    'collector': False,
    'calculator': False,
    'value_detector': False,
    'api_validator': False
}

# Tentar importar módulos internos (sem quebrar se não existirem)
try:
    from data.collector import FootballDataCollector
    MODULES_AVAILABLE['collector'] = True
except Exception as e:
    st.sidebar.warning(f"⚠️ data.collector não disponível")

try:
    from analysis.calculator import PrognosisCalculator
    MODULES_AVAILABLE['calculator'] = True
except Exception as e:
    st.sidebar.warning(f"⚠️ analysis.calculator não disponível")

try:
    from analysis.value_detector import ValueBetDetector
    MODULES_AVAILABLE['value_detector'] = True
except Exception as e:
    st.sidebar.warning(f"⚠️ analysis.value_detector não disponível")

try:
    from utils.api_validator import APIValidator
    MODULES_AVAILABLE['api_validator'] = True
except Exception as e:
    st.sidebar.warning(f"⚠️ utils.api_validator não disponível")


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
    .stAlert {
        margin: 1rem 0;
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
        st.subheader("📦 Módulos Internos")
        for module, available in MODULES_AVAILABLE.items():
            if available:
                st.success(f"✅ {module}")
            else:
                st.error(f"❌ {module}")
        
        # Modo de operação
        st.markdown("---")
        if all(MODULES_AVAILABLE.values()):
            st.info("🚀 **Modo:** Produção completa")
        else:
            st.warning("🧪 **Modo:** Demonstração (módulos faltando)")


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
        
        use_mock = st.checkbox(
            "🧪 Usar dados simulados",
            value=True,
            help="Marque para testar sem API"
        )
    
    # Conteúdo principal
    if not SCIENTIFIC_IMPORTS_OK:
        st.error("❌ Sistema indisponível - bibliotecas científicas não carregadas")
        st.info("💡 Verifique se pandas, numpy e plotly estão instalados")
        return
    
    # Interface principal
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Time Mandante")
        home_team = st.selectbox(
            "Selecione o time da casa",
            ["Flamengo", "Palmeiras", "Corinthians", "São Paulo",
             "Atlético-MG", "Fluminense", "Internacional", "Grêmio",
             "Botafogo", "Cruzeiro", "Vasco", "Santos",
             "Athletico-PR", "Fortaleza", "Bahia", "Goiás",
             "Coritiba", "Cuiabá", "América-MG", "Bragantino"],
            key="home"
        )
    
    with col2:
        st.subheader("✈️ Time Visitante")
        away_team = st.selectbox(
            "Selecione o time visitante",
            ["Flamengo", "Palmeiras", "Corinthians", "São Paulo",
             "Atlético-MG", "Fluminense", "Internacional", "Grêmio",
             "Botafogo", "Cruzeiro", "Vasco", "Santos",
             "Athletico-PR", "Fortaleza", "Bahia", "Goiás",
             "Coritiba", "Cuiabá", "América-MG", "Bragantino"],
            index=1,
            key="away"
        )
    
    st.markdown("---")
    
    # Configurações avançadas
    with st.expander("⚙️ Configurações Avançadas"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            distance = st.slider("📍 Distância (km)", 0, 3000, 1000)
        with col2:
            altitude = st.slider("⛰️ Altitude (m)", 0, 1000, 500)
        with col3:
            match_type = st.selectbox(
                "🏆 Tipo de Confronto",
                ["Normal", "Clássico", "Derby"]
            )
    
    # Botão de análise
    if st.button("🔮 GERAR PROGNÓSTICO", type="primary", use_container_width=True):
        
        if home_team == away_team:
            st.error("❌ Selecione times diferentes!")
            return
        
        with st.spinner("Processando análise..."):
            
            # Se todos módulos disponíveis, usar lógica real
            if all(MODULES_AVAILABLE.values()) and not use_mock:
                try:
                    st.info("🔄 Usando módulos reais (implementação pendente)")
                    # Aqui viria a lógica real quando os módulos estiverem prontos
                    # collector = FootballDataCollector()
                    # calculator = PrognosisCalculator()
                    # results = calculator.calculate(home_team, away_team)
                    
                    st.warning("⚠️ Módulos reais ainda não implementados completamente")
                    st.info("💡 Usando dados simulados por enquanto")
                    
                except Exception as e:
                    st.error(f"❌ Erro ao processar: {e}")
                    st.info("💡 Usando dados simulados como fallback")
            
            # Resultados simulados (sempre funciona)
            st.success(f"✅ Análise: **{home_team}** vs **{away_team}**")
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "🏠 Vitória Mandante",
                    "45.2%",
                    "+2.3%",
                    help="Probabilidade de vitória do time da casa"
                )
            
            with col2:
                st.metric(
                    "🤝 Empate",
                    "28.5%",
                    "-1.1%",
                    help="Probabilidade de empate"
                )
            
            with col3:
                st.metric(
                    "✈️ Vitória Visitante",
                    "26.3%",
                    "-1.2%",
                    help="Probabilidade de vitória do time visitante"
                )
            
            # Gráfico de probabilidades
            st.subheader("📊 Distribuição de Probabilidades")
            
            fig = go.Figure(data=[
                go.Bar(
                    x=['Vitória Casa', 'Empate', 'Vitória Fora'],
                    y=[45.2, 28.5, 26.3],
                    marker_color=['#1f77b4', '#ff7f0e', '#d62728'],
                    text=['45.2%', '28.5%', '26.3%'],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Probabilidades do Resultado",
                yaxis_title="Probabilidade (%)",
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Placares prováveis
            st.subheader("🎯 Placares Mais Prováveis")
            
            scores_data = {
                'Placar': ['2-1', '1-1', '2-0', '1-0', '2-2'],
                'Probabilidade': [12.5, 11.8, 10.2, 9.5, 8.1],
                'Odd Típica': [7.5, 6.0, 8.0, 6.5, 9.5]
            }
            
            df = pd.DataFrame(scores_data)
            st.dataframe(
                df.style.background_gradient(subset=['Probabilidade'], cmap='RdYlGn'),
                use_container_width=True
            )
    
    # Informações adicionais
    with st.expander("ℹ️ Sobre o Sistema"):
        st.markdown("""
        ### 📊 Sistema de Prognósticos Brasileirão
        
        **Modelos Utilizados:**
        - Dixon-Coles (Poisson bivariada)
        - Monte Carlo (50k simulações)
        - Calibração específica do Brasileirão
        
        **Parâmetros:**
        - HFA (Home Field Advantage): 1.53
        - Média de gols: 1.82 por time
        - Correlação: -0.11
        
        **Status Atual:**
        - Interface: ✅ Funcional
        - Dados simulados: ✅ Disponível
        - Módulos reais: ⏳ Em desenvolvimento
        
        ⚠️ **Aviso:** Sistema para fins educacionais.
        """)
    
    # Rodapé
    st.markdown("---")
    st.caption("Sistema de Prognósticos Brasileirão - v2.0 (Modo Robusto)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Erro crítico: {e}")
        
        with st.expander("🐛 Detalhes do Erro"):
            import traceback
            st.code(traceback.format_exc())
        
        st.info("""
        💡 **Como resolver:**
        1. Verifique se todos os módulos estão presentes
2. Verifique erros de sintaxe nos arquivos Python
        3. Consulte os logs do Streamlit Cloud
        """)
