# 🔐 GUIA COMPLETO - CRIAR USUÁRIO IAM NA AWS

## 📋 O QUE VOCÊ ESTÁ FAZENDO

Você está na **Etapa 1 de 4** do processo de criação de usuário IAM na AWS.

A tela mostra: **"Especificar detalhes do usuário"**

---

## ✅ PASSO A PASSO - CRIAR USUÁRIO IAM

### ETAPA 1: ESPECIFICAR DETALHES DO USUÁRIO (VOCÊ ESTÁ AQUI)

#### Campo 1: Nome do Usuário
```
✅ Já preenchido: "wmarquinho"
✅ Está correto!
```

#### Campo 2: Fornecer acesso para os usuários ao Console de Gerenciamento da AWS
```
✅ Checkbox marcado: SIM
✅ Isso permite que o usuário acesse a console AWS
✅ Recomendado para administradores
```

#### Campo 3: Senha da Console
```
Opção selecionada: "Senha gerada automaticamente"
✅ Recomendado - AWS gera senha forte automaticamente
```

#### Campo 4: Os usuários devem criar uma nova senha na próxima sessão
```
✅ Checkbox marcado: SIM
✅ Recomendado por segurança
✅ Força o usuário a criar sua própria senha
```

---

## 🎯 O QUE FAZER AGORA

### Passo 1: Revisar as Configurações
```
✅ Nome do usuário: wmarquinho
✅ Acesso à console: Ativado
✅ Senha: Gerada automaticamente
✅ Criar nova senha: Obrigatório
```

### Passo 2: Clicar em "Próximo"
```
1. Clique no botão laranja "Próximo" no canto inferior direito
2. Você irá para a ETAPA 2: Definir permissões
```

---

## 📊 PRÓXIMAS ETAPAS (2, 3, 4)

### ETAPA 2: DEFINIR PERMISSÕES
```
O que você fará:
- Adicionar permissões ao usuário
- Opções:
  1. Adicionar usuário a um grupo
  2. Copiar permissões de outro usuário
  3. Anexar políticas diretamente

Recomendação para você:
- Selecione "Anexar políticas diretamente"
- Procure por: "AdministratorAccess"
- Isso dá acesso total (necessário para criar infraestrutura)
```

### ETAPA 3: REVISAR E CRIAR
```
O que você fará:
- Revisar todas as configurações
- Clicar em "Criar usuário"
```

### ETAPA 4: RECUPERAR CREDENCIAIS
```
O que você fará:
- Copiar a senha gerada
- Salvar em local seguro
- Fazer download do arquivo CSV com credenciais
- Guardar a chave de acesso (Access Key ID)
- Guardar a chave secreta (Secret Access Key)
```

---

## 🔑 CREDENCIAIS QUE VOCÊ RECEBERÁ

Após criar o usuário, você receberá:

```
1. Nome do usuário: wmarquinho
2. Senha da console: [gerada automaticamente]
3. Access Key ID: AKIA...
4. Secret Access Key: [chave secreta]
5. URL de login: https://[seu-id-conta].signin.aws.amazon.com/console
```

**⚠️ IMPORTANTE:**
- Salve essas credenciais em local seguro
- Não compartilhe com ninguém
- Você precisará delas para:
  - Fazer login na console AWS
  - Configurar AWS CLI
  - Criar infraestrutura

---

## 📝 INSTRUÇÕES DETALHADAS - ETAPA 1

### O que você vê na tela:

1. **Nome do usuário: wmarquinho**
   - ✅ Já preenchido
   - ✅ Válido (até 64 caracteres)
   - ✅ Pode conter: A-Z, a-z, 0-9, e alguns símbolos

2. **Fornecer acesso para os usuários ao Console de Gerenciamento da AWS**
   - ✅ Checkbox marcado
   - ✅ Permite login na console
   - ✅ Necessário para gerenciar infraestrutura

3. **Senha da Console**
   - ✅ "Senha gerada automaticamente" selecionado
   - ✅ AWS gera senha forte
   - ✅ Você pode copiar depois

4. **Os usuários devem criar uma nova senha na próxima sessão**
   - ✅ Checkbox marcado
   - ✅ Força mudança de senha no primeiro login
   - ✅ Aumenta segurança

---

## ✅ CHECKLIST ANTES DE CLICAR "PRÓXIMO"

- [x] Nome do usuário preenchido: wmarquinho
- [x] Acesso à console ativado
- [x] Senha gerada automaticamente
- [x] Obrigar criar nova senha marcado
- [ ] Pronto para clicar "Próximo"

---

## 🎯 PRÓXIMO PASSO

### Clique em "Próximo" (botão laranja)

Você irá para:
**ETAPA 2: Definir permissões**

Lá você vai:
1. Selecionar "Anexar políticas diretamente"
2. Procurar por "AdministratorAccess"
3. Marcar o checkbox
4. Clicar "Próximo" novamente

---

## 📋 RESUMO DO PROCESSO

```
ETAPA 1: Especificar detalhes ← VOCÊ ESTÁ AQUI
   ↓
ETAPA 2: Definir permissões
   ↓
ETAPA 3: Revisar e criar
   ↓
ETAPA 4: Recuperar credenciais
   ↓
✅ Usuário IAM criado com sucesso!
```

---

## 🔐 SEGURANÇA

### Boas Práticas:
1. ✅ Use senha forte
2. ✅ Ative MFA (Multi-Factor Authentication)
3. ✅ Guarde credenciais em local seguro
4. ✅ Não compartilhe chaves de acesso
5. ✅ Revise permissões regularmente

### Após criar o usuário:
1. Faça login com as credenciais
2. Vá para "Security credentials"
3. Ative MFA (Google Authenticator ou Authy)
4. Crie chaves de acesso para AWS CLI

---

## 💡 DICAS

### Se cometer erro:
- Você pode voltar clicando em "Cancelar"
- Ou clicar na seta "Voltar" para editar

### Depois de criar:
- Você pode editar permissões depois
- Você pode resetar a senha
- Você pode desativar o usuário

---

## 📞 PRÓXIMOS PASSOS APÓS CRIAR O USUÁRIO

1. **Fazer login com o novo usuário**
   - URL: https://[seu-id-conta].signin.aws.amazon.com/console
   - Usuário: wmarquinho
   - Senha: [a que foi gerada]

2. **Criar chaves de acesso para AWS CLI**
   - Ir para "Security credentials"
   - Clicar em "Create access key"
   - Salvar Access Key ID e Secret Access Key

3. **Configurar AWS CLI**
   ```bash
   aws configure
   # Inserir:
   # AWS Access Key ID: [sua-access-key]
   # AWS Secret Access Key: [sua-secret-key]
   # Default region: us-east-1
   # Default output format: json
   ```

4. **Criar infraestrutura AWS**
   - VPC
   - Security Groups
   - EC2
   - RDS
   - ElastiCache

---

## ✨ CONCLUSÃO

Você está no caminho certo! 

**Próximo passo:** Clique em "Próximo" para ir para a ETAPA 2.

---

**Data:** 29/10/2025
**Status:** ✅ Guia Completo
**Próximo:** ETAPA 2 - Definir Permissões