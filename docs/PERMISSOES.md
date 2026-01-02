# 🔐 Sistema de Permissões - WebReceptivo

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Grupos Padrão](#grupos-padrão)
3. [Como Configurar](#como-configurar)
4. [Permissões Disponíveis](#permissões-disponíveis)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O WebReceptivo implementa um sistema completo de permissões baseado no sistema nativo do Django, permitindo controle granular de acesso a todas as funcionalidades.

### Hierarquia de Permissões

```
1️⃣ SUPERUSUÁRIO (is_superuser=True)
   └─ Acesso TOTAL a tudo, sem restrições

2️⃣ PERMISSÕES INDIVIDUAIS
   └─ Atribuídas diretamente ao usuário
   └─ SOBRESCREVEM permissões do grupo

3️⃣ PERMISSÕES DO GRUPO
   └─ Aplicadas quando usuário não tem permissão individual
   └─ Usuário pode estar em múltiplos grupos
```

### Tipos de Permissão (CRUD)

Para cada modelo do sistema, existem 4 tipos de permissão:

| Permissão | Ação | Exemplo |
|-----------|------|---------|
| `view_*` | Visualizar/Listar | Ver lista de categorias |
| `add_*` | Criar/Adicionar | Criar nova categoria |
| `change_*` | Editar/Atualizar | Editar categoria existente |
| `delete_*` | Deletar/Remover | Excluir categoria |

---

## Grupos Padrão

### 👨‍💼 Operador
**Perfil:** Atendimento ao cliente, criação de ordens de serviço

**Permissões:**
- ✅ Visualizar cadastros (Categorias, Serviços, Transfers, Meia Entrada)
- ✅ Visualizar Ordens de Serviço
- ✅ Criar novas Ordens de Serviço
- ❌ Editar ou deletar ordens
- ❌ Modificar cadastros base

**Casos de Uso:**
- Atendente de receptivo criando roteiros para clientes
- Operador de reservas consultando serviços disponíveis

---

### 👨‍💼 Coordenador
**Perfil:** Supervisão de operações, controle total de ordens

**Permissões:**
- ✅ TUDO do Operador +
- ✅ Editar Ordens de Serviço
- ✅ Deletar Ordens de Serviço
- ❌ Modificar cadastros base

**Casos de Uso:**
- Supervisor ajustando ordens criadas pela equipe
- Coordenador corrigindo valores ou removendo ordens incorretas

---

### 👨‍💼 Gestor de Cadastros
**Perfil:** Responsável por manter cadastros atualizados

**Permissões:**
- ✅ CRUD completo em:
  - Categorias
  - Serviços (Subcategorias)
  - Transfers
  - Tipos de Meia Entrada
- ✅ Visualizar Ordens de Serviço
- ❌ Criar/Editar/Deletar ordens

**Casos de Uso:**
- Gerente de produto atualizando preços de serviços
- Responsável por cadastros criando novos atrativos

---

### 👨‍💼 Gerente
**Perfil:** Acesso completo ao módulo de serviços

**Permissões:**
- ✅ CRUD completo em TUDO:
  - Categorias
  - Serviços
  - Transfers
  - Meia Entrada
  - Ordens de Serviço
  - Lançamentos
  - Transfers OS

**Casos de Uso:**
- Gerente geral com visão completa
- Responsável por auditoria e correções

---

## Como Configurar

### 1️⃣ Criar Grupos (Primeira Vez)

Execute o comando que cria automaticamente todos os grupos:

```bash
python manage.py criar_grupos
```

**Saída esperada:**
```
🔧 Criando grupos de permissões...

✅ Grupo "Operador" criado
   📋 6 permissões configuradas
   ℹ️  Operadores podem visualizar e criar ordens de serviço

✅ Grupo "Coordenador" criado
   📋 8 permissões configuradas
   ℹ️  Coordenadores têm controle total de ordens de serviço

✅ Grupo "Gestor de Cadastros" criado
   📋 17 permissões configuradas
   ℹ️  Gestores podem criar e editar todos os cadastros base

✅ Grupo "Gerente" criado
   📋 28 permissões configuradas
   ℹ️  Gerentes têm acesso completo ao módulo de serviços

============================================================
✨ RESUMO:
   🆕 Grupos criados: 4
   🔑 Total de permissões configuradas: 59
============================================================
```

### 2️⃣ Atribuir Usuário a Grupo

#### Opção A: Via Admin Django (Recomendado)

1. Acesse: `http://localhost:8000/admin/`
2. Vá em **Autenticação e Autorização** → **Usuários**
3. Clique no usuário desejado
4. Na seção **Permissões**, role até **Grupos**
5. Selecione o(s) grupo(s) desejado(s):
   - `Operador`
   - `Coordenador`
   - `Gestor de Cadastros`
   - `Gerente`
6. Clique em **Salvar**

#### Opção B: Via Shell Django

```python
python manage.py shell

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

# Atribuir usuário a um grupo
user = User.objects.get(username='joao')
grupo = Group.objects.get(name='Operador')
user.groups.add(grupo)

# Verificar grupos do usuário
print(user.groups.all())
```

### 3️⃣ Atribuir Permissão Individual

Quando um usuário precisa de uma permissão específica que o grupo não tem:

```python
from django.contrib.auth.models import Permission

# Buscar permissão
perm = Permission.objects.get(codename='delete_ordemservico')

# Atribuir ao usuário
user.user_permissions.add(perm)

# Remover permissão
user.user_permissions.remove(perm)
```

---

## Permissões Disponíveis

### 📁 Categorias (`categoria`)
```
servicos.view_categoria       # Visualizar categorias
servicos.add_categoria        # Criar categoria
servicos.change_categoria     # Editar categoria
servicos.delete_categoria     # Deletar categoria
```

### 🎫 Serviços (`subcategoria`)
```
servicos.view_subcategoria    # Visualizar serviços
servicos.add_subcategoria     # Criar serviço
servicos.change_subcategoria  # Editar serviço
servicos.delete_subcategoria  # Deletar serviço
```

### 🚐 Transfers (`transfer`)
```
servicos.view_transfer        # Visualizar transfers
servicos.add_transfer         # Criar transfer
servicos.change_transfer      # Editar transfer
servicos.delete_transfer      # Deletar transfer
```

### 🎟️ Meia Entrada (`tipomeiaentrada`)
```
servicos.view_tipomeiaentrada    # Visualizar tipos
servicos.add_tipomeiaentrada     # Criar tipo
servicos.change_tipomeiaentrada  # Editar tipo
servicos.delete_tipomeiaentrada  # Deletar tipo
```

### 📋 Ordens de Serviço (`ordemservico`)
```
servicos.view_ordemservico       # Visualizar ordens
servicos.add_ordemservico        # Criar ordem
servicos.change_ordemservico     # Editar ordem
servicos.delete_ordemservico     # Deletar ordem
```

### 📝 Lançamentos (`lancamentoservico`)
```
servicos.view_lancamentoservico    # Visualizar lançamentos
servicos.add_lancamentoservico     # Criar lançamento
servicos.change_lancamentoservico  # Editar lançamento
servicos.delete_lancamentoservico  # Deletar lançamento
```

### 🚗 Transfers OS (`transferos`)
```
servicos.view_transferos       # Visualizar transfers em OS
servicos.add_transferos        # Adicionar transfer
servicos.change_transferos     # Editar transfer
servicos.delete_transferos     # Remover transfer
```

---

## Exemplos Práticos

### Exemplo 1: Operador Especial

**Situação:** João é operador mas precisa editar ordens (não só criar).

**Solução:**
1. Manter João no grupo "Operador"
2. Adicionar permissão individual `servicos.change_ordemservico`

```python
# Via shell
user = User.objects.get(username='joao')
perm = Permission.objects.get(codename='change_ordemservico')
user.user_permissions.add(perm)
```

**Resultado:**
- João pode criar ordens (grupo Operador)
- João pode editar ordens (permissão individual) ✅
- João NÃO pode deletar ordens ❌

---

### Exemplo 2: Coordenador que também Gerencia Cadastros

**Situação:** Maria é coordenadora e também responsável por atualizar preços.

**Solução:**
1. Adicionar Maria a DOIS grupos:
   - "Coordenador"
   - "Gestor de Cadastros"

```python
# Via shell
user = User.objects.get(username='maria')
user.groups.add(
    Group.objects.get(name='Coordenador'),
    Group.objects.get(name='Gestor de Cadastros')
)
```

**Resultado:**
- Maria tem TODAS as permissões de ambos os grupos
- CRUD completo em cadastros ✅
- CRUD completo em ordens ✅

---

### Exemplo 3: Verificar Permissões de Usuário

```python
from servicos.permissions import listar_permissoes_usuario

# Via shell
user = User.objects.get(username='joao')
print(listar_permissoes_usuario(user))
```

**Saída:**
```
👤 Usuário: João Silva
📋 Grupos: Operador

🔑 Total de permissões: 6

👥 Permissões dos grupos (6):
   - servicos.view_categoria (via Operador)
   - servicos.view_subcategoria (via Operador)
   - servicos.view_transfer (via Operador)
   - servicos.view_tipomeiaentrada (via Operador)
   - servicos.view_ordemservico (via Operador)
   - servicos.add_ordemservico (via Operador)
```

---

## Troubleshooting

### ❌ Usuário não consegue acessar página

**Erro na tela:**
```
Você não tem permissão para acessar esta página.
Entre em contato com o administrador.
```

**Verificações:**

1. **Usuário está logado?**
   - Se não → redireciona para login
   - Se sim → continua

2. **Usuário é superusuário?**
   ```python
   user.is_superuser  # True = acesso total
   ```

3. **Usuário tem a permissão necessária?**
   ```python
   user.has_perm('servicos.view_categoria')  # True/False
   ```

4. **Verificar grupos do usuário:**
   ```python
   user.groups.all()  # Lista todos os grupos
   ```

5. **Verificar permissões individuais:**
   ```python
   user.user_permissions.all()  # Lista permissões diretas
   ```

---

### ❌ Grupo criado mas sem permissões

**Problema:** Grupo aparece vazio no admin.

**Solução:** Execute novamente o comando:
```bash
python manage.py criar_grupos
```

O comando é **idempotente** - pode executar várias vezes sem problemas.

---

### ❌ Permissão não encontrada

**Erro ao criar grupos:**
```
⚠️  Permissão não encontrada: servicos.view_categoria
```

**Causas possíveis:**

1. **Migrações não aplicadas:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Model não existe no código:**
   - Verifique se o model está em `servicos/models.py`
   - Verifique se está importado corretamente

3. **Nome da permissão incorreto:**
   - Padrão: `app.ação_modelo`
   - Exemplo: `servicos.view_categoria`
   - Modelo sempre em minúsculo e singular

---

### 🔍 Como saber qual permissão está faltando?

Quando tentar acessar uma página, o erro mostrará:

```
Permissão necessária: servicos.add_categoria
```

Você pode então:
1. Adicionar o usuário a um grupo que tenha essa permissão
2. Ou atribuir a permissão individual

---

## 🎯 Boas Práticas

### ✅ Recomendado

1. **Use grupos para equipes:**
   - Todos operadores no grupo "Operador"
   - Todos coordenadores no grupo "Coordenador"

2. **Use permissões individuais para exceções:**
   - Operador que precisa editar: permissão individual
   - Temporário: adiciona e depois remove

3. **Documente exceções:**
   - Mantenha registro de por que usuário X tem permissão Y

4. **Revise periodicamente:**
   - Remova usuários de grupos quando mudarem de função
   - Remova permissões individuais não usadas

### ❌ Evite

1. **Não dê acesso de superusuário sem necessidade**
   - Superusuário bypassa TODAS as verificações
   - Use apenas para administradores do sistema

2. **Não misture permissões individuais demais**
   - Se muitos usuários precisam da mesma permissão → crie um grupo

3. **Não deixe usuários sem grupo**
   - Todo usuário deve estar em pelo menos um grupo
   - Facilita gestão e auditoria

---

## 📚 Recursos Adicionais

### Código Fonte

- **Permissões:** `servicos/permissions.py`
- **Management Command:** `servicos/management/commands/criar_grupos.py`
- **Decorators em uso:** Todas as views em `servicos/views.py`

### Documentação Django

- [User authentication](https://docs.djangoproject.com/en/5.0/topics/auth/)
- [Permissions and authorization](https://docs.djangoproject.com/en/5.0/topics/auth/default/#permissions-and-authorization)
- [Groups](https://docs.djangoproject.com/en/5.0/topics/auth/default/#groups)

---

## 📞 Suporte

Problemas com permissões? Verifique:

1. Logs do sistema (`python manage.py runserver`)
2. Console do navegador (F12) para erros de permissão
3. Execute `listar_permissoes_usuario(user)` para debug

**Última atualização:** Janeiro 2026
