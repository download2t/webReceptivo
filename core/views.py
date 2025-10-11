from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta


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
        'system_uptime': '2 dias, 14 horas',
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required 
def home_redirect(request):
    """
    Redireciona para o dashboard (view helper)
    """
    return render(request, 'core/dashboard.html')
