"""
Testes para times 2025 via API Football
"""
import sys
sys.path.insert(0, '/opt/prognosticos-brasileirao')

from data.collector import FootballDataCollector

def test_brasileiro_id_fixed():
    """Testa se o bug brasileiro_id foi corrigido"""
    collector = FootballDataCollector()
    
    # Deve ter o atributo brasileiro_id para backward compatibility
    assert hasattr(collector, 'brasileiro_id'), "Atributo brasileiro_id não encontrado"
    assert collector.brasileiro_id is not None, "brasileiro_id é None"
    assert collector.brasileiro_id == 'BSA', f"brasileiro_id incorreto: {collector.brasileiro_id}"
    
    print("✅ Bug brasileiro_id corrigido")
    return True

def test_api_teams_loaded():
    """Testa se times foram carregados da API"""
    collector = FootballDataCollector()
    teams_list = collector.get_teams('BSA', season=2025)
    
    assert teams_list is not None, "Lista de times é None"
    assert len(teams_list) > 0, "Lista de times está vazia"
    
    print(f"✅ {len(teams_list)} times carregados da API")
    return True

def test_no_duplicates_api():
    """Testa que não há duplicidade na lista da API"""
    collector = FootballDataCollector()
    teams_list = collector.get_teams('BSA', season=2025)
    
    names = [team['name'] for team in teams_list]
    
    # Verificar duplicidades
    assert len(names) == len(set(names)), "Há nomes duplicados na lista"
    
    print("✅ Nenhuma duplicidade - nomes oficiais da API")
    return True

def test_ceara_present():
    """Testa que Ceará está presente"""
    collector = FootballDataCollector()
    teams_list = collector.get_teams('BSA', season=2025)
    
    names = [team['name'] for team in teams_list]
    
    # Verificar que Ceará está na lista
    ceara_found = any('Ceará' in team or 'Ceara' in team for team in names)
    assert ceara_found, "Ceará não encontrado na lista de times"
    
    print("✅ Ceará presente na lista")
    return True

def test_rebaixados_removed_api():
    """Testa que times rebaixados foram removidos"""
    collector = FootballDataCollector()
    teams_list = collector.get_teams('BSA', season=2025)
    
    names = [team['name'] for team in teams_list]
    
    rebaixados = ['Athletico', 'Cuiabá', 'Atlético-GO']
    
    for rebaixado in rebaixados:
        found = any(rebaixado.lower() in team.lower() for team in names)
        assert not found, f"Time rebaixado '{rebaixado}' ainda na lista!"
    
    print("✅ Times rebaixados removidos")
    return True

def test_20_teams():
    """Testa que há exatamente 20 times"""
    collector = FootballDataCollector()
    teams_list = collector.get_teams('BSA', season=2025)
    
    assert len(teams_list) == 20, f"Esperado 20 times, encontrado {len(teams_list)}"
    
    print("✅ 20 times no Brasileirão 2025")
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("TESTES - PROMPT 0.1-0.2 FUSIONADO")
    print("=" * 70)
    print()
    
    tests = [
        test_brasileiro_id_fixed,
        test_api_teams_loaded,
        test_no_duplicates_api,
        test_ceara_present,
        test_rebaixados_removed_api,
        test_20_teams
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: Erro - {e}")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"RESULTADO: {passed} passou, {failed} falhou")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n⚠️ {failed} teste(s) falharam")
        sys.exit(1)
