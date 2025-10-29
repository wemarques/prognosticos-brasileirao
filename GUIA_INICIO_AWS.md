# 🚀 GUIA COMPLETO - INICIANDO NO AWS

## 📋 PRÉ-REQUISITOS

### 1. Conta AWS
- [ ] Criar conta em https://aws.amazon.com
- [ ] Verificar email
- [ ] Adicionar método de pagamento
- [ ] Ativar MFA (Multi-Factor Authentication)
- [ ] Criar usuário IAM com permissões

### 2. Ferramentas Locais
- [ ] Instalar AWS CLI
- [ ] Instalar Git
- [ ] Instalar Docker
- [ ] Instalar Python 3.11+
- [ ] Instalar Node.js (opcional)

### 3. Chaves de API
- [ ] Football-Data.org API Key
- [ ] FootyStats API Key
- [ ] The Odds API Key

---

## 🔧 PASSO 1: CONFIGURAR CONTA AWS

### 1.1 Criar Conta AWS

```bash
# 1. Ir para https://aws.amazon.com
# 2. Clicar em "Create an AWS Account"
# 3. Preencher informações:
#    - Email
#    - Senha forte
#    - Nome da conta
#    - Tipo de conta (Personal)
# 4. Adicionar método de pagamento
# 5. Verificar identidade (telefone)
# 6. Escolher plano de suporte (Basic - Gratuito)
```

### 1.2 Ativar MFA

```bash
# 1. Ir para AWS Console
# 2. Account → Security credentials
# 3. Multi-factor authentication (MFA)
# 4. Ativar MFA device
# 5. Usar Google Authenticator ou Authy
# 6. Salvar backup codes
```

### 1.3 Criar Usuário IAM

```bash
# 1. Ir para IAM Dashboard
# 2. Users → Create user
# 3. Nome: prognosticos-admin
# 4. Permissões: AdministratorAccess
# 5. Criar access key
# 6. Salvar em local seguro
```

---

## 💻 PASSO 2: INSTALAR FERRAMENTAS

### 2.1 AWS CLI

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Baixar em https://aws.amazon.com/cli/

# Verificar instalação
aws --version
```

### 2.2 Configurar AWS CLI

```bash
# Configurar credenciais
aws configure

# Será solicitado:
# AWS Access Key ID: [sua-access-key]
# AWS Secret Access Key: [sua-secret-key]
# Default region name: us-east-1
# Default output format: json

# Verificar configuração
aws sts get-caller-identity
```

### 2.3 Git

```bash
# macOS
brew install git

# Linux
sudo apt install git

# Windows
# Baixar em https://git-scm.com/

# Configurar
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@example.com"
```

### 2.4 Docker

```bash
# macOS
brew install docker

# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Windows
# Baixar Docker Desktop em https://www.docker.com/products/docker-desktop

# Verificar instalação
docker --version
```

### 2.5 Python 3.11+

```bash
# macOS
brew install python@3.11

# Linux
sudo apt install python3.11 python3.11-venv

# Windows
# Baixar em https://www.python.org/

# Verificar instalação
python3 --version
```

---

## 🔑 PASSO 3: OBTER CHAVES DE API

### 3.1 Football-Data.org

```bash
# 1. Ir para https://www.football-data.org/
# 2. Clicar em "Sign up"
# 3. Preencher formulário
# 4. Verificar email
# 5. Ir para "Account"
# 6. Copiar API Key
# 7. Salvar em local seguro
```

### 3.2 FootyStats

```bash
# 1. Ir para https://www.footystats.com/
# 2. Clicar em "API"
# 3. Fazer login ou criar conta
# 4. Copiar API Key
# 5. Salvar em local seguro
```

### 3.3 The Odds API

```bash
# 1. Ir para https://the-odds-api.com/
# 2. Clicar em "Sign up"
# 3. Preencher formulário
# 4. Verificar email
# 5. Copiar API Key
# 6. Salvar em local seguro
```

---

## 📦 PASSO 4: PREPARAR REPOSITÓRIO

### 4.1 Clonar Repositório

```bash
# Clonar
git clone https://github.com/wemarques/prognosticos-brasileirao.git
cd prognosticos-brasileirao

# Verificar branch
git branch -a

# Estar na branch main
git checkout main
```

### 4.2 Criar Arquivo .env

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas chaves
nano .env

# Adicionar:
FOOTBALL_DATA_API_KEY=sua_chave_aqui
FOOTYSTATS_API_KEY=sua_chave_aqui
ODDS_API_KEY=sua_chave_aqui
POSTGRES_PASSWORD=senha_segura_aqui
```

### 4.3 Instalar Dependências

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

---

## 🏗️ PASSO 5: CRIAR INFRAESTRUTURA AWS

### 5.1 Criar VPC (Virtual Private Cloud)

