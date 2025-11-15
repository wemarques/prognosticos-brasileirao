# 🔄 Sincronização GitHub → AWS

**Data:** 2025-11-15
**Status:** ⚠️ DESATUALIZADO - AWS rodando versão antiga

---

## ❌ Problema Identificado

A instância AWS está rodando uma **versão desatualizada** do código, anterior ao merge da PR #16.

### Comparação de Versões

| Aspecto | AWS (Versão Antiga) | GitHub (Versão Atual) |
|---------|---------------------|----------------------|
| **Commit** | Anterior a `eaad11e` | `d970729` (HEAD) |
| **Data Collector** | `FootballDataCollectorV2` | `HybridDataCollector` |
| **Arquitetura** | 100% API | CSV + Odds API |
| **Sidebar** | Sem seção "Fonte de Dados" | ✅ Com seção "Fonte de Dados" |
| **Performance** | 2-5s por consulta | 0.1s (20x mais rápido) |
| **Arquivos CSV** | ❌ Não usa | ✅ Usa 3 CSVs (60+ registros) |

---

## 🎯 Mudanças na Versão Nova

### 1. **Layout do Sidebar**
```diff
+ st.sidebar.header("⚙️ Configurações")
+
+ # Nova seção: Informações sobre fonte de dados
+ with st.sidebar.expander("📊 Fonte de Dados", expanded=False):
+     csv_info = collector.get_csv_info()
+     st.write(f"**Liga:** {csv_info['league']}")
+
+     for file_type, info in csv_info['files'].items():
+         if info['exists']:
+             st.success(f"✅ {file_type.title()}: {info['rows']} registros")
+         else:
+             st.error(f"❌ {file_type.title()}: Não encontrado")
```

### 2. **Data Collector**
```diff
- from data.collectors.football_data_collector_v2 import FootballDataCollectorV2
+ from data.collectors.hybrid_collector import HybridDataCollector

- api_config = get_api_config(selected_league)
- collector = FootballDataCollectorV2(selected_league, api_config)
+ odds_api_key = os.getenv('ODDS_API_KEY')
+ collector = HybridDataCollector(league_key=selected_league, odds_api_key=odds_api_key)
```

### 3. **Arquivos CSV Adicionados**
```
data/csv/brasileirao/
├── 2025_matches.csv      (20 jogos)
├── 2025_teams.csv        (20 times)
└── 2025_standings.csv    (30 entradas)
```

---

## 🚀 Comandos para Sincronizar AWS

### **Opção 1: Atualização Rápida (Recomendado)** ⭐

```bash
# 1. Conectar à instância EC2
ssh -i sua-chave.pem ubuntu@34.205.26.29

# 2. Ir para o diretório do projeto
cd ~/prognosticos-brasileirao

# 3. Verificar branch atual
git branch
# Deve mostrar: claude/prognosticos-brasileirao-aws-01EmQDeGg8s6giY3fKHkD4bv

# 4. Fazer pull das últimas mudanças
git fetch origin
git pull origin claude/prognosticos-brasileirao-aws-01EmQDeGg8s6giY3fKHkD4bv

# 5. Verificar que os CSVs foram baixados
ls -la data/csv/brasileirao/
# Deve listar: 2025_matches.csv, 2025_teams.csv, 2025_standings.csv

# 6. Parar containers
docker-compose down

# 7. Rebuild (limpar cache para garantir)
docker-compose build --no-cache

# 8. Iniciar novamente
docker-compose up -d

# 9. Verificar logs
docker-compose logs -f app
```

### **Opção 2: Reset Completo (Se Opção 1 falhar)**

```bash
# 1. Conectar à EC2
ssh -i sua-chave.pem ubuntu@34.205.26.29

# 2. Parar tudo
cd ~/prognosticos-brasileirao
docker-compose down -v

# 3. Fazer backup do .env (se existir)
cp .env .env.backup 2>/dev/null || true

# 4. Remover diretório atual
cd ~
mv prognosticos-brasileirao prognosticos-brasileirao.old

# 5. Clonar novamente
git clone https://github.com/wemarques/prognosticos-brasileirao.git
cd prognosticos-brasileirao

# 6. Checkout da branch correta
git checkout claude/prognosticos-brasileirao-aws-01EmQDeGg8s6giY3fKHkD4bv

# 7. Restaurar .env (se tinha)
cp ~/prognosticos-brasileirao.old/.env .env 2>/dev/null || true

# 8. Verificar CSVs
ls -la data/csv/brasileirao/

# 9. Build e start
docker-compose build
docker-compose up -d

# 10. Verificar logs
docker-compose logs -f app
```

---

## ✅ Checklist de Verificação

Após sincronizar, verificar no navegador (`http://34.205.26.29:8501`):

