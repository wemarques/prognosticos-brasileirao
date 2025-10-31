# 🚀 GUIA DE USO - SCRIPTS DE CONFIGURAÇÃO

## 📋 O QUE FAZEM OS SCRIPTS

Os scripts automatizam a configuração das variáveis de ambiente no EC2:

1. ✅ Conectam ao EC2 via SSH
2. ✅ Enviam o arquivo .env com suas chaves de API
3. ✅ Reiniciam o Docker Compose
4. ✅ Verificam o status dos containers

---

## 🖥️ PARA LINUX/MAC

### Pré-requisitos
```bash
# Ter SSH instalado (padrão em Linux/Mac)
# Ter o arquivo prognosticos-brasileirao-key.pem no diretório
```

### Como usar

**1. Navegue até o diretório do projeto:**
```bash
cd ~/OneDrive/Desktop/prognosticos-brasileirao
```

**2. Dê permissão de execução ao script:**
```bash
chmod +x scripts/configure_env.sh
```

**3. Execute o script:**
```bash
bash scripts/configure_env.sh
```

**4. Insira suas chaves de API quando solicitado:**
```
FOOTBALL_DATA_API_KEY: sua_chave_aqui
FOOTYSTATS_API_KEY: sua_chave_aqui
ODDS_API_KEY: sua_chave_aqui
```

**5. Aguarde a conclusão**

---

## 🪟 PARA WINDOWS (PowerShell)

### Pré-requisitos
```powershell
# Ter SSH instalado (Windows 10+)
# Ter o arquivo prognosticos-brasileirao-key.pem no diretório
# Executar PowerShell como Administrador
```

### Como usar

**1. Abra PowerShell como Administrador**

**2. Navegue até o diretório do projeto:**
```powershell
cd $env:USERPROFILE\OneDrive\Desktop\prognosticos-brasileirao
```

**3. Permita execução de scripts (primeira vez apenas):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**4. Execute o script:**
```powershell
.\scripts\configure_env.ps1
```

**5. Insira suas chaves de API quando solicitado:**
```
FOOTBALL_DATA_API_KEY: sua_chave_aqui
FOOTYSTATS_API_KEY: sua_chave_aqui
ODDS_API_KEY: sua_chave_aqui
```

**6. Aguarde a conclusão**

---

## 🔑 ONDE OBTER AS CHAVES DE API

### Football-Data.org
1. Acesse: https://www.football-data.org/client/register
2. Crie uma conta
3. Copie sua API Key

### FootyStats
1. Acesse: https://www.footystats.org/
2. Registre-se
3. Copie sua API Key (fornecida: test85g57)

### Odds API (Opcional)
1. Acesse: https://the-odds-api.com/
2. Registre-se
3. Copie sua API Key

---

## ✅ O QUE ESPERAR

### Durante a execução
```
🚀 Script de Configuração - Prognósticos Brasileirão
==================================================

Chave encontrada: prognosticos-brasileirao-key.pem

Insira suas chaves de API:

FOOTBALL_DATA_API_KEY: [você digita aqui]
FOOTYSTATS_API_KEY: [você digita aqui]
ODDS_API_KEY: [você digita aqui]

Conectando ao EC2...
Enviando configurações para EC2...
✓ Arquivo .env enviado com sucesso
Reiniciando Docker Compose...
✓ Docker Compose reiniciado com sucesso
Aguardando containers iniciarem...
Verificando status dos containers...
```

### Ao final
```
==================================================
✓ Configuração concluída com sucesso!
==================================================

Sua aplicação está rodando em:
http://34.205.26.29:8501

Para ver os logs:
ssh -i prognosticos-brasileirao-key.pem ubuntu@34.205.26.29
cd /opt/prognosticos-brasileirao
docker-compose logs -f app

✓ Pronto! Acesse a aplicação no navegador.
```

---

## 🆘 TROUBLESHOOTING

### Erro: "Arquivo não encontrado"
```bash
# Verifique se o arquivo .pem está no diretório
ls -la prognosticos-brasileirao-key.pem

# Se não estiver, procure por ele
find ~ -name "prognosticos-brasileirao-key.pem"
```

### Erro: "Permission denied (publickey)"
```bash
# Verifique as permissões da chave
chmod 400 prognosticos-brasileirao-key.pem

# Tente conectar manualmente
ssh -i prognosticos-brasileirao-key.pem ubuntu@34.205.26.29
```

### Erro: "SSH command not found" (Windows)
```powershell
# Instale OpenSSH
# Windows 10+: Settings → Apps → Optional Features → Add OpenSSH Client

# Ou use Git Bash que já tem SSH
```

### Erro: "Docker Compose not found"
```bash
# Conecte ao EC2 e verifique
ssh -i prognosticos-brasileirao-key.pem ubuntu@34.205.26.29
docker-compose --version
```

### Erro: "Containers unhealthy"
```bash
# Verifique os logs
ssh -i prognosticos-brasileirao-key.pem ubuntu@34.205.26.29
cd /opt/prognosticos-brasileirao
docker-compose logs app
```

---

## 📊 PRÓXIMOS PASSOS

### 1. Executar o script
```bash
# Linux/Mac
bash scripts/configure_env.sh

# Windows PowerShell
.\scripts\configure_env.ps1
```

### 2. Acessar a aplicação
```
http://34.205.26.29:8501
```

### 3. Verificar se os dados estão carregando
- Você deve ver os prognósticos do Brasileirão
- Se não aparecer, verifique os logs

### 4. Configurar domínio (opcional)
- Compre um domínio
- Aponte para 34.205.26.29
- Configure SSL/HTTPS

---

## 🎯 RESUMO

| Ação | Linux/Mac | Windows |
|------|-----------|---------|
| Navegar | `cd ~/OneDrive/Desktop/prognosticos-brasileirao` | `cd $env:USERPROFILE\OneDrive\Desktop\prognosticos-brasileirao` |
| Permissão | `chmod +x scripts/configure_env.sh` | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Executar | `bash scripts/configure_env.sh` | `.\scripts\configure_env.ps1` |
| Tempo | ~2 minutos | ~2 minutos |

---

## 📞 SUPORTE

Se tiver problemas:

1. **Verifique se SSH está funcionando:**
```bash
ssh -i prognosticos-brasileirao-key.pem ubuntu@34.205.26.29
```

2. **Verifique os logs:**
```bash
docker-compose logs app
```

3. **Reinicie manualmente:**
```bash
docker-compose restart
```

---

**Pronto! Execute o script e sua aplicação estará 100% configurada!** ✅