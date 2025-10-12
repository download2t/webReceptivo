from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    # Listagem e busca
    path('', views.user_list, name='user_list'),
    
    # CRUD de usuários
    path('create/', views.user_create, name='user_create'),
    path('<int:pk>/', views.user_detail, name='user_detail'),
    path('<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # Ações AJAX
    path('<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    
    # Gerenciamento de senhas e permissões
    path('<int:pk>/change-password/', views.user_change_password, name='user_change_password'),
    path('<int:pk>/permissions/', views.permissions_manage, name='permissions_manage'),
]
