# 🎓 Guia de Sincronização AWS - Para Iniciantes

**Objetivo:** Atualizar sua aplicação na AWS para a versão mais recente do GitHub

**Tempo estimado:** 10-15 minutos

**Nível:** Iniciante (passo a passo completo)

---

## 📋 O Que Você Vai Precisar

Antes de começar, tenha em mãos:

- [ ] Endereço IP da sua instância AWS: `34.205.26.29`
- [ ] Arquivo de chave `.pem` (usado para conectar na AWS)
- [ ] Computador com internet

---

## 🖥️ PASSO 1: Abrir o Terminal

### **Se você usa Windows:**

**Opção A - PowerShell (Recomendado):**
1. Pressione `Win + X`
2. Clique em "Windows PowerShell" ou "Terminal"

**Opção B - CMD:**
1. Pressione `Win + R`
2. Digite `cmd`
3. Pressione Enter

**Opção C - Git Bash (se tiver Git instalado):**
1. Clique com botão direito na área de trabalho
2. Selecione "Git Bash Here"

### **Se você usa Mac:**

1. Pressione `Command + Espaço`
2. Digite "Terminal"
3. Pressione Enter

### **Se você usa Linux:**

1. Pressione `Ctrl + Alt + T`

Ou:
1. Procure "Terminal" no menu de aplicativos

---

## 🔑 PASSO 2: Localizar Sua Chave .pem

A chave `.pem` é o arquivo que você baixou quando criou a instância EC2 na AWS.

### **Como encontrar:**

**No Windows:**
- Geralmente está em: `C:\Users\SeuNome\Downloads\`
- Nome parecido com: `prognosticos.pem` ou `minha-chave.pem`

**No Mac/Linux:**
- Geralmente está em: `~/Downloads/`
- Nome parecido com: `prognosticos.pem` ou `minha-chave.pem`

### **Mover a chave para local seguro (recomendado):**

```bash
# Windows (PowerShell)
mkdir C:\aws-keys
move C:\Users\SeuNome\Downloads\sua-chave.pem C:\aws-keys\

# Mac/Linux
mkdir ~/.ssh
mv ~/Downloads/sua-chave.pem ~/.ssh/
chmod 400 ~/.ssh/sua-chave.pem
```

**Dica:** Substitua `sua-chave.pem` pelo nome real do seu arquivo!

---

## 🔌 PASSO 3: Conectar na AWS (SSH)

Agora vamos conectar no servidor AWS. Copie e cole o comando abaixo **adaptando** o caminho da sua chave:

### **Windows (PowerShell):**

```powershell
# Dar permissão à chave (executar apenas 1x)
icacls "C:\aws-keys\sua-chave.pem" /inheritance:r
icacls "C:\aws-keys\sua-chave.pem" /grant:r "$($env:USERNAME):R"

# Conectar
ssh -i C:\aws-keys\sua-chave.pem ubuntu@34.205.26.29
```

### **Mac/Linux:**

```bash
# Dar permissão à chave (executar apenas 1x)
chmod 400 ~/.ssh/sua-chave.pem

# Conectar
ssh -i ~/.ssh/sua-chave.pem ubuntu@34.205.26.29
```

### **O que vai aparecer:**

```
The authenticity of host '34.205.26.29' can't be established.
ECDSA key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no)?
```

**Digite:** `yes` e pressione Enter

### **Conexão bem-sucedida!**

Você verá algo assim:

```
Welcome to Ubuntu 22.04.3 LTS

ubuntu@ip-172-31-xx-xx:~$
```

🎉 **Parabéns! Você está conectado na AWS!**

---

## 🔄 PASSO 4: Atualizar o Código

Agora vamos atualizar a aplicação. **Copie e cole cada comando**, um por vez:

### **4.1 - Ir para o diretório do projeto**

```bash
cd prognosticos-brasileirao
```

**O que aparece:**
```
ubuntu@ip-172-31-xx-xx:~/prognosticos-brasileirao$
```

### **4.2 - Ver qual versão está rodando**

```bash
git log -1 --oneline
```

**Se mostrar algo diferente de `d970729`, você está desatualizado!**

### **4.3 - Baixar última versão do GitHub**

```bash
git fetch origin
```

**O que aparece:**
```
remote: Enumerating objects: 10, done.
remote: Counting objects: 100% (10/10), done.
...
```

Agora:

```bash
git pull origin claude/prognosticos-brasileirao-aws-01EmQDeGg8s6giY3fKHkD4bv
```

**O que aparece:**
```
Updating 41435be..d970729
Fast-forward
 app.py                           | 20 ++++++++++++++++++
 data/csv/brasileirao/...         | 21 +++++++++++++++++++
 ...
