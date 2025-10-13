# Sistema de Permissões - WebReceptivo

## Visão Geral

O sistema de permissões foi completamente reestruturado para implementar uma hierarquia robusta e segura de usuários com regras claras de acesso e operações.

## Hierarquia de Usuários

### 1. Usuários Básicos
- **Acesso**: Apenas ao próprio perfil
- **Permissões**: 
  - Visualizar e alterar próprios dados básicos
  - Alterar própria senha
- **Restrições**: 
  - Não acessam área administrativa
  - Não gerenciam outros usuários
- **Menu**: Não mostrado menu de administração

### 2. Operadores
- **Acesso**: Sistema operacional do negócio
- **Permissões**:
  - Todas as do Usuário Básico
  - Acesso a funcionalidades operacionais (futuras implementações)
- **Restrições**:
  - Não acessam área de administração de usuários
  - Não gerenciam usuários
- **Menu**: Não mostrado menu de administração

### 3. Gerentes
- **Acesso**: Área de administração limitada
- **Permissões**:
  - Criar, visualizar e editar Operadores e Usuários Básicos
  - Acesso a relatórios gerenciais (futuras implementações)
- **Restrições**:
  - NÃO podem mexer em Administradores
  - NÃO podem mexer em outros Gerentes
  - NÃO podem dar acesso ao painel admin Django
  - NÃO podem criar superusuários
- **Menu**: Mostra menu de administração com opção "Gerenciar Usuários"

### 4. Administradores
- **Acesso**: Administração completa exceto Admin Principal
- **Permissões**:
  - Criar, visualizar, editar e deletar Gerentes, Operadores e Usuários
  - Dar acesso ao painel admin Django (is_staff)
  - Acesso a todas as áreas administrativas
- **Restrições**:
  - NÃO podem alterar outros Administradores
  - NÃO podem mexer no Admin Principal (ID=1)
  - NÃO podem criar superusuários
- **Menu**: Menu completo de administração

### 5. Administrador Principal (ID=1)
- **Acesso**: Irrestrito em todo o sistema
- **Permissões**:
  - Pode fazer qualquer coisa no sistema
  - Único que pode alterar outros Administradores
  - Pode criar superusuários
- **Proteções Especiais**:
  - **INTOCÁVEL**: Não pode ser editado por ninguém
  - Sempre mantém `is_superuser=True`
  - Sempre mantém `is_active=True`
  - Username não pode ser alterado
  - Não pode ser deletado
- **Menu**: Acesso total a todas as funcionalidades

## Regras de Proteção

### Regras Gerais
1. **Autoedição**: Ninguém pode editar a si mesmo através da administração
2. **Hierarquia**: Cada nível só pode gerenciar níveis inferiores
3. **Admin Principal**: ID=1 é completamente protegido
4. **Escalação**: Usuários não podem elevar privilégios além do que possuem

### Operações Específicas

#### Visualização de Usuários
- Admin Principal: vê todos
- Administradores: veem gerentes, operadores e usuários básicos
- Gerentes: veem apenas operadores e usuários básicos
- Outros: não veem usuários na administração

#### Edição de Usuários
- Admin Principal: edita todos (exceto ID=1)
- Administradores: editam gerentes, operadores e usuários básicos
- Gerentes: editam apenas operadores e usuários básicos
- Outros: não editam ninguém

#### Deleção de Usuários
- Admin Principal: deleta todos (exceto ID=1)
- Administradores: deletam apenas operadores e usuários básicos
- Gerentes: deletam apenas operadores e usuários básicos
- Outros: não deletam ninguém
- **ID=1 NUNCA pode ser deletado**

#### Criação de Usuários
- Admin Principal: pode criar qualquer nível
- Administradores: podem criar até gerentes
- Gerentes: podem criar até operadores
- Outros: não podem criar usuários

#### Atribuição de Grupos
- Admin Principal: pode atribuir qualquer grupo
- Administradores: podem atribuir até "Gerentes"
- Gerentes: podem atribuir apenas "Operadores" e "Usuários Básicos"
- Outros: não podem atribuir grupos

## Implementação Técnica

### Arquivos Principais

