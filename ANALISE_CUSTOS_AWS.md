# 💰 ANÁLISE DE CUSTOS - AWS

## 📊 Configuração Atual do Sistema

### Serviços AWS Utilizados

1. **EC2 (Computação)**
   - Tipo: t3.micro
   - vCPU: 1
   - Memória: 1 GB
   - Armazenamento: 30 GB (EBS)

2. **RDS (Banco de Dados - PostgreSQL)**
   - Tipo: db.t3.micro
   - Armazenamento: 20 GB
   - Backup: 7 dias

3. **ElastiCache (Redis)**
   - Tipo: cache.t3.micro
   - Memória: 0.5 GB

4. **S3 (Armazenamento)**
   - Logs e backups
   - Estimado: 10 GB/mês

5. **CloudWatch (Monitoramento)**
   - Logs
   - Métricas

---

## 💵 CUSTOS MENSAIS - DENTRO DO FREE TIER

### ✅ Serviços Gratuitos (Primeiros 12 Meses)

| Serviço | Limite Gratuito | Seu Uso | Custo |
|---------|-----------------|---------|-------|
| **EC2** | 750 horas/mês | 730 horas | **$0** |
| **RDS PostgreSQL** | 750 horas/mês | 730 horas | **$0** |
| **ElastiCache** | 750 horas/mês | 730 horas | **$0** |
| **EBS** | 30 GB/mês | 30 GB | **$0** |
| **S3** | 5 GB/mês | 10 GB | **$1.00** |
| **Data Transfer** | 100 GB/mês | 50 GB | **$0** |
| **CloudWatch** | 10 métricas grátis | 5 métricas | **$0** |

### **TOTAL MENSAL (Free Tier):** $1.00

---

## 💸 CUSTOS MENSAIS - APÓS EXPIRAÇÃO DO FREE TIER

### ❌ Serviços Pagos (Após 12 meses)

#### 1. EC2 (t3.micro - Linux)
```
Preço: $0.0104/hora
Horas/mês: 730
Custo: 730 × $0.0104 = $7.59/mês
```

#### 2. RDS PostgreSQL (db.t3.micro)
```
Preço: $0.017/hora
Horas/mês: 730
Custo: 730 × $0.017 = $12.41/mês
```

#### 3. EBS (30 GB)
```
Preço: $0.10/GB/mês
Custo: 30 × $0.10 = $3.00/mês
```

#### 4. ElastiCache Redis (cache.t3.micro)
```
Preço: $0.017/hora
Horas/mês: 730
Custo: 730 × $0.017 = $12.41/mês
```

#### 5. S3 (10 GB)
```
Armazenamento: 10 GB × $0.023/GB = $0.23/mês
Requisições PUT: 1000 × $0.005/1000 = $0.01/mês
Requisições GET: 10000 × $0.0004/1000 = $0.01/mês
Total S3: $0.25/mês
```

#### 6. Data Transfer (50 GB saída)
```
Primeiros 1 GB: Grátis
Próximos 9.999 TB: $0.09/GB
50 GB × $0.09 = $4.50/mês
```

#### 7. CloudWatch
```
Métricas customizadas: 5 × $0.30 = $1.50/mês
Logs: 1 GB × $0.50 = $0.50/mês
Total CloudWatch: $2.00/mês
```

#### 8. Backup RDS (7 dias)
```
Armazenamento: 20 GB × $0.095/GB = $1.90/mês
```

### **TOTAL MENSAL (Pós Free Tier):** $44.06/mês

---

## 📈 CENÁRIOS DE CUSTO

### Cenário 1: Uso Mínimo (Atual)
```
EC2:           $7.59
RDS:          $12.41
EBS:           $3.00
ElastiCache:  $12.41
S3:            $0.25
Data Transfer: $4.50
CloudWatch:    $2.00
Backup:        $1.90
─────────────────────
TOTAL:        $44.06/mês
```

### Cenário 2: Uso Moderado (2x Tráfego)
```
EC2:           $7.59
RDS:          $12.41
EBS:           $6.00 (60 GB)
ElastiCache:  $12.41
S3:            $0.50 (20 GB)
Data Transfer: $9.00 (100 GB)
CloudWatch:    $3.00
Backup:        $3.80 (40 GB)
─────────────────────
TOTAL:        $54.71/mês
```

### Cenário 3: Uso Alto (5x Tráfego)
```
EC2:           $7.59
RDS:          $12.41
EBS:          $15.00 (150 GB)
ElastiCache:  $12.41
S3:            $1.15 (50 GB)
Data Transfer: $22.50 (250 GB)
CloudWatch:    $5.00
Backup:        $9.50 (100 GB)
─────────────────────
TOTAL:        $85.56/mês
```

### Cenário 4: Escalado (Múltiplas Instâncias)
```
EC2 (3x):      $22.77
RDS (db.t3.small): $24.82
EBS:           $30.00 (300 GB)
ElastiCache:   $24.82
S3:            $2.30 (100 GB)
Data Transfer: $45.00 (500 GB)
CloudWatch:    $10.00
Backup:        $19.00 (200 GB)
─────────────────────
TOTAL:        $178.71/mês
```

---

## 🎯 OTIMIZAÇÕES PARA REDUZIR CUSTOS

