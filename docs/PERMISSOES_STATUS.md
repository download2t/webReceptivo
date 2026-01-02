# ✅ SISTEMA DE PERMISSÕES - ATUALIZADO

## 📊 Status Atual

✅ **Grupos temporários removidos:**
- ~~Operador~~
- ~~Coordenador~~
- ~~Gestor de Cadastros~~
- ~~Gerente~~

✅ **Grupos existentes atualizados:**
- **Administradores** (35 permissões) - 28 novas adicionadas
- **Gerentes** (32 permissões) - 28 novas adicionadas
- **Operadores** (16 permissões) - 16 novas adicionadas
- **Usuários Básicos** (7 permissões) - 7 novas adicionadas

---

## 🔐 Permissões por Grupo

### 👑 Administradores (35 permissões)

**Gestão de Usuários (7):**
- add_group, change_group, view_group
- add_user, change_user, delete_user, view_user

**Módulo de Serviços - CRUD COMPLETO (28):**
- ✅ Categorias: view, add, change, delete
- ✅ Serviços (SubCategoria): view, add, change, delete
- ✅ Transfers: view, add, change, delete
- ✅ Meia Entrada: view, add, change, delete
- ✅ Ordens de Serviço: view, add, change, delete
- ✅ Lançamentos: view, add, change, delete
- ✅ Transfers OS: view, add, change, delete

**Casos de Uso:**
- Administrador do sistema
- Controle total sobre usuários E serviços

---

### 👨‍💼 Gerentes (32 permissões)

**Gestão de Usuários (4):**
- add_user, change_user, view_user, view_group
- ❌ NÃO pode deletar usuários ou editar grupos

**Módulo de Serviços - CRUD COMPLETO (28):**
- ✅ Categorias: view, add, change, delete
- ✅ Serviços: view, add, change, delete
- ✅ Transfers: view, add, change, delete
- ✅ Meia Entrada: view, add, change, delete
- ✅ Ordens de Serviço: view, add, change, delete
- ✅ Lançamentos: view, add, change, delete
- ✅ Transfers OS: view, add, change, delete

**Casos de Uso:**
- Gerente geral da operação
- Pode criar/editar usuários mas não deletar
- Acesso total aos serviços turísticos

---

### 👨‍💻 Operadores (16 permissões)

**Módulo de Serviços - VISUALIZAÇÃO de Cadastros (4):**
- ✅ view_categoria
- ✅ view_subcategoria
- ✅ view_transfer
- ✅ view_tipomeiaentrada
- ❌ NÃO pode criar/editar/deletar cadastros

**Módulo de Serviços - CRUD de Ordens (12):**
- ✅ Ordens de Serviço: view, add, change, delete
- ✅ Lançamentos: view, add, change, delete
- ✅ Transfers OS: view, add, change, delete

**Casos de Uso:**
- Operador de atendimento
- Cria e gerencia ordens de serviço
- Consulta cadastros mas não pode alterá-los

---

### 👤 Usuários Básicos (7 permissões)

**Módulo de Serviços - SOMENTE VISUALIZAÇÃO (7):**
- ✅ view_categoria
- ✅ view_subcategoria
- ✅ view_transfer
- ✅ view_tipomeiaentrada
- ✅ view_ordemservico
- ✅ view_lancamentoservico
- ✅ view_transferos
- ❌ NÃO pode criar, editar ou deletar NADA

**Casos de Uso:**
- Usuário de consulta
- Relatórios e análises
- Visualização apenas

---

## 🎯 Matriz de Permissões

| Ação | Administradores | Gerentes | Operadores | Usuários Básicos |
|------|----------------|----------|------------|------------------|
| **Usuários** | | | | |
| Ver usuários | ✅ | ✅ | ❌ | ❌ |
| Criar usuários | ✅ | ✅ | ❌ | ❌ |
| Editar usuários | ✅ | ✅ | ❌ | ❌ |
| Deletar usuários | ✅ | ❌ | ❌ | ❌ |
| Editar grupos | ✅ | ❌ | ❌ | ❌ |
| **Categorias** | | | | |
| Ver | ✅ | ✅ | ✅ | ✅ |
| Criar | ✅ | ✅ | ❌ | ❌ |
| Editar | ✅ | ✅ | ❌ | ❌ |
| Deletar | ✅ | ✅ | ❌ | ❌ |
| **Serviços** | | | | |
| Ver | ✅ | ✅ | ✅ | ✅ |
| Criar | ✅ | ✅ | ❌ | ❌ |
| Editar | ✅ | ✅ | ❌ | ❌ |
| Deletar | ✅ | ✅ | ❌ | ❌ |
| **Transfers** | | | | |
| Ver | ✅ | ✅ | ✅ | ✅ |
| Criar | ✅ | ✅ | ❌ | ❌ |
| Editar | ✅ | ✅ | ❌ | ❌ |
| Deletar | ✅ | ✅ | ❌ | ❌ |
| **Meia Entrada** | | | | |
| Ver | ✅ | ✅ | ✅ | ✅ |
| Criar | ✅ | ✅ | ❌ | ❌ |
| Editar | ✅ | ✅ | ❌ | ❌ |
| Deletar | ✅ | ✅ | ❌ | ❌ |
| **Ordens de Serviço** | | | | |
| Ver | ✅ | ✅ | ✅ | ✅ |
| Criar | ✅ | ✅ | ✅ | ❌ |
| Editar | ✅ | ✅ | ✅ | ❌ |
| Deletar | ✅ | ✅ | ✅ | ❌ |

---

## ⚡ Como Atribuir Usuário a Grupo

### Via Admin Django:
1. http://localhost:8000/admin/
2. **Autenticação e Autorização** → **Usuários**
3. Clique no usuário
4. Seção **Permissões** → **Grupos**
5. Selecione: Administradores, Gerentes, Operadores ou Usuários Básicos
6. **Salvar**

### Via Shell:
```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()
user = User.objects.get(username='joao')

# Adicionar a grupo
grupo = Group.objects.get(name='Operadores')
user.groups.add(grupo)

# Verificar
print(user.groups.all())
```

---

## 🔄 Atualizar Permissões

Se adicionar novos models ou precisar reconfigurar:

```bash
python manage.py criar_grupos
```

O comando:
- ✅ Preserva permissões antigas
- ✅ Adiciona apenas as novas
- ✅ Não remove nada
- ✅ Pode executar quantas vezes quiser

---

## 📝 Arquivos Importantes

- **Definição:** `servicos/permissions.py`
- **Command:** `servicos/management/commands/criar_grupos.py`
- **Views protegidas:** `servicos/views.py`
- **Template exemplo:** `templates/servicos/categoria_list.html`

---

## ✅ Checklist de Implementação

- [x] Sistema de permissões criado
- [x] 4 grupos configurados
- [x] Todas as views protegidas
- [x] Grupos temporários removidos
- [x] Permissões antigas preservadas
- [x] Novas permissões adicionadas (79 total)
- [x] Templates com verificação condicional
- [ ] Aplicar verificações em todos os templates restantes
- [ ] Testar cada grupo com usuário real

---

**Última atualização:** 02/01/2026 14:50