### **1. Sidebar - Seção "Fonte de Dados"**
- [ ] Expandir "📊 Fonte de Dados" no sidebar
- [ ] Verificar mensagens:
  - ✅ Matches: 20 registros
  - ✅ Teams: 20 registros
  - ✅ Standings: 30 registros
  - ⚠️ Odds API não configurada (se não tiver key)

### **2. Performance**
- [ ] Carregar página < 1 segundo
- [ ] Mudar de liga: resposta imediata
- [ ] Sem mensagens de erro de API

### **3. Funcionalidades**
- [ ] Seletor de liga funcionando
- [ ] Seletor de rodada funcionando
- [ ] Times listados corretamente
- [ ] Próximos jogos aparecendo

---

## 🔍 Comandos de Diagnóstico

### **Verificar versão do código**
```bash
ssh -i sua-chave.pem ubuntu@34.205.26.29
cd ~/prognosticos-brasileirao

# Ver commit atual
git log -1 --oneline
# Deve mostrar: d970729 Merge pull request #16...

# Ver diferença com versão anterior
git diff 41435be HEAD app.py | grep -A5 "HybridDataCollector"
```

### **Verificar CSVs**
```bash
# Contar linhas (deve ser 21, 21, 31)
wc -l data/csv/brasileirao/*.csv

# Ver primeiras linhas
head -3 data/csv/brasileirao/2025_matches.csv
```

### **Verificar containers**
```bash
# Status
docker-compose ps

# Logs em tempo real
docker-compose logs -f app

# Entrar no container
docker-compose exec app bash
ls -la data/csv/brasileirao/
```

### **Verificar que está usando HybridCollector**
```bash
# Buscar no código
grep -n "HybridDataCollector" app.py
# Deve retornar linha 4 e 146

# Verificar que arquivo existe
ls -la data/collectors/hybrid_collector.py
```

---

## 🐛 Troubleshooting

### **Problema: CSVs não aparecem após sync**

```bash
# Verificar se arquivo existe no git
git ls-files | grep csv

# Se não existir, pode ter .gitignore bloqueando
cat .gitignore | grep csv

# Forçar add (se necessário)
git add -f data/csv/brasileirao/*.csv
git commit -m "Force add CSVs"
git push
```

### **Problema: Docker build falha**

```bash
# Limpar tudo do Docker
docker system prune -a
docker volume prune

# Build novamente
docker-compose build --no-cache
```

### **Problema: Aplicação não inicia**

```bash
# Ver logs detalhados
docker-compose logs app

# Verificar porta
sudo lsof -i :8501

# Matar processo se necessário
sudo kill -9 $(sudo lsof -t -i:8501)
docker-compose up -d
```

---

## 📊 Diferenças Visuais Esperadas

### **ANTES (Versão Antiga)**
```
Sidebar:
├── ⚙️ Configurações
│   ├── Liga: [selector]
│   ├── ✅ Brasileirão 2025 carregado
├── 💰 Gestão de Banca
│   └── ...
└── Número da Rodada
```

### **DEPOIS (Versão Nova)** ✅
```
Sidebar:
├── ⚙️ Configurações
│   ├── Liga: [selector]
│   ├── ✅ Brasileirão 2025 carregado
├── 📊 Fonte de Dados (NOVO!)
│   ├── Liga: brasileirao
│   ├── ✅ Matches: 20 registros
│   ├── ✅ Teams: 20 registros
│   ├── ✅ Standings: 30 registros
│   └── ⚠️ Odds API não configurada
├── 💰 Gestão de Banca
│   └── ...
└── Número da Rodada
```

---

## 📝 Commits Relevantes

| Commit | Descrição | Data |
|--------|-----------|------|
| `d970729` | Merge PR #16 - CSV hybrid architecture | 2025-11-15 |
| `28a9861` | docs: Add AWS deployment guide | 2025-11-14 |
| `eaad11e` | feat: Implement hybrid CSV + Odds API | 2025-11-14 |
| `41435be` | ⬅️ **Versão rodando na AWS** | Anterior |

---

## 🎯 Próximos Passos Após Sincronização

1. ✅ Verificar que layout está correto
2. ✅ Testar performance (deve ser instantânea)
3. 📸 Tirar screenshot do novo layout
4. 📝 Documentar versão em produção
5. 🔄 Configurar auto-deploy (opcional)

---

## 📞 Contato

Se problemas persistirem:
1. Executar comandos de diagnóstico acima
2. Coletar logs: `docker-compose logs app > logs.txt`
3. Verificar branch: `git log -1`
4. Reportar issue com logs

---

**Criado:** 2025-11-15
**Branch:** `claude/prognosticos-brasileirao-aws-01EmQDeGg8s6giY3fKHkD4bv`
**Commit esperado na AWS:** `d970729`