### 1. Usar Reserved Instances (Economia: 40-60%)
```
EC2 Reserved (1 ano):
- Sob demanda: $7.59/mês
- Reserved: $4.55/mês (40% desconto)
- Economia: $3.04/mês

RDS Reserved (1 ano):
- Sob demanda: $12.41/mês
- Reserved: $7.45/mês (40% desconto)
- Economia: $4.96/mês

ElastiCache Reserved (1 ano):
- Sob demanda: $12.41/mês
- Reserved: $7.45/mês (40% desconto)
- Economia: $4.96/mês

TOTAL ECONOMIA: $13.00/mês
NOVO TOTAL: $31.06/mês
```

### 2. Usar Savings Plans (Economia: 30-50%)
```
Compute Savings Plan (1 ano):
- Economia: 30-50%
- Aplicável a: EC2, RDS, ElastiCache
- Economia estimada: $15.00/mês
```

### 3. Otimizar Armazenamento
```
Usar S3 Intelligent-Tiering:
- Economia: 20-30%
- Custo: $0.0125/GB (vs $0.023/GB)
- Economia: $0.10/mês

Usar Glacier para backups antigos:
- Economia: 80%
- Custo: $0.004/GB (vs $0.095/GB)
- Economia: $1.50/mês
```

### 4. Usar Spot Instances (Economia: 70%)
```
EC2 Spot (t3.micro):
- Sob demanda: $7.59/mês
- Spot: $2.28/mês (70% desconto)
- Economia: $5.31/mês
- Risco: Pode ser interrompida
```

### 5. Consolidar Serviços
```
Usar RDS Aurora Serverless:
- Paga apenas pelo que usa
- Economia: 50-70%
- Custo: $6.20/mês (vs $12.41/mês)
- Economia: $6.21/mês
```

---

## 📊 COMPARAÇÃO COM OUTRAS PLATAFORMAS

| Plataforma | Custo Mensal | Características |
|-----------|--------------|-----------------|
| **AWS (Atual)** | $44.06 | Completo, escalável |
| **AWS (Otimizado)** | $20.00 | Com Reserved Instances |
| **Heroku** | $50.00 | Simples, gerenciado |
| **DigitalOcean** | $12.00 | Droplet + DB |
| **Streamlit Cloud** | $0.00 | Gratuito (limitado) |
| **Google Cloud** | $40.00 | Similar ao AWS |
| **Azure** | $45.00 | Similar ao AWS |

---

## 🚨 ALERTAS DE CUSTO

### Configurar Alertas na AWS

```bash
# 1. Ir para AWS Billing Dashboard
# 2. Budgets → Create Budget
# 3. Configurar:
#    - Limite: $50/mês
#    - Alerta: 80% do limite
#    - Email: seu-email@example.com
```

### Monitorar Custos

```bash
# AWS CLI
aws ce get-cost-and-usage \
  --time-period Start=2025-10-01,End=2025-10-31 \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE
```

---

## 💡 RECOMENDAÇÕES

### Para Desenvolvimento
```
✅ Usar Free Tier (12 meses)
✅ Usar t3.micro para tudo
✅ Usar S3 para logs
✅ Custo: $1.00/mês
```

### Para Produção Pequena
```
✅ Usar Reserved Instances (1 ano)
✅ Usar t3.small para EC2
✅ Usar db.t3.small para RDS
✅ Usar Savings Plan
✅ Custo: $30-40/mês
```

### Para Produção Média
```
✅ Usar Reserved Instances (3 anos)
✅ Usar t3.medium para EC2
✅ Usar db.t3.medium para RDS
✅ Usar Aurora Serverless
✅ Usar CloudFront para CDN
✅ Custo: $80-120/mês
```

### Para Produção Grande
```
✅ Usar Reserved Instances (3 anos)
✅ Usar m5.large para EC2
✅ Usar db.r5.large para RDS
✅ Usar Aurora com Multi-AZ
✅ Usar ElastiCache com Multi-AZ
✅ Usar CloudFront + S3
✅ Custo: $300-500/mês
```

---

## 📋 CHECKLIST DE OTIMIZAÇÃO

- [ ] Ativar Free Tier (primeiros 12 meses)
- [ ] Configurar alertas de custo
- [ ] Usar Reserved Instances
- [ ] Usar Savings Plans
- [ ] Otimizar armazenamento
- [ ] Usar CloudFront para CDN
- [ ] Limpar recursos não utilizados
- [ ] Usar Auto Scaling
- [ ] Monitorar custos mensalmente
- [ ] Revisar relatórios de custo

---

## 🎯 CONCLUSÃO

### Custo Atual (Free Tier)
- **Mensal:** $1.00
- **Anual:** $12.00

### Custo Após Free Tier (Sem Otimização)
- **Mensal:** $44.06
- **Anual:** $528.72

### Custo Após Free Tier (Com Otimização)
- **Mensal:** $20.00
- **Anual:** $240.00

### Economia com Otimização
- **Mensal:** $24.06
- **Anual:** $288.72

---

## 📞 PRÓXIMOS PASSOS

1. **Aproveitar Free Tier** (12 meses)
2. **Configurar Alertas** de custo
3. **Planejar Otimizações** antes de expirar
4. **Considerar Alternativas** (DigitalOcean, Heroku)
5. **Monitorar Custos** mensalmente

---

**Data:** 29/10/2025
**Versão:** 1.0.0
**Status:** ✅ Análise Completa

💰 **Seu sistema é muito econômico na AWS!** 💰