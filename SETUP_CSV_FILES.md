# 📋 Guia: Configuração dos Arquivos CSV

## Estrutura de Diretórios Criada

```
data/csv/
├── brasileirao/
│   ├── 2025_matches.csv
│   ├── 2025_teams.csv
│   └── 2025_standings.csv
└── premier_league/
    ├── 2025_matches.csv
    ├── 2025_teams.csv
    └── 2025_standings.csv
```

## ⚠️ AÇÃO NECESSÁRIA: Copiar Arquivos CSV

Você precisa copiar os arquivos da sua pasta Downloads para o projeto.

### Passo 1: Copiar Arquivos do Brasil (Série A)

**Arquivos na pasta Downloads:**
- `C:\Users\wxamb\Downloads\brazil-serie-a-matches-2025-to-2025-stats (3).csv`
- `C:\Users\wxamb\Downloads\brazil-serie-a-teams-2025-to-2025-stats (3).csv`

**Para onde copiar:**
```
Copie brazil-serie-a-matches-2025-to-2025-stats (3).csv
  → Para: data/csv/brasileirao/2025_matches.csv

Copie brazil-serie-a-teams-2025-to-2025-stats (3).csv
  → Para: data/csv/brasileirao/2025_teams.csv
```

### Passo 2: Copiar Arquivos da Premier League

**Arquivos na pasta Downloads:**
- `C:\Users\wxamb\Downloads\england-premier-league-matches-2025-to-2026-stats (1).csv`
- `C:\Users\wxamb\Downloads\england-premier-league-teams-2025-to-2026-stats (1).csv`

**Para onde copiar:**
```
Copie england-premier-league-matches-2025-to-2026-stats (1).csv
  → Para: data/csv/premier_league/2025_matches.csv

Copie england-premier-league-teams-2025-to-2026-stats (1).csv
  → Para: data/csv/premier_league/2025_teams.csv
```

## 🖥️ Como Copiar (Windows)

### Opção 1: Via Explorador de Arquivos
1. Abra a pasta Downloads
2. Copie cada arquivo
3. Cole na pasta correspondente do projeto
4. Renomeie conforme indicado acima

### Opção 2: Via PowerShell (mais rápido)

Abra PowerShell na pasta raiz do projeto e execute:

```powershell
# Brasileirão
Copy-Item "C:\Users\wxamb\Downloads\brazil-serie-a-matches-2025-to-2025-stats (3).csv" -Destination ".\data\csv\brasileirao\2025_matches.csv" -Force
Copy-Item "C:\Users\wxamb\Downloads\brazil-serie-a-teams-2025-to-2025-stats (3).csv" -Destination ".\data\csv\brasileirao\2025_teams.csv" -Force

# Premier League
Copy-Item "C:\Users\wxamb\Downloads\england-premier-league-matches-2025-to-2026-stats (1).csv" -Destination ".\data\csv\premier_league\2025_matches.csv" -Force
Copy-Item "C:\Users\wxamb\Downloads\england-premier-league-teams-2025-to-2026-stats (1).csv" -Destination ".\data\csv\premier_league\2025_teams.csv" -Force
```

## ✅ Verificação

Após copiar, os arquivos devem estar em:
- `data/csv/brasileirao/2025_matches.csv` ✓
- `data/csv/brasileirao/2025_teams.csv` ✓
- `data/csv/premier_league/2025_matches.csv` ✓
- `data/csv/premier_league/2025_teams.csv` ✓

## 📝 Nota sobre Standings

O arquivo `2025_standings.csv` será gerado automaticamente pelo sistema baseado nos resultados dos jogos, ou você pode criá-lo manualmente se necessário.

## ❓ Precisa de Ajuda?

Se os arquivos CSV tiverem formato diferente do esperado pelo sistema, me avise e podemos ajustar o código para ler corretamente.
