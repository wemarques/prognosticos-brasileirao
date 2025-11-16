#!/bin/bash

# 🚀 Script de Deploy Manual para AWS EC2
# Use este script se o GitHub Actions não estiver disponível

set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando deploy manual para AWS EC2...${NC}"

# Verificar variáveis de ambiente
if [ -z "$EC2_HOST" ]; then
    read -p "Digite o IP ou hostname da EC2: " EC2_HOST
fi

if [ -z "$EC2_KEY_PATH" ]; then
    read -p "Digite o caminho para o arquivo .pem: " EC2_KEY_PATH
fi

EC2_USER=${EC2_USER:-ubuntu}
DEPLOY_PATH=${DEPLOY_PATH:-/home/ubuntu/prognosticos-brasileirao}
BRANCH=${BRANCH:-$(git branch --show-current)}

echo -e "${BLUE}📋 Configuração:${NC}"
echo "  Host: $EC2_HOST"
echo "  User: $EC2_USER"
echo "  Key: $EC2_KEY_PATH"
echo "  Path: $DEPLOY_PATH"
echo "  Branch: $BRANCH"
echo ""

read -p "Continuar com deploy? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Deploy cancelado${NC}"
    exit 1
fi

echo -e "${BLUE}🔐 Testando conexão SSH...${NC}"
ssh -i "$EC2_KEY_PATH" -o ConnectTimeout=10 "$EC2_USER@$EC2_HOST" 'echo "✅ SSH OK"'

echo -e "${BLUE}📦 Fazendo deploy...${NC}"
ssh -i "$EC2_KEY_PATH" "$EC2_USER@$EC2_HOST" << EOF
    set -e

    echo "📂 Navegando para diretório da aplicação..."
    cd $DEPLOY_PATH

    echo "🔄 Atualizando código..."
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH

    echo "🛑 Parando containers..."
    docker-compose down

    echo "🏗️ Fazendo build..."
    docker-compose build --no-cache

    echo "🚀 Iniciando containers..."
    docker-compose up -d

    echo "⏳ Aguardando inicialização..."
    sleep 10

    echo "✅ Verificando status..."
    docker-compose ps

    echo "📊 Logs recentes:"
    docker-compose logs --tail=30 app
EOF

echo -e "${BLUE}🔍 Verificando saúde da aplicação...${NC}"
sleep 5
if curl -f -s "http://$EC2_HOST:8501/_stcore/health" > /dev/null; then
    echo -e "${GREEN}✅ Aplicação está saudável!${NC}"
    echo -e "${GREEN}🌐 Acesse: http://$EC2_HOST:8501${NC}"
else
    echo -e "${RED}⚠️ Aplicação pode não estar respondendo corretamente${NC}"
    echo "Verifique os logs manualmente"
fi

echo -e "${GREEN}✅ Deploy concluído!${NC}"
