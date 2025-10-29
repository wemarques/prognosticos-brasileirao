# 🎯 Integração The Odds API Gratuita

## 📊 Resumo Executivo

Documentação completa para integrar **The Odds API (versão gratuita)** ao sistema de prognósticos multi-liga.

---

## 🔑 Informações da API Gratuita

### Limites
- **Requisições:** 500/mês (hard cap: 1 req/segundo)
- **Custo:** Gratuito
- **Atualização:** Periódica (não em tempo real)

### Endpoints Disponíveis

#### 1. **GET /sports** - Listar esportes e ligas
```
https://api.the-odds-api.com/v4/sports?apiKey=YOUR_API_KEY
```

**Resposta:**
```json
[
  {
    "key": "soccer_epl",
    "group": "Soccer",
    "title": "Premier League",
    "description": "English Premier League",
    "active": true,
    "has_outrights": false
  },
  {
    "key": "soccer_brazil_campeonato",
    "group": "Soccer",
    "title": "Brazil Série A",
    "description": "Brasileirão Série A",
    "active": true,
    "has_outrights": false
  }
]
```

#### 2. **GET /odds** - Obter odds para uma liga
```
https://api.the-odds-api.com/v4/odds?apiKey=YOUR_API_KEY&sport=soccer_epl&region=eu&markets=h2h
```

**Parâmetros:**
- `sport`: soccer_epl, soccer_brazil_campeonato, etc.
- `region`: eu, us, uk, au
- `markets`: h2h (1x2), spreads, totals

**Resposta:**
```json
{
  "success": true,
  "data": [
    {
      "id": "d689bc4a1d0fe53463e500059280057e",
      "sport_key": "soccer_epl",
      "sport_nice": "EPL",
      "teams": ["Arsenal", "West Ham United"],
      "commence_time": 1535205600,
      "home_team": "Arsenal",
      "away_team": "West Ham United",
      "sites": [
        {
          "site_key": "unibet",
          "site_nice": "Unibet",
          "last_update": 1535157373,
          "odds": {
            "h2h": [1.38, 8.75, 5.5]
          }
        },
        {
          "site_key": "betvictor",
          "site_nice": "BetVictor",
          "last_update": 1535157373,
          "odds": {
            "h2h": [1.40, 8.50, 5.25]
          }
        }
      ]
    }
  ]
}
```

#### 3. **GET /odds/history** - Histórico de odds
```
https://api.the-odds-api.com/v4/odds/history?apiKey=YOUR_API_KEY&sport=soccer_epl&eventId=EVENT_ID
```

---

## 🏆 Ligas Suportadas (Gratuito)

### Soccer - Europa
- `soccer_epl` - Premier League (Inglaterra)
- `soccer_germany_bundesliga` - Bundesliga (Alemanha)
- `soccer_italy_serie_a` - Serie A (Itália)
- `soccer_spain_la_liga` - La Liga (Espanha)
- `soccer_france_ligue_1` - Ligue 1 (França)
- `soccer_portugal_primeira_liga` - Primeira Liga (Portugal)

### Soccer - América
- `soccer_brazil_campeonato` - Brasileirão (Brasil) ✅
- `soccer_usa_mls` - MLS (EUA)
- `soccer_argentina_primera_division` - Primeira División (Argentina)

### Outras Ligas
- `soccer_spl` - Scottish Premier League
- `soccer_sweden_allsvenskan` - Allsvenskan (Suécia)
- E muitas outras...

---

## 🔄 Mapeamento de Ligas

```python
ODDS_API_LEAGUES = {
    'brasileirao': {
        'odds_api_key': 'soccer_brazil_campeonato',
        'regions': ['eu', 'us'],
        'markets': ['h2h'],
    },
    'premier_league': {
        'odds_api_key': 'soccer_epl',
        'regions': ['eu', 'uk'],
        'markets': ['h2h'],
    }
}
```

---

## 📝 Estrutura de Dados Normalizada

```python
{
    'match_id': 'd689bc4a1d0fe53463e500059280057e',
    'home_team': 'Arsenal',
    'away_team': 'West Ham United',
    'commence_time': 1535205600,
    'bookmakers': [
        {
            'name': 'Unibet',
            'key': 'unibet',
            'last_update': 1535157373,
            'odds': {
                'home_win': 1.38,
                'draw': 8.75,
                'away_win': 5.5
            }
        },
        {
            'name': 'BetVictor',
            'key': 'betvictor',
            'last_update': 1535157373,
            'odds': {
                'home_win': 1.40,
                'draw': 8.50,
                'away_win': 5.25
            }
        }
    ],
    'average_odds': {
        'home_win': 1.39,
        'draw': 8.625,
        'away_win': 5.375
    }
}
```

---

## 🛠️ Implementação

