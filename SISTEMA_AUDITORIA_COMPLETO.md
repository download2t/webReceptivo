# 📊 Sistema de Auditoria - WebReceptivo

## 🎯 **Visão Geral**

O Sistema de Auditoria do WebReceptivo é uma solução completa e extensível para registro, monitoramento e análise de todas as ações realizadas no sistema. Ele foi projetado para fornecer transparência, segurança e rastreabilidade completa das operações.

## ⭐ **Funcionalidades Principais**

### 🔍 **Monitoramento Automático**
- **Captura automática** de todas as ações através de signals do Django
- **Registro de contexto** completo (IP, User-Agent, sessão, timestamp)
- **Detecção de mudanças** em modelos com comparação antes/depois
- **Logs de autenticação** (login, logout, tentativas falhadas)
- **Rastreamento de permissões** e alterações de grupos

### 📈 **Dashboard Interativo**
- **Estatísticas em tempo real** com gráficos dinâticos
- **Métricas de atividade** por período (dia, semana, mês)
- **Usuários mais ativos** e ações mais comuns
- **Indicadores de erro** e monitoramento de falhas
- **Atualização automática** a cada 5 minutos

### 🔎 **Sistema de Busca e Filtros**
- **Filtros avançados** por ação, usuário, data, status
- **Busca textual** em objetos, IPs, mensagens de erro
- **Paginação otimizada** com 50 registros por página
- **Ordenação** por múltiplos critérios
- **Exportação em CSV** com filtros aplicados

### 👤 **Histórico Individual**
- **Perfil completo** de atividades por usuário
- **Ações realizadas** pelo usuário
- **Modificações feitas** no usuário por outros
- **Estatísticas pessoais** de atividade
- **Navegação integrada** com sistema de usuários

### 📊 **Análise e Relatórios**
- **Resumos pré-calculados** para consultas rápidas
- **Estatísticas por período** com granularidade flexível
- **API JSON** para integração com dashboards externos
- **Comandos de manutenção** automatizados
- **Limpeza automática** de logs antigos

## 🏗️ **Arquitetura do Sistema**

### 📦 **Componentes**

```
audit_system/
├── models.py          # Modelo AuditLog e AuditLogSummary
├── signals.py         # Captura automática de eventos
├── middleware.py      # Interceptação de requisições
├── views.py           # Dashboard e interfaces web
├── admin.py           # Interface administrativa
├── decorators.py      # Decoradores para auditoria manual
├── urls.py           # Rotas do sistema
└── management/
    └── commands/      # Comandos de manutenção
```

### 🔄 **Fluxo de Dados**

1. **Captura**: Middleware + Signals capturam eventos
2. **Processamento**: Dados são enriquecidos com contexto
3. **Armazenamento**: Registros salvos no banco otimizado
4. **Visualização**: Dashboard e interfaces web
5. **Manutenção**: Comandos automatizados de limpeza

### 🎨 **Modelo de Dados**

#### **AuditLog** (Registro Principal)
```python
- action: Tipo de ação (USER_CREATED, LOGIN, etc.)
- content_object: Referência genérica ao objeto
- object_repr: Representação textual do objeto
- changes: JSON com alterações (antes/depois)
- user: Usuário que realizou a ação
- timestamp: Data/hora da ação
- ip_address: IP do usuário
- user_agent: Navegador/aplicação
- session_key: Identificador da sessão
- success: Se a ação foi bem-sucedida
- error_message: Mensagem de erro (se houver)
- extra_data: Dados adicionais específicos
```

#### **AuditLogSummary** (Resumos)
```python
- date: Data do resumo
- user: Usuário (opcional)
- action: Tipo de ação
- count: Número de ocorrências
```

## 🚀 **Como Usar**

### 🔧 **Configuração Inicial**

1. **App já instalado** em `INSTALLED_APPS`
2. **Middleware configurado** automaticamente
3. **URLs integradas** em `/audit/`
4. **Migrations aplicadas** automaticamente

### 📊 **Acessando o Dashboard**

1. **Menu do usuário** → "Sistema de Auditoria"
2. **URL direta**: `/audit/`
3. **Requisitos**: Usuário staff (is_staff=True)

### 🔍 **Visualizando Logs**

