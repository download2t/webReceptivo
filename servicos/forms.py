"""
Formulários para gerenciamento de serviços
"""
from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import (
    Categoria, SubCategoria, TipoMeiaEntrada, LancamentoServico,
    Transfer, Cliente, OrdemServico, TransferOrdemServico
)


class CategoriaForm(forms.ModelForm):
    """Formulário para cadastro de categorias"""
    
    class Meta:
        model = Categoria
        fields = ['nome', 'ativo', 'ordem']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Atrativos, Hospedagem, Transporte'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordem': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }


class SubCategoriaForm(forms.ModelForm):
    """Formulário para cadastro de serviços (subcategorias)"""
    
    class Meta:
        model = SubCategoria
        fields = [
            'categoria', 'nome', 'descricao',
            'valor_inteira',
            'aceita_meia_entrada', 'valor_meia', 'regras_meia_entrada',
            'permite_infantil', 'valor_infantil', 'idade_minima_infantil', 'idade_maxima_infantil',
            'possui_isencao', 'idade_isencao_min', 'idade_isencao_max', 'texto_isencao',
            'tem_idade_minima', 'idade_minima',
            'ativo'
        ]
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do serviço'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição detalhada do serviço'
            }),
            'valor_inteira': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'aceita_meia_entrada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'valor_meia': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.00'
            }),
            'regras_meia_entrada': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ex: EST. DE 9 A 16 ANOS COM RG, EST. COM CARTEIRINHA, PROF BR, IDOSO, DOADOR DE SANGUE, POL.BR, PCD E ACOM.'
            }),
            'permite_infantil': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'valor_infantil': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.00'
            }),
            'idade_minima_infantil': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '17',
                'placeholder': '0'
            }),
            'idade_maxima_infantil': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '17',
                'placeholder': '17'
            }),
            'possui_isencao': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'idade_isencao_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '17',
                'placeholder': '0'
            }),
            'idade_isencao_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '17',
                'placeholder': '6'
            }),
            'texto_isencao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: CRIANÇA DE 0 A 6 ANOS'
            }),
            'tem_idade_minima': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'idade_minima': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '17',
                'placeholder': '0'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas categorias ativas
        self.fields['categoria'].queryset = Categoria.objects.filter(ativo=True)


