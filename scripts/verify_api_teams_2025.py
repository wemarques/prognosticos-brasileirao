#!/usr/bin/env python3
"""
Verifica times do Brasileirão 2025 DIRETO DA API FOOTBALL
Confirma lista oficial sem duplicidade
"""
import sys
sys.path.insert(0, '/opt/prognosticos-brasileirao')

from data.collector import FootballDataCollector
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def verify_api_teams_2025():
    """Verifica times atuais do Brasileirão 2025 DIRETO DA API"""
    collector = FootballDataCollector()
    
    print("=" * 70)
    print(f"VERIFICAÇÃO OFICIAL - TIMES BRASILEIRÃO SÉRIE A 2025")
    print(f"FONTE: API FOOTBALL-DATA.ORG")
    print("=" * 70)
    
    try:
        # Buscar DIRETO DA API
        teams_list = collector.get_teams('BSA', season=2025)
        
        if teams_list and len(teams_list) > 0:
            print(f"\n✅ {len(teams_list)} times encontrados DIRETAMENTE DA API:\n")
            
            # Lista ordenada por nome
            for i, team in enumerate(sorted(teams_list, key=lambda x: x['name']), 1):
                print(f"{i:2d}. {team['name']:30s} (ID: {team['id']})")
            
            # VALIDAÇÃO 1: Contagem de times
            print(f"\n--- VALIDAÇÃO ---")
            if len(teams_list) == 20:
                print("✅ CONTAGEM: 20 times (Brasileirão completo)")
            else:
                print(f"❌ CONTAGEM: {len(teams_list)}/20 times (INCOMPLETO)")
            
            # VALIDAÇÃO 2: Duplicidades
            names = [team['name'] for team in teams_list]
            duplicates = set([x for x in names if names.count(x) > 1])
            
            if duplicates:
                print(f"❌ DUPLICIDADES: {duplicates}")
            else:
                print("✅ DUPLICIDADE: Nenhuma duplicidade encontrada")
                
            # VALIDAÇÃO 3: Times rebaixados 2024
            rebaixados_2024 = ['Athletico', 'Cuiabá', 'Atlético-GO', 'Goianiense']
            encontrados = [r for r in rebaixados_2024 if any(r.lower() in name.lower() for name in names)]
            
            if encontrados:
                print(f"❌ REBAIXADOS: {encontrados} ainda na lista")
            else:
                print("✅ REBAIXADOS: Todos removidos")
                
            # VALIDAÇÃO 4: Times promovidos 2025  
            promovidos_2025 = ['Santos', 'Mirassol', 'Ceará', 'Vitória']
            encontrados_promovidos = []
            faltantes = []
            
            for promovido in promovidos_2025:
                if any(promovido.lower() in name.lower() for name in names):
                    encontrados_promovidos.append(promovido)
                else:
                    faltantes.append(promovido)
            
            if encontrados_promovidos:
                print(f"✅ PROMOVIDOS: {encontrados_promovidos} presentes")
            if faltantes:
                print(f"⚠️ PROMOVIDOS FALTANTES: {faltantes}")
                
            # VALIDAÇÃO 5: Ceará presente
            if any('Ceará' in name or 'Ceara' in name for name in names):
                print("✅ CEARÁ: Presente na lista")
            else:
                print("❌ CEARÁ: Não encontrado na lista")
                
        else:
            print("❌ Nenhum dado retornado da API Football")
            print("   Verifique: API Key, conexão, temporada 2025")
            
    except Exception as e:
        print(f"❌ Erro ao acessar API: {e}")

if __name__ == "__main__":
    verify_api_teams_2025()
