"""
URLs do sistema de auditoria
"""
from django.urls import path
from . import views

app_name = 'audit_system'

urlpatterns = [
    # Dashboard principal
    path('', views.audit_dashboard, name='dashboard'),
    
    # Lista de logs
    path('logs/', views.audit_logs_list, name='logs_list'),
    
    # Detalhes de um log
    path('logs/<int:log_id>/', views.audit_log_detail, name='log_detail'),
    
    # Exportação
    path('export/csv/', views.audit_export_csv, name='export_csv'),
    
    # API para estatísticas
    path('api/stats/', views.audit_api_stats, name='api_stats'),
    
    # Histórico de usuário específico
    path('user/<int:user_id>/', views.user_audit_history, name='user_history'),
]
