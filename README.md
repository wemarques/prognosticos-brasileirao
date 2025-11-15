# Sistema de Prognósticos - Brasileirão

Sistema automatizado de análise e prognósticos para o Campeonato Brasileiro Série A.

## Tecnologias
- Python 3.9+
- Streamlit
- APIs: API-Football, The-Odds-API

## Funcionalidades
- Coleta automática de dados via APIs
- Modelos estatísticos (Dixon-Coles, Monte Carlo)
- Calibrações específicas para o Brasileirão
- Interface visual intuitiva
- Detecção automática de value bets

## Instalação e Configuração

### 1. Instalação de Dependências

```bash
pip install -r requirements.txt
```

### 2. Configuração de Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas API keys:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione suas chaves de API:

```env
# API-Football (obtenha em: https://www.api-football.com/)
API_FOOTBALL_KEY=sua_chave_aqui

# Odds API (opcional - obtenha em: https://the-odds-api.com/)
ODDS_API_KEY=sua_chave_aqui

# Logging configuration
LOG_LEVEL=INFO
```

### 3. Executar o Sistema

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

O sistema usa uma arquitetura híbrida:
- **CSV**: Dados históricos e cadastrais (gratuito, rápido)
- **API**: Odds em tempo real (quando configurado)

Os arquivos CSV ficam em `data/csv/{liga}/` e são atualizados periodicamente.

⚠️ **Aviso:** Use com responsabilidade. Aposte apenas o que pode perder.