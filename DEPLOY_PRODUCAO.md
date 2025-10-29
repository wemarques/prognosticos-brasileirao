# 🚀 GUIA DE DEPLOY EM PRODUÇÃO - PASSO A PASSO

## 📋 Opções de Deploy Disponíveis

### 1. **Streamlit Cloud** (Mais Fácil - Recomendado para Começar)
### 2. **Heroku** (Gratuito com limitações)
### 3. **AWS/Google Cloud** (Mais Robusto)
### 4. **DigitalOcean** (Bom custo-benefício)
### 5. **Docker Local/VPS** (Máximo controle)

---

## 🌐 OPÇÃO 1: STREAMLIT CLOUD (RECOMENDADO)

### Passo 1: Preparar o Repositório GitHub

```bash
# Certifique-se de que tudo está commitado
git status

# Se houver mudanças, faça commit
git add .
git commit -m "Preparar para deploy em Streamlit Cloud"

# Push para GitHub
git push origin main
```

### Passo 2: Criar Arquivo `requirements.txt`

```bash
# Gerar requirements.txt
pip freeze > requirements.txt

# Ou criar manualmente com as dependências principais:
cat > requirements.txt << EOF
streamlit==1.28.0
pandas==2.0.0
numpy==1.24.0
requests==2.31.0
python-dotenv==1.0.0
pytz==2023.3
psutil==5.9.5
pytest==7.4.0
redis==5.0.0
psycopg2-binary==2.9.7
EOF
```

### Passo 3: Criar Arquivo `.streamlit/config.toml`

```bash
mkdir -p .streamlit

cat > .streamlit/config.toml << EOF
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true

[logger]
level = "info"

[server]
port = 8501
headless = true
runOnSave = true
EOF
```

### Passo 4: Acessar Streamlit Cloud

1. Ir para https://streamlit.io/cloud
2. Clicar em "Sign up"
3. Conectar com GitHub
4. Autorizar Streamlit
5. Clicar em "New app"

### Passo 5: Configurar Aplicação

1. **Repository:** Selecionar `wemarques/prognosticos-brasileirao`
2. **Branch:** `main`
3. **Main file path:** `app.py`
4. Clicar em "Deploy"

### Passo 6: Configurar Secrets (Variáveis de Ambiente)

1. Ir para "Advanced settings"
2. Clicar em "Secrets"
3. Adicionar as chaves de API:

```
FOOTBALL_DATA_API_KEY=sua_chave_aqui
FOOTYSTATS_API_KEY=sua_chave_aqui
ODDS_API_KEY=sua_chave_aqui
```

### Passo 7: Acessar Aplicação

- URL: `https://prognosticos-brasileirao.streamlit.app`
- Compartilhar com qualquer pessoa

---

## 🐳 OPÇÃO 2: DOCKER + HEROKU

### Passo 1: Criar Conta no Heroku

```bash
# Instalar Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Criar aplicação
heroku create prognosticos-brasileirao
```

### Passo 2: Criar `heroku.yml`

```bash
cat > heroku.yml << EOF
build:
  docker:
    web: Dockerfile
run:
  web: streamlit run app.py --server.port=$PORT
EOF
```

### Passo 3: Configurar Variáveis de Ambiente

```bash
heroku config:set FOOTBALL_DATA_API_KEY=sua_chave
heroku config:set FOOTYSTATS_API_KEY=sua_chave
heroku config:set ODDS_API_KEY=sua_chave
```

### Passo 4: Deploy

```bash
# Adicionar remote do Heroku
git remote add heroku https://git.heroku.com/prognosticos-brasileirao.git

# Push para Heroku
git push heroku main

# Ver logs
heroku logs --tail
```

### Passo 5: Acessar Aplicação

- URL: `https://prognosticos-brasileirao.herokuapp.com`

---

## ☁️ OPÇÃO 3: AWS EC2

### Passo 1: Criar Instância EC2

```bash
# 1. Ir para AWS Console
# 2. EC2 → Instances → Launch Instance
# 3. Selecionar Ubuntu 22.04 LTS
# 4. Tipo: t3.micro (free tier)
# 5. Configurar security group:
#    - SSH (22): Seu IP
#    - HTTP (80): 0.0.0.0/0
#    - HTTPS (443): 0.0.0.0/0
#    - TCP (8501): 0.0.0.0/0
# 6. Criar key pair e salvar
```

### Passo 2: Conectar à Instância

```bash
# Dar permissão ao key pair
chmod 400 seu-key-pair.pem

# Conectar via SSH
ssh -i seu-key-pair.pem ubuntu@seu-ip-publico
```

### Passo 3: Instalar Dependências

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### Passo 4: Clonar Repositório

```bash
# Clonar
git clone https://github.com/wemarques/prognosticos-brasileirao.git
cd prognosticos-brasileirao

# Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Adicionar suas chaves
```

