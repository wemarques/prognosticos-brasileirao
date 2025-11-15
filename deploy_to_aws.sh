#!/bin/bash

# 🚀 Script de Deploy Automático para AWS EC2
# Data: 2025-11-14
# Versão: 1.0

set -e  # Exit on error

# Configurações
EC2_IP="34.205.26.29"
EC2_USER="ubuntu"
SSH_KEY="aws_key.pem"
PROJECT_DIR="prognosticos-brasileirao"
REPO_URL="https://github.com/wemarques/prognosticos-brasileirao.git"

echo "🚀 Iniciando deploy para AWS EC2..."
echo "📍 IP: $EC2_IP"
echo ""

# Função para executar comandos remotos
run_remote() {
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" "$@"
}

# Função para copiar arquivos
copy_to_ec2() {
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$1" "$EC2_USER@$EC2_IP:$2"
}

echo "✅ Testando conexão SSH..."
if run_remote "echo 'Conexão OK'" > /dev/null 2>&1; then
    echo "✅ Conexão SSH estabelecida com sucesso!"
else
    echo "❌ Erro ao conectar via SSH. Verifique as credenciais."
    exit 1
fi

echo ""
echo "📦 Verificando Docker na EC2..."
if run_remote "docker --version" > /dev/null 2>&1; then
    echo "✅ Docker já instalado: $(run_remote 'docker --version')"
else
    echo "📥 Instalando Docker..."
    run_remote "curl -fsSL https://get.docker.com | sudo sh"
    run_remote "sudo usermod -aG docker $EC2_USER"
    echo "✅ Docker instalado com sucesso!"
fi

echo ""
echo "📦 Verificando Docker Compose..."
if run_remote "docker-compose --version" > /dev/null 2>&1; then
    echo "✅ Docker Compose já instalado: $(run_remote 'docker-compose --version')"
else
    echo "📥 Instalando Docker Compose..."
    run_remote 'sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose'
    run_remote "sudo chmod +x /usr/local/bin/docker-compose"
    echo "✅ Docker Compose instalado com sucesso!"
fi

echo ""
echo "📂 Verificando projeto na EC2..."
if run_remote "test -d $PROJECT_DIR"; then
    echo "📁 Projeto já existe. Atualizando..."
    run_remote "cd $PROJECT_DIR && git fetch origin main"
    run_remote "cd $PROJECT_DIR && git checkout main"
    run_remote "cd $PROJECT_DIR && git pull origin main"
    echo "✅ Código atualizado!"
else
    echo "📥 Clonando repositório..."
    run_remote "git clone $REPO_URL $PROJECT_DIR"
    run_remote "cd $PROJECT_DIR && git checkout main"
    echo "✅ Repositório clonado!"
fi

echo ""
echo "🔧 Configurando variáveis de ambiente..."
echo "ODDS_API_KEY=" > .env.temp
copy_to_ec2 ".env.temp" "$PROJECT_DIR/.env"
rm .env.temp
echo "✅ Arquivo .env criado (configurar ODDS_API_KEY manualmente se necessário)"

echo ""
echo "🔍 Verificando arquivos CSV..."
run_remote "ls -lh $PROJECT_DIR/data/csv/brasileirao/"
echo "✅ CSV files verificados"

echo ""
echo "🐳 Parando containers antigos (se existirem)..."
run_remote "cd $PROJECT_DIR && docker-compose down" || true

echo ""
echo "🏗️ Construindo imagens Docker..."
run_remote "cd $PROJECT_DIR && docker-compose build"

echo ""
echo "🚀 Iniciando aplicação..."
run_remote "cd $PROJECT_DIR && docker-compose up -d"

echo ""
echo "⏳ Aguardando aplicação iniciar (30 segundos)..."
sleep 30

echo ""
echo "🔍 Verificando status dos containers..."
run_remote "cd $PROJECT_DIR && docker-compose ps"

echo ""
echo "📋 Últimas linhas dos logs..."
run_remote "cd $PROJECT_DIR && docker-compose logs --tail=20 app"

echo ""
echo "🎉 Deploy concluído com sucesso!"
echo ""
echo "📊 Informações de Acesso:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 URL: http://$EC2_IP:8501"
echo "🔗 Streamlit Health: http://$EC2_IP:8501/_stcore/health"
echo "📊 CSV Info: No sidebar, expandir 'Fonte de Dados'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Comandos úteis:"
echo "  Ver logs:       ssh -i $SSH_KEY $EC2_USER@$EC2_IP 'cd $PROJECT_DIR && docker-compose logs -f app'"
echo "  Reiniciar:      ssh -i $SSH_KEY $EC2_USER@$EC2_IP 'cd $PROJECT_DIR && docker-compose restart app'"
echo "  Parar:          ssh -i $SSH_KEY $EC2_USER@$EC2_IP 'cd $PROJECT_DIR && docker-compose down'"
echo "  Status:         ssh -i $SSH_KEY $EC2_USER@$EC2_IP 'cd $PROJECT_DIR && docker-compose ps'"
echo ""
echo "✅ Deploy finalizado!"
