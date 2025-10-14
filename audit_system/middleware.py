"""
Middleware para capturar automaticamente dados da requisição para auditoria.
"""
from .signals import set_current_request


class AuditMiddleware:
    """
    Middleware que armazena a requisição atual no thread local
    para permitir acesso aos dados da requisição nos signals
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Armazena a requisição no thread local
        set_current_request(request)
        
        response = self.get_response(request)
        
        # Limpa a requisição após o processamento
        set_current_request(None)
        
        return response
