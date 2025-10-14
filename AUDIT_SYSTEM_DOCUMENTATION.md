# 📊 Sistema de Logs e Auditoria - WebReceptivo

## 🎯 Objetivo

Implementar um sistema completo de auditoria que registra todas as ações realizadas no sistema, com foco inicial em usuários e grupos, mas extensível para todas as funcionalidades futuras.

## 🏗️ Arquitetura do Sistema

### 📁 Nova App: `audit_system`
```
audit_system/
├── models.py          # Modelo AuditLog principal
├── admin.py           # Interface admin para logs
├── views.py           # Views para consulta de logs
├── signals.py         # Sinais Django para captura automática
├── middleware.py      # Middleware para rastreamento de requisições
├── decorators.py      # Decoradores para auditoria
├── utils.py           # Utilitários e helpers
├── filters.py         # Filtros personalizados
└── management/
    └── commands/
        ├── cleanup_logs.py    # Limpeza de logs antigos
        └── export_audit.py    # Exportação de relatórios
```

## 📋 Modelo de Dados

### 🗃️ **AuditLog**
```python
class AuditLog(models.Model):
    # Identificação da ação
    action = models.CharField(max_length=50)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    model_name = models.CharField(max_length=100)  # User, Group, etc.
    object_id = models.CharField(max_length=100, null=True)  # ID do objeto
    object_repr = models.CharField(max_length=200)  # Representação do objeto
    
    # Dados da mudança
    changes = models.JSONField(default=dict)  # {"field": {"old": "valor", "new": "valor"}}
    
    # Contexto da ação
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(null=True)
    session_key = models.CharField(max_length=40, null=True)
    
    # Metadados
    success = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)
    extra_data = models.JSONField(default=dict)  # Dados adicionais específicos
```

## 🔄 Funcionalidades Implementadas

### 1️⃣ **Captura Automática via Signals**
- **post_save**: Criação e modificação de objetos
- **post_delete**: Exclusão de objetos
- **user_logged_in/out**: Eventos de autenticação
- **permission_changed**: Mudanças de permissões

### 2️⃣ **Middleware de Contexto**
- Captura IP, User-Agent, sessão
- Rastreamento de requisições
- Contexto de usuário para todas as ações

### 3️⃣ **Decoradores Personalizados**
```python
@audit_action('user_password_changed')
@audit_action('group_permissions_modified')
@audit_action('custom_action_name')
```

### 4️⃣ **Interface de Consulta**
- Dashboard com estatísticas
- Filtros avançados por usuário, data, ação
- Exportação de relatórios (CSV, PDF)
- Busca por texto e filtros dinâmicos

## 📊 Tipos de Ações Rastreadas

### 👥 **Usuários**
- `USER_CREATED` - Usuário criado
- `USER_UPDATED` - Dados do usuário alterados
- `USER_DELETED` - Usuário deletado
- `USER_ACTIVATED` - Usuário ativado
- `USER_DEACTIVATED` - Usuário desativado
- `USER_PASSWORD_CHANGED` - Senha alterada
- `USER_LOGIN` - Login realizado
- `USER_LOGOUT` - Logout realizado
- `USER_LOGIN_FAILED` - Tentativa de login falhada

### 👨‍👩‍👧‍👦 **Grupos**
- `GROUP_CREATED` - Grupo criado
- `GROUP_UPDATED` - Grupo modificado
- `GROUP_DELETED` - Grupo deletado
- `GROUP_USER_ADDED` - Usuário adicionado ao grupo
- `GROUP_USER_REMOVED` - Usuário removido do grupo
- `GROUP_PERMISSION_ADDED` - Permissão adicionada
- `GROUP_PERMISSION_REMOVED` - Permissão removida

### 🔐 **Permissões**
- `PERMISSION_GRANTED` - Permissão concedida
- `PERMISSION_REVOKED` - Permissão revogada
- `ROLE_CHANGED` - Papel/função alterada

### 🎯 **Extensível para Futuro**
- `BOOKING_CREATED` - Reserva criada
- `PAYMENT_PROCESSED` - Pagamento processado
- `REPORT_GENERATED` - Relatório gerado
- `FILE_UPLOADED` - Arquivo enviado
- `BACKUP_CREATED` - Backup realizado

## 🛡️ Segurança e Performance

### 🔒 **Segurança**
- Logs imutáveis após criação
- Acesso restrito por permissões
- Hash de integridade para logs críticos
- Sanitização de dados sensíveis

### ⚡ **Performance**
- Índices otimizados para consultas frequentes
- Particionamento por data
- Limpeza automática de logs antigos
- Compressão de dados históricos

## 🎛️ Dashboard de Auditoria

### 📈 **Métricas Principais**
- Total de ações por período
- Usuários mais ativos
- Tipos de ação mais frequentes
- Horários de pico de atividade
- Gráficos de tendências

### 🔍 **Filtros Avançados**
- Por usuário, grupo, data
- Por tipo de ação
- Por sucesso/falha
- Por IP ou dispositivo
- Busca textual em logs

## 🚀 Implementação em Fases

### **Fase 1: Base do Sistema** ✅
- Modelo AuditLog
- Signals básicos para User/Group
- Middleware de contexto
- Interface admin básica

### **Fase 2: Interface Web** 🔄
- Dashboard de auditoria
- Filtros e busca
- Exportação de relatórios
- Permissões de acesso

### **Fase 3: Funcionalidades Avançadas** 📋
- Alertas em tempo real
- Integração com sistema de notificações
- API REST para logs
- Relatórios automatizados

### **Fase 4: Otimização** 🎯
- Performance tuning
- Arquivamento automático
- Integração com sistemas externos
- Machine learning para detecção de anomalias

## 📝 Exemplos de Uso

### **Log de Criação de Usuário**
```json
{
  "action": "USER_CREATED",
  "model_name": "User",
  "object_id": "15",
  "object_repr": "João Silva (joao@email.com)",
  "changes": {
    "username": {"old": null, "new": "joao_silva"},
    "email": {"old": null, "new": "joao@email.com"},
    "is_active": {"old": null, "new": true}
  },
  "user": "admin",
  "timestamp": "2025-10-14T10:30:00Z",
  "ip_address": "192.168.1.100"
}
```

### **Log de Mudança de Permissão**
```json
{
  "action": "GROUP_PERMISSION_ADDED",
  "model_name": "Group",
  "object_id": "3",
  "object_repr": "Gerentes de Vendas",
  "changes": {
    "permissions": {
      "added": ["auth.add_user", "auth.change_user"],
      "removed": []
    }
  },
  "user": "admin",
  "extra_data": {
    "affected_users": 5,
    "permission_source": "group_management"
  }
}
```

## 🔧 Configurações

### **Settings.py**
```python
AUDIT_SYSTEM = {
    'ENABLED': True,
    'LOG_ANONYMOUS_USERS': False,
    'RETENTION_DAYS': 365,  # 1 ano
    'EXCLUDED_MODELS': ['Session', 'LogEntry'],
    'TRACK_FIELDS_CHANGES': True,
    'COMPRESS_OLD_LOGS': True,
    'REALTIME_ALERTS': True,
}
```

---
*Sistema projetado para ser escalável e extensível para todas as funcionalidades futuras do WebReceptivo.*
