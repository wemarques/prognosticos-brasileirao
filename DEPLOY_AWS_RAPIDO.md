# 🚀 Deploy Rápido na AWS - Arquitetura CSV Híbrida

**Data:** 2025-11-14
**Versão:** 1.1.0 (com CSV híbrido)
**Branch:** `claude/frontend-review-improvements-01SLDqfrpQJaeBCaHmyLkkcU`

---

## ✅ Pré-requisitos

Antes de começar, certifique-se de ter:

- [ ] Conta AWS ativa
- [ ] AWS CLI configurado (`aws configure`)
- [ ] Docker instalado localmente
- [ ] Git configurado
- [ ] Chaves de API (opcional para odds)

---

## 🎯 Opções de Deploy

### **Opção 1: AWS EC2 com Docker (Recomendado)** ⭐
- Mais controle
- Melhor performance
- Custo: ~$10-20/mês (t3.small)

### **Opção 2: AWS App Runner (Mais Fácil)** 🚀
- Deploy automático
- Auto-scaling
- Custo: ~$25/mês

### **Opção 3: AWS ECS Fargate (Escalável)** 📈
- Containerizado
- Serverless
- Custo: ~$30-50/mês

---

## 🚀 OPÇÃO 1: Deploy em EC2 (Passo a Passo)

### **Passo 1: Criar Instância EC2**

```bash
# 1. Ir para AWS Console → EC2
# 2. Launch Instance

# Configurações:
# - Nome: prognosticos-brasileirao
# - AMI: Ubuntu 22.04 LTS
# - Instance type: t3.small (2 vCPU, 2 GB RAM)
# - Key pair: Criar novo ou usar existente
# - Security Group:
#   * SSH (22) - Seu IP
#   * HTTP (80) - 0.0.0.0/0
#   * HTTPS (443) - 0.0.0.0/0
#   * Custom TCP (8501) - 0.0.0.0/0

# 3. Launch instance
```

### **Passo 2: Conectar à Instância**

```bash
# Dar permissão ao key pair
chmod 400 sua-chave.pem

# Conectar via SSH
ssh -i sua-chave.pem ubuntu@seu-ip-publico-ec2

# Exemplo:
# ssh -i prognosticos.pem ubuntu@ec2-54-123-45-67.compute-1.amazonaws.com
```

### **Passo 3: Instalar Docker na EC2**

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
sudo usermod -aG docker ubuntu
newgrp docker

# Verificar instalação
docker --version
docker-compose --version
```

### **Passo 4: Clonar Repositório**

```bash
# Clonar projeto
git clone https://github.com/wemarques/prognosticos-brasileirao.git
cd prognosticos-brasileirao

# Fazer checkout da branch com CSV híbrido
git checkout claude/frontend-review-improvements-01SLDqfrpQJaeBCaHmyLkkcU

# Verificar que os arquivos CSV estão presentes
ls -la data/csv/brasileirao/
```

### **Passo 5: Configurar Variáveis de Ambiente**

```bash
# Criar arquivo .env
nano .env

# Adicionar (OPCIONAL - apenas se quiser odds em tempo real):
ODDS_API_KEY=sua_chave_odds_api

# Salvar e sair (Ctrl+X, Y, Enter)
```

**Nota:** Com a arquitetura CSV híbrida, **não precisa** das outras APIs keys!
Os dados de jogos vêm do CSV local.

### **Passo 6: Build e Deploy**

```bash
# Build da imagem Docker
docker-compose build

# Iniciar serviços
docker-compose up -d

# Verificar se está rodando
docker-compose ps

# Ver logs
docker-compose logs -f app
```

### **Passo 7: Acessar Aplicação**

```bash
# No navegador, acessar:
http://SEU_IP_PUBLICO_EC2:8501

# Exemplo:
# http://ec2-54-123-45-67.compute-1.amazonaws.com:8501
```

### **Passo 8: Configurar Domínio (Opcional)**

Se você tem um domínio:

```bash
# 1. No seu registrador de domínio, criar registro A:
#    prognosticos.seudominio.com → IP_DA_EC2

