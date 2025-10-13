from django.urls import path
from . import views
from . import group_views

app_name = 'user_management'

urlpatterns = [
    # =====================
    # GERENCIAMENTO DE USUÁRIOS
    # =====================
    
    # Listagem e busca de usuários
    path('', views.user_list, name='user_list'),
    
    # CRUD de usuários (sem delete - apenas inativar)
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    
    # Ações AJAX de usuários
    path('users/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    
    # Gerenciamento de senhas e permissões de usuários
    path('users/<int:pk>/change-password/', views.user_change_password, name='user_change_password'),
    path('users/<int:pk>/permissions/', views.permissions_manage, name='permissions_manage'),
    
    # =====================
    # GERENCIAMENTO DE GRUPOS
    # =====================
    
    # Listagem e busca de grupos
    path('groups/', group_views.group_list, name='group_list'),
    
    # CRUD de grupos
    path('groups/create/', group_views.group_create, name='group_create'),
    path('groups/<int:pk>/', group_views.group_detail, name='group_detail'),
    path('groups/<int:pk>/edit/', group_views.group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', group_views.group_delete, name='group_delete'),
]
