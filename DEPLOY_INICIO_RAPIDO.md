# 🚀 Deploy AWS - Início Rápido

## Passo 1: Criar EC2 na AWS

1. Acesse **AWS Console** → **EC2** → **Launch Instance**
2. Configure:
   - **Nome**: `prognosticos-brasileirao`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance type**: t3.small (2 vCPU, 2 GB RAM) - ~$17/mês
   - **Key pair**:
     - Clique em "Create new key pair"
     - Nome: `prognosticos-aws`
     - Tipo: RSA
     - Formato: .pem
     - **SALVE O ARQUIVO .pem!**

3. **Network settings**:
   - Marcar: "Allow SSH traffic from" → "My IP"
   - Marcar: "Allow HTTP traffic from the internet"
   - Marcar: "Allow HTTPS traffic from the internet"

4. Clique em **"Edit"** nos Security Groups e adicionar:
   - Type: Custom TCP
   - Port: 8501
   - Source: Anywhere (0.0.0.0/0)

5. **Configure storage**: 20 GB (default está OK)

6. Clique em **"Launch instance"**

7. **IMPORTANTE**: Copie o IP público da instância (ex: `52.12.34.56`)

---

## Passo 2: Conectar à EC2

No **Git Bash** do seu computador:

```bash
# Dar permissão ao arquivo .pem (só precisa fazer 1x)
chmod 400 ~/Downloads/prognosticos-aws.pem

# Conectar via SSH (substitua SEU-IP-PUBLICO pelo IP da sua EC2)
ssh -i ~/Downloads/prognosticos-aws.pem ubuntu@SEU-IP-PUBLICO
```

**Exemplo:**
```bash
ssh -i ~/Downloads/prognosticos-aws.pem ubuntu@52.12.34.56
```

Digite `yes` quando perguntar sobre autenticidade.

---

## Passo 3: Instalar Docker (na EC2)

Cole estes comandos **um por vez** no terminal SSH:

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

Você deve ver as versões instaladas.

---

## Passo 4: Clonar Projeto (na EC2)

```bash
# Clonar repositório
git clone https://github.com/wemarques/prognosticos-brasileirao.git
cd prognosticos-brasileirao

# Usar branch com CSVs
git checkout claude/frontend-review-improvements-01SLDqfrpQJaeBCaHmyLkkcU

# Verificar que CSVs estão presentes
ls -lh data/csv/brasileirao/
ls -lh data/csv/premier_league/
```

Você deve ver os arquivos CSV listados.

---

## Passo 5: Configurar Variável de Ambiente (na EC2)

```bash
# Criar arquivo .env
nano .env
```

Cole esta linha (com sua chave real):
```
ODDS_API_KEY=652ee755d767058ec48c4994326eaa3d
LOG_LEVEL=INFO
```

Salvar: `Ctrl + X` → `Y` → `Enter`

---

## Passo 6: Build e Deploy (na EC2)

```bash
# Build da imagem Docker
docker-compose build

# Iniciar aplicação
docker-compose up -d

# Verificar se está rodando
docker-compose ps
```

Você deve ver `prognosticos-brasileirao` com status `Up`.

---

## Passo 7: Ver Logs (na EC2)

```bash
# Ver logs em tempo real
docker-compose logs -f app
```

Aguarde até ver: `You can now view your Streamlit app in your browser.`

Pressione `Ctrl + C` para sair dos logs.

---

## Passo 8: Acessar Aplicação

No seu navegador, acesse:

```
http://SEU-IP-PUBLICO:8501
```

**Exemplo:**
```
http://52.12.34.56:8501
```

✅ **Pronto!** O sistema deve estar rodando!

---

## 🔍 Testar Funcionalidades

1. No sidebar, selecione a liga (Brasileirão 🇧🇷 ou Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿)
2. Expanda "📊 Fonte de Dados" no sidebar
3. Verifique que os CSVs foram carregados:
   - ✅ Matches: X registros
   - ✅ Teams: X registros
4. Selecione uma rodada
5. Escolha dois times
6. Clique em "🔮 GERAR PROGNÓSTICO"

---

## 🛠️ Comandos Úteis

### Ver status dos containers
```bash
docker-compose ps
```

### Ver logs
```bash
docker-compose logs -f app
```

### Reiniciar aplicação
```bash
docker-compose restart app
```

### Parar aplicação
```bash
docker-compose down
```

### Atualizar código
```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🐛 Resolução de Problemas

### Aplicação não inicia
```bash
# Ver logs detalhados
docker-compose logs app

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Porta 8501 não acessível
1. Verificar Security Group da EC2
2. Garantir que porta 8501 está liberada para 0.0.0.0/0

### CSVs não encontrados
```bash
# Verificar estrutura
ls -la data/csv/brasileirao/
ls -la data/csv/premier_league/

# Se não existirem, a branch está errada
git branch
# Deve estar em: claude/frontend-review-improvements-01SLDqfrpQJaeBCaHmyLkkcU
```

---

## 💰 Custos

- **EC2 t3.small**: ~$15/mês
- **Storage 20GB**: ~$2/mês
- **Data Transfer**: Gratuito (dentro dos limites)
- **Total**: ~$17/mês

Para parar e economizar:
```bash
# Parar containers (na EC2)
docker-compose down
```

No AWS Console: **EC2 → Instances → Stop instance**

---

## 📞 Suporte

- `DEPLOY_AWS_CSV.md` - Guia completo
- `SETUP_CSV_FILES.md` - Como atualizar CSVs

---

**Boa sorte com o deploy!** 🚀