### Passo 5: Deploy com Docker Compose

```bash
# Iniciar serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f app
```

### Passo 6: Configurar Nginx (Reverse Proxy)

```bash
# Instalar Nginx
sudo apt install nginx -y

# Criar configuração
sudo nano /etc/nginx/sites-available/prognosticos

# Adicionar:
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Ativar site
sudo ln -s /etc/nginx/sites-available/prognosticos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Passo 7: Configurar SSL (HTTPS)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Gerar certificado
sudo certbot --nginx -d seu-dominio.com

# Auto-renovação
sudo systemctl enable certbot.timer
```

---

## 💻 OPÇÃO 4: DIGITALOCEAN APP PLATFORM

### Passo 1: Conectar GitHub

1. Ir para https://cloud.digitalocean.com
2. Apps → Create App
3. Conectar GitHub
4. Selecionar repositório `prognosticos-brasileirao`

### Passo 2: Configurar Aplicação

1. **Name:** prognosticos-brasileirao
2. **Source:** GitHub
3. **Branch:** main
4. **Dockerfile:** Usar Dockerfile existente

### Passo 3: Configurar Variáveis de Ambiente

1. Ir para "Environment"
2. Adicionar:
   - `FOOTBALL_DATA_API_KEY`
   - `FOOTYSTATS_API_KEY`
   - `ODDS_API_KEY`

### Passo 4: Deploy

1. Clicar em "Create Resources"
2. Aguardar deploy (2-5 minutos)
3. Acessar URL fornecida

---

## 🖥️ OPÇÃO 5: DOCKER LOCAL/VPS

### Passo 1: Preparar Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker e Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Passo 2: Clonar e Configurar

```bash
# Clonar repositório
git clone https://github.com/wemarques/prognosticos-brasileirao.git
cd prognosticos-brasileirao

# Configurar variáveis
cp .env.example .env
nano .env
```

### Passo 3: Iniciar Serviços

```bash
# Build e start
docker-compose up -d

# Verificar
docker-compose ps

# Logs
docker-compose logs -f app
```

### Passo 4: Configurar Domínio

```bash
# Apontar domínio para IP do servidor
# No seu registrador de domínio:
# A record: seu-dominio.com → IP_DO_SERVIDOR
```

### Passo 5: Configurar Nginx

```bash
# Instalar Nginx
sudo apt install nginx -y

# Criar configuração
sudo nano /etc/nginx/sites-available/prognosticos

# Adicionar configuração (ver OPÇÃO 3)

# Ativar
sudo ln -s /etc/nginx/sites-available/prognosticos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📊 MONITORAMENTO PÓS-DEPLOY

### Verificar Status

```bash
# Streamlit Cloud
# Ir para https://share.streamlit.io/wemarques/prognosticos-brasileirao

# Docker
docker-compose ps
docker-compose logs -f app

# Heroku
heroku logs --tail

# AWS/DigitalOcean
# Acessar console e verificar logs
```

### Monitorar Performance

```bash
# Ver métricas
docker stats prognosticos-brasileirao

# Ver uso de disco
df -h

# Ver uso de memória
free -h
```

### Fazer Backup

```bash
# Backup de dados
tar -czf backup_$(date +%Y%m%d).tar.gz data/ logs/

# Backup de banco de dados
docker-compose exec postgres pg_dump -U prognosticos prognosticos > backup.sql
```

---

## 🔧 TROUBLESHOOTING

### Aplicação não inicia

```bash
# Verificar logs
docker-compose logs app

# Reconstruir
docker-compose build --no-cache
docker-compose up -d
```

### Erro de API

```bash
# Verificar conectividade
curl -I https://api.football-data.org/v4/competitions

# Verificar chaves
grep API_KEY .env

# Ver logs de API
tail -f logs/api.log
```

### Problema de Memória

```bash
# Verificar uso
docker stats

# Limpar cache
docker exec prognosticos-brasileirao rm -rf /app/cache/*

# Reiniciar
docker-compose restart app
```

---

## 📈 PRÓXIMOS PASSOS

1. **Monitoramento Avançado**
   - Integrar com Prometheus/Grafana
   - Configurar alertas

2. **CI/CD Pipeline**
   - GitHub Actions para testes automáticos
   - Deploy automático

3. **Escalabilidade**
   - Load balancer
   - Múltiplas instâncias
   - Cache distribuído

4. **Segurança**
   - WAF (Web Application Firewall)
   - DDoS protection
   - Backup automático

---

## 📞 SUPORTE

- **Documentação:** README_PRODUCAO.md
- **Issues:** GitHub Issues
- **Email:** suporte@prognosticos-brasileirao.com

---

**Data:** 29/10/2025
**Versão:** 1.0.0
**Status:** ✅ Pronto para Deploy