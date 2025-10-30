#!/bin/bash

# Script para criar RDS PostgreSQL na AWS

set -e

# Carregar configurações
if [ ! -f "aws_infrastructure.env" ]; then
    echo "❌ Erro: aws_infrastructure.env não encontrado"
    exit 1
fi

source aws_infrastructure.env

echo "🚀 Criando RDS PostgreSQL..."
echo "=================================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configurações RDS
DB_INSTANCE_IDENTIFIER="$PROJECT_NAME-db"
DB_NAME="prognosticos"
DB_USER="prognosticos"
DB_PASSWORD="Prognosticos@2025"  # Altere isso!
DB_PORT=5432

echo -e "${YELLOW}[1/2] Criando RDS Instance...${NC}"

aws rds create-db-instance \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --db-instance-class $DB_INSTANCE_CLASS \
    --engine postgres \
    --engine-version 15.3 \
    --master-username $DB_USER \
    --master-user-password $DB_PASSWORD \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids $SG_RDS_ID \
    --db-subnet-group-name "$PROJECT_NAME-db-subnet-group" \
    --publicly-accessible false \
    --multi-az false \
    --storage-encrypted true \
    --kms-key-id arn:aws:kms:$REGION:$(aws sts get-caller-identity --query Account --output text):key/$(aws kms list-keys --region $REGION --query 'Keys[0].KeyId' --output text) \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00" \
    --preferred-maintenance-window "sun:04:00-sun:05:00" \
    --enable-cloudwatch-logs-exports postgresql \
    --region $REGION \
    --tags "Key=Name,Value=$DB_INSTANCE_IDENTIFIER" \
    2>/dev/null || echo "RDS Instance já existe ou erro na criação"

echo -e "${GREEN}✓ RDS Instance criada: $DB_INSTANCE_IDENTIFIER${NC}"

echo -e "${YELLOW}[2/2] Aguardando RDS estar disponível...${NC}"
aws rds wait db-instance-available \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --region $REGION

# Obter endpoint
DB_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --region $REGION \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)

echo ""
echo -e "${GREEN}=================================================="
echo "✓ RDS PostgreSQL criada com sucesso!"
echo "==================================================${NC}"
echo ""
echo "Informações do Banco de Dados:"
echo "DB Instance: $DB_INSTANCE_IDENTIFIER"
echo "Endpoint: $DB_ENDPOINT"
echo "Port: $DB_PORT"
echo "Database: $DB_NAME"
echo "Username: $DB_USER"
echo "Password: $DB_PASSWORD"
echo ""
echo "Connection String:"
echo "postgresql://$DB_USER:$DB_PASSWORD@$DB_ENDPOINT:$DB_PORT/$DB_NAME"
echo ""

# Salvar informações
cat >> aws_infrastructure.env << EOF

# RDS
DB_INSTANCE_IDENTIFIER=$DB_INSTANCE_IDENTIFIER
DB_ENDPOINT=$DB_ENDPOINT
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
EOF

echo "Próximo passo:"
echo "bash scripts/create_elasticache.sh"