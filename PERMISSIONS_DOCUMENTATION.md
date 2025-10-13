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

## Sistema de Grupos Dinâmico

### Visão Geral do Gerenciamento de Grupos

O sistema agora permite criar, editar, excluir e configurar permissões de grupos/cargos dinamicamente através da interface web, sem necessidade de programação.

### Funcionalidades Implementadas

#### 1. **Criação de Grupos Personalizados**
- Interface amigável para criar novos grupos/cargos
- Validação automática baseada no nível do usuário
- Seleção visual de permissões por categoria
- Prevenção de nomes duplicados e protegidos

#### 2. **Edição de Grupos Existentes**
- Alteração de nomes (exceto grupos protegidos)
- Adição/remoção de permissões
- Visualização de impacto nos usuários
- Validações de segurança automáticas

#### 3. **Exclusão Segura de Grupos**
- Proteção contra exclusão de grupos básicos do sistema
- Visualização de usuários que serão afetados
- Confirmação dupla para operações perigosas
- Remoção automática de usuários do grupo (sem deletá-los)

#### 4. **Visualização Detalhada**
- Lista de usuários no grupo
- Permissões organizadas por aplicação
- Estatísticas em tempo real
- Indicadores visuais de status

### Regras de Permissão para Grupos

#### **Admin Principal (ID=1)**
- ✅ Pode criar qualquer tipo de grupo
- ✅ Pode editar todos os grupos (incluindo Administradores)
- ✅ Pode atribuir qualquer permissão
- ✅ Pode excluir grupos não-protegidos
- ❌ Não pode excluir grupos protegidos do sistema

#### **Administradores**
- ✅ Podem criar grupos até nível "Gerente"
- ✅ Podem editar grupos não-administrativos
- ✅ Podem atribuir maioria das permissões (exceto críticas)
- ✅ Podem excluir grupos criados por eles
- ❌ Não podem mexer no grupo "Administradores"

#### **Gerentes**
- ✅ Podem criar grupos personalizados
- ✅ Podem editar grupos de nível inferior
- ✅ Podem atribuir permissões básicas
- ✅ Podem excluir grupos não-protegidos que criaram
- ❌ Não podem mexer em grupos "Administradores" ou "Gerentes"

#### **Operadores e Usuários Básicos**
- ❌ Não podem gerenciar grupos

### Interface de Usuário

#### **Lista de Grupos** (`/user-management/groups/`)
- Cards visuais com informações resumidas
- Filtro de busca por nome
- Indicadores de grupos protegidos
- Contador de usuários e permissões
- Ações contextuais baseadas em permissões

#### **Criação/Edição** (`/user-management/groups/create/`, `/edit/`)
- Formulário intuitivo com seções organizadas
- Seleção visual de permissões agrupadas por aplicação
- Botões "Selecionar Todas" / "Desmarcar Todas"
- Validação em tempo real
- Estatísticas do grupo (na edição)

#### **Detalhes do Grupo** (`/user-management/groups/{id}/`)
- Estatísticas em cards coloridos
- Lista de usuários com avatars
- Permissões organizadas por aplicação
- Ações disponíveis baseadas em permissões

#### **Exclusão Segura** (`/user-management/groups/{id}/delete/`)
- Visualização de impacto nos usuários
- Lista de usuários que serão removidos do grupo
- Confirmação dupla com avisos visuais
- Informações sobre consequências da ação

### Navegação Integrada

- **Tabs de Navegação**: Usuários ↔ Grupos
- **Menu Principal**: Link no dropdown do usuário
- **Breadcrumbs**: Navegação consistente
- **Links Contextuais**: Entre usuários e grupos relacionados

### Grupos Protegidos

Os seguintes grupos são **protegidos** e têm restrições especiais:

1. **Administradores**
   - Nome não pode ser alterado
   - Só pode ser editado pelo Admin Principal
   - Não pode ser excluído

2. **Gerentes**
   - Nome não pode ser alterado
   - Pode ser editado por Administradores+
   - Não pode ser excluído

3. **Operadores**
   - Nome não pode ser alterado
   - Pode ser editado por Gerentes+
   - Não pode ser excluído

4. **Usuários Básicos**
   - Nome não pode ser alterado
   - Pode ser editado por Gerentes+
   - Não pode ser excluído

### Validações de Segurança

#### **Criação de Grupos**
- Verificar se usuário tem permissão para criar grupos
- Validar nível máximo de permissões que pode atribuir
- Impedir criação de grupos com nomes protegidos
- Verificar duplicatas de nomes

#### **Edição de Grupos**
- Verificar se pode editar o grupo específico
- Validar cada permissão sendo adicionada/removida
- Proteger alterações em grupos críticos
- Manter integridade do sistema

#### **Exclusão de Grupos**
- Impedir exclusão de grupos protegidos
- Verificar se tem permissão para excluir
- Calcular impacto nos usuários
- Confirmar ação antes de executar

### Exemplo de Uso Prático

```python
# Via interface web, um Gerente pode:

# 1. Criar um grupo "Supervisores"
grupo_supervisores = {
    'name': 'Supervisores',
    'permissions': [
        'auth.view_user',           # Ver usuários
        'core.view_dashboard',      # Ver dashboard
        'reports.view_report'       # Ver relatórios (futuro)
    ]
}

# 2. Atribuir usuários ao grupo via edição de usuário

# 3. Posteriormente, adicionar mais permissões conforme necessário

# 4. Se necessário, excluir o grupo (usuários não são afetados)
```

### Integração com Sistema de Usuários

- **Formulário de Usuário**: Mostra apenas grupos que pode atribuir
- **Lista de Usuários**: Filtro por grupo
- **Detalhes do Usuário**: Link para detalhes do grupo
- **Detalhes do Grupo**: Link para usuários do grupo

### Preparação para Futuras Funcionalidades

O sistema de grupos está preparado para:

1. **Módulos Futuros**: Facilmente adicionar novas permissões
2. **Relatórios Avançados**: Auditoria de grupos e permissões
3. **Workflows**: Aprovação de criação de grupos
4. **Templates de Grupo**: Grupos pré-configurados
5. **Herança de Permissões**: Grupos hierárquicos

### Comandos de Gerenciamento

```bash
# Criar/atualizar grupos básicos
python manage.py setup_groups

# Auditoria de permissões (futuro)
python manage.py audit_permissions

# Limpeza de grupos órfãos (futuro) 
python manage.py cleanup_groups
```
