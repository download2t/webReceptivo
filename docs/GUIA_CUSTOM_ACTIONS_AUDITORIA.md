# 🔧 GUIA DE CUSTOM ACTIONS - Sistema de Auditoria WebReceptivo

## 📋 **O QUE SÃO CUSTOM ACTIONS?**

As **Custom Actions** são uma funcionalidade poderosa do sistema de auditoria que permite monitorar **qualquer ação específica** da sua aplicação que não é automaticamente capturada pelos sinais padrão do Django (como criação, edição, exclusão de modelos).

### 🎯 **Casos de Uso Principais**
- **Exportação de dados** (CSV, PDF, Excel)
- **Operações de sistema** (backup, restore, limpeza)
- **Ações de negócio** (geração de relatórios, aprovações)
- **Integrações externas** (APIs, sincronizações)
- **Operações críticas** (configurações, migrações)

---

## 🚀 **MÉTODO 1: USANDO DECORADORES (RECOMENDADO)**

### ✅ **Implementação Simples**

```python
from audit_system.decorators import audit_action

@audit_action('export_users', 'Usuários exportados com sucesso')
def export_users_csv(request):
    """Exportar usuários para CSV"""
    # Sua lógica de exportação aqui
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="usuarios.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Data Cadastro'])
    
    for user in User.objects.all():
        writer.writerow([user.username, user.email, user.date_joined])
    
    return response
```

### ✅ **Com Parâmetros Dinâmicos**

```python
@audit_action('generate_report')
def generate_monthly_report(request, year, month):
    """Gerar relatório mensal"""
    # Lógica do relatório
    report_data = process_monthly_data(year, month)
    
    # O decorador automaticamente captura os parâmetros
    return render(request, 'reports/monthly.html', {
        'report': report_data,
        'period': f"{month}/{year}"
    })
```

### ✅ **Para Ações com Objetos Específicos**

```python
from audit_system.decorators import audit_model_action

@audit_model_action('user_profile_view', 'user_id')
def user_profile_detail(request, user_id):
    """Visualizar perfil detalhado do usuário"""
    user = get_object_or_404(User, pk=user_id)
    
    # A ação será registrada automaticamente
    return render(request, 'users/profile_detail.html', {'user': user})
```

---

## ⚙️ **MÉTODO 2: USANDO SINAIS DIRETOS (FLEXÍVEL)**

### ✅ **Importação**

```python
from audit_system.signals import log_custom_action
```

### ✅ **Ação Simples**

```python
def backup_database(request):
    """Fazer backup do banco de dados"""
    try:
        # Sua lógica de backup
        backup_file = create_database_backup()
        
        # Registrar sucesso
        log_custom_action(
            action_name='database_backup',
            user=request.user,
            request=request,
            success=True,
            extra_data={
                'backup_file': backup_file,
                'backup_size': get_file_size(backup_file),
                'backup_type': 'full'
            }
        )
        
        messages.success(request, 'Backup realizado com sucesso!')
        
    except Exception as e:
        # Registrar erro
        log_custom_action(
            action_name='database_backup',
            user=request.user,
            request=request,
            success=False,
            error_message=str(e),
            extra_data={
                'error_type': type(e).__name__,
                'attempted_backup_type': 'full'
            }
        )
        
        messages.error(request, f'Erro no backup: {e}')
```

### ✅ **Ação com Objeto Relacionado**

```python
def approve_document(request, document_id):
    """Aprovar documento"""
    document = get_object_or_404(Document, pk=document_id)
    
    # Salvar estado anterior
    old_status = document.status
    
    # Aplicar aprovação
    document.status = 'approved'
    document.approved_by = request.user
    document.approved_at = timezone.now()
    document.save()
    
    # Registrar ação customizada
    log_custom_action(
        action_name='document_approval',
        obj=document,  # Objeto sendo modificado
        user=request.user,
        request=request,
        success=True,
        changes={
            'status': {'old': old_status, 'new': 'approved'},
            'approved_by': {'old': None, 'new': request.user.username}
        },
        extra_data={
            'document_type': document.type,
            'department': document.department,
            'urgency': document.urgency_level
        }
    )
```

### ✅ **Ação em Lote**

