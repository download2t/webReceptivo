from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta
import time
import os


def get_system_uptime():
    """
    Calcula o uptime do sistema Django
    """
    try:
        # Tempo desde que o processo Python iniciou
        boot_time = time.time() - time.process_time()
        uptime_seconds = time.time() - boot_time
        
        # Converter para formato legível
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        if days > 0:
            return f"{days} dia{'s' if days != 1 else ''}, {hours} hora{'s' if hours != 1 else ''}"
        elif hours > 0:
            return f"{hours} hora{'s' if hours != 1 else ''}, {minutes} minuto{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes} minuto{'s' if minutes != 1 else ''}"
            
    except Exception:
        # Fallback para tempo desde o import do módulo
        if not hasattr(get_system_uptime, 'start_time'):
            get_system_uptime.start_time = time.time()
        
        uptime_seconds = time.time() - get_system_uptime.start_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        if days > 0:
            return f"{days} dia{'s' if days != 1 else ''}, {hours} hora{'s' if hours != 1 else ''}"
        elif hours > 0:
            return f"{hours} hora{'s' if hours != 1 else ''}, {minutes} minuto{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes} minuto{'s' if minutes != 1 else ''}"


@login_required
def dashboard(request):
    """
    Dashboard principal do sistema com estatísticas e informações
    """
    # Mock data para demonstração - em produção viria do banco
    context = {
        'stats': {
            'reservas_hoje': 12,
            'receita_mensal': 'R$ 45.680,00',
            'clientes_ativos': 156,
            'pendencias': 3,
        },
        'recent_activities': [
            {
                'title': 'Nova reserva criada',
                'description': 'Cliente João Silva - Tour Centro Histórico',
                'created_at': timezone.now() - timedelta(minutes=15)
            },
            {
                'title': 'Pagamento recebido',
                'description': 'Reserva #1234 - R$ 350,00',
                'created_at': timezone.now() - timedelta(hours=1)
            },
            {
                'title': 'Cliente cadastrado',
                'description': 'Maria Oliveira adicionada ao sistema',
                'created_at': timezone.now() - timedelta(hours=2)
            },
        ],
        'system_uptime': get_system_uptime(),
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required 
def home_redirect(request):
    """
    Redireciona para o dashboard (view helper)
    """
    return render(request, 'core/dashboard.html')
