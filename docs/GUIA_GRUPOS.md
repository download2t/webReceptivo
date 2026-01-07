# 📋 Guia de Grupos e Permissões - WebReceptivo

## 🎯 Visão Geral

O sistema WebReceptivo possui 4 níveis de permissões, organizados em grupos:

1. **Administradores** - Controle total do sistema
2. **Gerentes** - Gestão operacional completa  
3. **Operadores** - Foco em ordens de serviço
4. **Usuários Básicos** - Apenas consulta

---

## 📊 Tabela de Permissões

| Funcionalidade | Administradores | Gerentes | Operadores | Usuários Básicos |
|---|:---:|:---:|:---:|:---:|
| **Usuários** | | | | |
| Visualizar usuários | ✅ | ✅ | ❌ | ❌ |
| Criar usuários | ✅ | ✅ | ❌ | ❌ |
| Editar usuários | ✅ | ✅ | ❌ | ❌ |
| Gerenciar grupos | ✅ | 👁️ Ver | ❌ | ❌ |
| **Categorias** | | | | |
| Visualizar | ✅ | ✅ | 👁️ Ver | ❌ |
| Criar | ✅ | ✅ | ❌ | ❌ |
| Editar | ✅ | ✅ | ❌ | ❌ |
| Excluir | ✅ | ✅ | ❌ | ❌ |
| **Serviços** | | | | |
| Visualizar | ✅ | ✅ | 👁️ Ver | 👁️ Ver |
| Criar | ✅ | ✅ | ❌ | ❌ |
| Editar | ✅ | ✅ | ❌ | ❌ |
| Excluir | ✅ | ✅ | ❌ | ❌ |
| **Transfers** | | | | |
| Visualizar | ✅ | ✅ | 👁️ Ver | ❌ |
| Criar | ✅ | ✅ | ❌ | ❌ |
| Editar | ✅ | ✅ | ❌ | ❌ |
| Excluir | ✅ | ✅ | ❌ | ❌ |
| **Tipos de Meia Entrada** | | | | |
| Visualizar | ✅ | ✅ | 👁️ Ver | ❌ |
| Criar | ✅ | ✅ | ❌ | ❌ |
| Editar | ✅ | ✅ | ❌ | ❌ |
| Excluir | ✅ | ✅ | ❌ | ❌ |
| **Ordens de Serviço** | | | | |
| Visualizar | ✅ | ✅ | ✅ | 👁️ Ver |
| Criar | ✅ | ✅ | ✅ | ❌ |
| Editar | ✅ | ✅ | ✅ | ❌ |
| Excluir | ✅ | ✅ | ✅ | ❌ |

**Legenda:**
- ✅ = Acesso completo (CRUD)
- 👁️ Ver = Apenas visualização (read-only)
- ❌ = Sem acesso

---

## 🔷 ADMINISTRADORES

**Papel:** Controle total do sistema

### ✅ Permissões Completas:
- Gerenciar usuários (criar, editar, visualizar, atribuir grupos)
- Gerenciar grupos de permissões
- CRUD completo de todas as entidades:
  - Categorias
  - Serviços
  - Transfers
  - Tipos de Meia Entrada
  - Ordens de Serviço

### 🎯 Uso Recomendado:
- Proprietário/Sócio da empresa
- Responsável de TI
- Gerente Geral

---

## 🔶 GERENTES

**Papel:** Gestão operacional completa

### ✅ Pode:
- Criar e editar usuários
- Visualizar grupos (não pode criar ou modificar grupos)
- CRUD completo de:
  - Categorias
  - Serviços
  - Transfers
  - Tipos de Meia Entrada
  - Ordens de Serviço

### ❌ Não Pode:
- Criar ou editar grupos de permissões

### 🎯 Uso Recomendado:
- Gerente de operações
- Supervisor
- Coordenador

---

## 🔹 OPERADORES

**Papel:** Foco em criar e gerenciar ordens de serviço

### ✅ Pode:
- **Ordens de Serviço:** CRUD completo (criar, editar, excluir)
- **Lançamentos de Serviço:** CRUD completo
- **Transfers em OS:** CRUD completo

