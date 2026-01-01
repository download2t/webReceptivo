# Changelog - Sistema de Faixas Etárias e Precificação

## Data: 2024
## Versão: 2.0

---

## 📋 Resumo das Mudanças

Implementação completa de sistema de faixas etárias para categoria infantil, incluindo validação de idades de 0 a 17 anos e lógica de precificação em três níveis (GRÁTIS, INFANTIL, INTEIRA).

---

## 🗄️ Mudanças no Banco de Dados

### Migration 0007: adicionar_idades_infantil

**Novos campos em SubCategoria:**

1. **permite_infantil** (BooleanField)
   - Controla se o serviço possui categoria infantil
   - Default: False
   - Quando True: mostra campos de idade infantil no formulário

2. **idade_minima_infantil** (PositiveIntegerField)
   - Idade mínima para categoria infantil
   - Default: 0
   - Validators: MaxValueValidator(17)
   - Range: 0-17 anos

3. **idade_maxima_infantil** (PositiveIntegerField)
   - Idade máxima para categoria infantil
   - Default: 17
   - Validators: MaxValueValidator(17)
   - Range: 0-17 anos

4. **possui_isencao** (BooleanField)
   - Controla se o serviço possui isenção por idade
   - Default: False
   - Quando True: mostra campos de isenção no formulário

**Campos atualizados:**

- **idade_isencao_min**: Adicionado MaxValueValidator(17)
- **idade_isencao_max**: Adicionado MaxValueValidator(17)
- **idade_minima**: Adicionado MaxValueValidator(17)

---

## 🎯 Lógica de Precificação (3 Níveis)

### Nível 1: GRÁTIS (R$ 0,00) - Prioridade MÁXIMA
**Condição:** Criança dentro da faixa de isenção

**Critérios:**
- `possui_isencao = True`
- `idade_isencao_min <= idade <= idade_isencao_max`

**Exemplo:**
- Serviço isenta 0-6 anos
- Criança de 3 anos → **R$ 0,00**

**Identificação Visual:** Borda verde com fundo verde claro

---

### Nível 2: VALOR INFANTIL - Prioridade MÉDIA
**Condição:** Criança fora da isenção + dentro da faixa infantil + serviço permite infantil e aceita meia

**Critérios:**
- NÃO está na faixa de isenção
- `permite_infantil = True`
- `aceita_meia_entrada = True`
- `idade_minima_infantil <= idade <= idade_maxima_infantil`

**Exemplo:**
- Serviço isenta 0-6 anos
- Serviço permite infantil 7-12 anos
- Serviço aceita meia entrada
- Criança de 8 anos → **VALOR INFANTIL**

**Identificação Visual:** Borda azul com fundo azul claro

---

### Nível 3: VALOR INTEIRA - Prioridade BAIXA
**Condição:** Qualquer outra situação

**Critérios (qualquer um):**
- NÃO está na faixa de isenção E
- Está fora da faixa infantil OU
- Serviço não permite infantil (`permite_infantil = False`) OU
- Serviço não aceita meia (`aceita_meia_entrada = False`)

**Exemplos:**
- Criança de 14 anos (fora da faixa infantil 7-12) → **VALOR INTEIRA**
- Criança de 8 anos em serviço que não aceita meia → **VALOR INTEIRA**
- Criança de 8 anos em serviço que não permite infantil → **VALOR INTEIRA**

**Identificação Visual:** Borda amarela

---

## 📝 Mudanças no Código

### 1. Models (servicos/models.py)

#### SubCategoria
- Adicionados campos: `permite_infantil`, `idade_minima_infantil`, `idade_maxima_infantil`, `possui_isencao`
- Adicionado `MaxValueValidator(17)` a todos os campos de idade
- Importado `MaxValueValidator` de `django.core.validators`

#### LancamentoServico

**Propriedade `qtd_infantil_pagam_inteira`:**
```python
def qtd_infantil_pagam_inteira(self):
    """
    Retorna quantas crianças pagam valor de inteira.
    Considera:
    1. Não estão isentas E
    2. Estão fora da faixa infantil OU serviço não permite infantil OU não aceita meia
    """
```

**Propriedade `qtd_infantil_pagam_infantil`:**
```python
def qtd_infantil_pagam_infantil(self):
    """
    Retorna quantas crianças pagam valor infantil.
    Considera:
    1. Não estão isentas E
    2. Estão dentro da faixa infantil E
    3. Serviço permite infantil E aceita meia
    """
```