```python
def bulk_update_users(request):
    """Atualização em lote de usuários"""
    user_ids = request.POST.getlist('user_ids')
    new_status = request.POST.get('status')
    
    updated_count = 0
    
    for user_id in user_ids:
        try:
            user = User.objects.get(pk=user_id)
            old_status = user.is_active
            
            if new_status == 'active':
                user.is_active = True
            else:
                user.is_active = False
            
            user.save()
            updated_count += 1
            
            # Log individual para cada usuário
            log_custom_action(
                action_name='bulk_user_status_update',
                obj=user,
                user=request.user,
                request=request,
                success=True,
                changes={
                    'is_active': {'old': old_status, 'new': user.is_active}
                },
                extra_data={
                    'batch_operation': True,
                    'total_in_batch': len(user_ids),
                    'operation_type': new_status
                }
            )
            
        except Exception as e:
            # Log do erro
            log_custom_action(
                action_name='bulk_user_status_update',
                user=request.user,
                request=request,
                success=False,
                error_message=str(e),
                extra_data={
                    'failed_user_id': user_id,
                    'batch_operation': True,
                    'operation_type': new_status
                }
            )
    
    # Log do resumo da operação
    log_custom_action(
        action_name='bulk_operation_summary',
        user=request.user,
        request=request,
        success=True,
        extra_data={
            'operation_type': 'bulk_user_status_update',
            'total_requested': len(user_ids),
            'total_successful': updated_count,
            'total_failed': len(user_ids) - updated_count
        }
    )
```

---

## 🎨 **EXEMPLOS PRÁTICOS POR CATEGORIA**

### 📊 **Relatórios e Exportações**

```python
# Geração de relatório
log_custom_action(
    action_name='monthly_report_generated',
    user=request.user,
    request=request,
    success=True,
    extra_data={
        'report_type': 'sales_summary',
        'period': '2025-10',
        'total_records': 1250,
        'export_format': 'PDF'
    }
)

# Exportação de dados
log_custom_action(
    action_name='data_export',
    user=request.user,
    request=request,
    success=True,
    extra_data={
        'export_type': 'customer_list',
        'format': 'Excel',
        'filtered_by': 'active_customers',
        'record_count': 500
    }
)
```

### 🔧 **Operações de Sistema**

```python
# Backup automático
log_custom_action(
    action_name='automated_backup',
    user=None,  # Ação do sistema
    success=True,
    extra_data={
        'backup_type': 'incremental',
        'files_backed_up': 1847,
        'backup_duration': '00:02:34',
        'storage_used': '2.5GB'
    }
)

# Limpeza de arquivos temporários
log_custom_action(
    action_name='temp_files_cleanup',
    user=request.user,
    request=request,
    success=True,
    extra_data={
        'files_deleted': 23,
        'space_freed': '150MB',
        'cleanup_type': 'manual'
    }
)
```

### 🔄 **Integrações Externas**

```python
# Sincronização com API externa
log_custom_action(
    action_name='external_api_sync',
    user=request.user,
    request=request,
    success=True,
    extra_data={
        'api_endpoint': 'https://api.partner.com/sync',
        'records_sent': 100,
        'records_received': 95,
        'sync_duration': '00:00:45'
    }
)
```

### 📋 **Aprovações e Workflows**

```python
# Processo de aprovação
log_custom_action(
    action_name='workflow_approval',
    obj=document,
    user=request.user,
    request=request,
    success=True,
    extra_data={
        'workflow_step': 'manager_approval',
        'approval_level': 2,
        'next_approver': 'director',
        'comments': 'Approved with conditions'
    }
)
```

---

## 🔍 **VISUALIZAÇÃO NO DASHBOARD**

### 📊 **Como Aparece**

Quando você usa custom actions, elas aparecem no dashboard de auditoria como:

- **Nome da Ação**: O `action_name` que você definiu
- **Tipo**: "CUSTOM_ACTION" 
- **Usuário**: Quem executou (se aplicável)
- **Objeto**: Objeto relacionado (se aplicável)
- **Status**: Sucesso/Erro com ícone colorido
- **Detalhes**: Todos os `extra_data` em formato estruturado
- **Timestamp**: Data e hora exatas

### 🎨 **Badges Customizados**

O sistema automaticamente gera badges coloridos para suas custom actions:

