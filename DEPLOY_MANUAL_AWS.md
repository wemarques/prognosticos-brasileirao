# 🚀 Deploy Manual na AWS EC2 - Passo a Passo

**EC2 IP:** 34.205.26.29
**URL:** http://34.205.26.29:8501
**Data:** 2025-11-14

---

## ⚠️ Execute no SEU COMPUTADOR LOCAL

Estes comandos devem ser executados no **seu terminal local** (não neste ambiente).

---

## 📋 Passo 1: Salvar Chave SSH

No seu computador local, crie o arquivo com a chave SSH:

```bash
# Criar arquivo da chave
cat > ~/prognosticos-aws-key.pem << 'EOF'
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAsWAYQaTuZeTeJLElGsH58UcElxXJltwGh1fYBXHpiAafAj81
i0OCBmd52ExKGsmvp9wWNXvO1UCKOkKAJDGFBfQisZkEOQA176U/UljG3AgtfTox
MRpxadnfVkx/Fyp9MeB1RzFdssQetsUUm7a5BcLBfFxiJ8h9g5Rw9wdaDALTRLoW
YVyLHOhRTDH6RUljtdwXvkArxFOuT8Ne6etsh5SegFYmKgQeeL8oRrLcTY49UpBH
EWeWRdWZxQiEos22tvY/X0RvdzGVlEDn6QkY6M2kmvUwd7Zm26xUp0qsnBKFl55D
WKVrFGPLLerikwhMTfGPTAi3g9uImF72xn4D6wIDAQABAoIBAHhs5KsU3mLBq2y/
9JAhKJ/+dohZW3+YLLqREnJH76TR0f1FiwXdNJdCg8Ats5ZSXncZ/t4bC8dPRUne
wn9QO59aLH/lgq9sjDIDQGWZLpJO3wuJicJr0JpsOKyvzQ2eZFeLrDREuPfZHX07
ew1pVl8p5hGX63BVN5oxGy0siZ9i3aa1Db/+z92CbekqyPp4SrGG3R/hKG0szOmB
aV41DELjUqgJF6iFdEcRVFbgMYYMwfaXRslfO+Bs67/z19d5FVgitMoyrYY07NtP
hU8hr8C1E+Drg42pW42qxA2yHXxvUkrmhmSbcV+49hCgsGBGpPh6NkpCUjCIP+Ma
qy/V/yECgYEA5AqoK7E/WvYjl2raRE5fHd6OMGEYa3yKAJUKsGZzM8SYE5PHtAPf
Rpi6fzKPzYqx88gDItSDI3nJmtrEwBAD2MQvul0THUTNS16sh3PVWz0hxEZG+iF1
FzgtJVxXiYnkCNGCQyGcZBIc88KEVEuZZ+LJCl0xCgbWBESzQbUMqzECgYEAxx84
ZiO5+e9Nr0dpIaUMMzNs6UCjuBL2yn04ip07L7Y7xR+6psW3IbwkVLV0e+iYheMf
2MQcJuZBSIOXRNnCAkHT4SgNr48PYUj46jQLVEyuzSqBY95nyIBY3NHxLgW+ZPb8
bJeRU6w4abzvKnH9yhcPGJk0XP+VCknLay3qYdsCgYB8m4InVdQ7vRHXtHCOMJDy
/mCN+RBh84xpIwfTOjgrCnra/755FECWD/Cgfp1rgCUbA6kLCDqcUPkj3/Twyg+A
DDvURvWh4a2YSKRX46irEW15FbnFBjE4Pd8Vci73Hdz4IJtgWWZenDMr05eBhEnQ
JXEbc67PPssFTBDzj53bkQKBgBZfAJQhIWzeIOk3aa1ZALTj6zGNjJdKsiVvyiFw
psymebKc7Ph9sCR/IcnOlSayrCgmq1ZMOil4pw8BkcYvfOeKA8cBHACEXyL78tNF
Q5yV/PGZ++1/eEODf/hXMfSMuqZXRWbh5Hb1G2Vtz6UCJ5RD4PNPix2DrXf5cHw7
LWEPAoGABxpnkdLMdpEZN4qaVizgAn6LV7KHm4t5vc5Sft53S2IDpE7FZN/bKquX
PZHpKGxuV+YoBERobDJbGOR1/en1blbuYuE5fh44OiixeP4+CjdMYUKeDvrhU+sI
LBuC5CzZY1drelljktfiQnrNMz5wsL/UY7DLFIJpKBJvTBAWnzU=
-----END RSA PRIVATE KEY-----
EOF

# Dar permissões corretas
chmod 400 ~/prognosticos-aws-key.pem
```