**Propriedade `valor_total`:**
```python
def valor_total(self):
    """
    Calcula total considerando 3 níveis:
    - ISENTAS (R$ 0,00)
    - INFANTIL (valor_unit_infantil)
    - INTEIRA (valor_unit_inteira)
    """
```

---

### 2. Forms (servicos/forms.py)

**SubCategoriaForm:**
- Adicionados campos: `idade_minima_infantil`, `idade_maxima_infantil`
- Widgets com `min='0'` e `max='17'` em todos os campos de idade

---

### 3. Views (servicos/views.py)

**ajax_get_subcategoria_valores:**
- Adicionado ao JSON de resposta:
  - `permite_infantil`
  - `idade_minima_infantil`
  - `idade_maxima_infantil`
  - `possui_isencao`

---

### 4. Templates

#### subcategoria_form.html
**Estrutura Reorganizada em 7 Seções:**

1. **Informações Básicas** (sempre visível)
   - Categoria, nome, descrição

2. **Valor Inteira** (sempre visível)
   - valor_inteira

3. **Meia Entrada** (condicional: `aceita_meia_entrada`)
   - valor_meia, regras_meia_entrada

4. **Infantil** (condicional: `permite_infantil`)
   - valor_infantil
   - idade_minima_infantil (0-17)
   - idade_maxima_infantil (0-17)

5. **Isenção** (condicional: `possui_isencao`)
   - idade_isencao_min (0-17)
   - idade_isencao_max (0-17)
   - texto_isencao

6. **Idade Mínima Required** (condicional: `tem_idade_minima`)
   - idade_minima (0-17)

7. **Status** (sempre visível)
   - ativo

**JavaScript:**
- `toggleMeiaEntrada()`: mostra/oculta seção meia entrada
- `toggleInfantil()`: mostra/oculta seção infantil
- `toggleIsencao()`: mostra/oculta seção isenção
- `toggleIdadeMinima()`: mostra/oculta campo idade mínima
- Auto-limpa campos quando flag é desmarcada

---

#### lancamento_form.html

**JavaScript - Função `verificarIsencao(input)`:**
```javascript
// Verifica 3 estados (ordem de prioridade):
// 1. Isenção (borda verde + fundo verde)
// 2. Infantil (borda azul + fundo azul)
// 3. Inteira (borda amarela)
```

**JavaScript - Função `contarCriancasPorCategoria()`:**
```javascript
// Retorna objeto:
// { infantil: X, inteira: Y, isenta: Z }
// Onde X + Y + Z = total de crianças
```

**JavaScript - Função `calcularTotal()`:**
```javascript
// Calcula subtotalInfantil considerando:
// - qtdPagamInfantil * valorInfantil
// - qtdPagamInteira * valorInteira
// Mostra detalhamento: "5 (3 pagas: 2 infantil, 1 inteira)"
```

**AJAX - Carregamento de Subcategorias:**
```javascript
// Agora inclui no dataset da option:
option.dataset.permiteInfantil = subcategoria.permite_infantil
option.dataset.idadeMinimaInfantil = subcategoria.idade_minima_infantil
option.dataset.idadeMaximaInfantil = subcategoria.idade_maxima_infantil
option.dataset.possuiIsencao = subcategoria.possui_isencao
```

**Modal de Ajuda - Seção 3:**
- Atualizado para incluir identificação visual de borda azul (infantil)

**Modal de Ajuda - Seção 5:**
- Completamente reescrito explicando os 3 níveis de precificação
- Incluída ordem de verificação (prioridade)
- Exemplos práticos de cada caso

---

### 5. Management Commands

**adicionar_servicos_faltantes.py:**
```python
SubCategoria.objects.create(
    ...
    permite_infantil=True,
    idade_minima_infantil=0,
    idade_maxima_infantil=17,
    possui_isencao=(idade_isencao_max > 0),
    ...
)
```

---

## ✅ Validações Implementadas

### Backend (Django)

1. **MaxValueValidator(17)** em todos os campos de idade:
   - idade_minima_infantil
   - idade_maxima_infantil
   - idade_isencao_min
   - idade_isencao_max
   - idade_minima

2. **PositiveIntegerField** impede valores negativos automaticamente

3. **Validação em LancamentoServico.clean():**
   - Valida todas as idades ≤ 17
   - Valida idade mínima do serviço se `tem_idade_minima = True`

### Frontend (JavaScript)

1. **HTML `min='0'` e `max='17'`** em todos os inputs de idade

2. **Validação visual em tempo real:**
   - Verde: Isento
   - Azul: Infantil
   - Amarelo: Inteira
   - Vermelho: Abaixo da idade mínima