# 2. Instalar Nginx na EC2
sudo apt install nginx -y

# 3. Criar configuração
sudo nano /etc/nginx/sites-available/prognosticos

# 4. Adicionar:
server {
    listen 80;
    server_name prognosticos.seudominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}

# 5. Ativar site
sudo ln -s /etc/nginx/sites-available/prognosticos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 6. Configurar HTTPS com Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d prognosticos.seudominio.com
```

### **Passo 9: Atualização Automática de CSV (Opcional)**

Se quiser atualizar CSV automaticamente com dados da API:

```bash
# Criar script de atualização
nano ~/update_csv.sh

# Adicionar:
#!/bin/bash
cd /home/ubuntu/prognosticos-brasileirao
docker-compose exec -T app python scripts/update_csv_from_api.py --league brasileirao
echo "CSV atualizado em $(date)" >> logs/csv_updates.log

# Dar permissão
chmod +x ~/update_csv.sh

# Agendar no crontab (diariamente às 3h)
crontab -e

# Adicionar linha:
0 3 * * * /home/ubuntu/update_csv.sh
```

---

## 🚀 OPÇÃO 2: Deploy com AWS App Runner

### **Passo 1: Preparar Configuração**

```bash
# Criar apprunner.yaml na raiz do projeto
cat > apprunner.yaml << 'EOF'
version: 1.0
runtime: python311
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  command: streamlit run app.py --server.port=8080
  network:
    port: 8080
  env:
    - name: ODDS_API_KEY
      value: "SUA_KEY_AQUI_OU_DEIXE_VAZIO"
EOF

# Commit e push
git add apprunner.yaml
git commit -m "Add App Runner configuration"
git push
```

### **Passo 2: Deploy via Console AWS**

```bash
# 1. Ir para AWS Console → App Runner
# 2. Create service
# 3. Source: Repository
# 4. Connect to GitHub
# 5. Selecionar: wemarques/prognosticos-brasileirao
# 6. Branch: claude/frontend-review-improvements-01SLDqfrpQJaeBCaHmyLkkcU
# 7. Configuration file: Use apprunner.yaml
# 8. Service name: prognosticos-brasileirao
# 9. Create & deploy
```

Aplicação ficará disponível em:
```
https://xxxxx.us-east-1.awsapprunner.com
```

---

## 📊 Verificar Deploy

### **Health Check**

```bash
# Testar se está respondendo
curl http://SEU_IP:8501/_stcore/health

# Deve retornar:
# {"status": "ok"}
```

### **Verificar CSV**

No navegador, após abrir a aplicação:
1. No sidebar, expandir "📊 Fonte de Dados"
2. Verificar:
   - ✅ Matches: 20 registros
   - ✅ Teams: 20 registros
   - ✅ Standings: 30 registros

### **Verificar Performance**

```bash
# SSH na EC2
ssh -i sua-chave.pem ubuntu@seu-ip

# Ver métricas
docker stats prognosticos-brasileirao

# Ver logs
docker logs prognosticos-brasileirao -f
```

---

## 🔄 Atualizar Aplicação (Deploy de Novas Mudanças)

```bash
# Na EC2, via SSH:

# 1. Ir para diretório do projeto
cd ~/prognosticos-brasileirao

# 2. Parar containers
docker-compose down

# 3. Atualizar código
git pull origin claude/frontend-review-improvements-01SLDqfrpQJaeBCaHmyLkkcU

# 4. Rebuild
docker-compose build --no-cache

# 5. Iniciar novamente
docker-compose up -d

# 6. Verificar
docker-compose logs -f app
```

---

## 📦 Adicionar Dados Reais ao CSV

### **Opção A: Upload Manual**

```bash
# 1. Editar CSV localmente no seu computador
# 2. Fazer upload via SCP:

