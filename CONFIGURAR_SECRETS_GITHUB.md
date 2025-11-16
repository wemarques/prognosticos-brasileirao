# 🔐 Guia: Configurar Secrets no GitHub

## 📋 O que você precisa:

- [ ] Acesso ao repositório no GitHub
- [ ] IP público da sua EC2
- [ ] Arquivo `.pem` da sua chave SSH
- [ ] Sua ODDS_API_KEY

---

## 🎯 Passo a Passo

### **Passo 1: Acessar Configurações do Repositório**

1. Abra o navegador e vá para:
   ```
   https://github.com/wemarques/prognosticos-brasileirao
   ```

2. Clique na aba **"Settings"** (⚙️ Configurações)
   - Está no topo da página, ao lado de "Insights"

3. No menu lateral esquerdo, procure a seção **"Security"**

4. Clique em **"Secrets and variables"** → **"Actions"**

---

### **Passo 2: Adicionar Secret EC2_HOST**

1. Clique no botão verde **"New repository secret"**

2. Preencha:
   - **Name**: `EC2_HOST`
   - **Secret**: `SEU-IP-PUBLICO-DA-EC2`

   **Exemplo:**
   ```
   52.12.34.56
   ```

   ⚠️ **IMPORTANTE**:
   - Apenas o IP, sem `http://`
   - Sem porta `:8501`
   - Apenas números e pontos

3. Clique em **"Add secret"**

✅ **Secret EC2_HOST adicionado!**

---

### **Passo 3: Adicionar Secret EC2_SSH_KEY**

Este é o mais importante! A chave SSH completa.

#### 3.1 Copiar conteúdo do arquivo .pem

**No Windows (Git Bash):**

```bash
# Navegar até onde está o arquivo
cd ~/Downloads

# Exibir conteúdo (você vai copiar isso)
cat prognosticos-aws.pem
```

**O conteúdo deve começar assim:**
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
... (várias linhas)
...
-----END RSA PRIVATE KEY-----
```

**Copie TUDO** (incluindo as linhas BEGIN e END)

#### 3.2 Adicionar no GitHub

1. Clique em **"New repository secret"** novamente

2. Preencha:
   - **Name**: `EC2_SSH_KEY`
   - **Secret**: [Cole TODO o conteúdo do arquivo .pem]

3. Clique em **"Add secret"**

✅ **Secret EC2_SSH_KEY adicionado!**

---

### **Passo 4: Adicionar Secret ODDS_API_KEY (Opcional)**

Se você quiser que a ODDS_API_KEY seja gerenciada pelo GitHub:

1. Clique em **"New repository secret"**

2. Preencha:
   - **Name**: `ODDS_API_KEY`
   - **Secret**: `652ee755d767058ec48c4994326eaa3d`

3. Clique em **"Add secret"**

✅ **Secret ODDS_API_KEY adicionado!**

---

## ✅ Verificação Final

Você deve ter 3 secrets configurados:

1. ✅ **EC2_HOST** - IP da sua EC2
2. ✅ **EC2_SSH_KEY** - Chave privada SSH
3. ✅ **ODDS_API_KEY** - API key (opcional)

Para verificar:
- Vá em Settings → Secrets and variables → Actions
- Você deve ver os 3 secrets listados
- ⚠️ Os valores ficam ocultos (você não pode ver depois de adicionar)

---

## 🧪 Testar Configuração

### Opção 1: Fazer um Commit de Teste

```bash
# No seu computador (Git Bash):
cd ~/prognosticos-brasileirao

# Criar arquivo de teste
echo "# Deploy test" >> test-deploy.txt

# Commit e push
git add test-deploy.txt
git commit -m "test: Testing GitHub Actions deploy"
git push origin claude/frontend-review-improvements-01SLDqfrpQJaeBCaHmyLkkcU
```

### Opção 2: Executar Workflow Manualmente

1. Vá para: `https://github.com/wemarques/prognosticos-brasileirao/actions`

2. Clique em **"Deploy to AWS EC2"** (no menu lateral)

3. Clique em **"Run workflow"** (botão azul à direita)

4. Selecione a branch: `claude/frontend-review-improvements-01SLDqfrpQJaeBCaHmyLkkcU`

5. Clique em **"Run workflow"**

---

## 📊 Acompanhar Execução

1. Vá para: `https://github.com/wemarques/prognosticos-brasileirao/actions`

2. Você verá o workflow em execução (bolinha amarela 🟡)

3. Clique no workflow para ver detalhes

4. Clique em "deploy" para ver os logs em tempo real

**Status possíveis:**
- 🟡 **Em execução**: Deploy acontecendo agora
- ✅ **Sucesso**: Deploy completado!
- ❌ **Falhou**: Algo deu errado (veja os logs)

---

## 🐛 Solução de Problemas

### ❌ Erro: "Permission denied (publickey)"

**Problema**: Secret EC2_SSH_KEY incorreto

**Solução:**
1. Verifique que copiou o arquivo .pem COMPLETO
2. Deve incluir `-----BEGIN RSA PRIVATE KEY-----` e `-----END RSA PRIVATE KEY-----`
3. Sem espaços extras no início ou fim
4. Re-adicione o secret se necessário

### ❌ Erro: "Connection timed out"

**Problema**: EC2_HOST incorreto ou EC2 desligada

**Solução:**
1. Verifique o IP no AWS Console → EC2 → Instances
2. Confirme que a instância está "running" (verde)
3. Atualize o secret EC2_HOST se o IP mudou

### ❌ Erro: "Health check failed"

**Problema**: Aplicação não está respondendo

**Solução:**
```bash
# SSH na EC2
ssh -i ~/Downloads/prognosticos-aws.pem ubuntu@SEU-IP

# Ver logs
cd prognosticos-brasileirao
docker-compose logs app

# Reiniciar se necessário
docker-compose restart app
```

---

## 📝 Comandos Úteis

### Ver secrets configurados (sem os valores)
```bash
gh secret list
```

### Atualizar um secret via CLI
```bash
# Instalar GitHub CLI primeiro: https://cli.github.com/

# Atualizar EC2_HOST
gh secret set EC2_HOST -b "52.12.34.56"

# Atualizar EC2_SSH_KEY (do arquivo)
gh secret set EC2_SSH_KEY < ~/Downloads/prognosticos-aws.pem
```

---

## 🔐 Segurança

✅ **Boas práticas:**
- Secrets são criptografados pelo GitHub
- Nunca aparecem nos logs
- Só acessíveis pelos workflows
- Não são expostos em pull requests de forks

⚠️ **Importante:**
- Não compartilhe seus secrets
- Não commite o arquivo .pem no Git
- Não coloque secrets em arquivos de código
- Troque as chaves se suspeitar de vazamento

---

## ✨ Próximos Passos

Após configurar os secrets:

1. ✅ Fazer um commit de teste
2. ✅ Acompanhar deploy no GitHub Actions
3. ✅ Verificar aplicação na EC2
4. ✅ Partir para produção! 🚀

---

## 📞 Suporte

**Documentação GitHub Actions:**
- https://docs.github.com/en/actions/security-guides/encrypted-secrets

**Precisa de ajuda?**
- Abra uma issue no repositório
- Verifique os logs do workflow
- Consulte DEPLOY_AUTOMATICO.md

---

**Criado:** 2025-11-16
**Status:** ✅ Guia Completo
