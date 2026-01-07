"""
Custom template tags and filters for servicos app
"""
from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()


@register.filter
def mul(value, arg):
    """
    Multiplica dois valores
    Uso: {{ valor1|mul:valor2 }}
    """
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError, InvalidOperation):
        return 0

@register.filter
def get_item(dictionary, key):
    """
    Obtém um item de um dicionário
    Uso: {{ dict|get_item:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
