# 🚀 Deploy AWS - Arquitetura CSV-Only (Atualizado)

**Data:** 2025-11-16
**Branch:** `claude/fix-system-errors-01AK1ZbdXd1Pvipn2yyzNNcN`

---

## ✅ Pré-requisitos

- [ ] Conta AWS ativa
- [ ] AWS CLI configurado (opcional)
- [ ] Arquivos CSV copiados localmente
- [ ] ODDS_API_KEY configurada (opcional)

---

## 🚀 Deploy em EC2 (Recomendado)

### **Passo 1: Criar Instância EC2**

1. Ir para **AWS Console** → **EC2** → **Launch Instance**
2. Configurar:
   - **Nome**: `prognosticos-brasileirao`
   - **AMI**: Ubuntu 22.04 LTS
   - **Instance type**: t3.small (2 vCPU, 2 GB RAM)
   - **Key pair**: Criar novo ou usar existente (salve o .pem!)
   - **Security Group**:
     - SSH (22) → Seu IP
     - HTTP (80) → 0.0.0.0/0
     - HTTPS (443) → 0.0.0.0/0
     - Custom TCP (8501) → 0.0.0.0/0
3. Clicar em **Launch instance**

### **Passo 2: Conectar à Instância**

```bash
# Windows (Git Bash)
chmod 400 sua-chave.pem
ssh -i sua-chave.pem ubuntu@SEU-IP-PUBLICO-EC2

# Exemplo:
# ssh -i prognosticos.pem ubuntu@ec2-54-123-45-67.compute-1.amazonaws.com
```

### **Passo 3: Instalar Docker**

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

# Fazer checkout da branch com correções
git checkout claude/fix-system-errors-01AK1ZbdXd1Pvipn2yyzNNcN
```

### **Passo 5: Copiar Arquivos CSV para EC2**

**Opção A: Via SCP (do seu computador local)**

```bash
# Do seu computador Windows (Git Bash):
# Brasileirão
scp -i sua-chave.pem "C:/Users/wxamb/Downloads/brazil-serie-a-matches-2025-to-2025-stats (3).csv" ubuntu@SEU-IP-EC2:~/prognosticos-brasileirao/data/csv/brasileirao/2025_matches.csv

scp -i sua-chave.pem "C:/Users/wxamb/Downloads/brazil-serie-a-teams-2025-to-2025-stats (3).csv" ubuntu@SEU-IP-EC2:~/prognosticos-brasileirao/data/csv/brasileirao/2025_teams.csv

# Premier League
scp -i sua-chave.pem "C:/Users/wxamb/Downloads/england-premier-league-matches-2025-to-2026-stats (1).csv" ubuntu@SEU-IP-EC2:~/prognosticos-brasileirao/data/csv/premier_league/2025_matches.csv

scp -i sua-chave.pem "C:/Users/wxamb/Downloads/england-premier-league-teams-2025-to-2026-stats (1).csv" ubuntu@SEU-IP-EC2:~/prognosticos-brasileirao/data/csv/premier_league/2025_teams.csv
```

**Opção B: Upload via GitHub** (mais fácil)

```bash
# No seu computador local:
git add data/csv/
git commit -m "Add CSV data files"
git push

# Na EC2:
git pull origin claude/fix-system-errors-01AK1ZbdXd1Pvipn2yyzNNcN
```

### **Passo 6: Verificar CSV**

```bash
# Na EC2:
ls -lh data/csv/brasileirao/
ls -lh data/csv/premier_league/

# Deve mostrar os arquivos 2025_matches.csv e 2025_teams.csv
```

### **Passo 7: Configurar Variáveis de Ambiente**

```bash
# Editar .env
nano .env

# Adicionar sua ODDS_API_KEY (a que você já configurou localmente):
ODDS_API_KEY=652ee755d767058ec48c4994326eaa3d

# Salvar e sair (Ctrl+X, Y, Enter)
```

### **Passo 8: Build e Deploy**

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

### **Passo 9: Acessar Aplicação**

Abrir no navegador:
```
http://SEU-IP-PUBLICO-EC2:8501
```

Exemplo: `http://ec2-54-123-45-67.compute-1.amazonaws.com:8501`

