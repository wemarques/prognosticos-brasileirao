#!/usr/bin/env python3
"""
Script de teste para verificar se as variáveis de ambiente estão sendo carregadas
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("TESTE DE VARIÁVEIS DE AMBIENTE")
print("=" * 60)

# Carregar o arquivo .env
load_dotenv()

# Verificar se o arquivo .env existe
env_file = ".env"
if os.path.exists(env_file):
    print(f"✅ Arquivo '{env_file}' encontrado!")
    print(f"   Localização: {os.path.abspath(env_file)}")
else:
    print(f"❌ Arquivo '{env_file}' NÃO encontrado!")
    print(f"   Procurado em: {os.path.abspath('.')}")

print("\n" + "-" * 60)
print("VARIÁVEIS DE AMBIENTE:")
print("-" * 60)

# Verificar API_FOOTBALL_KEY
api_key = os.getenv("API_FOOTBALL_KEY")
if api_key:
    # Mostrar apenas os primeiros e últimos caracteres (segurança)
    masked_key = f"{api_key[:8]}...{api_key[-8:]}" if len(api_key) > 16 else "***"
    print(f"✅ API_FOOTBALL_KEY: {masked_key}")
    print(f"   Tamanho: {len(api_key)} caracteres")
else:
    print("❌ API_FOOTBALL_KEY: NÃO ENCONTRADA")

# Verificar ODDS_API_KEY
odds_key = os.getenv("ODDS_API_KEY")
if odds_key:
    masked_odds = f"{odds_key[:8]}...{odds_key[-8:]}" if len(odds_key) > 16 else "***"
    print(f"✅ ODDS_API_KEY: {masked_odds}")
    print(f"   Tamanho: {len(odds_key)} caracteres")
else:
    print("❌ ODDS_API_KEY: NÃO ENCONTRADA")

print("\n" + "=" * 60)

# Diagnóstico
if api_key and odds_key:
    print("✅ TUDO OK! As chaves foram carregadas corretamente.")
    print("\nVocê pode executar o Streamlit normalmente:")
    print("   streamlit run app.py")
elif api_key or odds_key:
    print("⚠️  ATENÇÃO! Apenas uma das chaves foi encontrada.")
    print("\nVerifique o arquivo .env e certifique-se que ambas estão lá:")
    print("   API_FOOTBALL_KEY=sua_chave_aqui")
    print("   ODDS_API_KEY=sua_chave_aqui")
else:
    print("❌ ERRO! Nenhuma chave foi encontrada.")
    print("\nSOLUÇÃO:")
    print("1. Crie o arquivo .env na raiz do projeto")
    print("2. Adicione as chaves:")
    print("   API_FOOTBALL_KEY=sua_chave_aqui")
    print("   ODDS_API_KEY=sua_chave_aqui")
    print("3. Execute este teste novamente: python test_env.py")

print("=" * 60)