---

## 🔌 Passo 2: Testar Conexão SSH

```bash
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29

# Se conectar com sucesso, você verá:
# Welcome to Ubuntu...
# ubuntu@ip-xxx-xxx-xxx-xxx:~$

# Digite 'exit' para sair
exit
```

---

## 🐳 Passo 3: Instalar Docker na EC2

Conecte novamente e execute:

```bash
# Conectar na EC2
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29

# Dentro da EC2, executar:

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sudo sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Sair e reconectar para aplicar permissões
exit
```

---

## 📦 Passo 4: Clonar e Configurar Projeto

Conecte novamente:

```bash
# Reconectar na EC2
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29

# Dentro da EC2:

# Clonar repositório
git clone https://github.com/wemarques/prognosticos-brasileirao.git
cd prognosticos-brasileirao

# Fazer checkout da branch main (com CSV híbrido)
git checkout main

# Verificar que arquivos CSV estão presentes
ls -la data/csv/brasileirao/

# Deve mostrar:
# 2025_matches.csv
# 2025_teams.csv
# 2025_standings.csv
```

---

## 🔧 Passo 5: Configurar Variáveis de Ambiente (Opcional)

```bash
# Ainda dentro da EC2, no diretório do projeto:

# Criar arquivo .env (OPCIONAL - apenas se quiser odds em tempo real)
cat > .env << 'EOF'
# Opcional: The Odds API (para odds em tempo real)
ODDS_API_KEY=

# Se não tiver, deixe vazio - o sistema funciona 100% com CSV
EOF

# Nota: Com a arquitetura CSV híbrida, você NÃO precisa de outras API keys!
# Os dados de jogos vêm do CSV local
```

---

## 🚀 Passo 6: Build e Deploy

```bash
# Ainda na EC2, no diretório prognosticos-brasileirao:

# Build das imagens
docker-compose build

# Iniciar aplicação
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f app

# Pressione Ctrl+C para parar de ver os logs
# (A aplicação continua rodando em background)
```

---

## ✅ Passo 7: Verificar Deploy

### No navegador:

```
http://34.205.26.29:8501
```

### Verificar saúde da aplicação:

```
http://34.205.26.29:8501/_stcore/health
```

### Na interface Streamlit:

1. Abrir sidebar
2. Expandir "📊 Fonte de Dados"
3. Verificar:
   - ✅ Matches: 20 registros
   - ✅ Teams: 20 registros
   - ✅ Standings: 30 registros

---

## 📊 Comandos Úteis

### Ver logs em tempo real:

```bash
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29 \
  "cd prognosticos-brasileirao && docker-compose logs -f app"
```

### Reiniciar aplicação:

```bash
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29 \
  "cd prognosticos-brasileirao && docker-compose restart app"
```

### Parar aplicação:

```bash
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29 \
  "cd prognosticos-brasileirao && docker-compose down"
```

### Atualizar código (quando houver mudanças):

```bash
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29 << 'ENDSSH'
cd prognosticos-brasileirao
docker-compose down
git pull origin main
docker-compose build --no-cache
docker-compose up -d
ENDSSH
```

### Ver status dos containers:

```bash
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29 \
  "cd prognosticos-brasileirao && docker-compose ps"
```

### Ver uso de recursos:

```bash
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29 \
  "docker stats --no-stream"
```

---

## 🔄 Atualizar CSV com Dados Reais

### Opção A: Atualizar via API (dentro da EC2)

