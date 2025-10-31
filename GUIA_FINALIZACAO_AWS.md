# 🎯 GUIA DE FINALIZAÇÃO - CONFIGURAÇÕES AWS

## 📋 O QUE FALTA FAZER

Você tem a infraestrutura rodando, mas precisa:

1. ✅ **Configurar variáveis de ambiente** (APIs)
2. ✅ **Configurar banco de dados** (RDS)
3. ✅ **Configurar cache** (ElastiCache)
4. ✅ **Configurar domínio** (opcional)
5. ✅ **Configurar SSL/HTTPS** (opcional)
6. ✅ **Configurar backups** (opcional)

---

## 🔧 PASSO 1: CONFIGURAR VARIÁVEIS DE AMBIENTE

### 1.1 Conectar ao EC2
```bash
ssh -i prognosticos-brasileirao-key.pem ubuntu@34.205.26.29
```

### 1.2 Editar arquivo .env
```bash
cd /opt/prognosticos-brasileirao
nano .env
```

### 1.3 Adicionar suas chaves de API
```
FOOTBALL_DATA_API_KEY=sua_chave_aqui
FOOTYSTATS_API_KEY=sua_chave_aqui
ODDS_API_KEY=sua_chave_aqui
POSTGRES_PASSWORD=Prognosticos@2025
POSTGRES_USER=prognosticos
POSTGRES_DB=prognosticos
REDIS_HOST=redis
REDIS_PORT=6379
```

### 1.4 Salvar e sair
```
Ctrl+O (salvar)
Enter
Ctrl+X (sair)
```

### 1.5 Reiniciar Docker Compose
```bash
docker-compose restart
```

### 1.6 Verificar se está funcionando
```bash
docker-compose logs app
```

---

## 🗄️ PASSO 2: CONFIGURAR BANCO DE DADOS (RDS)

### 2.1 Conectar ao RDS (do EC2)
```bash
psql -h <RDS_ENDPOINT> -U prognosticos -d prognosticos
```

**Onde `<RDS_ENDPOINT>` é o endpoint do RDS que você criou**

### 2.2 Criar tabelas (se necessário)
```sql
-- Exemplo de tabela para prognósticos
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP,
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    home_goals INT,
    away_goals INT,
    prediction VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exemplo de tabela para usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.3 Sair do psql
```
\q
```

---

## 💾 PASSO 3: CONFIGURAR CACHE (ELASTICACHE)

### 3.1 Testar conexão com Redis (do EC2)
```bash
redis-cli -h <CACHE_ENDPOINT> ping
```

**Você deve ver: `PONG`**

### 3.2 Verificar se está funcionando
```bash
redis-cli -h <CACHE_ENDPOINT>
```

Depois:
```
SET test "Hello"
GET test
```

Sair:
```
EXIT
```

---

## 🌐 PASSO 4: ACESSAR A APLICAÇÃO

### 4.1 No navegador
```
http://34.205.26.29:8501
```

### 4.2 Verificar se os dados estão carregando
- Você deve ver os prognósticos do Brasileirão
- Se não aparecer, verifique as chaves de API

---

## 🔐 PASSO 5: CONFIGURAR DOMÍNIO (OPCIONAL)

### 5.1 Comprar domínio
- Recomendado: Namecheap, GoDaddy, Route53

### 5.2 Apontar para EC2
- Criar registro A apontando para: **34.205.26.29**

### 5.3 Configurar no Nginx (no EC2)
```bash
sudo nano /etc/nginx/sites-available/default
```

Adicionar:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Reiniciar Nginx:
```bash
sudo systemctl restart nginx
```

---

## 🔒 PASSO 6: CONFIGURAR SSL/HTTPS (OPCIONAL)

### 6.1 Instalar Certbot
```bash
sudo apt-get install certbot python3-certbot-nginx
```

### 6.2 Gerar certificado
```bash
sudo certbot --nginx -d seu-dominio.com
```

### 6.3 Renovação automática
```bash
sudo systemctl enable certbot.timer
```

---

## 📊 PASSO 7: MONITORAMENTO

### 7.1 Ver logs da aplicação
```bash
docker-compose logs -f app
```

### 7.2 Ver uso de recursos
```bash
docker stats
```

### 7.3 Ver status dos containers
```bash
docker-compose ps
```

---

## 🔄 PASSO 8: BACKUPS

### 8.1 Backup do banco de dados (RDS)
```bash
# AWS faz automaticamente (7 dias)
# Você pode aumentar em: AWS Console → RDS → Modify
```

### 8.2 Backup manual do banco
```bash
pg_dump -h <RDS_ENDPOINT> -U prognosticos -d prognosticos > backup.sql
```

### 8.3 Restaurar backup
```bash
psql -h <RDS_ENDPOINT> -U prognosticos -d prognosticos < backup.sql
```

---

## ✅ CHECKLIST FINAL

- [ ] Variáveis de ambiente configuradas
- [ ] Chaves de API adicionadas
- [ ] Docker Compose reiniciado
- [ ] Aplicação acessível em http://34.205.26.29:8501
- [ ] Dados carregando corretamente
- [ ] Banco de dados conectado
- [ ] Cache Redis funcionando
- [ ] Logs sem erros
- [ ] Monitoramento ativo

---

## 🆘 TROUBLESHOOTING

### Problema: Aplicação não carrega
```bash
docker-compose logs app
```

### Problema: Sem dados da API
- Verifique as chaves de API no .env
- Verifique se as APIs estão online

### Problema: Banco de dados não conecta
```bash
psql -h <RDS_ENDPOINT> -U prognosticos -d prognosticos
```

### Problema: Cache não funciona
```bash
redis-cli -h <CACHE_ENDPOINT> ping
```

---

## 📞 PRÓXIMOS PASSOS

1. **Configure as variáveis de ambiente** (PASSO 1)
2. **Reinicie a aplicação**
3. **Acesse em http://34.205.26.29:8501**
4. **Verifique se os dados estão carregando**

**Quando terminar, me avise!** ✅