### 1. OddsCollector (`data/collectors/odds_collector.py`)

```python
import requests
from typing import Dict, List, Any
from datetime import datetime
import time

class OddsCollector:
    """Collector para The Odds API (versão gratuita)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4"
        self.headers = {}
        self.cache = {}
        self.cache_ttl = 3600  # 1 hora
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 segundo (rate limit)
    
    def _rate_limit(self):
        """Respeita rate limit de 1 req/segundo"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def get_sports(self) -> List[Dict]:
        """Obtém lista de esportes e ligas disponíveis"""
        self._rate_limit()
        
        url = f"{self.base_url}/sports"
        params = {'apiKey': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro ao obter sports: {e}")
            return []
    
    def get_odds(
        self,
        sport_key: str,
        region: str = 'eu',
        markets: str = 'h2h'
    ) -> List[Dict]:
        """
        Obtém odds para uma liga específica
        
        Args:
            sport_key: Chave da liga (ex: 'soccer_epl')
            region: Região (eu, us, uk, au)
            markets: Mercados (h2h, spreads, totals)
            
        Returns:
            Lista de eventos com odds
        """
        # Verificar cache
        cache_key = f"{sport_key}_{region}_{markets}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
        
        self._rate_limit()
        
        url = f"{self.base_url}/odds"
        params = {
            'apiKey': self.api_key,
            'sport': sport_key,
            'region': region,
            'markets': markets
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json().get('data', [])
            
            # Armazenar em cache
            self.cache[cache_key] = (data, time.time())
            
            return data
        except Exception as e:
            print(f"Erro ao obter odds: {e}")
            return []
    
    def get_odds_history(
        self,
        sport_key: str,
        event_id: str
    ) -> List[Dict]:
        """Obtém histórico de odds para um evento"""
        self._rate_limit()
        
        url = f"{self.base_url}/odds/history"
        params = {
            'apiKey': self.api_key,
            'sport': sport_key,
            'eventId': event_id
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            print(f"Erro ao obter histórico: {e}")
            return []
```

### 2. Adaptador de Odds (`data/adapters/odds_adapter.py`)

```python
from typing import Dict, List, Any

class OddsAdapter:
    """Adaptador para normalizar dados de odds"""
    
    @staticmethod
    def normalize_odds(raw_odds: Dict) -> Dict[str, Any]:
        """
        Normaliza dados brutos da API para formato padrão
        
        Args:
            raw_odds: Dados brutos da The Odds API
            
        Returns:
            Dados normalizados
        """
        bookmakers = []
        all_odds = {'home_win': [], 'draw': [], 'away_win': []}
        
        for site in raw_odds.get('sites', []):
            h2h_odds = site.get('odds', {}).get('h2h', [])
            
            if len(h2h_odds) >= 3:
                bookmaker = {
                    'name': site.get('site_nice'),
                    'key': site.get('site_key'),
                    'last_update': site.get('last_update'),
                    'odds': {
                        'home_win': h2h_odds[0],
                        'draw': h2h_odds[1],
                        'away_win': h2h_odds[2]
                    }
                }
                bookmakers.append(bookmaker)
                
                # Coletar para média
                all_odds['home_win'].append(h2h_odds[0])
                all_odds['draw'].append(h2h_odds[1])
                all_odds['away_win'].append(h2h_odds[2])
        
        # Calcular médias
        average_odds = {
            'home_win': sum(all_odds['home_win']) / len(all_odds['home_win']) if all_odds['home_win'] else 0,
            'draw': sum(all_odds['draw']) / len(all_odds['draw']) if all_odds['draw'] else 0,
            'away_win': sum(all_odds['away_win']) / len(all_odds['away_win']) if all_odds['away_win'] else 0
        }
        
        return {
            'match_id': raw_odds.get('id'),
            'home_team': raw_odds.get('home_team'),
            'away_team': raw_odds.get('away_team'),
            'commence_time': raw_odds.get('commence_time'),
            'bookmakers': bookmakers,
            'average_odds': average_odds,
            'num_bookmakers': len(bookmakers)
        }
```

### 3. Integração com DataCollector