```bash
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29

# Dentro da EC2:
cd prognosticos-brasileirao
docker-compose exec app python scripts/update_csv_from_api.py --league brasileirao

# Ver resultado
docker-compose logs app | grep "CSV atualizado"
```

### Opção B: Upload manual de CSV

```bash
# Do seu computador local:
scp -i ~/prognosticos-aws-key.pem \
  caminho/para/seu/2025_matches.csv \
  ubuntu@34.205.26.29:~/prognosticos-brasileirao/data/csv/brasileirao/

# Reiniciar container
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29 \
  "cd prognosticos-brasileirao && docker-compose restart app"
```

---

## 🛡️ Segurança

### Configurar Firewall (UFW):

```bash
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29

# Dentro da EC2:
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8501/tcp
sudo ufw enable
```

### Verificar Security Group na AWS:

1. AWS Console → EC2 → Security Groups
2. Verificar regras de entrada:
   - SSH (22): Apenas seu IP
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
   - Custom TCP (8501): 0.0.0.0/0

---

## 🌐 Configurar Domínio (Opcional)

Se você tem um domínio:

```bash
# 1. No registrador de domínio, criar registro A:
#    prognosticos.seudominio.com → 34.205.26.29

# 2. Na EC2, instalar Nginx
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29

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

# 5. Ativar
sudo ln -s /etc/nginx/sites-available/prognosticos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 6. Configurar HTTPS (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d prognosticos.seudominio.com
```

---

## 📋 Checklist Final

- [ ] Chave SSH salva e com permissões corretas (400)
- [ ] Conexão SSH funcionando
- [ ] Docker e Docker Compose instalados na EC2
- [ ] Repositório clonado (branch main)
- [ ] CSV files verificados (data/csv/brasileirao/)
- [ ] Docker containers rodando (docker-compose ps)
- [ ] Aplicação acessível no navegador
- [ ] Sidebar mostrando "Fonte de Dados" com CSV ✅
- [ ] (Opcional) Domínio configurado
- [ ] (Opcional) HTTPS configurado

---

## 🐛 Troubleshooting

### Erro: "Permission denied (publickey)"

```bash
# Verificar permissões da chave
chmod 400 ~/prognosticos-aws-key.pem
ls -l ~/prognosticos-aws-key.pem
# Deve mostrar: -r-------- 1 seu_usuario ...
```

### Porta 8501 não acessível

```bash
# Verificar Security Group na AWS Console
# Deve ter regra: Custom TCP 8501 → 0.0.0.0/0

# Verificar firewall na EC2
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29
sudo ufw status
# Se bloqueado, executar:
sudo ufw allow 8501/tcp
```

### Container não inicia

```bash
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29
cd prognosticos-brasileirao

# Ver logs detalhados
docker-compose logs app

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### CSV não encontrado

```bash
ssh -i ~/prognosticos-aws-key.pem ubuntu@34.205.26.29
cd prognosticos-brasileirao

# Verificar estrutura
ls -la data/csv/brasileirao/

# Se vazio, garantir que está na branch correta
git status
git checkout main
git pull origin main
```

---

## 📊 Informações do Deploy

**EC2:**
- IP: 34.205.26.29
- Região: us-east-1 (provavelmente)
- Sistema: Ubuntu
- Tipo: (verificar no AWS Console)

**Aplicação:**
- URL: http://34.205.26.29:8501
- Health: http://34.205.26.29:8501/_stcore/health
- Porta: 8501
- Container: prognosticos-brasileirao

**Arquitetura:**
- CSV local (25x mais rápido)
- Docker + Docker Compose
- Opcional: Odds API para odds em tempo real

---

## ✅ Deploy Concluído!

Após seguir todos os passos, sua aplicação estará rodando com:

- ⚡ Performance 25x mais rápida (CSV local)
- 💰 Custo zero para dados de jogos
- 📊 20 jogos + 20 times funcionando
- 🚀 Pronto para uso em produção
- 🔄 Fácil de atualizar (git pull + docker-compose)

**Acesse:** http://34.205.26.29:8501

Aproveite! 🎉

---

**Criado:** 2025-11-14
**EC2 IP:** 34.205.26.29
**Branch:** main
