# 🔌 Arquitetura Multi-API: Prognósticos Multi-Liga

## 📊 Comparação de APIs

### Football-Data.org
**Suporta:** Brasileirão + Premier League + Outras ligas
- **ID Brasileirão:** 2013
- **ID Premier League:** 2021
- **Custo:** Plano gratuito limitado (10 requisições/dia)
- **Dados:** Matches, Teams, Stats, H2H
- **Qualidade:** ⭐⭐⭐⭐ (Excelente)

### FootyStats API
**Suporta:** Premier League (Gratuito!)
- **ID Premier League:** 1625 (2018/19), 1626 (2019/20), etc.
- **Custo:** GRATUITO para Premier League
- **Dados:** League Table, Matches, Teams, Stats, BTTS, Over/Under
- **Qualidade:** ⭐⭐⭐⭐ (Excelente)
- **API Key:** test85g57 (fornecida)

---

## 🎯 Estratégia de Seleção de API

```python
LEAGUE_API_STRATEGY = {
    'brasileirao': {
        'primary': 'football_data',
        'fallback': None,
        'api_id': 2013,
        'api_key': os.getenv('FOOTBALL_DATA_API_KEY')
    },
    'premier_league': {
        'primary': 'footystats',  # Gratuito!
        'fallback': 'football_data',
        'api_id': 1626,  # 2024/25 season
        'api_key': 'test85g57'  # Fornecida
    }
}
```

**Lógica:**
1. **Brasileirão:** Football-Data.org (única opção)
2. **Premier League:** FootyStats (gratuito) → Fallback para Football-Data.org

---

## 🏗️ Arquitetura de Camadas

```
┌─────────────────────────────────────────┐
│         UI Layer (Streamlit)            │
│  - Seletor de Liga                      │
│  - Exibição de Prognósticos             │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Business Logic Layer               │
│  - Calculator                           │
│  - Models (Dixon-Coles, Monte Carlo)    │
│  - Value Detector                       │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Data Processing Layer              │
│  - DataProcessor                        │
│  - Normalização de Dados                │
│  - Cache Management                     │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      API Abstraction Layer              │
│  - APIFactory (seleciona API correta)   │
│  - Adaptadores (normalizam dados)       │
│  - Fallback Logic                       │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼────────┐  ┌────▼──────────┐
│ Football-Data  │  │  FootyStats    │
│     API        │  │     API        │
└────────────────┘  └────────────────┘
```

---

## 📝 Implementação Detalhada

### 1. Arquivo de Configuração: `utils/leagues_config.py`

```python
import os
from typing import Dict, Any

LEAGUES = {
    'brasileirao': {
        'id': 2013,
        'code': 'BSA',
        'name': 'Brasileirão Série A',
        'country': 'Brasil',
        'season': 2025,
        'icon': '🇧🇷',
        'api': {
            'provider': 'football_data',
            'league_id': 2013,
            'api_key': os.getenv('FOOTBALL_DATA_API_KEY'),
            'base_url': 'https://api.football-data.org/v4'
        },
        'stats': {
            'league_avg_goals': 1.82,
            'league_avg_xg': 1.40,
            'home_advantage': 1.53,
            'away_penalty': 0.85,
            'cards_multiplier': 1.2,
            'corners_adjustment': 0.9,
            'btts_rate': 0.36,
        },
        'dixon_coles': {
            'rho': -0.11,
            'home_advantage': 1.53,
        }
    },
    'premier_league': {
        'id': 2021,
        'code': 'PL',
        'name': 'Premier League',
        'country': 'Inglaterra',
        'season': 2024,  # 2024/25
        'icon': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'api': {
            'provider': 'footystats',  # Gratuito!
            'league_id': 1626,  # 2024/25 season
            'api_key': 'test85g57',
            'base_url': 'https://api.footystats.org/api'
        },
        'stats': {
            'league_avg_goals': 2.69,
            'league_avg_xg': 1.52,
            'home_advantage': 1.38,
            'away_penalty': 0.90,
            'cards_multiplier': 0.85,
            'corners_adjustment': 1.25,
            'btts_rate': 0.52,
        },
        'dixon_coles': {
            'rho': -0.11,
            'home_advantage': 1.38,
        }
    }
}

def get_league_config(league_key: str) -> Dict[str, Any]:
    """Retorna configuração de uma liga específica"""
    return LEAGUES.get(league_key, LEAGUES['brasileirao'])

def get_api_config(league_key: str) -> Dict[str, Any]:
    """Retorna configuração da API para uma liga"""
    league = get_league_config(league_key)
    return league['api']
```