```python
# Lista geral de logs
/audit/logs/

# Detalhes de um log específico
/audit/logs/<id>/

# Histórico de um usuário
/audit/user/<user_id>/

# Exportar dados (CSV)
/audit/export/csv/
```

### 🛠️ **Comandos de Manutenção**

```bash
# Testar o sistema (criar logs de exemplo)
python manage.py test_audit_system --count=10

# Gerar resumos para otimização
python manage.py generate_audit_summaries --days=30

# Limpar logs antigos (preserva erros)
python manage.py clean_old_audit_logs --days=365 --keep-errors

# Simulação (ver o que seria removido)
python manage.py clean_old_audit_logs --days=365 --dry-run
```

## 💻 **Para Desenvolvedores**

### 🎯 **Auditoria Manual**

#### **Usando Signals Diretos**
```python
from audit_system.signals import log_custom_action, log_user_activation

# Log de ação customizada
log_custom_action(
    action_name='data_export',
    obj=some_object,
    user=request.user,
    request=request,
    extra_data={'export_type': 'users', 'count': 100}
)

# Log de mudança de status
log_user_activation(user, activated=True, request=request)
```

#### **Usando Decoradores**
```python
from audit_system.decorators import audit_action

@audit_action('report_generated')
def generate_report(request):
    # Função será automaticamente auditada
    return generate_user_report()
```

### 🔄 **Extensão para Novos Modelos**

Para auditar novos modelos automaticamente:

1. **Adicionar signals** em `signals.py`:
```python
@receiver(post_save, sender=YourModel)
def log_your_model_changes(sender, instance, created, **kwargs):
    action = 'YOUR_MODEL_CREATED' if created else 'YOUR_MODEL_UPDATED'
    AuditLog.log_action(action=action, obj=instance, request=get_current_request())
```

2. **Adicionar choices** em `models.py`:
```python
ACTION_CHOICES = [
    # ...existentes...
    ('YOUR_MODEL_CREATED', 'Seu Modelo Criado'),
    ('YOUR_MODEL_UPDATED', 'Seu Modelo Atualizado'),
]
```

### 🎨 **Customização da Interface**

#### **CSS Temático**
O sistema usa variáveis CSS do tema principal:
```css
/* Personalizações em static/css/audit.css */
.audit-dashboard { /* Estilos do dashboard */ }
.action-badge { /* Badges de ação */ }
```

#### **Templates Customizáveis**
```
templates/audit_system/
├── dashboard.html      # Dashboard principal
├── logs_list.html      # Lista de logs
├── log_detail.html     # Detalhes do log
└── user_history.html   # Histórico do usuário
```

## 📚 **Tipos de Ação Disponíveis**

### 👤 **Usuários**
- `USER_CREATED` - Usuário criado
- `USER_UPDATED` - Usuário atualizado
- `USER_DELETED` - Usuário excluído
- `USER_ACTIVATED` - Usuário ativado
- `USER_DEACTIVATED` - Usuário desativado
- `USER_PASSWORD_CHANGED` - Senha alterada
- `USER_LOGIN` - Login realizado
- `USER_LOGOUT` - Logout realizado
- `USER_LOGIN_FAILED` - Tentativa de login falhada

### 👥 **Grupos**
- `GROUP_CREATED` - Grupo criado
- `GROUP_UPDATED` - Grupo atualizado
- `GROUP_DELETED` - Grupo excluído
- `GROUP_USER_ADDED` - Usuário adicionado ao grupo
- `GROUP_USER_REMOVED` - Usuário removido do grupo
- `GROUP_PERMISSION_ADDED` - Permissão adicionada ao grupo
- `GROUP_PERMISSION_REMOVED` - Permissão removida do grupo

### 🔐 **Permissões**
- `PERMISSION_GRANTED` - Permissão concedida
- `PERMISSION_REVOKED` - Permissão revogada
- `ROLE_CHANGED` - Papel/função alterada

### ⚙️ **Sistema**
- `SYSTEM_ACCESS` - Acesso ao sistema
- `DATA_EXPORT` - Dados exportados
- `SETTINGS_CHANGED` - Configurações alteradas
- `CUSTOM_ACTION` - Ação customizada

## 🔒 **Segurança e Privacidade**

