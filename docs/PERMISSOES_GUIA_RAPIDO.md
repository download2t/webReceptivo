# 🚀 GUIA RÁPIDO - Sistema de Permissões

## ✅ O que foi implementado

1. **Sistema completo de permissões** em TODAS as views do app `servicos`
2. **4 grupos padrão** prontos para uso
3. **Proteção em templates** - botões aparecem apenas se usuário tem permissão
4. **Command management** para criar grupos automaticamente
5. **Documentação completa** em `docs/PERMISSOES.md`

---

## 📦 Arquivos Criados/Modificados

### Novos Arquivos:
- ✅ `servicos/permissions.py` - Sistema de permissões centralizado
- ✅ `servicos/management/commands/criar_grupos.py` - Command para criar grupos
- ✅ `docs/PERMISSOES.md` - Documentação completa (280 linhas)
- ✅ `docs/PERMISSOES_GUIA_RAPIDO.md` - Este arquivo

### Arquivos Modificados:
- ✅ `servicos/views.py` - Todas as views protegidas com `@require_permission`
- ✅ `templates/servicos/categoria_list.html` - Botões condicionais

---

## 🎯 Grupos Criados

| Grupo | Descrição | Use para |
|-------|-----------|----------|
| **Operador** | Cria OS, visualiza cadastros | Atendentes, recepcionistas |
| **Coordenador** | CRUD de OS, visualiza cadastros | Supervisores, coordenadores |
| **Gestor de Cadastros** | CRUD de cadastros, visualiza OS | Gerentes de produto |
| **Gerente** | CRUD completo em tudo | Gerentes gerais |

---

## ⚡ Como Usar (3 passos)

### 1. Grupos já foram criados ✅
```bash
# JÁ EXECUTADO - Não precisa rodar novamente
python manage.py criar_grupos
```

**Resultado:** 4 grupos com 59 permissões configuradas

### 2. Atribua usuários aos grupos

**Via Admin (Recomendado):**
1. Acesse: http://localhost:8000/admin/
2. **Autenticação e Autorização** → **Usuários**
3. Clique no usuário
4. Role até **Grupos** e selecione:
   - `Operador`
   - `Coordenador`
   - `Gestor de Cadastros`
   - `Gerente`
5. **Salvar**

**Via Shell (Avançado):**
```python
python manage.py shell

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()
user = User.objects.get(username='joao')
grupo = Group.objects.get(name='Operador')
user.groups.add(grupo)
```

### 3. Teste o sistema

1. **Logout** do usuário atual
2. **Login** com usuário do grupo testado
3. Acesse `http://localhost:8000/servicos/categorias/`
4. Observe:
   - **Operador**: Vê lista, NÃO vê botões (sem permissão)
   - **Gestor de Cadastros**: Vê lista E botões de editar/excluir
   - **Gerente**: Vê tudo

---

## 🔐 Permissões por Funcionalidade

### Categorias
```python
perms.servicos.view_categoria       # Ver lista
perms.servicos.add_categoria        # Botão "Nova"
perms.servicos.change_categoria     # Botão "Editar"
perms.servicos.delete_categoria     # Botão "Excluir"
```

### Serviços (SubCategoria)
```python
perms.servicos.view_subcategoria    # Ver lista
perms.servicos.add_subcategoria     # Criar
perms.servicos.change_subcategoria  # Editar
perms.servicos.delete_subcategoria  # Excluir
```

### Transfers
```python
perms.servicos.view_transfer        # Ver lista
perms.servicos.add_transfer         # Criar
perms.servicos.change_transfer      # Editar
perms.servicos.delete_transfer      # Excluir
```

### Meia Entrada
```python
perms.servicos.view_tipomeiaentrada    # Ver lista
perms.servicos.add_tipomeiaentrada     # Criar
perms.servicos.change_tipomeiaentrada  # Editar
perms.servicos.delete_tipomeiaentrada  # Excluir
```

### Ordens de Serviço
```python
perms.servicos.view_ordemservico    # Ver/Listar
perms.servicos.add_ordemservico     # Criar
perms.servicos.change_ordemservico  # Editar
perms.servicos.delete_ordemservico  # Excluir
```

---

## 📋 Templates Protegidos

### Exemplo: Botão aparece apenas com permissão

**ANTES:**
```django
<a href="{% url 'servicos:categoria_create' %}" class="btn btn-primary">
    Nova Categoria
</a>
```

**DEPOIS:**
```django
{% if perms.servicos.add_categoria %}
<a href="{% url 'servicos:categoria_create' %}" class="btn btn-primary">
    Nova Categoria
</a>
{% endif %}
```

