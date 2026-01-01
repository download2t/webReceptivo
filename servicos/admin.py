"""
Configuração do Django Admin para serviços turísticos
"""
from django.contrib import admin
from .models import (
    Categoria, SubCategoria, TipoMeiaEntrada, LancamentoServico,
    Transfer, Cliente, OrdemServico, TransferOS
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ordem', 'ativo', 'criado_em')
    list_filter = ('ativo',)
    search_fields = ('nome',)
    ordering = ('ordem', 'nome')


@admin.register(SubCategoria)
class SubCategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'valor_inteira', 'valor_meia', 'valor_infantil', 'ativo')
    list_filter = ('categoria', 'ativo')
    search_fields = ('nome', 'descricao')
    ordering = ('categoria__ordem', 'categoria__nome', 'nome')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('categoria', 'nome', 'descricao', 'ativo')
        }),
        ('Valores', {
            'fields': ('valor_inteira', 'valor_meia', 'valor_infantil')
        }),
        ('Configurações de Meia Entrada', {
            'fields': ('aceita_meia_entrada', 'regras_meia_entrada'),
            'description': 'Defina se este serviço aceita meia entrada e quais as regras aplicáveis'
        }),
        ('Configurações de Isenção', {
            'fields': ('idade_isencao_min', 'idade_isencao_max', 'texto_isencao'),
            'description': 'Configure a faixa etária de isenção para este serviço'
        }),
    )


@admin.register(TipoMeiaEntrada)
class TipoMeiaEntradaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo', 'criado_em')
    list_filter = ('ativo',)
    search_fields = ('nome', 'descricao')


@admin.register(LancamentoServico)
class LancamentoServicoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'data_servico', 'categoria', 'subcategoria', 
        'total_pax', 'valor_total', 'criado_por', 'criado_em'
    )
    list_filter = ('categoria', 'data_servico', 'criado_em')
    search_fields = ('subcategoria__nome', 'obs_publica', 'obs_privada')
    date_hierarchy = 'data_servico'
    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por')
    
    fieldsets = (
        ('Informações do Serviço', {
            'fields': ('data_servico', 'categoria', 'subcategoria')
        }),
        ('Quantidades', {
            'fields': ('qtd_inteira', 'qtd_meia', 'qtd_infantil', 'idades_criancas', 'tipos_meia_entrada'),
            'description': 'Informe as idades das crianças separadas por vírgula e os tipos de meia entrada (um por linha)'
        }),
        ('Valores Unitários (snapshot)', {
            'fields': ('valor_unit_inteira', 'valor_unit_meia', 'valor_unit_infantil'),
            'description': 'Valores capturados automaticamente do cadastro do serviço'
        }),
        ('Observações', {
            'fields': ('obs_publica', 'obs_privada')
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em', 'criado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor', 'ativo', 'criado_em')
    list_filter = ('ativo',)
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'whatsapp', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'email', 'cpf', 'telefone', 'whatsapp')
    ordering = ('nome',)
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'ativo')
        }),
        ('Contatos', {
            'fields': ('email', 'telefone', 'whatsapp')
        }),
        ('Documentos', {
            'fields': ('cpf',)
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )


class LancamentoServicoInline(admin.TabularInline):
    model = LancamentoServico
    extra = 0
    fields = ('data_servico', 'categoria', 'subcategoria', 'qtd_inteira', 'qtd_meia', 'qtd_infantil', 'valor_total')
    readonly_fields = ('valor_total',)


class TransferOSInline(admin.TabularInline):
    model = TransferOS
    extra = 0
    fields = ('data_transfer', 'transfer', 'quantidade', 'valor', 'observacoes')


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('numero_os', 'cliente', 'status', 'data_inicio', 'data_fim', 'valor_total', 'data_criacao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('numero_os', 'cliente__nome')
    date_hierarchy = 'data_criacao'
    readonly_fields = ('numero_os', 'valor_total', 'data_criacao', 'atualizado_em', 'criado_por')
    inlines = [LancamentoServicoInline, TransferOSInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero_os', 'cliente', 'status')
        }),
        ('Período', {
            'fields': ('data_inicio', 'data_fim')
        }),
        ('Roteiro', {
            'fields': ('roteiro',),
            'description': 'Roteiro formatado para o cliente (editável)'
        }),
        ('Valores', {
            'fields': ('valor_total',)
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('data_criacao', 'atualizado_em', 'criado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
        obj.calcular_total()


@admin.register(TransferOS)
class TransferOSAdmin(admin.ModelAdmin):
    list_display = ('ordem_servico', 'transfer', 'data_transfer', 'quantidade', 'valor')
    list_filter = ('data_transfer',)
    search_fields = ('ordem_servico__numero_os', 'transfer__nome')
    date_hierarchy = 'data_transfer'
