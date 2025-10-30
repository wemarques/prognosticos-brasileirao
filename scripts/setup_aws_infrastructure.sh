#!/bin/bash

# Script de Setup Automático da Infraestrutura AWS
# Este script cria toda a infraestrutura necessária para o Prognosticos Brasileirão

set -e

echo "🚀 Iniciando setup da infraestrutura AWS..."
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
PROJECT_NAME="prognosticos-brasileirao"
REGION="us-east-1"
INSTANCE_TYPE="t3.micro"
DB_INSTANCE_CLASS="db.t3.micro"
CACHE_NODE_TYPE="cache.t3.micro"

echo -e "${YELLOW}Configurações:${NC}"
echo "Projeto: $PROJECT_NAME"
echo "Região: $REGION"
echo "EC2 Type: $INSTANCE_TYPE"
echo "RDS Type: $DB_INSTANCE_CLASS"
echo "ElastiCache Type: $CACHE_NODE_TYPE"
echo ""

# 1. Criar VPC
echo -e "${YELLOW}[1/8] Criando VPC...${NC}"
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=$PROJECT_NAME-vpc}]" \
  --region $REGION \
  --query 'Vpc.VpcId' \
  --output text)
echo -e "${GREEN}✓ VPC criada: $VPC_ID${NC}"

# 2. Criar Internet Gateway
echo -e "${YELLOW}[2/8] Criando Internet Gateway...${NC}"
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=$PROJECT_NAME-igw}]" \
  --region $REGION \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)
aws ec2 attach-internet-gateway \
  --internet-gateway-id $IGW_ID \
  --vpc-id $VPC_ID \
  --region $REGION
echo -e "${GREEN}✓ Internet Gateway criado: $IGW_ID${NC}"

# 3. Criar Subnet Pública
echo -e "${YELLOW}[3/8] Criando Subnet Pública...${NC}"
SUBNET_PUBLIC_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ${REGION}a \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-subnet-public}]" \
  --region $REGION \
  --query 'Subnet.SubnetId' \
  --output text)
echo -e "${GREEN}✓ Subnet Pública criada: $SUBNET_PUBLIC_ID${NC}"

# 4. Criar Subnet Privada para RDS
echo -e "${YELLOW}[4/8] Criando Subnet Privada...${NC}"
SUBNET_PRIVATE_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone ${REGION}b \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=$PROJECT_NAME-subnet-private}]" \
  --region $REGION \
  --query 'Subnet.SubnetId' \
  --output text)
echo -e "${GREEN}✓ Subnet Privada criada: $SUBNET_PRIVATE_ID${NC}"

# 5. Criar Route Table
echo -e "${YELLOW}[5/8] Criando Route Table...${NC}"
ROUTE_TABLE_ID=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=$PROJECT_NAME-rt}]" \
  --region $REGION \
  --query 'RouteTable.RouteTableId' \
  --output text)
aws ec2 create-route \
  --route-table-id $ROUTE_TABLE_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID \
  --region $REGION
aws ec2 associate-route-table \
  --subnet-id $SUBNET_PUBLIC_ID \
  --route-table-id $ROUTE_TABLE_ID \
  --region $REGION
echo -e "${GREEN}✓ Route Table criada: $ROUTE_TABLE_ID${NC}"

# 6. Criar Security Groups
echo -e "${YELLOW}[6/8] Criando Security Groups...${NC}"

# Security Group para EC2
SG_EC2_ID=$(aws ec2 create-security-group \
  --group-name "$PROJECT_NAME-sg-ec2" \
  --description "Security group for EC2 Streamlit" \
  --vpc-id $VPC_ID \
  --region $REGION \
  --query 'GroupId' \
  --output text)

# Permitir SSH (22)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_EC2_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0 \
  --region $REGION

# Permitir HTTP (80)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_EC2_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region $REGION

# Permitir HTTPS (443)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_EC2_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0 \
  --region $REGION