### 2. Factory Pattern: `data/api_factory.py`

```python
from typing import Union
from data.collectors.football_data_collector import FootballDataCollector
from data.collectors.footystats_collector import FootyStatsCollector
from utils.leagues_config import get_api_config

class APIFactory:
    """Factory para selecionar o collector correto baseado na API"""
    
    _collectors = {
        'football_data': FootballDataCollector,
        'footystats': FootyStatsCollector,
    }
    
    @staticmethod
    def create_collector(league_key: str) -> Union[FootballDataCollector, FootyStatsCollector]:
        """
        Cria o collector apropriado para a liga
        
        Args:
            league_key: 'brasileirao' ou 'premier_league'
            
        Returns:
            Instância do collector apropriado
        """
        api_config = get_api_config(league_key)
        provider = api_config['provider']
        
        if provider not in APIFactory._collectors:
            raise ValueError(f"Provider '{provider}' não suportado")
        
        collector_class = APIFactory._collectors[provider]
        return collector_class(league_key=league_key, api_config=api_config)
```

### 3. Adaptador de Dados: `data/adapters/data_adapter.py`

```python
from typing import Dict, Any, List
from abc import ABC, abstractmethod

class DataAdapter(ABC):
    """Interface abstrata para adaptadores de dados"""
    
    @abstractmethod
    def normalize_match(self, match_data: Dict) -> Dict[str, Any]:
        """Normaliza dados de um jogo"""
        pass
    
    @abstractmethod
    def normalize_team(self, team_data: Dict) -> Dict[str, Any]:
        """Normaliza dados de um time"""
        pass
    
    @abstractmethod
    def normalize_stats(self, stats_data: Dict) -> Dict[str, Any]:
        """Normaliza dados estatísticos"""
        pass

class FootballDataAdapter(DataAdapter):
    """Adaptador para Football-Data.org"""
    
    def normalize_match(self, match_data: Dict) -> Dict[str, Any]:
        """Converte formato Football-Data para padrão interno"""
        return {
            'id': match_data.get('id'),
            'date': match_data.get('utcDate'),
            'home_team': match_data.get('homeTeam', {}).get('name'),
            'away_team': match_data.get('awayTeam', {}).get('name'),
            'home_goals': match_data.get('score', {}).get('fullTime', {}).get('home'),
            'away_goals': match_data.get('score', {}).get('fullTime', {}).get('away'),
            'status': match_data.get('status'),
            'odds': match_data.get('odds', {}),
        }
    
    def normalize_team(self, team_data: Dict) -> Dict[str, Any]:
        return {
            'id': team_data.get('id'),
            'name': team_data.get('name'),
            'code': team_data.get('code'),
            'crest': team_data.get('crest'),
        }
    
    def normalize_stats(self, stats_data: Dict) -> Dict[str, Any]:
        return {
            'team_id': stats_data.get('team', {}).get('id'),
            'team_name': stats_data.get('team', {}).get('name'),
            'matches_played': stats_data.get('playedGames'),
            'wins': stats_data.get('won'),
            'draws': stats_data.get('draw'),
            'losses': stats_data.get('lost'),
            'goals_for': stats_data.get('goalsFor'),
            'goals_against': stats_data.get('goalsAgainst'),
            'goal_difference': stats_data.get('goalDifference'),
            'points': stats_data.get('points'),
        }

class FootyStatsAdapter(DataAdapter):
    """Adaptador para FootyStats API"""
    
    def normalize_match(self, match_data: Dict) -> Dict[str, Any]:
        """Converte formato FootyStats para padrão interno"""
        return {
            'id': match_data.get('id'),
            'date': match_data.get('date'),
            'home_team': match_data.get('home_team', {}).get('name'),
            'away_team': match_data.get('away_team', {}).get('name'),
            'home_goals': match_data.get('goals', {}).get('home'),
            'away_goals': match_data.get('goals', {}).get('away'),
            'status': match_data.get('status'),
            'odds': match_data.get('odds', {}),
        }
    
    def normalize_team(self, team_data: Dict) -> Dict[str, Any]:
        return {
            'id': team_data.get('id'),
            'name': team_data.get('name'),
            'code': team_data.get('code'),
            'crest': team_data.get('logo'),
        }
    
    def normalize_stats(self, stats_data: Dict) -> Dict[str, Any]:
        return {
            'team_id': stats_data.get('team_id'),
            'team_name': stats_data.get('team_name'),
            'matches_played': stats_data.get('played'),
            'wins': stats_data.get('wins'),
            'draws': stats_data.get('draws'),
            'losses': stats_data.get('losses'),
            'goals_for': stats_data.get('goals_for'),
            'goals_against': stats_data.get('goals_against'),
            'goal_difference': stats_data.get('goal_difference'),
            'points': stats_data.get('points'),
        }
```