3. **Cálculo automático** de totais considerando 3 níveis de preço

---

## 🎨 Identificação Visual

| Cor | Status | Significado | Valor |
|-----|--------|-------------|-------|
| 🟢 Verde | Isento | Dentro da faixa de isenção | R$ 0,00 |
| 🔵 Azul | Infantil | Dentro da faixa infantil | valor_infantil |
| 🟡 Amarelo | Inteira | Fora das faixas ou serviço não permite | valor_inteira |
| 🔴 Vermelho | Erro | Abaixo da idade mínima | ❌ Bloqueado |

---

## 📊 Fluxo de Decisão de Preço

```
CRIANÇA DE X ANOS
        ↓
┌───────────────────────────────┐
│ Está na faixa de isenção?     │
│ (possui_isencao = true)       │
└───────────┬───────────────────┘
            │
    ┌───────┴────────┐
    │ SIM            │ NÃO
    ↓                ↓
 R$ 0,00   ┌────────────────────────────┐
           │ Está na faixa infantil?    │
           │ (permite_infantil = true   │
           │  AND aceita_meia = true)   │
           └─────────┬──────────────────┘
                     │
             ┌───────┴────────┐
             │ SIM            │ NÃO
             ↓                ↓
        VALOR INFANTIL   VALOR INTEIRA
```

---

## 🚀 Como Usar

### 1. Cadastro de Serviço (Admin)

1. Preencher **Informações Básicas**
2. Definir **Valor Inteira** (obrigatório)
3. Marcar **"Aceita Meia Entrada"** se aplicável
   - Preencher valor_meia e regras
4. Marcar **"Permite Infantil"** se aplicável
   - Definir faixa etária (ex: 7-12 anos)
   - Preencher valor_infantil
5. Marcar **"Possui Isenção"** se aplicável
   - Definir faixa etária (ex: 0-6 anos)
   - Informar texto explicativo
6. Marcar **"Tem Idade Mínima"** se aplicável
   - Definir idade mínima (ex: 6 anos)

### 2. Lançamento de Serviço (Booking)

1. Selecionar categoria e serviço
2. Informar quantidades:
   - Inteira
   - Meia (se serviço aceitar)
   - Infantil
3. Preencher idades das crianças individualmente
4. Observar feedback visual:
   - Verde = grátis
   - Azul = infantil
   - Amarelo = inteira
   - Vermelho = não permitido
5. Conferir resumo do cálculo
6. Salvar

---

## 📌 Notas Importantes

1. **Ordem de Prioridade:** Isenção > Infantil > Inteira
2. **Idade Máxima Universal:** 17 anos para todos os campos
3. **Flags Condicionais:** Campos só aparecem se flags estiverem ativas
4. **Auto-cálculo:** Sistema calcula automaticamente categoria de cada criança
5. **Validação Dupla:** Frontend (UX) + Backend (segurança)

---

## 🐛 Correções de Bugs

1. **Sintaxe Error:** Corrigido campo `idade_minima` duplicado/malformado
2. **Import Missing:** Adicionado `MaxValueValidator` aos imports
3. **Dataset AJAX:** Incluídos novos campos na resposta AJAX
4. **Cálculo de Total:** Atualizado para considerar 3 níveis de preço

---

## ✨ Melhorias de UX

1. **Formulário Reorganizado:** 7 seções lógicas e condicionais
2. **Feedback Visual:** 4 cores diferentes para diferentes estados
3. **Tooltips Informativos:** Cada campo de idade mostra sua categoria ao passar o mouse
4. **Modal de Ajuda Completo:** 8 seções explicando todas as regras
5. **Detalhamento no Resumo:** Mostra quantas crianças em cada categoria

---

## 🔄 Compatibilidade

- ✅ Django 5.2.7
- ✅ PostgreSQL
- ✅ Bootstrap 5
- ✅ JavaScript ES6+

---

## 📚 Referências

- **Migration:** `servicos/migrations/0007_adicionar_idades_infantil.py`
- **Models:** `servicos/models.py` (linhas 80-135, 280-395)
- **Forms:** `servicos/forms.py` (linhas 15-60)
- **Views:** `servicos/views.py` (função ajax_get_subcategoria_valores)
- **Templates:** 
  - `servicos/templates/servicos/subcategoria_form.html`
  - `servicos/templates/servicos/lancamento_form.html`

---

**Desenvolvido por:** GitHub Copilot
**Data da Implementação:** Janeiro 2024
**Status:** ✅ Completo e Testado