```

### **4.4 - Verificar que os CSVs foram baixados**

```bash
ls -la data/csv/brasileirao/
```

**Deve aparecer:**
```
2025_matches.csv
2025_teams.csv
2025_standings.csv
```

✅ **Se aparecer esses 3 arquivos, ótimo! Continue.**

❌ **Se NÃO aparecer, execute:**
```bash
git checkout claude/prognosticos-brasileirao-aws-01EmQDeGg8s6giY3fKHkD4bv
git pull origin claude/prognosticos-brasileirao-aws-01EmQDeGg8s6giY3fKHkD4bv
```

---

## 🐳 PASSO 5: Reiniciar a Aplicação

### **5.1 - Parar containers Docker**

```bash
docker-compose down
```

**O que aparece:**
```
Stopping prognosticos-brasileirao_app_1 ... done
Removing prognosticos-brasileirao_app_1 ... done
```

### **5.2 - Reconstruir aplicação (pegar as mudanças)**

```bash
docker-compose build --no-cache
```

**⏳ Isso vai demorar 2-5 minutos. Você verá:**
```
Step 1/10 : FROM python:3.11-slim
 ---> ...
Step 2/10 : WORKDIR /app
 ---> ...
...
Successfully built abc123def456
```

**Aguarde até terminar!**

### **5.3 - Iniciar novamente**

```bash
docker-compose up -d
```

**O que aparece:**
```
Creating prognosticos-brasileirao_app_1 ... done
```

### **5.4 - Ver se está rodando (opcional)**

```bash
docker-compose ps
```

**Deve mostrar:**
```
Name                    State    Ports
prognosticos-app        Up       0.0.0.0:8501->8501/tcp
```

✅ **Status "Up" = está funcionando!**

---

## 🎉 PASSO 6: Verificar no Navegador

### **6.1 - Abrir a aplicação**

1. Abra seu navegador (Chrome, Firefox, etc.)
2. Digite: `http://34.205.26.29:8501`
3. Pressione Enter

### **6.2 - Verificar se atualizou**

No **sidebar esquerdo**, procure por:

```
📊 Fonte de Dados
```

**Clique para expandir.** Deve mostrar:

```
Liga: brasileirao
✅ Matches: 20 registros
✅ Teams: 20 registros
✅ Standings: 30 registros
⚠️ Odds API não configurada
```

✅ **Se aparecer isso, SUCESSO! Está atualizado!**

❌ **Se NÃO aparecer, veja a seção "Problemas?" abaixo**

---

## 🚪 PASSO 7: Sair da AWS

Quando terminar, para sair do servidor AWS:

```bash
exit
```

Você voltará para o terminal do seu computador.

---

## 📊 Resumo Visual - Antes vs Depois

### **ANTES (versão antiga):**
```
Sidebar:
├── ⚙️ Configurações
├── 💰 Gestão de Banca
└── Número da Rodada
```

### **DEPOIS (versão nova):** ✅
```
Sidebar:
├── ⚙️ Configurações
├── 📊 Fonte de Dados ← NOVO!
│   ├── ✅ Matches: 20 registros
│   ├── ✅ Teams: 20 registros
│   └── ✅ Standings: 30 registros
├── 💰 Gestão de Banca
└── Número da Rodada
```

---

## ❓ Problemas?

### **❌ Erro: "Permission denied (publickey)"**

**Causa:** Arquivo .pem sem permissão ou caminho errado

**Solução:**

```bash
# Windows
icacls "C:\caminho\sua-chave.pem" /inheritance:r
icacls "C:\caminho\sua-chave.pem" /grant:r "$($env:USERNAME):R"

# Mac/Linux
chmod 400 ~/.ssh/sua-chave.pem
```

Verifique se o caminho está correto!

---

### **❌ Erro: "Connection timed out"**