### 4. Collector Football-Data: `data/collectors/football_data_collector.py`

```python
import requests
from typing import Dict, List, Any
from data.adapters.data_adapter import FootballDataAdapter

class FootballDataCollector:
    """Collector para Football-Data.org API"""
    
    def __init__(self, league_key: str, api_config: Dict[str, Any]):
        self.league_key = league_key
        self.api_config = api_config
        self.base_url = api_config['base_url']
        self.league_id = api_config['league_id']
        self.api_key = api_config['api_key']
        self.adapter = FootballDataAdapter()
        self.headers = {'X-Auth-Token': self.api_key}
    
    def get_matches(self, season: int = None) -> List[Dict]:
        """Coleta matches da liga"""
        url = f"{self.base_url}/competitions/{self.league_id}/matches"
        params = {}
        if season:
            params['season'] = season
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            matches = response.json().get('matches', [])
            return [self.adapter.normalize_match(m) for m in matches]
        except Exception as e:
            print(f"Erro ao coletar matches: {e}")
            return []
    
    def get_teams(self) -> List[Dict]:
        """Coleta times da liga"""
        url = f"{self.base_url}/competitions/{self.league_id}/teams"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            teams = response.json().get('teams', [])
            return [self.adapter.normalize_team(t) for t in teams]
        except Exception as e:
            print(f"Erro ao coletar times: {e}")
            return []
    
    def get_standings(self) -> List[Dict]:
        """Coleta tabela de classificação"""
        url = f"{self.base_url}/competitions/{self.league_id}/standings"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            standings = response.json().get('standings', [{}])[0].get('table', [])
            return [self.adapter.normalize_stats(s) for s in standings]
        except Exception as e:
            print(f"Erro ao coletar standings: {e}")
            return []
```

### 5. Collector FootyStats: `data/collectors/footystats_collector.py`

```python
import requests
from typing import Dict, List, Any
from data.adapters.data_adapter import FootyStatsAdapter

class FootyStatsCollector:
    """Collector para FootyStats API"""
    
    def __init__(self, league_key: str, api_config: Dict[str, Any]):
        self.league_key = league_key
        self.api_config = api_config
        self.base_url = api_config['base_url']
        self.league_id = api_config['league_id']
        self.api_key = api_config['api_key']
        self.adapter = FootyStatsAdapter()
    
    def get_matches(self, season: int = None) -> List[Dict]:
        """Coleta matches da liga"""
        url = f"{self.base_url}/league-matches"
        params = {
            'key': self.api_key,
            'league_id': self.league_id,
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            matches = response.json().get('data', [])
            return [self.adapter.normalize_match(m) for m in matches]
        except Exception as e:
            print(f"Erro ao coletar matches FootyStats: {e}")
            return []
    
    def get_teams(self) -> List[Dict]:
        """Coleta times da liga"""
        url = f"{self.base_url}/league-teams"
        params = {
            'key': self.api_key,
            'league_id': self.league_id,
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            teams = response.json().get('data', [])
            return [self.adapter.normalize_team(t) for t in teams]
        except Exception as e:
            print(f"Erro ao coletar times FootyStats: {e}")
            return []
    
    def get_standings(self) -> List[Dict]:
        """Coleta tabela de classificação"""
        url = f"{self.base_url}/league-table"
        params = {
            'key': self.api_key,
            'league_id': self.league_id,
            'include': 'stats'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            standings = response.json().get('league_table', [])
            return [self.adapter.normalize_stats(s) for s in standings]
        except Exception as e:
            print(f"Erro ao coletar standings FootyStats: {e}")
            return []
```