### 🛡️ **Proteções Implementadas**
- **Dados sensíveis**: Senhas nunca são registradas
- **Acesso controlado**: Apenas staff pode visualizar logs
- **IPs anônimos**: Suporte a proxies e load balancers
- **Integridade**: Logs são somente-leitura via interface web
- **Retenção**: Limpeza automática de logs antigos

### 🔐 **Controle de Acesso**
```python
# Verificação automática em todas as views
@staff_member_required
def audit_view(request):
    # Apenas usuários staff podem acessar
```

### 🗃️ **Gestão de Dados**
- **Backup automático** antes da limpeza
- **Compressão** de dados antigos
- **Índices otimizados** para consultas rápidas
- **Particionamento** por data (futuro)

## 📊 **Performance e Otimização**

### ⚡ **Otimizações Implementadas**
- **Índices de banco** em campos críticos
- **Select related** para evitar N+1 queries
- **Paginação eficiente** com LIMIT/OFFSET
- **Cache de resumos** para estatísticas rápidas
- **Queries assíncronas** para gráficos (futuro)

### 📈 **Monitoramento de Performance**
```python
# Comando para verificar performance
python manage.py audit_performance_check

# Resumos pré-calculados para dashboards rápidos
python manage.py generate_audit_summaries --days=7
```

## 🔧 **Manutenção e Troubleshooting**

### 🐛 **Problemas Comuns**

#### **Logs não aparecem**
```bash
# Verificar se o middleware está ativo
python manage.py shell
>>> from django.conf import settings
>>> 'audit_system.middleware.AuditMiddleware' in settings.MIDDLEWARE

# Testar criação manual
python manage.py test_audit_system --count=1
```

#### **Performance lenta**
```bash
# Gerar resumos para otimização
python manage.py generate_audit_summaries

# Limpar logs antigos
python manage.py clean_old_audit_logs --days=90 --dry-run
```

#### **Erro de permissão**
- Verificar se o usuário tem `is_staff=True`
- Confirmar que as URLs estão configuradas
- Checar se o middleware está carregando

### 📊 **Estatísticas do Sistema**

```bash
# Ver estatísticas gerais
python manage.py shell
>>> from audit_system.models import AuditLog
>>> AuditLog.objects.count()  # Total de logs
>>> AuditLog.objects.filter(success=False).count()  # Erros
```

## 🚀 **Roadmap e Melhorias Futuras**

### 🎯 **Versão 2.0** (Planejada)
- [ ] **Dashboard em tempo real** com WebSockets
- [ ] **Alertas automáticos** para ações suspeitas
- [ ] **API REST completa** para integração externa
- [ ] **Machine Learning** para detecção de anomalias
- [ ] **Exportação** para sistemas SIEM
- [ ] **Relatórios avançados** em PDF
- [ ] **Workflow de aprovação** para ações críticas

### 🔮 **Funcionalidades Avançadas**
- [ ] **Auditoria de arquivos** (uploads, downloads)
- [ ] **Geolocalização** de acessos
- [ ] **Análise de comportamento** de usuários
- [ ] **Backup automático** de logs críticos
- [ ] **Integração com Active Directory**
- [ ] **Notificações** via email/Slack
- [ ] **Dashboard mobile** responsivo

## 📞 **Suporte e Contribuição**

### 🤝 **Como Contribuir**
1. Fork do projeto
2. Criar branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit das alterações (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Criar Pull Request

### 🐛 **Reportar Bugs**
- Usar o sistema de Issues do Git
- Incluir logs de erro completos
- Especificar versão do Django e Python
- Descrever passos para reproduzir

### 💡 **Sugestões**
- Abrir issue com tag "enhancement"
- Descrever caso de uso detalhadamente
- Incluir mockups se relevante

---

## 📝 **Changelog**

### **v1.0.0** (14/10/2025)
- ✅ Sistema completo de auditoria implementado
- ✅ Dashboard interativo com estatísticas
- ✅ Interface web completa para visualização
- ✅ Captura automática via signals
- ✅ Middleware para contexto de requisição
- ✅ Comandos de manutenção
- ✅ Exportação em CSV
- ✅ Histórico individual por usuário
- ✅ Interface administrativa
- ✅ Decoradores para auditoria manual
- ✅ Sistema de filtros avançados
- ✅ Documentação completa

---

**© 2025 WebReceptivo - Sistema de Auditoria**  
*Transparência, Segurança e Rastreabilidade Total*