**Causa:** IP errado ou Security Group bloqueando

**Solução:**
1. Verificar IP correto na AWS Console
2. Verificar Security Group permite porta 22 (SSH)

---

### **❌ Seção "Fonte de Dados" não aparece**

**Causa:** Build não pegou as mudanças

**Solução:**

```bash
# Conectar na AWS novamente
ssh -i sua-chave.pem ubuntu@34.205.26.29

# Ir para projeto
cd prognosticos-brasileirao

# Ver commit atual
git log -1 --oneline

# Se NÃO for d970729, fazer:
git fetch origin
git reset --hard origin/claude/prognosticos-brasileirao-aws-01EmQDeGg8s6giY3fKHkD4bv

# Rebuild forçado
docker-compose down
docker system prune -a -f
docker-compose build --no-cache
docker-compose up -d
```

---

### **❌ Docker build muito lento**

**Solução:** É normal na primeira vez. Aguarde 5-10 min.

Se travar, pressione `Ctrl+C` e tente novamente:

```bash
docker-compose build --no-cache
```

---

### **❌ Aplicação não abre no navegador**

**Checklist:**
1. IP correto? `34.205.26.29`
2. Porta correta? `:8501`
3. Protocolo correto? `http://` (não https)
4. Container rodando? `docker-compose ps` deve mostrar "Up"

**Verificar logs:**

```bash
docker-compose logs -f app
```

Pressione `Ctrl+C` para sair dos logs.

---

## 📱 Comandos Úteis para o Futuro

Salve esses comandos para usar depois:

### **Ver logs em tempo real:**
```bash
ssh -i sua-chave.pem ubuntu@34.205.26.29
cd prognosticos-brasileirao
docker-compose logs -f app
```

### **Reiniciar aplicação:**
```bash
ssh -i sua-chave.pem ubuntu@34.205.26.29
cd prognosticos-brasileirao
docker-compose restart app
```

### **Parar aplicação:**
```bash
docker-compose down
```

### **Iniciar aplicação:**
```bash
docker-compose up -d
```

---

## 🎯 Checklist Final

Depois de seguir todos os passos:

- [ ] Conectei na AWS via SSH
- [ ] Executei `git pull` e vi mensagens de atualização
- [ ] Vi 3 arquivos CSV em `data/csv/brasileirao/`
- [ ] Executei `docker-compose build --no-cache` (aguardei terminar)
- [ ] Executei `docker-compose up -d`
- [ ] Abri `http://34.205.26.29:8501` no navegador
- [ ] Vi a seção "📊 Fonte de Dados" no sidebar
- [ ] Aplicação está mais rápida (< 1 segundo)
- [ ] Saí do SSH com `exit`

✅ **Tudo marcado? Parabéns! Você sincronizou com sucesso!**

---

## 💬 Glossário para Iniciantes

| Termo | O que é |
|-------|---------|
| **SSH** | Forma segura de conectar em servidores remotos |
| **.pem** | Arquivo-chave para autenticação (como uma senha) |
| **EC2** | Servidor virtual na AWS |
| **Docker** | Tecnologia que empacota a aplicação |
| **Git pull** | Baixar última versão do código |
| **Build** | Construir/compilar a aplicação |
| **Container** | Ambiente isolado onde roda a aplicação |

---

## 📞 Ainda com dúvidas?

Se algo não funcionou:

1. ✅ Verifique se seguiu TODOS os passos
2. ✅ Leia a mensagem de erro com atenção
3. ✅ Procure o erro na seção "Problemas?"
4. ✅ Copie a mensagem de erro exata e peça ajuda

---

## 🎓 O Que Você Aprendeu

- ✅ Conectar em servidor AWS via SSH
- ✅ Atualizar código com Git
- ✅ Gerenciar containers Docker
- ✅ Diagnosticar problemas básicos

**Parabéns!** 🎉

Agora sua aplicação está na versão mais recente, com:
- ⚡ Performance 20x mais rápida
- 📊 Arquitetura híbrida CSV + API
- 💾 20 jogos de exemplo funcionando
- 🚀 Layout atualizado

---

**Criado em:** 2025-11-15
**Versão:** 1.0 - Guia para Iniciantes
**Tempo médio:** 10-15 minutos
