#!/bin/bash

# Script para criar EC2 na AWS
# Carrega configurações do arquivo anterior

set -e

# Carregar configurações
if [ ! -f "aws_infrastructure.env" ]; then
    echo "❌ Erro: aws_infrastructure.env não encontrado"
    echo "Execute primeiro: bash scripts/setup_aws_infrastructure.sh"
    exit 1
fi

source aws_infrastructure.env

echo "🚀 Criando EC2 Instance..."
echo "=================================================="

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configurações EC2
KEY_PAIR_NAME="$PROJECT_NAME-key"
INSTANCE_NAME="$PROJECT_NAME-server"

# 1. Criar Key Pair
echo -e "${YELLOW}[1/4] Criando Key Pair...${NC}"
if aws ec2 describe-key-pairs --key-names $KEY_PAIR_NAME --region $REGION 2>/dev/null; then
    echo "Key Pair já existe"
else
    aws ec2 create-key-pair \
        --key-name $KEY_PAIR_NAME \
        --region $REGION \
        --query 'KeyMaterial' \
        --output text > $KEY_PAIR_NAME.pem
    chmod 400 $KEY_PAIR_NAME.pem
    echo -e "${GREEN}✓ Key Pair criada: $KEY_PAIR_NAME.pem${NC}"
fi

# 2. Obter AMI ID (Ubuntu 22.04 LTS)
echo -e "${YELLOW}[2/4] Obtendo AMI ID...${NC}"
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text \
    --region $REGION)
echo -e "${GREEN}✓ AMI ID: $AMI_ID${NC}"

# 3. Criar User Data Script
echo -e "${YELLOW}[3/4] Preparando User Data Script...${NC}"
cat > user_data.sh << 'USERDATA'
#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
apt-get install -y docker.io docker-compose

# Start Docker
systemctl start docker
systemctl enable docker

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Install AWS CLI
apt-get install -y awscli

# Create app directory
mkdir -p /opt/prognosticos-brasileirao
cd /opt/prognosticos-brasileirao

# Clone repository
git clone https://github.com/wemarques/prognosticos-brasileirao.git .

# Create .env file (será preenchido depois)
cat > .env << 'EOF'
FOOTBALL_DATA_API_KEY=your_key_here
FOOTYSTATS_API_KEY=your_key_here
ODDS_API_KEY=your_key_here
POSTGRES_PASSWORD=prognosticos123
POSTGRES_USER=prognosticos
POSTGRES_DB=prognosticos
REDIS_HOST=redis
REDIS_PORT=6379
EOF

# Start Docker Compose
docker-compose up -d

echo "✓ Setup concluído!"
USERDATA

# 4. Criar EC2 Instance
echo -e "${YELLOW}[4/4] Criando EC2 Instance...${NC}"
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_PAIR_NAME \
    --security-group-ids $SG_EC2_ID \
    --subnet-id $SUBNET_PUBLIC_ID \
    --associate-public-ip-address \
    --user-data file://user_data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --region $REGION \
    --query 'Instances[0].InstanceId' \
    --output text)

echo -e "${GREEN}✓ EC2 Instance criada: $INSTANCE_ID${NC}"

# Aguardar instância estar em running
echo -e "${YELLOW}Aguardando instância iniciar...${NC}"
aws ec2 wait instance-running \
    --instance-ids $INSTANCE_ID \
    --region $REGION

# Obter IP público
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo ""
echo -e "${GREEN}=================================================="
echo "✓ EC2 Instance criada com sucesso!"
echo "==================================================${NC}"
echo ""
echo "Informações da Instância:"
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Key Pair: $KEY_PAIR_NAME.pem"
echo ""
echo "Para conectar via SSH:"
echo "ssh -i $KEY_PAIR_NAME.pem ubuntu@$PUBLIC_IP"
echo ""
echo "Acesse a aplicação em:"
echo "http://$PUBLIC_IP:8501"
echo ""

# Salvar informações
cat >> aws_infrastructure.env << EOF

# EC2
INSTANCE_ID=$INSTANCE_ID
PUBLIC_IP=$PUBLIC_IP
KEY_PAIR_NAME=$KEY_PAIR_NAME
AMI_ID=$AMI_ID
USERDATA_SCRIPT=user_data.sh
EOF

echo "Próximos passos:"
echo "1. Execute: bash scripts/create_rds.sh"
echo "2. Execute: bash scripts/create_elasticache.sh"