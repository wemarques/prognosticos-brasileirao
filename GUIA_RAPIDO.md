# 🚀 Guia Rápido de Início

## ⚡ Começar em 5 Minutos

### 1️⃣ Clonar o Repositório

```bash
git clone https://github.com/wemarques/prognosticos-brasileirao.git
cd prognosticos-brasileirao
```

### 2️⃣ Instalar Dependências

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# No Linux/Mac:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 3️⃣ Configurar API (Opcional para Teste)

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env e adicionar sua chave (ou deixar vazio para modo teste)
# API_FOOTBALL_KEY=sua_chave_aqui
```

**Para obter chave gratuita da API:**
- Acesse: https://www.api-football.com/
- Registre-se (plano gratuito: 100 requisições/dia)
- Copie sua chave e cole no arquivo `.env`

### 4️⃣ Executar o Sistema

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`

### 5️⃣ Usar a Interface

1. **Marque "Usar dados simulados"** (para testar sem API)
2. **Selecione os times** no menu lateral
3. **Configure contexto** (distância, altitude, tipo de jogo)
4. **Clique em "GERAR PROGNÓSTICO"**
5. **Veja os resultados** em abas organizadas

## 📊 O Que o Sistema Faz?

### Análises Automáticas
- ✅ **Probabilidades 1X2** (Vitória Casa / Empate / Vitória Fora)
- ✅ **Over/Under** (1.5, 2.5, 3.5 gols)
- ✅ **BTTS** (Ambos marcam)
- ✅ **Placares prováveis** (top 5)
- ✅ **Value Bets** (apostas com edge positivo)
- ✅ **Recomendações de stake** (critério de Kelly)

### Modelos Utilizados
- **Dixon-Coles**: Modelo estatístico de Poisson bivariada
- **Monte Carlo**: 50.000 simulações para validação
- **Calibrações BR**: Ajustes específicos para o Brasileirão

### Ajustes Contextuais
- 🏠 **Home Field Advantage** (1.53x para mandante)
- ✈️ **Distância de viagem** (penaliza visitante)
- ⛰️ **Altitude do estádio** (afeta visitante)
- 🔥 **Clássicos/Derbies** (bônus de intensidade)

## 🎯 Exemplo de Uso

### Cenário: Flamengo vs Palmeiras

**Entrada:**
- Time mandante: Flamengo
- Time visitante: Palmeiras
- Distância: 1.500 km
- Altitude: 10m
- Tipo: Clássico

**Saída (exemplo):**
```
Probabilidades:
  Vitória Flamengo: 52.3%
  Empate: 26.1%
  Vitória Palmeiras: 21.6%

Over 2.5 gols: 58.7%
Ambos marcam: 64.2%

Placar mais provável: 2-1

Value Bets Detectadas:
  🎯 Vitória Flamengo
     Edge: 8.3%
     Stake recomendado: 2.1% do bankroll
```

## 🔧 Resolução de Problemas

### Erro: "API key not found"
- Marque "Usar dados simulados" na interface
- OU configure a chave no arquivo `.env`

### Erro: "Module not found"
- Execute: `pip install -r requirements.txt`
- Certifique-se de estar no ambiente virtual

### Interface não abre
- Verifique se a porta 8501 está livre
- Tente: `streamlit run app.py --server.port 8502`

## 📚 Próximos Passos

1. **Teste com dados simulados** para entender o sistema
2. **Configure a API** para dados reais
3. **Explore as abas** da interface
4. **Analise value bets** detectadas
5. **Ajuste contextos** para diferentes cenários

## 🌐 Deploy Online (Opcional)

Para colocar o sistema na nuvem gratuitamente:

### Streamlit Cloud
1. Faça fork do repositório
2. Acesse: https://share.streamlit.io
3. Conecte seu GitHub
4. Selecione o repositório
5. Configure variáveis de ambiente (API keys)
6. Deploy automático!

## ⚠️ Aviso Importante

Este sistema é para **fins educacionais e análise estatística**.

- ❌ Não incentivamos apostas
- ❌ Não garantimos lucros
- ❌ Não nos responsabilizamos por perdas
- ✅ Use com responsabilidade
- ✅ Aposte apenas o que pode perder

## 💡 Dicas

- **Comece pequeno**: Teste com stakes baixos
- **Valide resultados**: Compare com suas próprias análises
- **Entenda os modelos**: Leia sobre Dixon-Coles e Monte Carlo
- **Ajuste calibrações**: Adapte para sua estratégia
- **Mantenha registros**: Acompanhe performance ao longo do tempo

## 📞 Suporte

- **Issues**: https://github.com/wemarques/prognosticos-brasileirao/issues
- **Documentação API**: https://www.api-football.com/documentation-v3

---

**Bom prognóstico! ⚽📊**