```bash
# 1. Ir para VPC Dashboard
# 2. VPCs → Create VPC
# 3. Nome: prognosticos-vpc
# 4. CIDR: 10.0.0.0/16
# 5. Criar
```

### 5.2 Criar Security Groups

```bash
# 1. Ir para EC2 Dashboard
# 2. Security Groups → Create security group
# 3. Nome: prognosticos-sg
# 4. Descrição: Security group para prognosticos
# 5. VPC: prognosticos-vpc
# 6. Adicionar regras:
#    - SSH (22): Seu IP
#    - HTTP (80): 0.0.0.0/0
#    - HTTPS (443): 0.0.0.0/0
#    - TCP (8501): 0.0.0.0/0
# 7. Criar
```

### 5.3 Criar Key Pair

```bash
# 1. Ir para EC2 Dashboard
# 2. Key Pairs → Create key pair
# 3. Nome: prognosticos-key
# 4. Tipo: RSA
# 5. Formato: .pem
# 6. Criar
# 7. Salvar arquivo em local seguro
# 8. Dar permissão: chmod 400 prognosticos-key.pem
```

### 5.4 Criar Instância EC2

```bash
# 1. Ir para EC2 Dashboard
# 2. Instances → Launch instances
# 3. Configurar:
#    - Nome: prognosticos-app
#    - AMI: Ubuntu 22.04 LTS
#    - Tipo: t3.micro (free tier)
#    - Key pair: prognosticos-key
#    - VPC: prognosticos-vpc
#    - Security group: prognosticos-sg
#    - Storage: 30 GB (gp3)
# 4. Launch
# 5. Aguardar até "running"
# 6. Copiar IP público
```

### 5.5 Criar RDS (PostgreSQL)

```bash
# 1. Ir para RDS Dashboard
# 2. Databases → Create database
# 3. Configurar:
#    - Engine: PostgreSQL
#    - Version: 15.x
#    - Template: Free tier
#    - DB instance identifier: prognosticos-db
#    - Master username: prognosticos
#    - Master password: [senha forte]
#    - DB instance class: db.t3.micro
#    - Storage: 20 GB
#    - VPC: prognosticos-vpc
#    - Security group: prognosticos-sg
# 4. Create database
# 5. Aguardar até "available"
# 6. Copiar endpoint
```

### 5.6 Criar ElastiCache (Redis)

```bash
# 1. Ir para ElastiCache Dashboard
# 2. Clusters → Create cluster
# 3. Configurar:
#    - Engine: Redis
#    - Name: prognosticos-cache
#    - Node type: cache.t3.micro
#    - Number of nodes: 1
#    - VPC: prognosticos-vpc
#    - Security group: prognosticos-sg
# 4. Create
# 5. Aguardar até "available"
# 6. Copiar endpoint
```

---

## 🔗 PASSO 6: CONECTAR À INSTÂNCIA EC2

### 6.1 Conectar via SSH

```bash
# Dar permissão ao key pair
chmod 400 prognosticos-key.pem

# Conectar
ssh -i prognosticos-key.pem ubuntu@seu-ip-publico

# Você deve estar conectado como ubuntu@ip-privado
```

### 6.2 Atualizar Sistema

```bash
# Atualizar pacotes
sudo apt update && sudo apt upgrade -y

# Instalar ferramentas básicas
sudo apt install -y curl wget git vim htop
```

### 6.3 Instalar Docker

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalação
docker --version
docker-compose --version
```

---

## 📥 PASSO 7: FAZER DEPLOY

### 7.1 Clonar Repositório na EC2

```bash
# Clonar
git clone https://github.com/wemarques/prognosticos-brasileirao.git
cd prognosticos-brasileirao

# Verificar arquivos
ls -la
```

### 7.2 Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar
nano .env

# Adicionar:
FOOTBALL_DATA_API_KEY=sua_chave
FOOTYSTATS_API_KEY=sua_chave
ODDS_API_KEY=sua_chave
POSTGRES_PASSWORD=sua_senha
POSTGRES_USER=prognosticos
POSTGRES_DB=prognosticos
REDIS_HOST=seu-redis-endpoint
REDIS_PORT=6379
```

### 7.3 Iniciar com Docker Compose

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f app
```

### 7.4 Acessar Aplicação

```bash
# Acessar em:
# http://seu-ip-publico:8501

# Ou configurar domínio
# Apontar domínio para IP público
# A record: seu-dominio.com → IP_PUBLICO
```

---

## 🔒 PASSO 8: CONFIGURAR SEGURANÇA

### 8.1 Configurar Nginx (Reverse Proxy)

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

### 8.2 Configurar SSL (HTTPS)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Gerar certificado
sudo certbot --nginx -d seu-dominio.com

# Auto-renovação
sudo systemctl enable certbot.timer
```

### 8.3 Configurar Firewall