# Permitir Streamlit (8501)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_EC2_ID \
  --protocol tcp \
  --port 8501 \
  --cidr 0.0.0.0/0 \
  --region $REGION

echo -e "${GREEN}✓ Security Group EC2 criado: $SG_EC2_ID${NC}"

# Security Group para RDS
SG_RDS_ID=$(aws ec2 create-security-group \
  --group-name "$PROJECT_NAME-sg-rds" \
  --description "Security group for RDS PostgreSQL" \
  --vpc-id $VPC_ID \
  --region $REGION \
  --query 'GroupId' \
  --output text)

# Permitir PostgreSQL (5432) do EC2
aws ec2 authorize-security-group-ingress \
  --group-id $SG_RDS_ID \
  --protocol tcp \
  --port 5432 \
  --source-group $SG_EC2_ID \
  --region $REGION

echo -e "${GREEN}✓ Security Group RDS criado: $SG_RDS_ID${NC}"

# Security Group para ElastiCache
SG_CACHE_ID=$(aws ec2 create-security-group \
  --group-name "$PROJECT_NAME-sg-cache" \
  --description "Security group for ElastiCache Redis" \
  --vpc-id $VPC_ID \
  --region $REGION \
  --query 'GroupId' \
  --output text)

# Permitir Redis (6379) do EC2
aws ec2 authorize-security-group-ingress \
  --group-id $SG_CACHE_ID \
  --protocol tcp \
  --port 6379 \
  --source-group $SG_EC2_ID \
  --region $REGION

echo -e "${GREEN}✓ Security Group ElastiCache criado: $SG_CACHE_ID${NC}"

# 7. Criar DB Subnet Group para RDS
echo -e "${YELLOW}[7/8] Criando DB Subnet Group...${NC}"
aws rds create-db-subnet-group \
  --db-subnet-group-name "$PROJECT_NAME-db-subnet-group" \
  --db-subnet-group-description "Subnet group for RDS" \
  --subnet-ids $SUBNET_PRIVATE_ID $SUBNET_PUBLIC_ID \
  --region $REGION 2>/dev/null || echo "DB Subnet Group já existe"

echo -e "${GREEN}✓ DB Subnet Group criado${NC}"

# 8. Salvar configurações em arquivo
echo -e "${YELLOW}[8/8] Salvando configurações...${NC}"
cat > aws_infrastructure.env << EOF
# AWS Infrastructure Configuration
# Gerado em: $(date)

# VPC
VPC_ID=$VPC_ID
IGW_ID=$IGW_ID

# Subnets
SUBNET_PUBLIC_ID=$SUBNET_PUBLIC_ID
SUBNET_PRIVATE_ID=$SUBNET_PRIVATE_ID

# Route Table
ROUTE_TABLE_ID=$ROUTE_TABLE_ID

# Security Groups
SG_EC2_ID=$SG_EC2_ID
SG_RDS_ID=$SG_RDS_ID
SG_CACHE_ID=$SG_CACHE_ID

# Configurações
REGION=$REGION
INSTANCE_TYPE=$INSTANCE_TYPE
DB_INSTANCE_CLASS=$DB_INSTANCE_CLASS
CACHE_NODE_TYPE=$CACHE_NODE_TYPE
PROJECT_NAME=$PROJECT_NAME
EOF

echo -e "${GREEN}✓ Configurações salvas em aws_infrastructure.env${NC}"

echo ""
echo -e "${GREEN}=================================================="
echo "✓ Infraestrutura VPC criada com sucesso!"
echo "==================================================${NC}"
echo ""
echo "Próximos passos:"
echo "1. Execute: bash scripts/create_ec2.sh"
echo "2. Execute: bash scripts/create_rds.sh"
echo "3. Execute: bash scripts/create_elasticache.sh"
echo ""
echo "Ou execute tudo de uma vez:"
echo "bash scripts/setup_all.sh"