---

## 🔄 Atualizar Aplicação (Deploy de Novas Mudanças)

```bash
# SSH na EC2
ssh -i sua-chave.pem ubuntu@SEU-IP-EC2

# Ir para diretório do projeto
cd ~/prognosticos-brasileirao

# Parar containers
docker-compose down

# Atualizar código
git pull origin claude/fix-system-errors-01AK1ZbdXd1Pvipn2yyzNNcN

# Rebuild
docker-compose build --no-cache

# Iniciar novamente
docker-compose up -d

# Verificar
docker-compose logs -f app
```

---

## 📦 Atualizar Arquivos CSV

### **Opção A: Via SCP**

```bash
# Do seu computador local:
scp -i sua-chave.pem novo_arquivo.csv ubuntu@SEU-IP-EC2:~/prognosticos-brasileirao/data/csv/brasileirao/2025_matches.csv

# Na EC2:
cd prognosticos-brasileirao
docker-compose restart app
```

### **Opção B: Via Git**

```bash
# No seu computador local:
# Atualizar CSV
cp "novo_arquivo.csv" data/csv/brasileirao/2025_matches.csv
git add data/csv/
git commit -m "Update CSV data"
git push

# Na EC2:
cd prognosticos-brasileirao
git pull
docker-compose restart app
```

---

## 🌐 Configurar Domínio (Opcional)

### **Se você tem um domínio:**

1. **No registrador de domínio**, criar registro A:
   ```
   prognosticos.seudominio.com → IP_DA_EC2
   ```

2. **Instalar Nginx na EC2:**

```bash
sudo apt install nginx -y

# Criar configuração
sudo nano /etc/nginx/sites-available/prognosticos
```

3. **Adicionar configuração:**

```nginx
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
```

4. **Ativar site:**

```bash
sudo ln -s /etc/nginx/sites-available/prognosticos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. **Configurar HTTPS:**

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d prognosticos.seudominio.com
```

---

## 💰 Custos Estimados AWS

### **EC2 t3.small (On-Demand)**
- Custo/hora: $0.0208
- Custo/mês: ~$15.00
- Storage (20 GB): $2.00
- **Total: ~$17/mês**

### **Economia com CSV:**
- ❌ **Antes:** API calls = $$$
- ✅ **Agora:** CSV local = $0
- 💰 **Economia:** 100% em custos de API

---

## 🛡️ Segurança

```bash
# Configurar firewall UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8501/tcp
sudo ufw enable
```

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
ls -la data/csv/premier_league/

# Criar diretórios se necessário
mkdir -p data/csv/premier_league
```

### **Erro de permissão**

```bash
# Dar permissão aos CSVs
chmod 644 data/csv/brasileirao/*.csv
chmod 644 data/csv/premier_league/*.csv
```

---

## 📋 Checklist Final

- [ ] EC2 criada e rodando
- [ ] Docker e Docker Compose instalados
- [ ] Repositório clonado (branch correta)
- [ ] Diretórios CSV criados
- [ ] Arquivos CSV copiados para EC2
- [ ] .env configurado com ODDS_API_KEY
- [ ] Docker containers rodando
- [ ] Aplicação acessível via navegador
- [ ] Seletor de ligas funcionando (Brasil + Premier League)
- [ ] (Opcional) Domínio configurado
- [ ] (Opcional) HTTPS configurado

---

## 🎉 Deploy Completo!

Sua aplicação está rodando na AWS com:
- ⚡ Performance máxima (CSV local)
- 💰 Zero custo para dados históricos
- 🚀 Deploy automatizado com Docker
- 🇧🇷🏴󠁧󠁢󠁥󠁮󠁧󠁿 Duas ligas funcionando
- 🔄 Atualização simples

**URL de Acesso:**
```
http://SEU-IP-EC2:8501
ou
https://seu-dominio.com
```

---

## 📞 Comandos Úteis

```bash
# Status dos containers
docker-compose ps

# Logs em tempo real
docker-compose logs -f app

# Reiniciar aplicação
docker-compose restart app

# Parar tudo
docker-compose down

# Ver uso de recursos
docker stats
```
