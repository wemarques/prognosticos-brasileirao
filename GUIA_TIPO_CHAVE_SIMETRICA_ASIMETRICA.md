# 🔐 GUIA - TIPO DE CHAVE: SIMÉTRICA vs ASSIMÉTRICA

## 📋 VOCÊ ESTÁ AQUI

Você está na **ETAPA 2 de 4** e viu que há **2 opções de tipo de chave**:
1. **Simétrica**
2. **Assimétrica**

---

## 🔑 COMPARAÇÃO: SIMÉTRICA vs ASSIMÉTRICA

### CHAVE SIMÉTRICA

#### O que é:
```
- Uma única chave para criptografar E descriptografar
- Mesma chave usada nos dois sentidos
- Mais rápida e simples
- Exemplo: AES-256
```

#### Vantagens:
```
✅ Mais rápida
✅ Mais simples de usar
✅ Menor overhead computacional
✅ Ideal para dados em repouso
✅ Recomendada para a maioria dos casos
```

#### Desvantagens:
```
❌ Precisa compartilhar a chave (risco de segurança)
❌ Difícil de gerenciar em larga escala
❌ Não é ideal para assinatura digital
```

#### Quando usar:
```
✅ Criptografia de dados em repouso (S3, EBS)
✅ Criptografia de banco de dados
✅ Criptografia de backups
✅ Proteção de dados sensíveis
✅ RECOMENDADO PARA SEU CASO
```

---

### CHAVE ASSIMÉTRICA

#### O que é:
```
- Duas chaves: pública e privada
- Chave pública para criptografar
- Chave privada para descriptografar
- Exemplo: RSA, ECC
```

#### Vantagens:
```
✅ Não precisa compartilhar a chave privada
✅ Ideal para assinatura digital
✅ Melhor para comunicação segura
✅ Mais segura para distribuição de chaves
✅ Ideal para certificados SSL/TLS
```

#### Desvantagens:
```
❌ Mais lenta que simétrica
❌ Mais complexa de implementar
❌ Maior overhead computacional
❌ Não ideal para criptografia de grandes volumes
```

#### Quando usar:
```
✅ Assinatura digital
✅ Certificados SSL/TLS
✅ Comunicação segura entre sistemas
✅ Troca de chaves
✅ Autenticação
```

---

## 📊 TABELA COMPARATIVA

| Aspecto | Simétrica | Assimétrica |
|---------|-----------|-------------|
| **Número de chaves** | 1 | 2 (pública + privada) |
| **Velocidade** | ⚡ Rápida | 🐢 Lenta |
| **Complexidade** | Simples | Complexa |
| **Segurança** | Boa | Excelente |
| **Compartilhamento** | Difícil | Fácil (pública) |
| **Assinatura digital** | ❌ Não | ✅ Sim |
| **Criptografia em massa** | ✅ Sim | ❌ Não |
| **Ideal para** | Dados em repouso | Comunicação segura |

---

## 🎯 RECOMENDAÇÃO PARA SEU CASO

### Para Prognosticos Brasileirão:

```
✅ ESCOLHA: SIMÉTRICA

Razões:
1. Você está criptografando dados em repouso (banco de dados)
2. Não precisa de assinatura digital
3. Melhor performance
4. Mais simples de gerenciar
5. Recomendado pela AWS para este caso
```

---

## 🔐 COMO FUNCIONA CADA UMA

### SIMÉTRICA (Recomendada)

```
Processo:
1. Gera uma chave única (ex: AES-256)
2. Usa a mesma chave para criptografar dados
3. Usa a mesma chave para descriptografar dados
4. Armazena a chave de forma segura no AWS KMS

Exemplo:
Dados originais: "senha123"
Chave: "abc123xyz789..."
Dados criptografados: "x7k9m2p5q8r1..."
Descriptografar com mesma chave: "senha123"
```

### ASSIMÉTRICA

```
Processo:
1. Gera um par de chaves (pública + privada)
2. Usa chave pública para criptografar
3. Usa chave privada para descriptografar
4. Distribui chave pública, guarda privada

Exemplo:
Dados originais: "senha123"
Chave pública: "pub_abc123..."
Dados criptografados: "x7k9m2p5q8r1..."
Chave privada: "priv_xyz789..."
Descriptografar com chave privada: "senha123"
```

---

## 📋 PASSO A PASSO - ESCOLHER SIMÉTRICA

### Opção 1: Se você vê "Simétrica" como opção
```
1. Clique no radio button "Simétrica"
2. Clique "Próximo"
3. Pronto!
```

### Opção 2: Se você vê "Tipo de chave"
```
1. Clique em "Tipo de chave"
2. Selecione "Simétrica"
3. Clique "Próximo"
```

---

## 🔑 CONFIGURAÇÃO RECOMENDADA

### Para seu caso (Prognosticos Brasileirão):

```
Tipo de chave: ✅ SIMÉTRICA
Uso da chave: ✅ Criptografar e descriptografar dados
Algoritmo: AES-256 (padrão AWS)
Armazenamento: AWS KMS (seguro)
```

---

## ⚠️ IMPORTANTE

### Não confunda com:

```
❌ Tipo de chave (Simétrica/Assimétrica)
   ↓
✅ Uso da chave (Criptografia de dados / Assinatura)
   ↓
✅ Algoritmo (AES-256, RSA, etc.)
```

Você está escolhendo o **TIPO** (Simétrica/Assimétrica), não o uso.

---

## 🎯 PRÓXIMO PASSO

### Após escolher Simétrica:

```
1. Clique "Próximo"
2. Você irá para ETAPA 3: Revisar e criar
3. Clique "Criar usuário"
4. Você irá para ETAPA 4: Recuperar credenciais
```

---

## 📊 RESUMO

```
Para Prognosticos Brasileirão:
✅ Tipo de chave: SIMÉTRICA
✅ Razão: Criptografia de dados em repouso
✅ Performance: Excelente
✅ Segurança: Ótima
✅ Complexidade: Baixa
```

---

## 💡 DICAS

### Se tiver dúvida:
```
1. Escolha SIMÉTRICA (padrão recomendado)
2. Você pode mudar depois se necessário
3. Para a maioria dos casos, simétrica é melhor
```

### Quando usar ASSIMÉTRICA:
```
❌ Não é necessário para seu caso
❌ Seria mais complexo
❌ Teria performance pior
```

---

## ✨ CONCLUSÃO

**Escolha: SIMÉTRICA**

Clique em "Próximo" e continue com o processo.

---

**Data:** 30/10/2025
**Status:** ✅ Guia Completo
**Próximo:** Clicar em "Próximo" para ETAPA 3