```python
# Modificar data/multi_league_collector.py

from data.collectors.odds_collector import OddsCollector
from data.adapters.odds_adapter import OddsAdapter
from utils.leagues_config import get_api_config

class DataCollector:
    """Collector unificado com suporte a odds"""
    
    def __init__(self, league_key: str = 'brasileirao', odds_api_key: str = None):
        self.league_key = league_key
        self.api_collector = APIFactory.create_collector(league_key)
        
        # Inicializar OddsCollector se API key fornecida
        self.odds_collector = None
        if odds_api_key:
            self.odds_collector = OddsCollector(odds_api_key)
    
    def get_matches_with_odds(self) -> List[Dict]:
        """Obtém matches com odds integradas"""
        # Obter matches
        matches = self.get_matches()
        
        if not self.odds_collector:
            return matches
        
        # Obter odds
        odds_api_key = self._get_odds_api_key()
        if not odds_api_key:
            return matches
        
        raw_odds = self.odds_collector.get_odds(odds_api_key)
        
        # Normalizar odds
        normalized_odds = {}
        for odd in raw_odds:
            normalized = OddsAdapter.normalize_odds(odd)
            normalized_odds[normalized['match_id']] = normalized
        
        # Mesclar matches com odds
        for match in matches:
            match_id = match.get('id')
            if match_id in normalized_odds:
                match['odds_data'] = normalized_odds[match_id]
        
        return matches
    
    def _get_odds_api_key(self) -> str:
        """Obtém chave da API de odds para a liga"""
        from utils.leagues_config import ODDS_API_LEAGUES
        return ODDS_API_LEAGUES.get(self.league_key, {}).get('odds_api_key')
```

---

## 📊 Uso Prático

### Exemplo 1: Coletar Odds da Premier League

```python
from data.multi_league_collector import DataCollector

# Inicializar collector com odds
collector = DataCollector(
    league_key='premier_league',
    odds_api_key='YOUR_ODDS_API_KEY'
)

# Obter matches com odds
matches_with_odds = collector.get_matches_with_odds()

# Acessar odds
for match in matches_with_odds:
    if 'odds_data' in match:
        odds = match['odds_data']
        print(f"{match['home_team']} vs {match['away_team']}")
        print(f"Odds médias: {odds['average_odds']}")
        print(f"Casas: {odds['num_bookmakers']}")
```

### Exemplo 2: Detectar Value Bets

```python
from analysis.value_detector import ValueBetDetector
from analysis.calculator import PredictionCalculator

# Calcular probabilidades
calculator = PredictionCalculator()
probs = calculator.calculate_probabilities(match_data)

# Obter odds
odds_data = match['odds_data']
market_odds = odds_data['average_odds']

# Detectar value bets
detector = ValueBetDetector()
value_bets = detector.find_value_bets(probs, market_odds)

for bet in value_bets:
    print(f"Value Bet: {bet['market']}")
    print(f"Edge: {bet['edge']:.2%}")
    print(f"Stake: {bet['stake']:.2%}")
```

---

## 🔐 Configuração de Variáveis de Ambiente

```bash
# .env
ODDS_API_KEY=your_free_api_key_here
FOOTBALL_DATA_API_KEY=your_football_data_key
```

```python
# utils/config.py
import os

ODDS_API_KEY = os.getenv('ODDS_API_KEY')
FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY')
```

---

## 📈 Monitoramento de Requisições

```python
class OddsCollectorMonitor:
    """Monitora uso da API gratuita"""
    
    def __init__(self):
        self.requests_this_month = 0
        self.max_requests = 500
    
    def check_quota(self) -> bool:
        """Verifica se ainda há quota disponível"""
        return self.requests_this_month < self.max_requests
    
    def log_request(self):
        """Registra uma requisição"""
        self.requests_this_month += 1
    
    def get_remaining(self) -> int:
        """Retorna requisições restantes"""
        return self.max_requests - self.requests_this_month
```

---

## ⚠️ Limitações da Versão Gratuita

1. **500 requisições/mês** - Planeje bem as coletas
2. **1 req/segundo** - Rate limit rigoroso
3. **Dados não em tempo real** - Atualização periódica
4. **Bookmakers limitados** - Apenas os principais
5. **Mercados limitados** - Principalmente H2H

---

## 💡 Estratégias de Otimização

### 1. Cache Agressivo
```python
# Armazenar odds por 1 hora
cache_ttl = 3600
```

### 2. Batch Requests
```python
# Coletar odds de múltiplas ligas em uma requisição
# Usar parâmetro 'sport' com múltiplos valores
```

### 3. Coleta Programada
```python
# Coletar odds uma vez por dia
# Usar scheduler para executar em horário fixo
```

### 4. Fallback para Mock Odds
```python
# Se quota excedida, usar odds mock
# Manter sistema funcionando
```

---

## 🎯 Próximos Passos

1. ✅ Obter API key gratuita em https://the-odds-api.com/
2. ✅ Implementar OddsCollector
3. ✅ Integrar com DataCollector
4. ✅ Conectar com Value Bet Detector
5. ✅ Adicionar UI para exibir odds
6. ✅ Implementar monitoramento de quota
7. ✅ Deploy em produção

---

## 📞 Suporte

- Documentação: https://the-odds-api.com/liveapi/guides/v4/
- GitHub: https://github.com/sportsdataverse/oddsapiR
- Comunidade: r/algobetting

---

**Data:** 29/10/2025
**Status:** Documentação Completa
**Versão:** 1.0