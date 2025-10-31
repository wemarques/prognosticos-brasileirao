# Script para configurar variáveis de ambiente no EC2 (Windows PowerShell)
# Execute este script: .\scripts\configure_env.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Script de Configuração - Prognósticos Brasileirão" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""

# Configurações
$EC2_IP = "34.205.26.29"
$KEY_FILE = "prognosticos-brasileirao-key.pem"
$EC2_USER = "ubuntu"
$APP_DIR = "/opt/prognosticos-brasileirao"

# Verificar se a chave existe
if (-not (Test-Path $KEY_FILE)) {
    Write-Host "❌ Erro: Arquivo $KEY_FILE não encontrado!" -ForegroundColor Red
    Write-Host "Procure pelo arquivo em:" -ForegroundColor Yellow
    Get-ChildItem -Path $env:USERPROFILE -Recurse -Filter $KEY_FILE -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_.FullName }
    exit 1
}

Write-Host "✓ Chave encontrada: $KEY_FILE" -ForegroundColor Green
Write-Host ""

# Solicitar chaves de API
Write-Host "Insira suas chaves de API:" -ForegroundColor Yellow
Write-Host ""

$FOOTBALL_DATA_API_KEY = Read-Host "FOOTBALL_DATA_API_KEY"
$FOOTYSTATS_API_KEY = Read-Host "FOOTYSTATS_API_KEY"
$ODDS_API_KEY = Read-Host "ODDS_API_KEY"

Write-Host ""
Write-Host "Conectando ao EC2..." -ForegroundColor Yellow

# Criar arquivo .env temporário
$env_content = @"
FOOTBALL_DATA_API_KEY=$FOOTBALL_DATA_API_KEY
FOOTYSTATS_API_KEY=$FOOTYSTATS_API_KEY
ODDS_API_KEY=$ODDS_API_KEY
POSTGRES_PASSWORD=Prognosticos@2025
POSTGRES_USER=prognosticos
POSTGRES_DB=prognosticos
REDIS_HOST=redis
REDIS_PORT=6379
"@

$env_temp = "$env:TEMP\env_temp"
Set-Content -Path $env_temp -Value $env_content

# Copiar arquivo .env para EC2
Write-Host "Enviando configurações para EC2..." -ForegroundColor Yellow

try {
    # Usar scp para copiar o arquivo
    & scp -i $KEY_FILE $env_temp "$EC2_USER@$EC2_IP`:$APP_DIR/.env"
    Write-Host "✓ Arquivo .env enviado com sucesso" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao enviar arquivo .env" -ForegroundColor Red
    exit 1
}

# Reiniciar Docker Compose
Write-Host "Reiniciando Docker Compose..." -ForegroundColor Yellow

try {
    & ssh -i $KEY_FILE "$EC2_USER@$EC2_IP" "cd $APP_DIR && docker-compose restart"
    Write-Host "✓ Docker Compose reiniciado com sucesso" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao reiniciar Docker Compose" -ForegroundColor Red
    exit 1
}

# Aguardar um pouco para os containers iniciarem
Write-Host "Aguardando containers iniciarem..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verificar status
Write-Host "Verificando status dos containers..." -ForegroundColor Yellow
& ssh -i $KEY_FILE "$EC2_USER@$EC2_IP" "cd $APP_DIR && docker-compose ps"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "✓ Configuração concluída com sucesso!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Sua aplicação está rodando em:" -ForegroundColor Green
Write-Host "http://34.205.26.29:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para ver os logs:" -ForegroundColor Yellow
Write-Host "ssh -i $KEY_FILE $EC2_USER@$EC2_IP" -ForegroundColor Cyan
Write-Host "cd $APP_DIR" -ForegroundColor Cyan
Write-Host "docker-compose logs -f app" -ForegroundColor Cyan
Write-Host ""

# Limpar arquivo temporário
Remove-Item -Path $env_temp -Force

Write-Host "✓ Pronto! Acesse a aplicação no navegador." -ForegroundColor Green