class TipoMeiaEntradaForm(forms.ModelForm):
    """Formulário para tipos de meia entrada"""
    
    class Meta:
        model = TipoMeiaEntrada
        fields = ['nome', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Estudante, Idoso, Doador de Sangue'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descrição opcional'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LancamentoServicoForm(forms.ModelForm):
    """Formulário para lançamento de serviços"""
    
    # Campos ocultos para armazenar dados em JSON
    idades_criancas_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    tipos_meia_json = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    class Meta:
        model = LancamentoServico
        fields = [
            'data_servico', 'categoria', 'subcategoria',
            'qtd_inteira', 'qtd_meia', 'qtd_infantil',
            'obs_publica', 'obs_privada'
        ]
        widgets = {
            'data_servico': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_categoria'
            }),
            'subcategoria': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_subcategoria'
            }),
            'qtd_inteira': forms.NumberInput(attrs={
                'class': 'form-control qty-input',
                'min': '0',
                'value': '0'
            }),
            'qtd_meia': forms.NumberInput(attrs={
                'class': 'form-control qty-input',
                'min': '0',
                'value': '0',
                'id': 'id_qtd_meia'
            }),
            'qtd_infantil': forms.NumberInput(attrs={
                'class': 'form-control qty-input',
                'min': '0',
                'value': '0',
                'id': 'id_qtd_infantil'
            }),
            'obs_publica': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações que aparecerão na OS e para o cliente'
            }),
            'obs_privada': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Anotações internas (não aparece para o cliente)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Marcar campos de quantidade como não obrigatórios
        self.fields['qtd_inteira'].required = False
        self.fields['qtd_meia'].required = False
        self.fields['qtd_infantil'].required = False
        self.fields['obs_publica'].required = False
        self.fields['obs_privada'].required = False
        
        # Filtrar apenas categorias ativas
        self.fields['categoria'].queryset = Categoria.objects.filter(ativo=True)
        
        # Se estiver editando, filtrar subcategorias pela categoria
        if self.instance and self.instance.pk and self.instance.categoria:
            self.fields['subcategoria'].queryset = SubCategoria.objects.filter(
                categoria=self.instance.categoria,
                ativo=True
            )
        else:
            # Na criação, inicialmente vazio
            self.fields['subcategoria'].queryset = SubCategoria.objects.none()
        
        # Se houver categoria no POST, filtrar subcategorias
        if 'categoria' in self.data:
            try:
                categoria_id = int(self.data.get('categoria'))
                self.fields['subcategoria'].queryset = SubCategoria.objects.filter(
                    categoria_id=categoria_id,
                    ativo=True
                )
            except (ValueError, TypeError):
                pass
        
        # Se estiver editando, preencher campos hidden com dados JSON
        if self.instance and self.instance.pk:
            import json
            if self.instance.idades_criancas:
                self.fields['idades_criancas_json'].initial = json.dumps(self.instance.idades_criancas)
            if self.instance.tipos_meia_entrada:
                # tipos_meia_entrada é um TextField, não ManyToMany
                # Converter texto em lista para JSON
                tipos_lista = [t.strip() for t in self.instance.tipos_meia_entrada.split('\n') if t.strip()]
                self.fields['tipos_meia_json'].initial = json.dumps(tipos_lista)
    
    def clean(self):
        """Validações customizadas"""
        cleaned_data = super().clean()
        
        # Tratar None como 0 para campos de quantidade
        qtd_inteira = cleaned_data.get('qtd_inteira') or 0
        qtd_meia = cleaned_data.get('qtd_meia') or 0
        qtd_infantil = cleaned_data.get('qtd_infantil') or 0
        
        # Atualizar valores no cleaned_data
        cleaned_data['qtd_inteira'] = qtd_inteira
        cleaned_data['qtd_meia'] = qtd_meia
        cleaned_data['qtd_infantil'] = qtd_infantil
        
        categoria = cleaned_data.get('categoria')
        subcategoria = cleaned_data.get('subcategoria')
        idades_criancas_json = cleaned_data.get('idades_criancas_json', '[]')
        tipos_meia_json = cleaned_data.get('tipos_meia_json', '[]')
        
        # Validar que pelo menos uma quantidade foi informada
        if qtd_inteira == 0 and qtd_meia == 0 and qtd_infantil == 0:
            raise ValidationError(
                'Informe ao menos uma quantidade (Inteira, Meia ou Infantil)'
            )
        
        # Validar idades das crianças
        if qtd_infantil > 0:
            try:
                import json
                idades = json.loads(idades_criancas_json) if idades_criancas_json else []
                if len(idades) != qtd_infantil:
                    raise ValidationError(
                        f'É necessário informar a idade de todas as {qtd_infantil} criança(s)'
                    )
                
                # Validar limite máximo de 17 anos
                for idade in idades:
                    if idade > 17:
                        raise ValidationError(
                            f'A idade máxima permitida para infantil é 17 anos. Idade informada: {idade} anos.'
                        )
                
                # Validar idade mínima do serviço
                if subcategoria and subcategoria.tem_idade_minima and subcategoria.idade_minima > 0:
                    for idade in idades:
                        if idade < subcategoria.idade_minima:
                            raise ValidationError(
                                f'Este serviço exige idade mínima de {subcategoria.idade_minima} anos. '
                                f'Criança com {idade} anos não atende o requisito.'
                            )
                
                # Salvar as idades no formato correto
                cleaned_data['idades_criancas'] = idades
            except (ValueError, json.JSONDecodeError):
                raise ValidationError(
                    'Formato inválido para as idades das crianças'
                )
        
        # Validar tipos de meia entrada obrigatório quando qtd_meia > 0
        if qtd_meia > 0:
            # Verificar se o serviço aceita meia entrada
            if subcategoria and not subcategoria.aceita_meia_entrada:
                raise ValidationError(
                    'Este serviço não aceita meia entrada'
                )
            else:
                try:
                    import json
                    tipos_ids = json.loads(tipos_meia_json) if tipos_meia_json else []
                    if len(tipos_ids) != qtd_meia:
                        raise ValidationError(
                            f'É necessário selecionar o tipo para todas as {qtd_meia} meia(s)'
                        )
                    # Salvar os IDs para uso posterior
                    cleaned_data['tipos_meia_ids'] = tipos_ids
                except (ValueError, json.JSONDecodeError):
                    raise ValidationError(
                        'Formato inválido para os tipos de meia entrada'
                    )
        
        # Validar que subcategoria pertence à categoria
        if categoria and subcategoria:
            if subcategoria.categoria != categoria:
                raise ValidationError(
                    'O serviço selecionado não pertence à categoria escolhida'
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        """Salvar o formulário processando idades e tipos de meia"""
        import json
        instance = super().save(commit=False)
        
        # Processar idades das crianças
        idades_json = self.cleaned_data.get('idades_criancas_json', '[]')
        try:
            instance.idades_criancas = json.loads(idades_json) if idades_json else []
        except (ValueError, json.JSONDecodeError):
            instance.idades_criancas = []
        
        if commit:
            instance.save()
            
            # Processar tipos de meia entrada
            tipos_ids = self.cleaned_data.get('tipos_meia_ids', [])
            if tipos_ids:
                instance.tipos_meia_entrada.set(tipos_ids)
        
        return instance


class TransferForm(forms.ModelForm):
    """Formulário para cadastro de transfers"""
    
    class Meta:
        model = Transfer
        fields = ['nome', 'valor', 'descricao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do Transfer'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.00'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição do transfer (opções, rotas, etc.)'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClienteForm(forms.ModelForm):
    """Formulário para cadastro de clientes"""
    
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'whatsapp', 'cpf', 'observacoes', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do cliente'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(45) 99999-9999'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(45) 99999-9999'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre o cliente'
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OrdemServicoForm(forms.ModelForm):
    """Formulário para cadastro de Ordens de Serviço"""
    
    class Meta:
        model = OrdemServico
        fields = ['clientes', 'hospedagem', 'data_inicio', 'data_fim', 'status', 'roteiro', 'observacoes']
        widgets = {
            'clientes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome(s) do(s) cliente(s) desta OS'
            }),
            'hospedagem': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Informação de hospedagem'
            }),
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'roteiro': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Roteiro será gerado automaticamente, mas pode ser editado aqui'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações internas sobre a OS'
            }),
        }


