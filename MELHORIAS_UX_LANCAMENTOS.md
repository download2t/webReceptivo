# Melhorias na UX de Lançamento de Serviços

## Alterações Realizadas

### 1. Modelo de Dados (models.py)

#### Antes:
- `idades_criancas`: CharField - texto separado por vírgulas ("3, 5, 8")
- `tipos_meia_entrada`: TextField - tipos em linhas separadas

#### Depois:
- `idades_criancas`: JSONField - lista de inteiros ([3, 5, 8])
- `tipos_meia_entrada`: ManyToManyField - relação com TipoMeiaEntrada

### 2. Formulário (forms.py)

#### Novos Campos:
- `idades_criancas_json`: Campo oculto para armazenar idades em formato JSON
- Widget `CheckboxSelectMultiple` para seleção de tipos de meia

#### Validações Atualizadas:
- Verifica quantidade de idades == qtd_infantil
- Verifica quantidade de tipos selecionados == qtd_meia

### 3. Template de Formulário (lancamento_form.html)

#### Campos Dinâmicos de Idade:
```javascript
// Gera campos individuais conforme qtd_infantil
Criança 01: [  ]
Criança 02: [  ]
Criança 03: [  ]
```

#### Checkboxes para Tipos de Meia:
- Exibe todos os tipos cadastrados como checkboxes
- Alerta informa quantos tipos devem ser selecionados
- Validação em tempo real

### 4. Template de Detalhamento (lancamento_detail.html)

#### Exibição de Idades:
- Antes: "Idades: 3, 5, 8"
- Depois: Badges individuais: [3 anos] [5 anos] [8 anos]

#### Exibição de Tipos:
- Antes: Texto multilinha
- Depois: Badges coloridos com nome de cada tipo

### 5. JavaScript (Dynamic Fields)

#### Funções Principais:
- `gerarCamposIdades()`: Cria campos dinâmicos baseado em qtd_infantil
- `atualizarIdadesJson()`: Atualiza campo hidden com array JSON
- `toggleTipoMeia()`: Mostra/oculta checkboxes conforme qtd_meia

### 6. Migração de Dados

Comando criado: `migrar_dados_lancamentos`
- Converte dados antigos (string) para novo formato (JSON/ManyToMany)
- Processa todos os lançamentos existentes
- Relatório detalhado de sucesso/erro

## Arquivos Modificados

1. `servicos/models.py`
   - Campos idades_criancas e tipos_meia_entrada
   - Métodos gerar_texto_whatsapp() e clean()

2. `servicos/forms.py`
   - Novo campo hidden idades_criancas_json
   - Widget CheckboxSelectMultiple
   - Validações atualizadas
   - Método save() personalizado

3. `servicos/templates/servicos/lancamento_form.html`
   - JavaScript para campos dinâmicos
   - CSS para novos elementos
   - Estrutura HTML para checkboxes

4. `servicos/templates/servicos/lancamento_detail.html`
   - Exibição de idades como badges
   - Exibição de tipos como badges

5. `servicos/views.py`
   - Removido select_related('tipo_meia_entrada')
   - Adicionado prefetch_related('tipos_meia_entrada')

6. `servicos/management/commands/migrar_dados_lancamentos.py`
   - Comando para migração de dados

## Migration Criada

`0004_remove_lancamentoservico_tipo_meia_entrada_and_more.py`
- Remove campo tipo_meia_entrada (ForeignKey)
- Altera idades_criancas para JSONField
- Remove campo tipos_meia_entrada (TextField)
- Adiciona tipos_meia_entrada (ManyToManyField)

## Como Testar

1. Acesse: http://localhost:8000/servicos/lancamentos/novo/
2. Selecione uma categoria e serviço
3. Informe quantidade infantil (ex: 3)
   - Observe os 3 campos "Criança 01:", "Criança 02:", "Criança 03:"
4. Informe quantidade meia (ex: 2)
   - Observe os checkboxes de tipos
   - Selecione exatamente 2 tipos
5. Salve o lançamento
6. Visualize os detalhes
   - Idades aparecem como badges individuais
   - Tipos aparecem como badges coloridos

## Benefícios

✅ UX muito mais intuitiva
✅ Campos numerados claramente
✅ Validação visual em tempo real
✅ Dados estruturados (JSON/ManyToMany)
✅ Mais fácil para relatórios e análises
✅ Tipos reutilizáveis e padronizados
