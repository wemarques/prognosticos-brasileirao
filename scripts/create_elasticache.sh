#!/bin/bash

# Script para criar ElastiCache Redis na AWS

set -e

# Carregar configurações
if [ ! -f "aws_infrastructure.env" ]; then
    echo "❌ Erro: aws_infrastructure.env não encontrado"
    exit 1
fi

source aws_infrastructure.env

echo "🚀 Criando ElastiCache Redis..."
echo "=================================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configurações ElastiCache
CACHE_CLUSTER_ID="$PROJECT_NAME-cache"
CACHE_PORT=6379

echo -e "${YELLOW}[1/2] Criando ElastiCache Cluster...${NC}"

aws elasticache create-cache-cluster \
    --cache-cluster-id $CACHE_CLUSTER_ID \
    --cache-node-type $CACHE_NODE_TYPE \
    --engine redis \
    --engine-version 7.0 \
    --num-cache-nodes 1 \
    --port $CACHE_PORT \
    --cache-parameter-group-name default.redis7 \
    --cache-subnet-group-name "$PROJECT_NAME-db-subnet-group" \
    --security-group-ids $SG_CACHE_ID \
    --auto-minor-version-upgrade true \
    --preferred-maintenance-window "sun:05:00-sun:06:00" \
    --tags "Key=Name,Value=$CACHE_CLUSTER_ID" \
    --region $REGION \
    2>/dev/null || echo "ElastiCache Cluster já existe ou erro na criação"

echo -e "${GREEN}✓ ElastiCache Cluster criada: $CACHE_CLUSTER_ID${NC}"

echo -e "${YELLOW}[2/2] Aguardando ElastiCache estar disponível...${NC}"
aws elasticache wait cache-cluster-available \
    --cache-cluster-id $CACHE_CLUSTER_ID \
    --region $REGION

# Obter endpoint
CACHE_ENDPOINT=$(aws elasticache describe-cache-clusters \
    --cache-cluster-id $CACHE_CLUSTER_ID \
    --show-cache-node-info \
    --region $REGION \
    --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
    --output text)

echo ""
echo -e "${GREEN}=================================================="
echo "✓ ElastiCache Redis criada com sucesso!"
echo "==================================================${NC}"
echo ""
echo "Informações do Cache:"
echo "Cluster ID: $CACHE_CLUSTER_ID"
echo "Endpoint: $CACHE_ENDPOINT"
echo "Port: $CACHE_PORT"
echo ""
echo "Connection String:"
echo "redis://$CACHE_ENDPOINT:$CACHE_PORT"
echo ""

# Salvar informações
cat >> aws_infrastructure.env << EOF

# ElastiCache
CACHE_CLUSTER_ID=$CACHE_CLUSTER_ID
CACHE_ENDPOINT=$CACHE_ENDPOINT
CACHE_PORT=$CACHE_PORT
EOF

echo -e "${GREEN}=================================================="
echo "✓ TODA A INFRAESTRUTURA FOI CRIADA COM SUCESSO!"
echo "==================================================${NC}"
echo ""
echo "Resumo da Infraestrutura:"
echo "- VPC: $VPC_ID"
echo "- EC2: $INSTANCE_ID ($PUBLIC_IP)"
echo "- RDS: $DB_ENDPOINT"
echo "- ElastiCache: $CACHE_ENDPOINT"
echo ""
echo "Próximos passos:"
echo "1. Conecte via SSH: ssh -i $KEY_PAIR_NAME.pem ubuntu@$PUBLIC_IP"
echo "2. Configure as variáveis de ambiente no EC2"
echo "3. Acesse a aplicação em: http://$PUBLIC_IP:8501"
echo ""
echo "Arquivo de configuração: aws_infrastructure.env"