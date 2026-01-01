"""
URLs para o app de serviços turísticos
"""
from django.urls import path
from . import views

app_name = 'servicos'

urlpatterns = [
    # Categorias
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/criar/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_edit, name='categoria_edit'),
    path('categorias/<int:pk>/deletar/', views.categoria_delete, name='categoria_delete'),
    
    # Subcategorias (Serviços)
    path('servicos/', views.subcategoria_list, name='subcategoria_list'),
    path('servicos/criar/', views.subcategoria_create, name='subcategoria_create'),
    path('servicos/<int:pk>/editar/', views.subcategoria_edit, name='subcategoria_edit'),
    path('servicos/<int:pk>/deletar/', views.subcategoria_delete, name='subcategoria_delete'),
    
    # Tipos de Meia Entrada
    path('tipos-meia/', views.tipo_meia_list, name='tipo_meia_list'),
    path('tipos-meia/criar/', views.tipo_meia_create, name='tipo_meia_create'),
    path('tipos-meia/<int:pk>/editar/', views.tipo_meia_edit, name='tipo_meia_edit'),
    path('tipos-meia/<int:pk>/deletar/', views.tipo_meia_delete, name='tipo_meia_delete'),
    
    # Transfers
    path('transfers/', views.transfer_list, name='transfer_list'),
    path('transfers/criar/', views.transfer_create, name='transfer_create'),
    path('transfers/<int:pk>/editar/', views.transfer_edit, name='transfer_edit'),
    path('transfers/<int:pk>/deletar/', views.transfer_delete, name='transfer_delete'),
    
    # Lançamentos
    path('', views.lancamento_list, name='lancamento_list'),
    path('lancamentos/criar/', views.lancamento_create, name='lancamento_create'),
    path('lancamentos/<int:pk>/', views.lancamento_detail, name='lancamento_detail'),
    path('lancamentos/<int:pk>/editar/', views.lancamento_edit, name='lancamento_edit'),
    path('lancamentos/<int:pk>/deletar/', views.lancamento_delete, name='lancamento_delete'),
    
    # AJAX endpoints
    path('ajax/subcategorias/', views.ajax_load_subcategorias, name='ajax_load_subcategorias'),
    path('ajax/valores/', views.ajax_get_subcategoria_valores, name='ajax_get_subcategoria_valores'),
    path('ajax/tipos-meia/', views.ajax_load_tipos_meia, name='ajax_load_tipos_meia'),
    path('ajax/servico-info/', views.ajax_get_servico_info, name='ajax_get_servico_info'),
]
