#!/bin/bash

# Script para configurar variáveis de ambiente no EC2
# Execute este script localmente: bash scripts/configure_env.sh

set -e

echo "🚀 Script de Configuração - Prognósticos Brasileirão"
echo "=================================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configurações
EC2_IP="34.205.26.29"
KEY_FILE="prognosticos-brasileirao-key.pem"
EC2_USER="ubuntu"
APP_DIR="/opt/prognosticos-brasileirao"

# Verificar se a chave existe
if [ ! -f "$KEY_FILE" ]; then
    echo -e "${RED}❌ Erro: Arquivo $KEY_FILE não encontrado!${NC}"
    echo "Procure pelo arquivo em:"
    find ~ -name "$KEY_FILE" 2>/dev/null || echo "Arquivo não encontrado no sistema"
    exit 1
fi

echo -e "${YELLOW}Chave encontrada: $KEY_FILE${NC}"
echo ""

# Solicitar chaves de API
echo -e "${YELLOW}Insira suas chaves de API:${NC}"
echo ""

read -p "FOOTBALL_DATA_API_KEY: " FOOTBALL_DATA_API_KEY
read -p "FOOTYSTATS_API_KEY: " FOOTYSTATS_API_KEY
read -p "ODDS_API_KEY: " ODDS_API_KEY

echo ""
echo -e "${YELLOW}Conectando ao EC2...${NC}"

# Criar arquivo .env temporário
cat > /tmp/env_temp << EOF
FOOTBALL_DATA_API_KEY=$FOOTBALL_DATA_API_KEY
FOOTYSTATS_API_KEY=$FOOTYSTATS_API_KEY
ODDS_API_KEY=$ODDS_API_KEY
POSTGRES_PASSWORD=Prognosticos@2025
POSTGRES_USER=prognosticos
POSTGRES_DB=prognosticos
REDIS_HOST=redis
REDIS_PORT=6379
EOF

# Copiar arquivo .env para EC2
echo -e "${YELLOW}Enviando configurações para EC2...${NC}"
scp -i "$KEY_FILE" /tmp/env_temp "$EC2_USER@$EC2_IP:$APP_DIR/.env"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Arquivo .env enviado com sucesso${NC}"
else
    echo -e "${RED}❌ Erro ao enviar arquivo .env${NC}"
    exit 1
fi

# Reiniciar Docker Compose
echo -e "${YELLOW}Reiniciando Docker Compose...${NC}"
ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" "cd $APP_DIR && docker-compose restart"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker Compose reiniciado com sucesso${NC}"
else
    echo -e "${RED}❌ Erro ao reiniciar Docker Compose${NC}"
    exit 1
fi

# Aguardar um pouco para os containers iniciarem
echo -e "${YELLOW}Aguardando containers iniciarem...${NC}"
sleep 5

# Verificar status
echo -e "${YELLOW}Verificando status dos containers...${NC}"
ssh -i "$KEY_FILE" "$EC2_USER@$EC2_IP" "cd $APP_DIR && docker-compose ps"

echo ""
echo -e "${GREEN}=================================================="
echo "✓ Configuração concluída com sucesso!"
echo "==================================================${NC}"
echo ""
echo "Sua aplicação está rodando em:"
echo -e "${GREEN}http://34.205.26.29:8501${NC}"
echo ""
echo "Para ver os logs:"
echo "ssh -i $KEY_FILE $EC2_USER@$EC2_IP"
echo "cd $APP_DIR"
echo "docker-compose logs -f app"
echo ""

# Limpar arquivo temporário
rm /tmp/env_temp

echo -e "${GREEN}✓ Pronto! Acesse a aplicação no navegador.${NC}"