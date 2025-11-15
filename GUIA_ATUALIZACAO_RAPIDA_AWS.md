# 🔄 Guia Rápido: Atualização na AWS

**Última atualização:** 2025-11-15
**Branch atual:** `claude/aws-terminal-login-guide-016jNcfoec5sLvemKmEboVM7`

---

## 📋 Antes de Começar

Você vai precisar de:
- ✅ IP da sua instância EC2 (ex: `34.205.26.29`)
- ✅ Chave SSH (arquivo `.pem` no seu computador)
- ✅ Nome do branch que quer atualizar

---

## 🚀 Atualizar Código na AWS

### 1️⃣ Conectar na AWS via SSH

```bash
ssh -i ~/.ssh/prognosticos-brasileirao-key.pem ubuntu@34.205.26.29
```

> **💡 Dica:** Substitua o IP pelo IP da sua instância EC2

**Se der erro de permissão:**
```bash
chmod 400 ~/.ssh/prognosticos-brasileirao-key.pem
```

---

### 2️⃣ Navegar até o Projeto

```bash
cd prognosticos-brasileirao
```

---

### 3️⃣ Verificar Status Atual

```bash
# Ver branch atual
git branch

# Ver últimos commits
git log --oneline -5

# Ver status dos containers
docker-compose ps
```

---

### 4️⃣ Baixar Nova Versão

```bash
# Atualizar código do branch atual
git pull origin claude/aws-terminal-login-guide-016jNcfoec5sLvemKmEboVM7
```

**Se quiser mudar para outro branch:**
```bash
git fetch origin
git checkout nome-do-branch
git pull origin nome-do-branch
```

---

### 5️⃣ Reiniciar Aplicação

#### **Opção A: Restart Rápido** (sem rebuild)
```bash
docker-compose restart app
```
⏳ Aguarde 10-20 segundos

#### **Opção B: Rebuild Completo** (se mudou dependências)
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```
⏳ Aguarde 1-2 minutos

---

### 6️⃣ Verificar que Está Funcionando

```bash
# Ver logs em tempo real
docker-compose logs -f app

# Pressione Ctrl+C para sair
```

**Deve aparecer:**
```
app_1  | 2025-11-15 ... Streamlit running on http://0.0.0.0:8501
app_1  | 2025-11-15 ... Application started successfully
```

---

### 7️⃣ Testar no Navegador

Abra seu navegador e acesse:
```
http://34.205.26.29:8501
```

**Teste completo:**
1. ✅ Página carrega sem erros
2. ✅ No sidebar, mude para "Número da Rodada: 1"
3. ✅ Selecione "📋 Todos os Jogos da Rodada"
4. ✅ Verifique se os dados aparecem corretamente

---

## 🔧 Comandos Úteis

### Ver Status dos Containers
```bash
docker-compose ps
```

### Ver Logs (últimas 50 linhas)
```bash
docker-compose logs --tail=50 app
```

### Ver Logs em Tempo Real
```bash
docker-compose logs -f app
```

### Parar Aplicação
```bash
docker-compose down
```

### Iniciar Aplicação
```bash
docker-compose up -d
```

### Ver Espaço em Disco
```bash
df -h
```

### Ver Uso de Memória
```bash
free -h
```

### Limpar Containers Antigos
```bash
docker system prune -a
```
⚠️ **Cuidado:** Remove imagens não utilizadas

---

## 🐛 Problemas Comuns

### ❌ Erro: "Permission denied (publickey)"

**Solução:**
```bash
chmod 400 ~/.ssh/prognosticos-brasileirao-key.pem
ssh -i ~/.ssh/prognosticos-brasileirao-key.pem ubuntu@34.205.26.29
```

---

### ❌ Container não inicia após update

**Solução:**
```bash
# Ver o erro nos logs
docker-compose logs app

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

### ❌ Aplicação não responde no navegador

**Verificar se está rodando:**
```bash
docker-compose ps
```

**Se não estiver:**
```bash
docker-compose up -d
docker-compose logs -f app
```

**Verificar se a porta está aberta:**
```bash
curl http://localhost:8501/_stcore/health
```

Deve retornar: `{"status": "ok"}`

---

### ❌ Espaço em disco cheio

**Ver uso:**
```bash
df -h
```

**Limpar:**
```bash
# Limpar containers antigos
docker system prune -a

# Limpar logs
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

---

### ❌ Git pull falha (conflitos)

**Resetar para versão remota:**
```bash
git fetch origin
git reset --hard origin/claude/aws-terminal-login-guide-016jNcfoec5sLvemKmEboVM7
```

⚠️ **Atenção:** Isso descarta mudanças locais!

---

## 📊 Monitoramento

### Ver Uso de Recursos
```bash
# CPU e memória em tempo real
docker stats

# Uso específico do container
docker stats prognosticos-brasileirao-app-1
```

### Ver Processos
```bash
htop
```
Pressione `q` para sair

---

## 🔐 Segurança

### Verificar Security Group
No AWS Console:
- EC2 → Security Groups
- Verificar portas abertas:
  - `22` (SSH) - Apenas seu IP ✅
  - `8501` (App) - 0.0.0.0/0 ✅
  - `80` (HTTP) - 0.0.0.0/0 (se usar Nginx)
  - `443` (HTTPS) - 0.0.0.0/0 (se usar Nginx)

### Atualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

---

## 📝 Checklist de Atualização

Antes de atualizar:
- [ ] Backup da versão atual (anotar commit hash)
- [ ] Avisar usuários (se aplicável)
- [ ] Verificar espaço em disco (`df -h`)

Durante atualização:
- [ ] SSH conectado
- [ ] Git pull executado
- [ ] Containers reiniciados
- [ ] Logs verificados (sem erros)

Após atualização:
- [ ] Aplicação acessível no navegador
- [ ] Teste básico funcionando
- [ ] Performance normal
- [ ] Logs sem erros críticos

---

## 🎯 Template de Comandos Rápido

Cole isso no seu terminal para atualizar tudo de uma vez:

```bash
# Conectar, atualizar e reiniciar
ssh -i ~/.ssh/prognosticos-brasileirao-key.pem ubuntu@34.205.26.29 << 'EOF'
cd prognosticos-brasileirao
echo "📥 Baixando atualizações..."
git pull origin claude/aws-terminal-login-guide-016jNcfoec5sLvemKmEboVM7
echo "🔄 Reiniciando aplicação..."
docker-compose restart app
echo "✅ Aguarde 15 segundos e teste em: http://34.205.26.29:8501"
sleep 15
docker-compose logs --tail=20 app
EOF
```

---

## 🆘 Precisa de Ajuda?

**Documentação completa:**
- `DEPLOY_AWS_RAPIDO.md` - Deploy completo
- `README_CSV.md` - Sistema de dados CSV
- `README.md` - Documentação geral

**Logs para debug:**
```bash
# Copiar logs para análise
docker-compose logs app > ~/app-logs.txt

# Baixar logs para seu computador
scp -i ~/.ssh/prognosticos-brasileirao-key.pem \
  ubuntu@34.205.26.29:~/app-logs.txt \
  ./app-logs.txt
```

---

## ✅ Pronto!

Sua aplicação está atualizada! 🎉

**Próximos passos:**
1. ✅ Teste a aplicação no navegador
2. ✅ Monitore os logs por alguns minutos
3. ✅ Informe os usuários da atualização

---

**Criado:** 2025-11-15
**Versão:** 1.0
**Autor:** Claude Code
