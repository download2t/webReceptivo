from django.urls import path
from . import views

app_name = 'company_settings'

urlpatterns = [
    # Main pages
    path('', views.settings_overview, name='overview'),
    path('empresa/', views.company_settings_view, name='company'),
    path('sistema/', views.system_settings_view, name='system'),
    path('smtp/', views.smtp_settings_view, name='smtp'),
    
    # AJAX endpoints
    path('ajax/current-datetime/', views.get_current_datetime, name='current_datetime'),
    path('ajax/test-smtp/', views.test_smtp_connection, name='test_smtp'),
    path('ajax/validate-cep/', views.validate_cep, name='validate_cep'),
]