**Resultado:**
- ✅ Usuário com permissão → vê botão
- ❌ Usuário sem permissão → não vê botão

### Templates Já Atualizados:
- ✅ `categoria_list.html`

### Templates Pendentes (mesma lógica):
- ⏳ `subcategoria_list.html`
- ⏳ `transfer_list.html`
- ⏳ `tipo_meia_list.html`
- ⏳ `ordem_servico_list.html` (lancamento_list.html)

---

## 🎓 Exemplos Práticos

### Cenário 1: Operador Júnior
**Perfil:** Apenas cria OS, não pode editar

**Configuração:**
```
Grupo: Operador
Permissões individuais: Nenhuma
```

**Resultado:**
- ✅ Vê lista de OS
- ✅ Cria nova OS
- ❌ Não vê botão "Editar"
- ❌ Não vê botão "Excluir"

---

### Cenário 2: Operador Sênior
**Perfil:** Cria E edita OS (exceção)

**Configuração:**
```
Grupo: Operador
Permissões individuais: servicos.change_ordemservico
```

**Resultado:**
- ✅ Vê lista de OS
- ✅ Cria nova OS
- ✅ VÊ e USA botão "Editar" (permissão individual!)
- ❌ Não vê botão "Excluir"

**Como fazer:**
```python
# Via shell
from django.contrib.auth.models import Permission
user = User.objects.get(username='maria')
perm = Permission.objects.get(codename='change_ordemservico')
user.user_permissions.add(perm)
```

---

### Cenário 3: Gerente de Produto
**Perfil:** Gerencia cadastros, não mexe em OS

**Configuração:**
```
Grupo: Gestor de Cadastros
```

**Resultado:**
- ✅ CRUD completo em Categorias
- ✅ CRUD completo em Serviços
- ✅ CRUD completo em Transfers
- ✅ CRUD completo em Meia Entrada
- ✅ Visualiza OS (mas não edita)

---

## 🐛 Troubleshooting Rápido

### Problema: "Você não tem permissão para acessar esta página"

**Checklist:**
1. ✅ Usuário está logado?
2. ✅ Usuário está em algum grupo?
   ```python
   user.groups.all()  # Deve retornar pelo menos 1 grupo
   ```
3. ✅ Grupo tem a permissão necessária?
   ```python
   grupo = Group.objects.get(name='Operador')
   grupo.permissions.all()  # Lista permissões do grupo
   ```

### Problema: Botões não aparecem

**Checklist:**
1. ✅ Template usa `{% if perms.servicos.xxx %}`?
2. ✅ Usuário tem a permissão específica?
   ```python
   user.has_perm('servicos.add_categoria')  # True/False
   ```

### Problema: Permissão não existe

**Solução:**
```bash
# Aplica migrações (cria permissões)
python manage.py migrate

# Recria grupos
python manage.py criar_grupos
```

---

## 🔍 Debug de Permissões

### Ver permissões de um usuário:
```python
python manage.py shell

from django.contrib.auth import get_user_model
from servicos.permissions import listar_permissoes_usuario

User = get_user_model()
user = User.objects.get(username='joao')

# Lista formatada
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
   ...
```

---

## ✅ Próximos Passos Recomendados

### 1. Proteger Templates Restantes
Aplicar mesma lógica de `categoria_list.html` em:
- `subcategoria_list.html`
- `transfer_list.html`
- `tipo_meia_list.html`
- `ordem_servico_list.html`

### 2. Criar Usuários de Teste
```python
# Via shell
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

# Operador de teste
operador = User.objects.create_user(
    username='operador_teste',
    password='teste123',
    first_name='João',
    last_name='Operador'
)
operador.groups.add(Group.objects.get(name='Operador'))

# Gerente de teste
gerente = User.objects.create_user(
    username='gerente_teste',
    password='teste123',
    first_name='Maria',
    last_name='Gerente'
)
gerente.groups.add(Group.objects.get(name='Gerente'))
```

### 3. Testar Cada Perfil
- [ ] Login como `operador_teste` → Verificar limitações
- [ ] Login como `gerente_teste` → Verificar acesso total
- [ ] Login como superusuário → Verificar bypass

---

## 📚 Documentação Completa

Para detalhes técnicos, exemplos avançados e arquitetura:
👉 **Leia:** `docs/PERMISSOES.md` (280 linhas de documentação completa)

---

**Status:** ✅ Sistema funcional e pronto para uso
**Última atualização:** Janeiro 2026