```bash
# Ativar UFW
sudo ufw enable

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP
sudo ufw allow 80/tcp

# Permitir HTTPS
sudo ufw allow 443/tcp

# Verificar status
sudo ufw status
```

---

## 📊 PASSO 9: MONITORAMENTO

### 9.1 Configurar CloudWatch

```bash
# 1. Ir para CloudWatch Dashboard
# 2. Dashboards → Create dashboard
# 3. Nome: prognosticos-dashboard
# 4. Adicionar widgets:
#    - EC2 CPU Utilization
#    - RDS CPU Utilization
#    - ElastiCache CPU Utilization
#    - Network In/Out
```

### 9.2 Configurar Alertas

```bash
# 1. Ir para CloudWatch
# 2. Alarms → Create alarm
# 3. Configurar:
#    - Métrica: EC2 CPU Utilization
#    - Threshold: 80%
#    - Ação: Enviar email
# 4. Criar
```

### 9.3 Monitorar Logs

```bash
# Ver logs da aplicação
docker-compose logs -f app

# Ver logs do sistema
sudo tail -f /var/log/syslog

# Ver logs do Nginx
sudo tail -f /var/log/nginx/access.log
```

---

## 💰 PASSO 10: OTIMIZAR CUSTOS

### 10.1 Ativar Free Tier Alerts

```bash
# 1. Ir para Billing Dashboard
# 2. Budgets → Create budget
# 3. Configurar:
#    - Limite: $50/mês
#    - Alerta: 80% do limite
#    - Email: seu-email@example.com
```

### 10.2 Comprar Reserved Instances

```bash
# 1. Ir para EC2 Dashboard
# 2. Reserved Instances → Purchase Reserved Instances
# 3. Configurar:
#    - Instance type: t3.micro
#    - Term: 1 year
#    - Payment: All upfront
# 4. Purchase
```

### 10.3 Usar Savings Plans

```bash
# 1. Ir para Savings Plans
# 2. Purchase Savings Plans
# 3. Configurar:
#    - Commitment: 1 year
#    - Payment: All upfront
# 4. Purchase
```

---

## ✅ CHECKLIST FINAL

- [ ] Conta AWS criada
- [ ] MFA ativado
- [ ] Usuário IAM criado
- [ ] AWS CLI instalado e configurado
- [ ] Git instalado
- [ ] Docker instalado
- [ ] Python 3.11+ instalado
- [ ] Chaves de API obtidas
- [ ] Repositório clonado
- [ ] .env configurado
- [ ] VPC criada
- [ ] Security groups criados
- [ ] Key pair criado
- [ ] EC2 criada
- [ ] RDS criada
- [ ] ElastiCache criada
- [ ] Conectado via SSH
- [ ] Docker Compose iniciado
- [ ] Nginx configurado
- [ ] SSL configurado
- [ ] Firewall configurado
- [ ] CloudWatch configurado
- [ ] Alertas configurados
- [ ] Free Tier alerts ativados
- [ ] Reserved Instances compradas (opcional)

---

## 🚨 TROUBLESHOOTING

### Não consegue conectar via SSH

```bash
# Verificar permissões do key pair
chmod 400 prognosticos-key.pem

# Verificar security group
# Certifique-se de que SSH (22) está permitido

# Verificar IP público
# Ir para EC2 Dashboard e copiar IP público correto
```

### Docker não inicia

```bash
# Verificar status
docker-compose ps

# Ver logs
docker-compose logs app

# Reconstruir
docker-compose build --no-cache
docker-compose up -d
```

### Aplicação não acessível

```bash
# Verificar se porta 8501 está aberta
sudo netstat -tlnp | grep 8501

# Verificar Nginx
sudo nginx -t
sudo systemctl restart nginx

# Verificar security group
# Certifique-se de que porta 8501 está permitida
```

### Erro de conexão com RDS

```bash
# Verificar endpoint do RDS
# Ir para RDS Dashboard e copiar endpoint correto

# Verificar security group
# Certifique-se de que PostgreSQL (5432) está permitido

# Testar conexão
psql -h seu-rds-endpoint -U prognosticos -d prognosticos
```

---

## 📞 SUPORTE

- **Documentação AWS:** https://docs.aws.amazon.com/
- **AWS Support:** https://console.aws.amazon.com/support/
- **GitHub Issues:** https://github.com/wemarques/prognosticos-brasileirao/issues
- **Email:** suporte@prognosticos-brasileirao.com

---

## 📈 PRÓXIMOS PASSOS

1. ✅ Seguir este guia passo a passo
2. 🔄 Testar aplicação em produção
3. 🔄 Monitorar performance
4. 🔄 Otimizar custos
5. 🔄 Escalar conforme necessário

---

**Data:** 29/10/2025
**Versão:** 1.0.0
**Status:** ✅ Guia Completo

🚀 **PRONTO PARA INICIAR NO AWS!** 🚀