```css
/* Exemplos de como ficam no CSS */
.action-badge.action-export_users { background: #28a745; color: white; }
.action-badge.action-database_backup { background: #17a2b8; color: white; }
.action-badge.action-document_approval { background: #ffc107; color: #212529; }
```

---

## 🛠️ **MELHORES PRÁTICAS**

### ✅ **Nomenclatura**

```python
# ✅ BOM - Descritivo e consistente
'user_password_reset'
'document_approval_level_2'  
'monthly_report_generated'
'backup_database_full'

# ❌ EVITAR - Vago ou inconsistente
'action1'
'do_stuff'
'update'
```

### ✅ **Dados Extras Úteis**

```python
extra_data={
    # Contexto da operação
    'operation_type': 'bulk_update',
    'affected_count': 50,
    
    # Performance
    'duration_seconds': 2.5,
    'memory_used': '15MB',
    
    # Resultados
    'success_rate': '95%',
    'failed_items': ['item1', 'item2'],
    
    # Configurações
    'export_format': 'PDF',
    'include_images': True,
    
    # Metadados
    'triggered_by': 'scheduled_job',
    'batch_id': 'batch_2025_10_001'
}
```

### ✅ **Tratamento de Erros**

```python
def risky_operation(request):
    try:
        # Operação que pode falhar
        result = perform_complex_task()
        
        # Log de sucesso
        log_custom_action(
            action_name='complex_task_execution',
            user=request.user,
            request=request,
            success=True,
            extra_data={'result_id': result.id, 'processing_time': result.duration}
        )
        
    except ValidationError as e:
        # Erro de validação
        log_custom_action(
            action_name='complex_task_execution',
            user=request.user,
            request=request,
            success=False,
            error_message=f"Validation failed: {e}",
            extra_data={'error_type': 'validation', 'invalid_fields': e.error_dict}
        )
        
    except DatabaseError as e:
        # Erro de banco
        log_custom_action(
            action_name='complex_task_execution',
            user=request.user,
            request=request,
            success=False,
            error_message=f"Database error: {e}",
            extra_data={'error_type': 'database', 'query': str(e)}
        )
        
    except Exception as e:
        # Erro genérico
        log_custom_action(
            action_name='complex_task_execution',
            user=request.user,
            request=request,
            success=False,
            error_message=str(e),
            extra_data={'error_type': type(e).__name__, 'stack_trace': traceback.format_exc()[:500]}
        )
```

---

## 🚀 **AUTOMATIZAÇÃO COM MANAGEMENT COMMANDS**

### ✅ **Command Personalizado**

```python
# management/commands/daily_maintenance.py
from django.core.management.base import BaseCommand
from audit_system.signals import log_custom_action

class Command(BaseCommand):
    help = 'Executar manutenção diária do sistema'
    
    def handle(self, *args, **options):
        try:
            # Executar limpeza
            deleted_files = self.cleanup_temp_files()
            optimized_tables = self.optimize_database()
            
            # Log de sucesso
            log_custom_action(
                action_name='daily_maintenance',
                user=None,  # Comando automático
                success=True,
                extra_data={
                    'deleted_temp_files': deleted_files,
                    'optimized_tables': optimized_tables,
                    'execution_mode': 'scheduled',
                    'duration': self.get_execution_time()
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Manutenção concluída: {deleted_files} arquivos removidos')
            )
            
        except Exception as e:
            # Log de erro
            log_custom_action(
                action_name='daily_maintenance',
                user=None,
                success=False,
                error_message=str(e),
                extra_data={
                    'execution_mode': 'scheduled',
                    'error_stage': 'cleanup' if 'cleanup' in str(e) else 'optimization'
                }
            )
            
            self.stdout.write(
                self.style.ERROR(f'Erro na manutenção: {e}')
            )
```

---

## 📊 **ANALYTICS E RELATÓRIOS**

### ✅ **Consultas Úteis**

```python
from audit_system.models import AuditLog

# Top 10 custom actions mais usadas
top_actions = AuditLog.objects.filter(
    action='CUSTOM_ACTION'
).values(
    'extra_data__custom_action_name'
).annotate(
    count=Count('id')
).order_by('-count')[:10]

# Custom actions por usuário
user_customs = AuditLog.objects.filter(
    action='CUSTOM_ACTION',
    user__isnull=False
).values(
    'user__username',
    'extra_data__custom_action_name'
).annotate(
    count=Count('id')
).order_by('-count')

# Ações que mais falham
failed_actions = AuditLog.objects.filter(
    action='CUSTOM_ACTION',
    success=False
).values(
    'extra_data__custom_action_name'
).annotate(
    fail_count=Count('id')
).order_by('-fail_count')[:5]
```

