# App Serviços Turísticos

Sistema completo para gerenciamento de lançamento de serviços turísticos.

## 🎯 Funcionalidades

### 1. **Categorias de Serviços**
- CRUD completo de categorias (Atrativos, Hospedagem, Alimentação, Transporte, etc.)
- Ordenação customizável
- Status ativo/inativo

### 2. **Serviços (Subcategorias)**
- Cadastro de serviços turísticos
- Três tipos de valores: Inteira, Meia e Infantil
- Vinculação com categorias
- Filtros e busca

### 3. **Tipos de Meia Entrada**
- Cadastro de justificativas para meia entrada
- Exemplos: Estudante, Idoso, PCD, Professor

### 4. **Lançamentos de Serviços**
- Registro de vendas/reservas de serviços
- Captura automática de valores (snapshot)
- Cálculo automático de totais
- Validações inteligentes:
  - Se `qtd_meia > 0`, tipo de meia entrada é obrigatório
  - Subcategoria deve pertencer à categoria selecionada
- Observações públicas e privadas

### 5. **Gerador de Texto WhatsApp**
- Geração automática de mensagem de confirmação
- Formatação profissional com emojis
- Botão copiar para área de transferência
- Inclui: data, serviço, quantidades, valores e total

## 📊 Estrutura de Dados

### Models

#### Categoria
```python
- nome: CharField (único)
- ativo: BooleanField
- ordem: IntegerField (para ordenação)
```

#### SubCategoria (Serviço)
```python
- categoria: ForeignKey(Categoria)
- nome: CharField
- descricao: TextField
- valor_inteira: DecimalField
- valor_meia: DecimalField
- valor_infantil: DecimalField
- ativo: BooleanField
```

#### TipoMeiaEntrada
```python
- nome: CharField (único)
- descricao: TextField
- ativo: BooleanField
```

#### LancamentoServico
```python
- data_servico: DateField
- categoria: ForeignKey(Categoria)
- subcategoria: ForeignKey(SubCategoria)
- qtd_inteira: IntegerField
- qtd_meia: IntegerField
- qtd_infantil: IntegerField
- tipo_meia_entrada: ForeignKey(TipoMeiaEntrada, optional)
- valor_unitario_inteira: DecimalField (snapshot)
- valor_unitario_meia: DecimalField (snapshot)
- valor_unitario_infantil: DecimalField (snapshot)
- obs_publica: TextField
- obs_privada: TextField
- criado_por: ForeignKey(User)

# Properties
- total_pax: int (soma de todas as quantidades)
- valor_total: Decimal (cálculo do valor total)

# Methods
- gerar_texto_whatsapp(): str (gera texto formatado)
```

## 🚀 Como Usar

### 1. Configuração Inicial

O app já está instalado e configurado. Para popular dados de exemplo:

```bash
python manage.py popular_servicos
```

Isso criará:
- 4 tipos de meia entrada
- 5 categorias
- 10 serviços de exemplo

### 2. Acessar o Sistema

```
URLs principais:
- /servicos/ - Lista de lançamentos
- /servicos/lancamentos/criar/ - Novo lançamento
- /servicos/categorias/ - Gerenciar categorias
- /servicos/servicos/ - Gerenciar serviços
- /servicos/tipos-meia/ - Gerenciar tipos de meia entrada
```

### 3. Fluxo de Uso Recomendado

1. **Configure Categorias** (`/servicos/categorias/`)
   - Ex: Atrativos Turísticos, Hospedagem, Alimentação

2. **Cadastre Serviços** (`/servicos/servicos/`)
   - Vincule à categoria
   - Defina os valores (inteira, meia, infantil)

3. **Configure Tipos de Meia** (`/servicos/tipos-meia/`)
   - Ex: Estudante, Idoso, PCD

4. **Crie Lançamentos** (`/servicos/lancamentos/criar/`)
   - Selecione categoria (carrega serviços automaticamente)
   - Escolha o serviço (mostra valores)
   - Informe quantidades
   - Se houver meia entrada, selecione o tipo

## ✨ Recursos Avançados

### Formulário Dinâmico

O formulário de lançamento possui recursos AJAX:

- **Filtro de Serviços**: Ao selecionar uma categoria, apenas os serviços daquela categoria aparecem
- **Preview de Valores**: Ao selecionar um serviço, os valores são exibidos para conferência
- **Validação Dinâmica**: Campo "Tipo de Meia Entrada" aparece automaticamente quando qtd_meia > 0

### Snapshot de Valores

Quando um lançamento é criado, os valores unitários do serviço são **capturados e salvos** no lançamento. Isso garante que:

- Alterações futuras nos preços não afetam lançamentos antigos
- Histórico de preços é mantido
- Relatórios financeiros são precisos

### Texto WhatsApp

Exemplo de saída gerada:

```
✅ CONFIRMAÇÃO DE SERVIÇO

📅 Data: 15/01/2024
🎫 Serviço: Cristo Redentor

👥 Passageiros:
• 2 Inteira(s) - R$ 120,00 cada
• 1 Meia(s) - Estudante - R$ 60,00 cada
• 1 Infantil(is) - R$ 40,00 cada

💰 TOTAL: R$ 340,00
👤 Total de PAX: 4

📝 Observações:
Encontro às 8h no hotel
```

## 🔒 Segurança

- Todas as views possuem `@login_required`
- Validações no backend (não apenas frontend)
- Sanitização de inputs
- Auditoria: criado_por, criado_em, atualizado_em

## 📱 Responsividade

Todos os templates são responsivos (Bootstrap 5) e funcionam em:
- Desktop
- Tablet
- Mobile

## 🛠️ Manutenção

### Adicionar Nova Categoria

```python
from servicos.models import Categoria

categoria = Categoria.objects.create(
    nome="Nova Categoria",
    ordem=10,
    ativo=True
)
```

### Adicionar Novo Serviço

```python
from servicos.models import SubCategoria, Categoria

categoria = Categoria.objects.get(nome="Atrativos Turísticos")
servico = SubCategoria.objects.create(
    categoria=categoria,
    nome="Museu do Amanhã",
    descricao="Ingresso para o Museu do Amanhã",
    valor_inteira=40.00,
    valor_meia=20.00,
    valor_infantil=10.00,
    ativo=True
)
```

## 📈 Relatórios e Estatísticas

A tela de lançamentos mostra:
- Total de lançamentos (com filtros aplicados)
- Total de PAX
- Filtros por: data inicial, data final, categoria, busca textual

## 🐛 Troubleshooting

### Subcategorias não aparecem no formulário

Verifique se:
1. A categoria tem subcategorias ativas
2. JavaScript está habilitado
3. Console do navegador não mostra erros

### Valores não são salvos corretamente

O modelo sobrescreve o método `save()` para capturar os valores. Certifique-se de:
1. A subcategoria existe
2. Os valores estão preenchidos na subcategoria

### Erro ao deletar categoria

Se a categoria tem serviços vinculados, eles também serão deletados (CASCADE).

## 🎨 Customização

### Alterar cores do texto WhatsApp

Edite o método `gerar_texto_whatsapp()` em `servicos/models.py`

### Adicionar campos

1. Adicione campo no Model
2. Execute `makemigrations` e `migrate`
3. Adicione campo no Form
4. Atualize template

## 📝 Licença

Este app faz parte do sistema WebReceptivo.