### 👁️ Pode Visualizar (somente leitura):
- Categorias
- Serviços
- Transfers
- Tipos de Meia Entrada

### ❌ Não Pode:
- Ver, criar ou editar usuários (https://mydevsystem.site/users/ retorna 403 Forbidden)
- Editar ou excluir cadastros (categorias, serviços, transfers, tipos de meia)

### 🎯 Uso Recomendado:
- Atendente
- Vendedor
- Operador de sistema

---

## 🔘 USUÁRIOS BÁSICOS

**Papel:** Apenas consulta de informações

### 👁️ Pode Visualizar:
- Serviços
- Ordens de Serviço
- Lançamentos em Ordens de Serviço

### ❌ Não Pode:
- Criar, editar ou excluir NADA
- Ver usuários
- Ver categorias, transfers ou tipos de meia entrada

### 🎯 Uso Recomendado:
- Estagiário
- Visualizador
- Auditoria/Relatórios

---

## 🚀 Como Aplicar os Grupos

### 1. Configurar grupos (primeira vez ou atualização)

**Produção:**
```bash
cd /usr/local/lsws/Example/html/demo/webReceptivo
source venv/bin/activate
python manage_production.py setup_groups
```

**Local:**
```bash
python manage.py setup_groups
```

### 2. Atribuir grupo a um usuário

**Via Django Admin:**
1. Acessar `/admin/auth/user/`
2. Editar o usuário
3. Selecionar o grupo em "Groups"
4. Salvar

**Via Python Shell:**
```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()
user = User.objects.get(username='nome_usuario')
group = Group.objects.get(name='Operadores')
user.groups.add(group)
```

### 3. Remover usuário de um grupo

```python
user.groups.remove(group)
```

---

## 🔐 Bloqueios no Sistema

### Operadores NÃO podem:
- ❌ Acessar `/users/` (lista de usuários) → Retorna 403 Forbidden
- ❌ Editar categorias → Botões de editar/excluir não aparecem
- ❌ Editar serviços → Botões de editar/excluir não aparecem
- ❌ Editar transfers → Botões de editar/excluir não aparecem
- ❌ Editar tipos de meia → Botões de editar/excluir não aparecem
- ✅ Ver listas e detalhes de todos os cadastros acima

### Usuários Básicos NÃO podem:
- ❌ Criar, editar ou excluir qualquer registro
- ❌ Acessar área de usuários
- ❌ Ver categorias, transfers ou tipos de meia entrada
- ✅ Ver serviços e ordens de serviço (apenas leitura)

---

## 🔄 Atualizar Permissões

Se as regras de permissões mudarem, execute:

```bash
python manage_production.py setup_groups
```

Isso irá:
- ✅ Atualizar permissões dos grupos existentes
- ✅ Criar grupos que não existem
- ✅ Remover permissões antigas
- ✅ Adicionar novas permissões
- ✅ Mostrar relatório detalhado das mudanças

---

## ❓ FAQ

**P: O que acontece se um usuário estiver em múltiplos grupos?**  
R: Django combina as permissões de todos os grupos. O usuário terá TODAS as permissões de TODOS os grupos.

**P: Como dar acesso temporário de admin?**  
R: Marque o campo `is_staff` e `is_superuser` no usuário. Superusuários ignoram grupos.

**P: Operador pode ver a lista de serviços no admin?**  
R: Sim, pode ver a lista e detalhes, mas NÃO pode editar ou excluir.

**P: Usuário Básico pode criar ordem de serviço?**  
R: Não. Apenas visualizar ordens existentes.

**P: Como bloquear acesso a uma view específica?**  
R: Use decorators `@permission_required` nas views ou `has_permission` no Django Admin.

**P: O sistema já bloqueia operadores de acessar /users/?**  
R: Sim! Operadores não têm permissão `auth.view_user`, então o acesso retorna 403 Forbidden.

---

## 📞 Suporte

Para dúvidas sobre permissões, consulte este guia ou execute:

```bash
python manage_production.py setup_groups
```

O comando mostra todas as permissões configuradas por grupo com relatório detalhado.
