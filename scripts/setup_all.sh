#!/bin/bash

# Script Master - Cria toda a infraestrutura AWS automaticamente

echo "🚀 INICIANDO SETUP COMPLETO DA INFRAESTRUTURA AWS"
echo "=================================================="
echo ""
echo "Este script irá criar:"
echo "✓ VPC (Virtual Private Cloud)"
echo "✓ EC2 (Servidor Web)"
echo "✓ RDS (Banco de Dados PostgreSQL)"
echo "✓ ElastiCache (Cache Redis)"
echo ""
echo "Tempo estimado: 15-20 minutos"
echo ""
read -p "Deseja continuar? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operação cancelada"
    exit 1
fi

echo ""
echo "=================================================="
echo "FASE 1: Criando VPC e Infraestrutura de Rede"
echo "=================================================="
bash scripts/setup_aws_infrastructure.sh

if [ $? -ne 0 ]; then
    echo "❌ Erro na Fase 1"
    exit 1
fi

echo ""
echo "=================================================="
echo "FASE 2: Criando EC2 Instance"
echo "=================================================="
bash scripts/create_ec2.sh

if [ $? -ne 0 ]; then
    echo "❌ Erro na Fase 2"
    exit 1
fi

echo ""
echo "=================================================="
echo "FASE 3: Criando RDS PostgreSQL"
echo "=================================================="
bash scripts/create_rds.sh

if [ $? -ne 0 ]; then
    echo "❌ Erro na Fase 3"
    exit 1
fi

echo ""
echo "=================================================="
echo "FASE 4: Criando ElastiCache Redis"
echo "=================================================="
bash scripts/create_elasticache.sh

if [ $? -ne 0 ]; then
    echo "❌ Erro na Fase 4"
    exit 1
fi

echo ""
echo "🎉 SETUP COMPLETO COM SUCESSO!"
echo "=================================================="
echo ""
echo "Sua infraestrutura AWS está pronta!"
echo ""
echo "Arquivo de configuração: aws_infrastructure.env"
echo ""
echo "Para ver todas as informações:"
echo "cat aws_infrastructure.env"