#### `permission_helpers.py`
Contém todas as regras de negócio e funções de validação:
- `get_user_level()`: Determina nível do usuário
- `can_access_user_management()`: Verifica acesso à administração
- `can_view_user()`: Verifica se pode visualizar usuário
- `can_edit_user()`: Verifica se pode editar usuário
- `can_delete_user()`: Verifica se pode deletar usuário
- `can_create_user_with_level()`: Verifica se pode criar usuário com nível
- `validate_user_form_submission()`: Valida submissão de formulários
- E muitas outras funções auxiliares

#### `views.py`
Views atualizadas com decorador customizado `@user_management_required` que:
- Substitui `@permission_required`
- Aplica automaticamente as regras de hierarquia
- Valida todas as operações antes de executar

#### `context_processors.py`
Context processor que adiciona variáveis globais aos templates:
- `user_can_access_admin_menu`: Se deve mostrar menu admin
- `user_can_manage_users`: Se deve mostrar link de usuários
- `user_level_display`: Nome amigável do nível do usuário

### Menu Dinâmico

O menu do navbar agora é completamente dinâmico baseado nas permissões:

```html
{% if user_can_access_admin_menu %}
<li><hr class="dropdown-divider"></li>
<li><h6 class="dropdown-header">Administração</h6></li>
<li><span class="dropdown-item-text small text-muted">{{ user_level_display }}</span></li>
{% endif %}

{% if user_can_manage_users %}
<li><a class="dropdown-item" href="{% url 'user_management:user_list' %}">Gerenciar Usuários</a></li>
{% endif %}
```

### Grupos Automáticos

O comando `setup_groups` cria automaticamente os grupos necessários:
- **Administradores**: Permissões completas de usuário
- **Gerentes**: Permissões limitadas de usuário  
- **Operadores**: Sem permissões de usuário
- **Usuários Básicos**: Sem permissões de usuário

## Como Usar

### Para Testar Permissões

1. **Criar grupos**: `python manage.py setup_groups`

2. **Criar usuários de teste**:
   ```python
   # Via shell do Django
   python manage.py shell
   
   from django.contrib.auth.models import User, Group
   
   # Criar gerente
   gerente = User.objects.create_user('gerente', 'gerente@test.com', 'senha123')
   grupo_gerente = Group.objects.get(name='Gerentes')
   gerente.groups.add(grupo_gerente)
   
   # Criar operador
   operador = User.objects.create_user('operador', 'operador@test.com', 'senha123')
   grupo_operador = Group.objects.get(name='Operadores')
   operador.groups.add(grupo_operador)
   ```

3. **Logar com diferentes usuários** e verificar:
   - Quais menus aparecem
   - Quais usuários são listados
   - Quais operações são permitidas

### Para Futuras Implementações

1. **Adicionar novas áreas administrativas**:
   - Use `can_access_user_management()` para controlar acesso
   - Use `get_user_level()` para personalizar interface
   - Siga o mesmo padrão de decoradores e validações

2. **Adicionar novas permissões**:
   - Atualize o comando `setup_groups`
   - Adicione funções em `permission_helpers.py`
   - Use nos templates e views

## Segurança

### Pontos de Proteção
- **Admin Principal (ID=1)** é completamente blindado
- Todas as views validam permissões antes de qualquer ação
- Formulários são filtrados baseado no nível do usuário
- Menu é construído dinamicamente baseado em permissões
- Context processor garante consistência em todos os templates

### Logs de Auditoria (Futuro)
O sistema está preparado para implementar logs de auditoria:
- Todas as ações passam por funções centralizadas
- Fácil adicionar logging das operações
- Rastreabilidade de quem fez o quê e quando

## Testes

Para garantir que as regras funcionam corretamente:

1. **Teste de Acesso**: Usuários básicos e operadores não devem ver menu de administração
2. **Teste de Hierarquia**: Gerentes não devem conseguir alterar administradores
3. **Teste de Proteção**: Admin Principal (ID=1) deve ser intocável
4. **Teste de Interface**: Menus e botões devem aparecer apenas para quem tem permissão

O sistema está robusto e preparado para escalar conforme novas funcionalidades administrativas sejam adicionadas ao WebReceptivo.
