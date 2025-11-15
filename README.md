# Sistema de Prognósticos - Multi-Ligas

Sistema automatizado de análise e prognósticos para futebol.

## Ligas Suportadas
- 🇧🇷 Brasileirão Série A
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)

## Tecnologias
- Python 3.9+
- Streamlit
- Dados: Arquivos CSV locais
- Odds: The Odds API (tempo real)

## Funcionalidades
- Leitura de dados de arquivos CSV (rápido e sem limites de API)
- Modelos estatísticos (Dixon-Coles, Monte Carlo)
- Calibrações específicas por liga
- Interface visual intuitiva
- Detecção automática de value bets
- Odds em tempo real via The Odds API

## Instalação e Configuração

### 1. Instalação de Dependências

```bash
pip install -r requirements.txt
```

### 2. Copiar Arquivos CSV

**IMPORTANTE**: O sistema usa arquivos CSV locais para dados de jogos e times.

Siga as instruções em `SETUP_CSV_FILES.md` para copiar os arquivos CSV necessários para as pastas corretas.

### 3. Configuração de Variáveis de Ambiente (Opcional)

O arquivo `.env` já foi criado. Se você quiser odds em tempo real, edite-o e adicione sua chave da The Odds API:

```env
# ODDS API (para buscar odds em tempo real das casas de apostas)
# Obtenha sua chave em: https://the-odds-api.com/
ODDS_API_KEY=sua_chave_aqui

# Logging configuration
LOG_LEVEL=INFO
```

**Nota**: O sistema funciona SEM a Odds API (usará apenas dados dos CSVs).

### 4. Executar o Sistema

```bash
streamlit run app.py
```

O sistema abrirá automaticamente no seu navegador em `http://localhost:8501`

## Como usar
1. Acesse o app (online ou local)
2. Selecione a liga no sidebar
3. Selecione os times mandante e visitante
4. Configure a rodada
5. Clique em "Gerar Prognóstico"
6. Analise os resultados e recomendações de apostas

## Estrutura de Dados

O sistema usa arquivos CSV locais:
- **CSV**: Todos os dados de jogos, times e classificações
- **The Odds API**: Apenas para odds em tempo real (opcional)

### Arquivos CSV Necessários

```
data/csv/
├── brasileirao/
│   ├── 2025_matches.csv
│   ├── 2025_teams.csv
│   └── 2025_standings.csv (opcional)
└── premier_league/
    ├── 2025_matches.csv
    ├── 2025_teams.csv
    └── 2025_standings.csv (opcional)
```

Consulte `SETUP_CSV_FILES.md` para instruções detalhadas.

⚠️ **Aviso:** Use com responsabilidade. Aposte apenas o que pode perder.