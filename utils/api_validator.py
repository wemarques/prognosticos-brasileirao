"""
Validador de APIs - Testa conectividade e validade das chaves
Autor: Sistema Multi-Persona (Engenheiro + Desenvolvedor + Cientista + Analista de Dados)
"""
import os
import requests
from typing import Dict, Tuple
import streamlit as st

class APIValidator:
    """Valida e testa chaves de API"""
    
    def __init__(self):
        self.api_football_key = os.getenv("API_FOOTBALL_KEY", "")
        self.odds_api_key = os.getenv("ODDS_API_KEY", "")
    
    def validate_api_football(self) -> Tuple[bool, str]:
        """
        Testa a chave da API-Football
        
        Returns:
            (is_valid, message)
        """
        if not self.api_football_key:
            return False, "❌ API_FOOTBALL_KEY não configurada"
        
        try:
            # Endpoint de teste (timezone - não consome quota)
            url = "https://v3.football.api-sports.io/timezone"
            headers = {"x-apisports-key": self.api_football_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            # Verificar se há erro de autenticação
            if 'errors' in data and data['errors']:
                error_msg = str(data['errors'])
                if 'token' in error_msg.lower() or 'key' in error_msg.lower():
                    return False, f"❌ API_FOOTBALL_KEY inválida: {error_msg}"
            
            # Verificar se retornou dados
            if data.get('results', 0) > 0:
                return True, "✅ API_FOOTBALL_KEY válida e funcionando"
            
            return False, f"⚠️ API_FOOTBALL_KEY responde mas sem dados: {data}"
            
        except requests.exceptions.Timeout:
            return False, "⏱️ Timeout ao conectar com API-Football"
        except requests.exceptions.RequestException as e:
            return False, f"🔌 Erro de conexão com API-Football: {str(e)}"
        except Exception as e:
            return False, f"❌ Erro inesperado: {str(e)}"
    
    def validate_odds_api(self) -> Tuple[bool, str]:
        """
        Testa a chave da The Odds API
        
        Returns:
            (is_valid, message)
        """
        if not self.odds_api_key:
            return False, "❌ ODDS_API_KEY não configurada"
        
        try:
            # Endpoint de teste (sports - não consome quota)
            url = f"https://api.the-odds-api.com/v4/sports/?apiKey={self.odds_api_key}"
            
            response = requests.get(url, timeout=10)
            
            # Verificar status code
            if response.status_code == 401:
                return False, "❌ ODDS_API_KEY inválida (401 Unauthorized)"
            elif response.status_code == 403:
                return False, "❌ ODDS_API_KEY sem permissão (403 Forbidden)"
            elif response.status_code == 429:
                return False, "⚠️ ODDS_API_KEY: Limite de requisições excedido"
            elif response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return True, "✅ ODDS_API_KEY válida e funcionando"
                return False, "⚠️ ODDS_API_KEY responde mas sem dados"
            else:
                return False, f"❌ Status inesperado: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "⏱️ Timeout ao conectar com The Odds API"
        except requests.exceptions.RequestException as e:
            return False, f"🔌 Erro de conexão com The Odds API: {str(e)}"
        except Exception as e:
            return False, f"❌ Erro inesperado: {str(e)}"
    
    def validate_all(self) -> Dict[str, Tuple[bool, str]]:
        """
        Valida todas as APIs
        
        Returns:
            Dict com resultados de cada API
        """
        return {
            'api_football': self.validate_api_football(),
            'odds_api': self.validate_odds_api()
        }
    
    def show_validation_ui(self):
        """Mostra UI de validação no Streamlit"""
        st.subheader("🔍 Status das APIs")
        
        results = self.validate_all()
        
        # API-Football
        is_valid_football, msg_football = results['api_football']
        if is_valid_football:
            st.success(msg_football)
        else:
            st.error(msg_football)
        
        # The Odds API
        is_valid_odds, msg_odds = results['odds_api']
        if is_valid_odds:
            st.success(msg_odds)
        else:
            st.warning(msg_odds + " (Opcional - não afeta prognósticos)")
        
        # Recomendação
        if not is_valid_football and not is_valid_odds:
            st.info("💡 **Recomendação:** Use o modo 'Dados Simulados' para testar o sistema")
        elif not is_valid_football:
            st.warning("⚠️ **Atenção:** API-Football não está funcionando. Use 'Dados Simulados'")
        
        return is_valid_football or is_valid_odds