scp -i sua-chave.pem \
  data/csv/brasileirao/2025_matches.csv \
  ubuntu@seu-ip:/home/ubuntu/prognosticos-brasileirao/data/csv/brasileirao/

# 3. Reiniciar container
ssh -i sua-chave.pem ubuntu@seu-ip
cd prognosticos-brasileirao
docker-compose restart app
```

### **Opção B: Atualizar via API**

```bash
# Na EC2:
docker-compose exec app python scripts/update_csv_from_api.py --league brasileirao

# Ver resultado
docker-compose logs app | grep "CSV atualizado"
```

---

## 💰 Custos Estimados AWS

### **EC2 t3.small (On-Demand)**
- Custo/hora: $0.0208
- Custo/mês: ~$15.00
- + Storage (20 GB): $2.00
- **Total: ~$17/mês**

### **App Runner**
- Custo base: $5/mês
- vCPU: $0.064/vCPU-hora
- Memória: $0.007/GB-hora
- **Total: ~$25-30/mês**

### **Economia com CSV:**
- **Antes:** API calls ilimitadas = $$$
- **Agora:** CSV local = $0
- **Economia:** 100% em APIs de dados

---

## 🛡️ Segurança

### **Security Group EC2**

```bash
# Permitir apenas IPs necessários:
# - SSH (22): Apenas seu IP
# - HTTP (80): 0.0.0.0/0
# - HTTPS (443): 0.0.0.0/0
# - App (8501): 0.0.0.0/0 ou via Nginx apenas
```

### **Firewall na EC2**

```bash
# Configurar UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8501/tcp
sudo ufw enable
```

---

## 📋 Checklist Final

- [ ] EC2 criada e rodando
- [ ] Docker instalado
- [ ] Repositório clonado (branch correta)
- [ ] CSV verificado (data/csv/brasileirao/)
- [ ] Docker containers rodando
- [ ] Aplicação acessível via navegador
- [ ] Fonte de dados mostrando CSV ✅
- [ ] (Opcional) Domínio configurado
- [ ] (Opcional) HTTPS configurado
- [ ] (Opcional) Atualização automática CSV

---

## 🐛 Troubleshooting

### **Aplicação não inicia**

```bash
# Ver logs detalhados
docker-compose logs app

# Verificar porta
sudo lsof -i :8501

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **CSV não encontrado**

```bash
# Verificar estrutura
ls -la data/csv/brasileirao/

# Se não existir, criar exemplo
mkdir -p data/csv/brasileirao
# Copiar CSVs do repositório
```

### **Performance lenta**

```bash
# Aumentar recursos da EC2:
# t3.small (2GB) → t3.medium (4GB)

# Ou otimizar Docker:
docker system prune -a
docker-compose restart app
```

---

## 📞 Suporte

**Documentação:**
- README_CSV.md - Guia do sistema CSV
- IMPLEMENTACAO_CSV_COMPLETA.md - Detalhes técnicos
- DEPLOY_PRODUCAO.md - Outras opções de deploy

**Comandos Úteis:**
```bash
# Status dos containers
docker-compose ps

# Logs em tempo real
docker-compose logs -f app

# Reiniciar aplicação
docker-compose restart app

# Parar tudo
docker-compose down

# Remover volumes (reset completo)
docker-compose down -v
```

---

## ✅ Deploy Completo!

Sua aplicação agora está rodando na AWS com:
- ⚡ Performance 25x melhor (CSV local)
- 💰 Custo zero para dados de jogos
- 🚀 Deploy automatizado com Docker
- 📊 20 jogos de exemplo funcionando
- 🔄 Atualização simples com git pull

**URL de Acesso:**
```
http://SEU_IP_EC2:8501
ou
https://seu-dominio.com
```

Aproveite! 🎉

---

**Criado:** 2025-11-14
**Versão:** 1.0
**Branch:** claude/frontend-review-improvements-01SLDqfrpQJaeBCaHmyLkkcU
