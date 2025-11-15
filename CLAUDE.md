# CLAUDE.md - AI Assistant Guide for Prognósticos Brasileirão

**Version:** 1.0
**Last Updated:** 2025-11-14
**Codebase Size:** ~11,525 lines of Python
**Primary Language:** Python 3.11+

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & Code Structure](#2-architecture--code-structure)
3. [Core Technologies & Dependencies](#3-core-technologies--dependencies)
4. [Development Workflows](#4-development-workflows)
5. [Coding Conventions](#5-coding-conventions)
6. [Data Flow & Processing](#6-data-flow--processing)
7. [Statistical Models](#7-statistical-models)
8. [Testing Strategy](#8-testing-strategy)
9. [Deployment](#9-deployment)
10. [AI Assistant Best Practices](#10-ai-assistant-best-practices)
11. [Common Tasks](#11-common-tasks)
12. [Recent Evolution](#12-recent-evolution)

---

## 1. Project Overview

### Purpose
**Automated prediction system for the Brazilian Football Championship (Brasileirão Série A)** using statistical models and real-time data analysis.

### Key Features
- **Statistical Models**: Dixon-Coles (1997) bivariate Poisson + Monte Carlo simulations
- **Hybrid CSV + API Architecture**: 25x performance improvement (0.1s vs 2-5s)
- **Value Bet Detection**: Automatic identification of profitable betting opportunities
- **Risk Management**: Kelly Criterion implementation with fractional betting
- **ROI Simulation**: Monte Carlo bankroll projections (30/60/90 days)
- **Multi-League Support**: Extensible architecture (currently Brasileirão, ready for Premier League, La Liga, etc.)

### Target Users
- **Football analysts** seeking data-driven predictions
- **Bettors** looking for value bet opportunities with proper risk management
- **Researchers** interested in sports statistics and modeling

### Critical Warning
**This system is for educational and analytical purposes. Betting involves risk - only bet what you can afford to lose.**

---

## 2. Architecture & Code Structure

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                UI Layer (Streamlit)                     │
│                     app.py (379 lines)                  │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│              Business Logic Layer                       │
│  ├─ models/      Dixon-Coles, Monte Carlo              │
│  ├─ analysis/    Calculators, Value Detection           │
│  └─ modules/roi/ Kelly Criterion, ROI Simulator         │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│               Data Access Layer                         │
│  ├─ data/collectors/  Hybrid CSV + API                 │
│  ├─ data/adapters/    Data transformation              │
│  └─ leagues/          League configurations            │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│          Infrastructure & Utilities                     │
│  ├─ utils/  Cache, Config, Logging                     │
│  └─ data/csv/ Local CSV storage (performance layer)    │
└─────────────────────────────────────────────────────────┘
```

### Directory Structure

```
prognosticos-brasileirao/
├── app.py                       # Main Streamlit application (379 lines)
├── analysis/                    # Prediction calculators and calibration
│   ├── calculator.py           # Main prediction engine
│   ├── calibration.py          # Brasileirão-specific calibrations
│   ├── value_detector.py       # Value bet identification
│   └── batch_processor.py      # Bulk match processing
├── data/                        # Data collection and processing
│   ├── collectors/
│   │   ├── hybrid_collector.py # CSV-first data access (385 lines)
│   │   ├── football_data_collector.py
│   │   └── footystats_collector.py
│   ├── adapters/               # Data normalization
│   │   └── data_adapter.py
│   ├── csv/                    # Local CSV data (performance layer)
│   │   └── brasileirao/
│   │       ├── 2025_matches.csv
│   │       ├── 2025_teams.csv
│   │       └── 2025_standings.csv
│   ├── processor.py            # Data transformation pipeline
│   └── odds_collector.py       # Real-time odds (optional)
├── models/                      # Statistical models
│   ├── dixon_coles.py          # Dixon-Coles bivariate Poisson (265 lines)
│   ├── monte_carlo.py          # Monte Carlo simulator (105 lines)
│   └── auto_calibration.py     # Automatic parameter tuning
├── modules/                     # Business logic modules
│   └── roi/
│       ├── kelly_criterion.py  # Kelly Criterion staking (256 lines)
│       └── roi_simulator.py    # ROI Monte Carlo (180 lines)
├── leagues/                     # League-specific configurations
│   ├── base_league.py          # Abstract base class
│   ├── brasileirao.py          # Brasileirão parameters
│   └── league_registry.py      # League factory
├── utils/                       # Infrastructure utilities
│   ├── cache_manager.py        # In-memory caching
│   ├── logger_config.py        # Centralized logging
│   ├── config.py               # Configuration management
│   └── timezone_utils.py       # Timezone handling (Brasília Time)
├── scripts/                     # Maintenance and updates
│   ├── update_csv_from_api.py  # Sync CSV data with APIs
│   └── verify_api_teams_2025.py
├── tests/                       # Unit and integration tests
│   ├── test_dixon_coles_calibration.py
│   ├── test_roi_simulator.py
│   ├── test_kelly_criterion.py
│   └── test_multi_api.py
├── ui/                          # UI components
│   ├── league_selector.py
│   └── round_analysis.py
├── requirements.txt             # Python dependencies (10 packages)
├── Dockerfile                   # Container configuration
├── docker-compose.yml           # Multi-service orchestration
└── .env.example                 # Environment variable template
```

### Total Codebase Statistics
- **Python files:** 50+
- **Total lines:** ~11,525
- **Average file size:** 230 lines
- **Largest file:** app.py (379 lines)
- **Documentation:** 15+ markdown files

---

## 3. Core Technologies & Dependencies

### Python Stack

```python
# requirements.txt (10 core dependencies)
streamlit>=1.32.0,<2.0.0      # Web UI framework
requests>=2.31.0              # HTTP client for APIs
pandas>=2.2.0                 # Data manipulation
numpy>=1.26.0                 # Numerical computing
scipy>=1.13.0                 # Statistical functions
plotly>=5.18.0                # Interactive visualizations
python-dotenv>=1.0.0          # Environment variables
pytz>=2024.1                  # Timezone handling (Brasília)
matplotlib>=3.8.0             # Static plotting
```

### Python Version
- **Production:** Python 3.11 (Dockerfile)
- **Target:** Python 3.14 (future compatibility)

### External APIs (Optional)
1. **Football-Data.org** - Match data, teams (optional with CSV architecture)
2. **The Odds API** - Real-time betting odds (optional)
3. **FootyStats** - Alternative data provider (legacy support)

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration
- **Redis** (optional) - Distributed caching
- **PostgreSQL** (optional) - Metrics storage
- **AWS EC2/App Runner/ECS** - Cloud deployment options

---

## 4. Development Workflows

### Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/wemarques/prognosticos-brasileirao.git
cd prognosticos-brasileirao

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional)
cp .env.example .env
# Edit .env with API keys if needed (not required for CSV-based usage)

# 5. Run application
streamlit run app.py

# Access at: http://localhost:8501
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Rebuild after changes
docker-compose up -d --build

# Stop services
docker-compose down
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_dixon_coles_calibration.py

# Run with coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### CSV Data Updates

```bash
# Update CSV data from API (optional)
python scripts/update_csv_from_api.py --league brasileirao --season 2025

# Verify data integrity
python scripts/verify_api_teams_2025.py
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, test locally
streamlit run app.py

# Commit with descriptive messages
git add .
git commit -m "feat: Add new calibration for defensive games"

# Push to remote
git push origin feature/your-feature-name

# Create pull request on GitHub
```

---

## 5. Coding Conventions

### Naming Conventions

```python
# Classes: PascalCase
class DixonColesModel:
class HybridDataCollector:
class KellyCriterion:

# Functions/Methods: snake_case
def calculate_lambda(self, ...):
def get_matches(self, ...):
def simulate_match(self, ...):

# Constants: UPPER_SNAKE_CASE
BRASILEIRAO_SERIE_A = 2013
MAX_STAKE_PERCENTAGE = 0.05
LEAGUE_AVG_GOALS = 1.65

# Private methods: _leading_underscore
def _load_parameters(self):
def _normalize_probabilities(self):
def _calculate_fallback(self):

# Module-level "private": __double_underscore (rare)
__internal_cache = {}
```

### Type Hints (Required)

```python
from typing import Dict, List, Optional, Tuple, Any

# All public methods must have type hints
def calculate_stake(
    self,
    probability: float,
    odds: float,
    bankroll: float
) -> Dict[str, Any]:
    """
    Calculate optimal stake using Kelly Criterion.

    Args:
        probability: Win probability (0.0-1.0)
        odds: Decimal odds (e.g., 2.00)
        bankroll: Total bankroll in currency

    Returns:
        Dict with keys: stake, edge, expected_value, is_value_bet
    """
    pass

# Optional parameters
def get_matches(
    self,
    round_number: Optional[int] = None,
    status: Optional[str] = None,
    team: Optional[str] = None
) -> List[Dict]:
    """Optional parameters properly typed"""
    pass
```

### Docstrings (Google Style - Required)

```python
def simulate_period(
    self,
    avg_bets_per_week: int,
    avg_edge: float,
    win_rate: float,
    weeks: int
) -> Dict[str, Any]:
    """
    Simulate betting performance over a period using Monte Carlo method.

    Runs 1000 simulations with variation in bets/week and edge to generate
    statistical distribution of outcomes (pessimistic, realistic, optimistic).

    Args:
        avg_bets_per_week: Average number of bets per week (1-50)
        avg_edge: Average edge over bookmaker (0.01-0.25)
        win_rate: Historical win rate (0.0-1.0)
        weeks: Number of weeks to simulate (1-52)

    Returns:
        Dict containing:
            - days: Number of days simulated
            - scenarios: Dict with pessimistic, realistic, optimistic outcomes
            - statistics: Mean, std, ROI percentage

    Raises:
        ValueError: If parameters are out of valid ranges

    Example:
        >>> simulator = ROISimulator(bankroll=1000, kelly_fraction=0.25)
        >>> result = simulator.simulate_period(
        ...     avg_bets_per_week=5,
        ...     avg_edge=0.08,
        ...     win_rate=0.55,
        ...     weeks=4
        ... )
        >>> print(result['scenarios']['realistic']['final_bankroll'])
        1150.00
    """
    pass
```

### Error Handling Pattern

```python
# 1. Graceful Degradation (Preferred)
def get_corners_prediction(lambda_corners: float, simulator) -> Dict:
    """Always return valid data, use fallbacks on error"""
    try:
        corners = simulator.simulate_corners(lambda_corners)

        # Validate output
        if corners is None or corners.get('p_over_85', 0) == 0:
            logger.warning("Invalid corners prediction, using fallback")
            return _calculate_corners_fallback()

    except Exception as e:
        logger.error(f"Corners prediction failed: {e}, using fallback")
        return _calculate_corners_fallback()

    return corners

# 2. Validation with Informative Errors
def __init__(self, bankroll: float, kelly_fraction: float = 0.25):
    """Validate inputs early"""
    if not (100 <= bankroll <= 100000):
        raise ValueError(
            f"Bankroll must be R$100-R$100,000. Got: R${bankroll}"
        )

    if not (0.1 <= kelly_fraction <= 0.5):
        raise ValueError(
            f"Kelly fraction must be 0.1-0.5. Got: {kelly_fraction}"
        )

    self.bankroll = bankroll
    self.kelly_fraction = kelly_fraction

# 3. Logging Best Practices
from utils.logger import setup_logger
logger = setup_logger(__name__)

logger.info("✅ Operation successful")           # Success
logger.warning("⚠️ Using fallback statistics")  # Degraded mode
logger.error(f"❌ Error: {exception}")           # Error
logger.debug(f"🔍 Debug info: {data}")           # Development only
```

### Code Organization

```python
# File structure within a module
# 1. Imports (grouped: stdlib, third-party, local)
import os
import time
from typing import Dict, List

import numpy as np
import pandas as pd

from utils.logger import setup_logger
from models.dixon_coles import DixonColesModel

# 2. Constants
MAX_STAKE_PERCENTAGE = 0.05
DEFAULT_KELLY_FRACTION = 0.25

# 3. Module-level logger
logger = setup_logger(__name__)

# 4. Classes
class KellyCriterion:
    """Main implementation"""
    pass

# 5. Helper functions (private)
def _validate_probability(prob: float) -> bool:
    """Private helper"""
    return 0.0 <= prob <= 1.0

# 6. Main execution (if script)
if __name__ == "__main__":
    # Example usage
    pass
```

---

## 6. Data Flow & Processing

### Complete Request Flow

```
USER ACTION: Click "Generate Prediction"
    ↓
app.py: Retrieve selections (home_team, away_team, bankroll)
    ↓
HybridDataCollector.get_match(home_team, away_team)
    ├─ Read: data/csv/brasileirao/2025_matches.csv (~0.05s)
    ├─ Filter: home_team=='Flamengo' & away_team=='Palmeiras'
    └─ Return: {date, referee, xG, shots, corners, cards}
    ↓
HybridDataCollector.get_team_stats(team, venue)
    ├─ Filter matches where team participated
    ├─ Aggregate: goals, xG, shots, corners, cards
    └─ Return: {avg_goals_for, avg_xg_for, ...}
    ↓
DixonColesModel.calculate_lambda()
    ├─ home_lambda = f(home_xg_for, away_xg_against, hfa)
    ├─ away_lambda = f(away_xg_for, home_xg_against, ava)
    ├─ Apply adjustments (travel, altitude, classics)
    └─ Return: (λ_home=1.75, λ_away=1.20)
    ↓
DixonColesModel.bivariate_poisson(λ_home, λ_away)
    ├─ Generate 10×10 probability matrix
    ├─ Calculate: P(home_win), P(draw), P(away_win)
    └─ Return: probabilities + most_likely_score
    ↓
MonteCarloSimulator.simulate_match(λ_home, λ_away)
    ├─ Run 50,000 simulations
    ├─ Generate: goals_home[], goals_away[]
    └─ Return: {p_home_wins, p_over_25, top_5_scores}
    ↓
BrasileiraoCalibrator.calibrate_*()
    ├─ calibrate_btts(p_btts * 0.85)
    ├─ calibrate_over25(p_over25 * 0.88)
    └─ Return: calibrated probabilities
    ↓
[Optional] OddsCollector.get_odds() via API
    └─ Return: {home: 1.85, draw: 3.20, over_25: 2.10}
    ↓
ValueBetDetector.find_value_bets(probs, odds)
    ├─ For each market: edge = p_model - (1 / odds)
    ├─ Filter: edge >= min_edge
    └─ Return: [{market, edge, stake_pct}, ...]
    ↓
KellyCriterion.calculate_stake(probability, odds)
    ├─ kelly = (b*p - q) / b
    ├─ stake = bankroll * kelly * kelly_fraction
    └─ Return: {stake, edge, expected_value}
    ↓
ROISimulator.simulate_multiple_periods()
    ├─ Simulate 1000 iterations × 3 periods
    └─ Return: {pessimistic, realistic, optimistic}
    ↓
Streamlit UI: Display Results
    ├─ Probabilities: Home Win (45%), Draw (28%), Away (27%)
    ├─ Value Bets: Over 2.5 (Edge: 8%, Stake: R$20)
    ├─ Kelly Stakes: R$25.00 (2.5% of bankroll)
    └─ ROI Simulation: 30d realistic = +R$150 (15% ROI)
```

**Total Execution Time:** ~0.5-1.0 seconds
- CSV reads: 0.1s
- Lambda calculations: 0.01s
- Dixon-Coles matrix: 0.05s
- Monte Carlo (50k): 0.3s
- UI rendering: 0.1s

### CSV Data Structure

```csv
# data/csv/brasileirao/2025_matches.csv
id,round,date,home_team,away_team,home_score,away_score,status,referee,
home_xg,away_xg,home_shots,away_shots,home_corners,away_corners,home_cards,away_cards

# Example row:
1,1,2025-04-13 16:00,Flamengo,Palmeiras,2,1,FINISHED,Wilton Sampaio,
1.85,1.42,15,12,6,4,3,2

# data/csv/brasileirao/2025_teams.csv
id,name,code,short_name,logo_url

# data/csv/brasileirao/2025_standings.csv
position,team,matches_played,wins,draws,losses,goals_for,goals_against,
goal_difference,points
```

### Hybrid Data Collection Pattern

```python
# Primary: CSV-based (fast, offline-capable)
matches = collector.get_matches(round_number=15)
# Returns: List[Dict] from CSV in ~0.1s

# Optional: API-based odds (real-time)
if collector.odds_collector:
    odds = collector.get_matches_with_odds(round_number=15)
    # Combines: CSV data + API odds in ~0.5s
else:
    # Graceful degradation: CSV-only mode
    odds = None
```

---

## 7. Statistical Models

### Dixon-Coles Model (`models/dixon_coles.py`)

#### Academic Foundation
**Dixon & Coles (1997)** - "Modelling Association Football Scores and Inefficiencies in the Football Betting Market"

#### Key Implementation

```python
class DixonColesModel:
    """
    Bivariate Poisson model with positive correlation.

    Key parameters (Brasileirão-calibrated):
    - hfa (home field advantage): 1.35
    - ava (away adjustment): 0.92
    - league_avg_goals: 1.65
    - rho (correlation): -0.12
    - correlation_k: 0.15 (positive correlation)
    """

    def calculate_lambda(
        self,
        xg_for: float,
        xgc_against: float,
        is_home: bool,
        adjustments: Dict = None
    ) -> float:
        """
        Calculate expected goals (lambda) for a team.

        Formula:
        λ = (attack × defense × league_avg) × venue_factor + venue_bonus

        With bounds: max(0.3, min(λ, 3.5))
        """
        attack_strength = (xg_for / self.league_avg_xg) * self.attack_strength
        defense_weakness = (xgc_against / self.league_avg_xg) * self.defense_strength

        lambda_base = attack_strength * defense_weakness * self.league_avg_goals

        if is_home:
            lambda_adj = lambda_base * self.hfa + self.home_advantage
        else:
            lambda_adj = lambda_base * self.ava

        # Apply contextual adjustments
        if adjustments:
            lambda_adj *= adjustments.get('travel_factor', 1.0)
            lambda_adj += adjustments.get('classic_bonus', 0.0)

        return max(0.3, min(lambda_adj, 3.5))  # Bounded

    def bivariate_poisson(
        self,
        lambda_home: float,
        lambda_away: float
    ) -> np.ndarray:
        """
        Bivariate Poisson with POSITIVE correlation.

        Uses trivariate reduction:
        λ₀ = k × min(λ_home, λ_away)  # Common component
        λ₁ = λ_home - λ₀
        λ₂ = λ_away - λ₀

        P(i,j) = Poisson(i; λ₁) × Poisson(j; λ₂) × Poisson(min(i,j); λ₀)
        """
        lambda_0 = self.correlation_k * min(lambda_home, lambda_away)
        lambda_1 = lambda_home - lambda_0
        lambda_2 = lambda_away - lambda_0

        prob_matrix = np.zeros((10, 10))
        for i in range(10):
            for j in range(10):
                prob = (
                    poisson.pmf(i, lambda_1) *
                    poisson.pmf(j, lambda_2) *
                    poisson.pmf(min(i, j), lambda_0)
                )
                prob_matrix[i, j] = prob

        return prob_matrix / prob_matrix.sum()  # Normalized
```

#### Brasileirão-Specific Adjustments

```python
# analysis/calibration.py
class BrasileiraoCalibrator:
    """Domain knowledge encoded as functions"""

    @staticmethod
    def get_travel_factor(distance_km: float) -> float:
        """
        Brazil is huge! Adjust for travel fatigue.

        Examples:
        - São Paulo → Rio (400km): 1.00 (no penalty)
        - São Paulo → Manaus (3900km): 0.82 (18% penalty)
        """
        if distance_km < 500:
            return 1.00
        elif distance_km < 1500:
            return 0.95
        elif distance_km < 2500:
            return 0.88
        else:
            return 0.82

    @staticmethod
    def calibrate_btts(p_btts: float) -> float:
        """
        Brasileirão has low BTTS rate (36% vs 50% Europe).
        Models overestimate → reduce by 15%.
        """
        if p_btts > 0.50:
            return p_btts * 0.85
        return p_btts
```

### Monte Carlo Simulator (`models/monte_carlo.py`)

```python
class MonteCarloSimulator:
    """
    Generate probability distributions via simulation.

    Default: 50,000 simulations for statistical convergence
    (standard error < 0.2%)
    """

    def simulate_match(
        self,
        lambda_home: float,
        lambda_away: float,
        correlation_k: float = 0.15
    ) -> Dict[str, Any]:
        """
        Simulate match with correlated goals.

        Returns:
            - p_home_wins, p_draws, p_away_wins
            - p_btts (both teams to score)
            - p_over_15, p_over_25, p_over_35
            - top_5_scores (most likely scorelines)
        """
        lambda_0 = correlation_k * min(lambda_home, lambda_away)
        lambda_h = lambda_home - lambda_0
        lambda_a = lambda_away - lambda_0

        # Vectorized simulation (numpy)
        goals_home = (
            np.random.poisson(lambda_h, self.n_simulations) +
            np.random.poisson(lambda_0, self.n_simulations)
        )
        goals_away = (
            np.random.poisson(lambda_a, self.n_simulations) +
            np.random.poisson(lambda_0, self.n_simulations)
        )

        total_goals = goals_home + goals_away

        return {
            'p_home_wins': (goals_home > goals_away).sum() / self.n_simulations,
            'p_draws': (goals_home == goals_away).sum() / self.n_simulations,
            'p_away_wins': (goals_away > goals_home).sum() / self.n_simulations,
            'p_btts': ((goals_home > 0) & (goals_away > 0)).sum() / self.n_simulations,
            'p_over_25': (total_goals > 2.5).sum() / self.n_simulations,
            'top_5_scores': self._extract_top_scores(goals_home, goals_away)
        }
```

### Kelly Criterion (`modules/roi/kelly_criterion.py`)

```python
class KellyCriterion:
    """
    Kelly Criterion: f* = (b*p - q) / b

    Where:
        b = odds - 1 (net odds)
        p = probability of winning
        q = 1 - p (probability of losing)
        f* = optimal fraction of bankroll to bet

    Safeguards:
    - Fractional Kelly (default 0.25 = Quarter Kelly)
    - Maximum stake cap (5% of bankroll)
    - Edge validation (only bet if positive)
    """

    def calculate_stake(
        self,
        probability: float,
        odds: float
    ) -> Dict[str, Any]:
        """
        Calculate optimal stake with safeguards.

        Example:
            Probability: 55% (0.55)
            Odds: 2.00
            Bankroll: R$1,000

            b = 2.00 - 1 = 1.00
            Implied prob = 1/2.00 = 0.50
            Edge = 0.55 - 0.50 = 0.05 (5%)

            Full Kelly = (1.00 × 0.55 - 0.45) / 1.00 = 0.10 (10%)
            Quarter Kelly = 0.10 × 0.25 = 0.025 (2.5%)

            Stake = R$1,000 × 0.025 = R$25.00
            EV = R$25.00 × (2.00 × 0.55 - 1) = R$2.50
        """
        b = odds - 1
        p = probability
        q = 1 - p

        implied_probability = 1 / odds
        edge = (probability - implied_probability) * 100

        if edge <= 0:
            return self._no_bet_result(f"Negative edge: {edge:.2f}%")

        # Full Kelly
        kelly_percentage = (b * p - q) / b

        # Apply conservative fraction
        adjusted_kelly = kelly_percentage * self.kelly_fraction

        # Apply maximum stake cap
        if adjusted_kelly > self.max_stake_percentage:
            adjusted_kelly = self.max_stake_percentage

        stake = round(self.bankroll * adjusted_kelly, 2)
        expected_value = round(stake * (odds * probability - 1), 2)

        return {
            'stake': stake,
            'kelly_percentage': round(adjusted_kelly * 100, 2),
            'is_value_bet': True,
            'edge': round(edge, 2),
            'expected_value': expected_value
        }
```

---

## 8. Testing Strategy

### Test Structure

```
tests/
├── test_dixon_coles_calibration.py   # Model accuracy tests
├── test_monte_carlo.py               # Simulation convergence
├── test_kelly_criterion.py           # Stake calculation validation
├── test_roi_simulator.py             # ROI projection tests
├── test_hybrid_collector.py          # CSV data loading
├── test_multi_api.py                 # API integration tests
└── test_integration.py               # End-to-end tests
```

### Testing Philosophy

1. **Unit Tests**: Core logic (models, calculators, utilities)
2. **Integration Tests**: Data flow (collector → model → UI)
3. **Property-Based Tests**: Statistical properties (e.g., probabilities sum to 1)
4. **Manual Tests**: UI interactions (Streamlit)

### Example Test

```python
# tests/test_dixon_coles_calibration.py
import pytest
from models.dixon_coles import DixonColesModel

def test_lambda_calculation():
    """Test lambda calculation with known inputs"""
    model = DixonColesModel('brasileirao')

    # Flamengo (strong attack) vs Cuiabá (weak defense)
    lambda_home = model.calculate_lambda(
        xg_for=1.8,
        xgc_against=1.6,
        is_home=True
    )

    # Should be high (strong team at home)
    assert 1.5 <= lambda_home <= 2.5

def test_probability_normalization():
    """Probabilities must sum to ~1.0"""
    model = DixonColesModel('brasileirao')
    prob_matrix = model.bivariate_poisson(1.5, 1.2)

    assert 0.99 <= prob_matrix.sum() <= 1.01

def test_defensive_game_adjustment():
    """Defensive games should have higher draw probability"""
    model = DixonColesModel('brasileirao')

    # Low-scoring game
    prob_matrix_defensive = model.bivariate_poisson(0.9, 0.8)
    p_draw_defensive = prob_matrix_defensive.trace()

    # High-scoring game
    prob_matrix_offensive = model.bivariate_poisson(2.5, 2.3)
    p_draw_offensive = prob_matrix_offensive.trace()

    # Defensive games have more draws
    assert p_draw_defensive > p_draw_offensive
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_dixon_coles_calibration.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run only fast tests (skip slow simulations)
pytest -m "not slow"

# Run in parallel (requires pytest-xdist)
pytest -n auto
```

---

## 9. Deployment

### Local Deployment (Development)

```bash
# Option 1: Direct Python
streamlit run app.py

# Option 2: Docker
docker-compose up -d
```

### Production Deployment (AWS EC2)

```bash
# 1. Launch EC2 instance (Ubuntu 22.04, t3.small)
# 2. Install Docker
curl -fsSL https://get.docker.com | sudo sh

# 3. Clone repository
git clone https://github.com/wemarques/prognosticos-brasileirao.git
cd prognosticos-brasileirao

# 4. Configure environment (optional)
echo "ODDS_API_KEY=your_key_here" >> .env

# 5. Deploy
docker-compose up -d

# 6. Configure reverse proxy (optional)
# See: DEPLOY_AWS_RAPIDO.md

# 7. Access
# http://your-ec2-ip:8501
```

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y gcc g++ git \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Create directories
RUN mkdir -p logs data cache

EXPOSE 8501

ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD ["streamlit", "run", "app.py", "--logger.level=info"]
```

### Environment Variables

```bash
# .env (optional - not required for CSV-based usage)
ODDS_API_KEY=your_key_here           # Optional: Real-time odds
LOG_LEVEL=INFO                       # DEBUG, INFO, WARNING, ERROR
STREAMLIT_SERVER_PORT=8501           # Default Streamlit port
```

### Health Monitoring

```yaml
# docker-compose.yml (excerpt)
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## 10. AI Assistant Best Practices

### General Guidelines

1. **Always check context first**
   - Read relevant files before making changes
   - Understand the data flow
   - Check existing patterns

2. **Maintain consistency**
   - Follow existing naming conventions
   - Use the same error handling patterns
   - Match existing docstring style

3. **Test changes**
   - Run affected tests after modifications
   - Add tests for new functionality
   - Verify UI still works (`streamlit run app.py`)

4. **Document decisions**
   - Add comments for complex logic
   - Update docstrings when changing signatures
   - Note WHY, not just WHAT

### Common Pitfalls to Avoid

#### ❌ Don't: Break the CSV-first architecture

```python
# BAD: Calling API for historical data
matches = api_collector.get_matches_from_api(season=2025)
```

```python
# GOOD: Use CSV for historical, API only for real-time odds
matches = collector.get_matches()  # CSV-based
if collector.odds_collector:
    odds = collector.get_odds_for_match(match_id)  # API only for odds
```

#### ❌ Don't: Ignore Brasileirão-specific calibrations

```python
# BAD: Generic prediction without calibration
p_btts = monte_carlo.simulate_btts(lambda_home, lambda_away)
return p_btts
```

```python
# GOOD: Apply Brasileirão calibration
p_btts_raw = monte_carlo.simulate_btts(lambda_home, lambda_away)
p_btts_calibrated = BrasileiraoCalibrator.calibrate_btts(p_btts_raw)
return p_btts_calibrated
```

#### ❌ Don't: Return unsafe predictions

```python
# BAD: No validation or bounds
def calculate_lambda(xg_for, xgc_against, is_home):
    return xg_for * 2.5  # Could be 10+ (unrealistic)
```

```python
# GOOD: Validated and bounded
def calculate_lambda(xg_for, xgc_against, is_home):
    lambda_val = (xg_for / self.league_avg_xg) * self.hfa
    return max(0.3, min(lambda_val, 3.5))  # Realistic bounds
```

#### ❌ Don't: Recommend unsafe betting

```python
# BAD: No stake limits
stake = bankroll * kelly_percentage  # Could be 50% of bankroll!
```

```python
# GOOD: Conservative limits
kelly_adjusted = kelly_percentage * self.kelly_fraction  # Quarter Kelly
stake = min(bankroll * kelly_adjusted, bankroll * 0.05)  # Max 5%
```

### Modification Guidelines

#### Adding a New League

1. **Create league configuration**
   ```python
   # leagues/premier_league.py
   from leagues.base_league import BaseLeague

   class PremierLeague(BaseLeague):
       def get_dixon_coles_params(self) -> dict:
           return {
               'hfa': 1.45,  # Research-based
               'ava': 0.90,
               'league_avg_goals': 2.85,  # Higher than Brasileirão
               'rho': -0.08
           }

       # Implement all abstract methods...
   ```

2. **Register league**
   ```python
   # leagues/league_registry.py
   from leagues.premier_league import PremierLeague

   LeagueRegistry.register_league('premier_league', PremierLeague)
   ```

3. **Add CSV data**
   ```bash
   data/csv/premier_league/
   ├── 2024_matches.csv
   ├── 2024_teams.csv
   └── 2024_standings.csv
   ```

4. **Test integration**
   ```python
   # tests/test_premier_league.py
   def test_premier_league_loading():
       collector = HybridDataCollector('premier_league')
       matches = collector.get_matches()
       assert len(matches) > 0
   ```

#### Modifying Statistical Models

1. **Research first**: Understand existing calibration
   ```python
   # Read: models/dixon_coles.py
   # Read: analysis/calibration.py
   # Read: tests/test_dixon_coles_calibration.py
   ```

2. **Document rationale**
   ```python
   def adjust_draw_probability(...):
       """
       Brasileirão-specific: Boost draws in defensive games.

       Rationale: Historical data shows 36% draw rate in low-scoring
       games (both lambda < 1.2) vs 28% in high-scoring games.

       Research: Analysis of 2022-2024 seasons (n=1140 matches)
       """
   ```

3. **Test against historical data**
   ```python
   # tests/test_model_accuracy.py
   def test_calibration_accuracy():
       """Verify model predictions match historical outcomes"""
       historical_matches = load_matches_2024()

       for match in historical_matches:
           predicted = model.predict(match)
           actual = match['result']

           # Log likelihood should be reasonable
           assert log_likelihood(predicted, actual) > threshold
   ```

4. **Update documentation**
   ```markdown
   # Update: MELHORIAS_SISTEMA.md or create new doc
   ## Model Improvement: Enhanced Draw Calibration

   ### Change
   - Added defensive game detection (lambda < 1.2)
   - Boost draw probability by 10% in defensive matchups

   ### Validation
   - Tested on 2024 season: accuracy improved 3.2%
   - Draw predictions: 36% (was 28%, actual 35%)
   ```

#### Adding New Features (Example: Referee Influence)

1. **Design data flow**
   ```
   CSV contains referee name
       ↓
   Load referee historical data
       ↓
   Calculate referee bias (cards, penalties)
       ↓
   Adjust model predictions
       ↓
   Display in UI
   ```

2. **Implement data layer**
   ```python
   # utils/referee_data.py
   class RefereeAnalyzer:
       def get_referee_stats(self, referee_name: str) -> Dict:
           """Get historical statistics for referee"""
           # Implementation...
   ```

3. **Integrate into model**
   ```python
   # models/dixon_coles.py
   def calculate_lambda(self, ..., referee_name=None):
       lambda_base = ...

       if referee_name:
           referee_adjustment = self._get_referee_adjustment(referee_name)
           lambda_base *= referee_adjustment

       return lambda_base
   ```

4. **Update UI**
   ```python
   # app.py
   if match.get('referee'):
       referee_stats = referee_analyzer.get_referee_stats(match['referee'])
       st.sidebar.markdown(f"**Referee:** {match['referee']}")
       st.sidebar.metric("Avg Cards/Game", referee_stats['avg_cards'])
   ```

5. **Test thoroughly**
   ```python
   # tests/test_referee_integration.py
   def test_referee_influence():
       model = DixonColesModel()

       # Lenient referee
       lambda_lenient = model.calculate_lambda(..., referee_name="Lenient Ref")

       # Strict referee
       lambda_strict = model.calculate_lambda(..., referee_name="Strict Ref")

       # Strict referees should slightly reduce attacking lambda
       assert lambda_strict < lambda_lenient
   ```

---

## 11. Common Tasks

### Task 1: Update CSV Data from API

```bash
# Run update script
python scripts/update_csv_from_api.py --league brasileirao --season 2025

# Verify updates
git diff data/csv/brasileirao/2025_matches.csv

# Commit if changes are valid
git add data/csv/brasileirao/
git commit -m "chore: Update match data for round 20"
```

### Task 2: Debug Prediction Accuracy

```python
# Create debug script: debug_prediction.py
from models.dixon_coles import DixonColesModel
from data.collectors.hybrid_collector import HybridDataCollector

collector = HybridDataCollector('brasileirao')
model = DixonColesModel('brasileirao')

# Get actual match result
match = collector.get_match('Flamengo', 'Palmeiras', round_number=15)
print(f"Actual: {match['home_score']}-{match['away_score']}")

# Get prediction
lambda_home, lambda_away = model.calculate_lambdas(
    home_team='Flamengo',
    away_team='Palmeiras',
    collector=collector
)
print(f"Predicted lambdas: {lambda_home:.2f}, {lambda_away:.2f}")

prob_matrix = model.bivariate_poisson(lambda_home, lambda_away)
most_likely_score = np.unravel_index(prob_matrix.argmax(), prob_matrix.shape)
print(f"Most likely score: {most_likely_score[0]}-{most_likely_score[1]}")
```

### Task 3: Add New Calibration Parameter

```python
# 1. Add parameter to league configuration
# leagues/brasileirao.py
def get_dixon_coles_params(self) -> dict:
    return {
        # ... existing params
        'new_parameter': 1.15,  # New calibration
    }

# 2. Use in model
# models/dixon_coles.py
def __init__(self, league_key='brasileirao'):
    params = self.league.get_dixon_coles_params()
    self.new_parameter = params.get('new_parameter', 1.0)  # Default fallback

# 3. Add tests
# tests/test_new_parameter.py
def test_new_parameter_loading():
    model = DixonColesModel('brasileirao')
    assert model.new_parameter == 1.15

# 4. Document in docstring
"""
New parameter: Controls X adjustment factor.
Default: 1.15 (calibrated from 2024 season data)
"""
```

### Task 4: Profile Performance

```python
# Create profiling script: profile_app.py
import cProfile
import pstats
from pstats import SortKey

def run_prediction():
    from models.dixon_coles import DixonColesModel
    from models.monte_carlo import MonteCarloSimulator

    model = DixonColesModel()
    simulator = MonteCarloSimulator(n_simulations=50000)

    # Run prediction
    lambda_home, lambda_away = 1.5, 1.2
    prob_matrix = model.bivariate_poisson(lambda_home, lambda_away)
    results = simulator.simulate_match(lambda_home, lambda_away)

    return results

# Profile
profiler = cProfile.Profile()
profiler.enable()

run_prediction()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats(SortKey.CUMULATIVE)
stats.print_stats(20)  # Top 20 functions by time
```

### Task 5: Generate Model Accuracy Report

```python
# scripts/model_accuracy_report.py
from data.collectors.hybrid_collector import HybridDataCollector
from models.dixon_coles import DixonColesModel
import pandas as pd

collector = HybridDataCollector('brasileirao')
model = DixonColesModel('brasileirao')

# Load completed matches
matches = collector.get_matches(status='FINISHED')

results = []
for match in matches:
    # Get prediction
    prob_home, prob_draw, prob_away = model.predict_match(
        match['home_team'],
        match['away_team'],
        collector
    )

    # Get actual result
    actual_result = get_actual_result(match)

    # Calculate log loss
    log_loss = calculate_log_loss(
        [prob_home, prob_draw, prob_away],
        actual_result
    )

    results.append({
        'match': f"{match['home_team']} vs {match['away_team']}",
        'predicted': f"{prob_home:.0%}/{prob_draw:.0%}/{prob_away:.0%}",
        'actual': actual_result,
        'log_loss': log_loss
    })

# Generate report
df = pd.DataFrame(results)
print(f"Average Log Loss: {df['log_loss'].mean():.4f}")
print(f"Accuracy: {df['predicted_correct'].sum() / len(df):.2%}")

# Save to CSV
df.to_csv('model_accuracy_report.csv', index=False)
```

---

## 12. Recent Evolution

### Major Milestones (Last 3 Months)

#### November 14, 2025: Hybrid CSV Architecture 🚀
**Impact: 25x Performance Improvement**

```
BEFORE:
- Every request = API call (2-5 seconds)
- Rate limits (10 req/min)
- Offline development impossible
- 85% uptime (API dependent)

AFTER:
- Historical data = CSV read (0.1 seconds)
- No rate limits for historical data
- Offline development enabled
- 99% uptime
```

**Changes:**
- Created `HybridDataCollector` (385 lines)
- Added CSV infrastructure: `data/csv/brasileirao/`
- Modified `app.py` to use CSV-first approach
- Created update script: `scripts/update_csv_from_api.py`

#### November 13, 2025: Kelly Criterion & ROI Simulation
**Impact: Professional Risk Management**

**Added:**
- `modules/roi/kelly_criterion.py` (256 lines)
- `modules/roi/roi_simulator.py` (180 lines)
- Bankroll management in UI
- 30/60/90 day ROI projections

**Safeguards:**
- Fractional Kelly (Quarter Kelly = 0.25)
- Maximum stake cap (5% of bankroll)
- Input validation (R$100-R$100,000)

#### November 8-9, 2025: Dixon-Coles Calibration Fixes
**Impact: 5 Critical Bugs Fixed**

1. ✅ **Positive correlation** (was negative → unrealistic draws)
2. ✅ **Defensive game adjustment** (+10% draw when λ < 1.2)
3. ✅ **Lambda capping** (max 3.5 to prevent outliers)
4. ✅ **Home advantage calibration** (1.35 multiplier + 0.30 additive)
5. ✅ **Normalization** (scaling 0.72, offset -0.15)

**Accuracy Improvement:**
- Draw predictions: 28% → 36% (actual: 35%)
- Over 2.5 predictions: 65% → 42% (actual: 40%)

#### November 12, 2025: Multi-League Architecture
**Impact: Extensibility**

**Created:**
- Abstract `BaseLeague` class
- `BrasileiraoSerieA` with calibrated parameters
- `LeagueRegistry` for easy extensibility

**Future-ready:**
- Adding Premier League = ~100 lines of code
- League-specific calibrations isolated
- No changes to core models required

### Code Quality Evolution

```
September 2025:  Initial implementation (3,000 lines)
                 - Basic Dixon-Coles
                 - API-based data collection

October 2025:    Enhancements (6,500 lines)
                 - Monte Carlo simulations
                 - Value bet detection
                 - Streamlit UI improvements

November 2025:   Production-ready (11,525 lines)
                 - Hybrid CSV architecture
                 - Risk management (Kelly)
                 - Multi-league support
                 - Comprehensive testing
                 - Professional logging
```

---

## Quick Reference Card

### File Navigation

| Task | File Location |
|------|---------------|
| Main UI | `app.py` |
| Prediction engine | `analysis/calculator.py` |
| Dixon-Coles model | `models/dixon_coles.py` |
| Monte Carlo | `models/monte_carlo.py` |
| Data collection | `data/collectors/hybrid_collector.py` |
| Kelly staking | `modules/roi/kelly_criterion.py` |
| League config | `leagues/brasileirao.py` |
| Calibrations | `analysis/calibration.py` |
| Logging | `utils/logger_config.py` |
| Cache | `utils/cache_manager.py` |

### Key Commands

```bash
# Development
streamlit run app.py              # Start UI
pytest                            # Run tests
python scripts/update_csv.py      # Update data

# Docker
docker-compose up -d              # Start services
docker-compose logs -f app        # View logs
docker-compose restart app        # Restart app

# Git
git checkout -b feature/name      # New branch
git add . && git commit -m "..."  # Commit
git push origin feature/name      # Push
```

### Key Constants

```python
# Brasileirão Parameters
HFA = 1.35                        # Home field advantage
AVA = 0.92                        # Away adjustment
LEAGUE_AVG_GOALS = 1.65           # Average goals per match
RHO = -0.12                       # Correlation parameter

# Risk Management
MAX_STAKE_PERCENTAGE = 0.05       # Never bet > 5%
DEFAULT_KELLY_FRACTION = 0.25     # Quarter Kelly (conservative)
MIN_BANKROLL = 100.0              # Minimum R$100
MAX_BANKROLL = 100000.0           # Maximum R$100,000

# Simulation
MONTE_CARLO_ITERATIONS = 50000    # Statistical convergence
ROI_SIMULATIONS = 1000            # Bankroll projections
```

---

## Support & Resources

### Documentation
- **Architecture:** `ARQUITETURA_MULTI_API.md`
- **CSV Implementation:** `IMPLEMENTACAO_CSV_COMPLETA.md`
- **Deployment:** `DEPLOY_AWS_RAPIDO.md`
- **Production:** `README_PRODUCAO.md`

### Git Repository
- **Main branch:** `main`
- **Development branch:** `claude/claude-md-mhziocqfqtrx4qwj-0113bzM6nUivxguDr6L67pL9`
- **GitHub:** https://github.com/wemarques/prognosticos-brasileirao

### Logging
- **Location:** `logs/` directory
- **Files:** `app.log`, `errors.log`, `performance.log`
- **Format:** Timestamp, level, module, message (emoji-enhanced)

---

**Remember:** This is an educational system. Always verify predictions independently and bet responsibly.

*Last updated: 2025-11-14 by AI Analysis*