---

## 🎯 **CASOS DE USO AVANÇADOS**

### ✅ **Audit Chain (Cadeia de Auditoria)**

```python
def process_document_workflow(request, document_id):
    """Processar documento através de workflow completo"""
    document = get_object_or_404(Document, pk=document_id)
    
    # 1. Início do processo
    workflow_id = str(uuid.uuid4())
    log_custom_action(
        action_name='workflow_started',
        obj=document,
        user=request.user,
        request=request,
        success=True,
        extra_data={
            'workflow_id': workflow_id,
            'workflow_type': 'document_approval',
            'total_steps': 4
        }
    )
    
    # 2. Validação
    try:
        validation_result = validate_document(document)
        log_custom_action(
            action_name='workflow_step_validation',
            obj=document,
            user=request.user,
            request=request,
            success=validation_result.is_valid,
            extra_data={
                'workflow_id': workflow_id,
                'step': 1,
                'validation_errors': validation_result.errors if not validation_result.is_valid else None
            }
        )
        
        if not validation_result.is_valid:
            return redirect('document_fix', document.id)
            
    except Exception as e:
        log_custom_action(
            action_name='workflow_step_validation',
            obj=document,
            user=request.user,
            request=request,
            success=False,
            error_message=str(e),
            extra_data={'workflow_id': workflow_id, 'step': 1}
        )
        raise
    
    # 3. Aprovação automática se possível
    if document.can_auto_approve():
        log_custom_action(
            action_name='workflow_auto_approval',
            obj=document,
            user=None,  # Sistema automático
            success=True,
            extra_data={
                'workflow_id': workflow_id,
                'step': 2,
                'auto_approval_reason': 'meets_criteria'
            }
        )
    else:
        # 4. Envio para aprovação manual
        assign_to_approver(document, request.user)
        log_custom_action(
            action_name='workflow_manual_approval_required',
            obj=document,
            user=request.user,
            request=request,
            success=True,
            extra_data={
                'workflow_id': workflow_id,
                'step': 2,
                'assigned_to': document.approver.username
            }
        )
```

---

## 📚 **RESUMO DE REFERÊNCIA RÁPIDA**

### 🔧 **Imports Necessários**

```python
# Para decoradores
from audit_system.decorators import audit_action, audit_model_action

# Para sinais diretos
from audit_system.signals import log_custom_action

# Para consultas
from audit_system.models import AuditLog
```

### ⚡ **Sintaxe Rápida**

```python
# Decorador simples
@audit_action('action_name', 'Success message')
def my_view(request): pass

# Sinal direto
log_custom_action(
    action_name='my_action',
    user=request.user,
    request=request,
    success=True,
    extra_data={'key': 'value'}
)
```

### 🎨 **Parâmetros Principais**

- **action_name** (obrigatório): Nome único da ação
- **obj** (opcional): Objeto Django relacionado
- **user** (opcional): Usuário que executou (None para sistema)
- **request** (opcional): Request HTTP para capturar IP/User-Agent
- **success** (padrão True): Status da operação
- **error_message** (opcional): Mensagem de erro se success=False
- **extra_data** (opcional): Dict com dados adicionais
- **changes** (opcional): Dict com mudanças antes/depois

---

## 🎉 **CONCLUSÃO**

As **Custom Actions** transformam o sistema de auditoria de um simples log de CRUD em uma **ferramenta completa de monitoramento empresarial**. Com elas você pode:

✅ **Monitorar qualquer ação crítica do negócio**  
✅ **Criar dashboards personalizados por departamento**  
✅ **Gerar relatórios de compliance automaticamente**  
✅ **Detectar padrões e otimizar processos**  
✅ **Investigar problemas com contexto completo**

**🚀 Comece hoje mesmo implementando custom actions nas suas operações mais importantes!**

---

*Guia criado para WebReceptivo v1.3.0 - Outubro 2025*  
*Para dúvidas, consulte a documentação técnica em SISTEMA_AUDITORIA_COMPLETO.md*