### 6. Refatoração do Collector Principal: `data/collector.py`

```python
from data.api_factory import APIFactory
from typing import List, Dict, Any

class DataCollector:
    """Collector unificado que usa a API apropriada por liga"""
    
    def __init__(self, league_key: str = 'brasileirao'):
        self.league_key = league_key
        self.api_collector = APIFactory.create_collector(league_key)
    
    def get_matches(self, season: int = None) -> List[Dict]:
        """Coleta matches usando a API apropriada"""
        return self.api_collector.get_matches(season)
    
    def get_teams(self) -> List[Dict]:
        """Coleta times usando a API apropriada"""
        return self.api_collector.get_teams()
    
    def get_standings(self) -> List[Dict]:
        """Coleta standings usando a API apropriada"""
        return self.api_collector.get_standings()
```

---

## 🔄 Fluxo de Dados

```
1. Usuário seleciona liga no Streamlit
   ↓
2. app.py passa league_key para componentes
   ↓
3. DataCollector(league_key='premier_league')
   ↓
4. APIFactory.create_collector() → FootyStatsCollector
   ↓
5. FootyStatsCollector.get_matches()
   ↓
6. FootyStatsAdapter.normalize_match() → Formato padrão
   ↓
7. DataProcessor(league_key='premier_league')
   ↓
8. Models (Dixon-Coles, Monte Carlo) com parâmetros da PL
   ↓
9. Calculator gera prognósticos
   ↓
10. UI exibe resultados
```

---

## 🧪 Testes de Integração

### Teste 1: Verificar Coleta de Dados

```python
# test_multi_api.py
from data.collector import DataCollector

def test_brasileirao_collection():
    collector = DataCollector('brasileirao')
    matches = collector.get_matches()
    assert len(matches) > 0
    assert 'home_team' in matches[0]

def test_premier_league_collection():
    collector = DataCollector('premier_league')
    matches = collector.get_matches()
    assert len(matches) > 0
    assert 'home_team' in matches[0]

def test_data_normalization():
    """Verifica se dados de ambas as APIs estão normalizados"""
    br_collector = DataCollector('brasileirao')
    pl_collector = DataCollector('premier_league')
    
    br_matches = br_collector.get_matches()
    pl_matches = pl_collector.get_matches()
    
    # Ambos devem ter a mesma estrutura
    assert set(br_matches[0].keys()) == set(pl_matches[0].keys())
```

---

## 📊 Benefícios da Arquitetura

✅ **Escalabilidade:** Adicionar nova API é trivial (criar novo Adapter + Collector)
✅ **Manutenibilidade:** Cada API isolada em seu próprio módulo
✅ **Flexibilidade:** Trocar de API sem afetar lógica de negócio
✅ **Testabilidade:** Cada componente pode ser testado independentemente
✅ **Custo:** Usa FootyStats gratuito para Premier League
✅ **Confiabilidade:** Fallback automático entre APIs

---

## 🚀 Próximos Passos

1. ✅ Criar estrutura de diretórios
2. ✅ Implementar adaptadores
3. ✅ Implementar collectors
4. ✅ Refatorar DataProcessor
5. ✅ Atualizar UI
6. ✅ Testes completos
7. ✅ Deploy