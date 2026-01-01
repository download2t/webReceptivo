"""
Models para gerenciamento de serviços turísticos
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone


class Categoria(models.Model):
    """Categoria de serviços (Ex: Atrativos, Hospedagem, Transporte)"""
    
    nome = models.CharField('Nome da Categoria', max_length=100, unique=True)
    ativo = models.BooleanField('Ativo', default=True)
    ordem = models.PositiveIntegerField('Ordem de Exibição', default=0)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome


class SubCategoria(models.Model):
    """Serviço específico dentro de uma categoria"""
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='subcategorias',
        verbose_name='Categoria'
    )
    nome = models.CharField('Nome do Serviço', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    
    # Valores
    valor_inteira = models.DecimalField(
        'Valor Inteira',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        default=Decimal('0.00')
    )
    valor_meia = models.DecimalField(
        'Valor Meia Entrada',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    valor_infantil = models.DecimalField(
        'Valor Infantil',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    
    # Configurações de meia entrada
    aceita_meia_entrada = models.BooleanField(
        'Aceita Meia Entrada',
        default=True,
        help_text='Define se este serviço aceita meia entrada'
    )
    regras_meia_entrada = models.TextField(
        'Regras de Meia Entrada',
        blank=True,
        help_text='Ex: EST. DE 9 A 16 ANOS COM RG, EST. COM CARTEIRINHA, PROF BR, IDOSO, etc.'
    )
    
    # Configurações de infantil
    permite_infantil = models.BooleanField(
        'Permite Infantil',
        default=True,
        help_text='Define se este serviço possui categoria infantil'
    )
    idade_minima_infantil = models.PositiveIntegerField(
        'Idade Mínima Infantil',
        default=0,
        validators=[MaxValueValidator(17)],
        help_text='Idade mínima para categoria infantil (ex: 0). Máximo 17 anos.'
    )
    idade_maxima_infantil = models.PositiveIntegerField(
        'Idade Máxima Infantil',
        default=17,
        validators=[MaxValueValidator(17)],
        help_text='Idade máxima para categoria infantil (ex: 12). Máximo 17 anos.'
    )
    
    # Configurações de isenção
    possui_isencao = models.BooleanField(
        'Possui Isenção por Idade',
        default=False,
        help_text='Define se este serviço possui isenção por faixa etária'
    )
    idade_isencao_min = models.PositiveIntegerField(
        'Idade Mínima Isenção',
        default=0,
        validators=[MaxValueValidator(17)],
        help_text='Idade mínima para isenção (ex: 0). Máximo 17 anos.'
    )
    idade_isencao_max = models.PositiveIntegerField(
        'Idade Máxima Isenção',
        default=0,
        validators=[MaxValueValidator(17)],
        help_text='Idade máxima para isenção (ex: 6). Máximo 17 anos. Use 0 se não houver isenção'
    )
    texto_isencao = models.CharField(
        'Texto da Isenção',
        max_length=200,
        blank=True,
        help_text='Ex: CRIANÇA DE 0 A 6 ANOS'
    )
    
    # Configurações de idade mínima
    tem_idade_minima = models.BooleanField(
        'Possui Idade Mínima',
        default=False,
        help_text='Define se este serviço exige idade mínima'
    )
    idade_minima = models.PositiveIntegerField(
        'Idade Mínima',
        default=0,
        validators=[MaxValueValidator(17)],
        help_text='Idade mínima permitida para este serviço (ex: 6). Máximo 17 anos. Use 0 se não houver restrição'
    )
    
    # Status
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['categoria__nome', 'nome']
        unique_together = [['categoria', 'nome']]
    
    def __str__(self):
        return f"{self.categoria.nome} - {self.nome}"


class TipoMeiaEntrada(models.Model):
    """Tipos de justificativa para meia entrada"""
    
    nome = models.CharField('Tipo', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Tipo de Meia Entrada'
        verbose_name_plural = 'Tipos de Meia Entrada'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Transfer(models.Model):
    """Transfer (transporte) com nome, valor e descrição"""
    
    nome = models.CharField('Nome do Transfer', max_length=200)
    valor = models.DecimalField(
        'Valor',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text='Valor do transfer'
    )
    descricao = models.TextField('Descrição', blank=True, help_text='Descrição detalhada do transfer')
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Transfer'
        verbose_name_plural = 'Transfers'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.valor}"


class Cliente(models.Model):
    """Cliente para Ordem de Serviço"""
    
    nome = models.CharField('Nome do Cliente', max_length=200)
    email = models.EmailField('E-mail', blank=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    cpf = models.CharField('CPF', max_length=14, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class OrdemServico(models.Model):
    """Ordem de Serviço - agrupa múltiplos lançamentos/serviços"""
    
    STATUS_CHOICES = [
        ('orcamento', 'Orçamento'),
        ('confirmado', 'Confirmado'),
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
    numero_os = models.CharField('Número da OS', max_length=20, unique=True, blank=True)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='ordens_servico',
        verbose_name='Cliente',
        null=True,
        blank=True
    )
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_inicio = models.DateField('Data de Início', null=True, blank=True)
    data_fim = models.DateField('Data de Fim', null=True, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='orcamento')
    
    # Roteiro formatado (editável pelo usuário)
    roteiro = models.TextField('Roteiro', blank=True, help_text='Roteiro formatado para o cliente')
    observacoes = models.TextField('Observações', blank=True)
    
    # Totalizadores
    valor_total = models.DecimalField(
        'Valor Total',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    criado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_criadas',
        verbose_name='Criado por'
    )
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"OS {self.numero_os} - {self.cliente.nome if self.cliente else 'Sem cliente'}"
    
    def save(self, *args, **kwargs):
        """Gera número da OS automaticamente"""
        if not self.numero_os:
            # Gerar número baseado no ano e sequencial
            ano = timezone.now().year
            ultima_os = OrdemServico.objects.filter(
                numero_os__startswith=f'{ano}'
            ).order_by('-numero_os').first()
            
            if ultima_os and ultima_os.numero_os:
                try:
                    ultimo_numero = int(ultima_os.numero_os.split('-')[1])
                    proximo_numero = ultimo_numero + 1
                except (IndexError, ValueError):
                    proximo_numero = 1
            else:
                proximo_numero = 1
            
            self.numero_os = f'{ano}-{proximo_numero:05d}'
        
        super().save(*args, **kwargs)
    
    def calcular_total(self):
        """Calcula o valor total somando todos os lançamentos"""
        total = Decimal('0.00')
        for lancamento in self.lancamentos.all():
            total += lancamento.valor_total
        for transfer in self.transfers_os.all():
            total += transfer.valor
        self.valor_total = total
        self.save(update_fields=['valor_total'])
    
    def gerar_roteiro(self):
        """Gera o roteiro formatado a partir dos lançamentos"""
        if self.roteiro:
            # Se já tem roteiro editado, não sobrescreve
            return self.roteiro
        
        roteiro_parts = []
        
        # Agrupar lançamentos por data
        lancamentos_por_data = {}
        for lancamento in self.lancamentos.select_related('subcategoria').order_by('data_servico'):
            data = lancamento.data_servico
            if data not in lancamentos_por_data:
                lancamentos_por_data[data] = []
            lancamentos_por_data[data].append(lancamento)
        
        # Gerar roteiro por data
        for data, lancamentos in lancamentos_por_data.items():
            dia_semana = data.strftime('%A').upper()
            data_formatada = data.strftime('%d/%m')
            
            roteiro_parts.append(f"{dia_semana} {data_formatada}\n")
            
            for lancamento in lancamentos:
                servico = lancamento.subcategoria
                roteiro_parts.append(f"\n{servico.nome}:")
                
                # Adicionar descrição se houver
                if servico.descricao:
                    descricao_lines = servico.descricao.strip().split('\n')
                    for line in descricao_lines:
                        if line.strip():
                            roteiro_parts.append(f"- {line.strip()}")
                
                # Adicionar valor se houver
                if lancamento.valor_total > 0:
                    roteiro_parts.append(f"R$ {lancamento.valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                
                roteiro_parts.append("")  # Linha em branco
            
            roteiro_parts.append("\n")
        
        self.roteiro = "\n".join(roteiro_parts)
        return self.roteiro
    
    def gerar_texto_whatsapp(self):
        """Gera texto formatado para WhatsApp"""
        texto = f"*ROTEIRO - OS {self.numero_os}*\n"
        texto += f"*Cliente:* {self.cliente.nome}\n"
        
        if self.data_inicio and self.data_fim:
            texto += f"*Período:* {self.data_inicio.strftime('%d/%m/%Y')} a {self.data_fim.strftime('%d/%m/%Y')}\n"
        
        texto += "\n" + "="*40 + "\n\n"
        
        # Usar roteiro editado ou gerar novo
        roteiro = self.roteiro if self.roteiro else self.gerar_roteiro()
        texto += roteiro
        
        texto += "\n" + "="*40 + "\n"
        texto += f"\n*VALOR TOTAL: R$ {self.valor_total:,.2f}*".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return texto


class TransferOS(models.Model):
    """Transfer vinculado a uma Ordem de Serviço"""
    
    ordem_servico = models.ForeignKey(
        OrdemServico,
        on_delete=models.CASCADE,
        related_name='transfers_os',
        verbose_name='Ordem de Serviço'
    )
    transfer = models.ForeignKey(
        Transfer,
        on_delete=models.PROTECT,
        related_name='lancamentos',
        verbose_name='Transfer'
    )
    data_transfer = models.DateField('Data do Transfer')
    quantidade = models.PositiveIntegerField('Quantidade', default=1)
    valor = models.DecimalField(
        'Valor',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00')
    )
    observacoes = models.TextField('Observações', blank=True)
    
    class Meta:
        verbose_name = 'Transfer da OS'
        verbose_name_plural = 'Transfers da OS'
        ordering = ['data_transfer']
    
    def __str__(self):
        return f"{self.transfer.nome} - {self.data_transfer}"
    
    def save(self, *args, **kwargs):
        """Captura o valor do transfer"""
        if not self.pk and self.transfer:
            self.valor = self.transfer.valor
        super().save(*args, **kwargs)


class LancamentoServico(models.Model):
    """Registro de venda/reserva de serviço vinculado a uma Ordem de Serviço"""
    
    # Vínculo com Ordem de Serviço
    ordem_servico = models.ForeignKey(
        OrdemServico,
        on_delete=models.CASCADE,
        related_name='lancamentos',
        verbose_name='Ordem de Serviço',
        null=True,
        blank=True
    )
    
    # Informações do serviço
    data_servico = models.DateField('Data do Serviço')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        verbose_name='Categoria'
    )
    subcategoria = models.ForeignKey(
        SubCategoria,
        on_delete=models.PROTECT,
        verbose_name='Serviço'
    )
    
    # Quantidades
    qtd_inteira = models.PositiveIntegerField(
        'Qtd Inteira',
        default=0,
        validators=[MinValueValidator(0)]
    )
    qtd_meia = models.PositiveIntegerField(
        'Qtd Meia Entrada',
        default=0,
        validators=[MinValueValidator(0)]
    )
    qtd_infantil = models.PositiveIntegerField(
        'Qtd Infantil',
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Idades das crianças (separadas por vírgula)
    idades_criancas = models.CharField(
        'Idades das Crianças',
        max_length=200,
        blank=True,
        help_text='Informe as idades separadas por vírgula. Ex: 3, 5, 8'
    )
    
    # Tipo de meia entrada (obrigatório apenas se qtd_meia > 0)
    tipo_meia_entrada = models.ForeignKey(
        TipoMeiaEntrada,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Meia Entrada',
        blank=True,
        null=True,
        help_text='Obrigatório quando houver quantidade de meia entrada'
    )
    
    # Tipos de meia entrada individuais (uma por linha, para múltiplas meias)
    tipos_meia_entrada = models.TextField(
        'Tipos de Meia Entrada',
        blank=True,
        help_text='Informe um tipo por linha quando houver múltiplas meias entradas. Ex:\nEstudante\nIdoso'
    )
    
    # Valores unitários no momento do lançamento (snapshot)
    valor_unit_inteira = models.DecimalField(
        'Valor Unit. Inteira',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    valor_unit_meia = models.DecimalField(
        'Valor Unit. Meia',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    valor_unit_infantil = models.DecimalField(
        'Valor Unit. Infantil',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Valores de Transfer (snapshot no momento do lançamento)
    valor_transfer_ida = models.DecimalField(
        'Valor Transfer Ida',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Valor total dos transfers de ida'
    )
    valor_transfer_volta = models.DecimalField(
        'Valor Transfer Volta',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Valor total dos transfers de volta'
    )
    
    # Observações
    obs_publica = models.TextField(
        'Observações Públicas',
        blank=True,
        help_text='Visível na OS e para o cliente'
    )
    obs_privada = models.TextField(
        'Observações Privadas',
        blank=True,
        help_text='Uso interno, não aparece na OS'
    )
    
    # Controle
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    criado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='lancamentos_criados',
        verbose_name='Criado por'
    )
    
    class Meta:
        verbose_name = 'Lançamento de Serviço'
        verbose_name_plural = 'Lançamentos de Serviços'
        ordering = ['-data_servico', '-criado_em']
    
    def __str__(self):
        return f"{self.subcategoria.nome} - {self.data_servico.strftime('%d/%m/%Y')}"
    
    def get_idades_lista(self):
        """Converte o campo idades_criancas (string CSV) para lista de inteiros"""
        if not self.idades_criancas:
            return []
        
        if isinstance(self.idades_criancas, list):
            return [int(i) if isinstance(i, str) else i for i in self.idades_criancas]
        
        # Se for string, separar por vírgula e converter para int
        try:
            return [int(idade.strip()) for idade in self.idades_criancas.split(',') if idade.strip()]
        except (ValueError, AttributeError):
            return []
    
    @property
    def total_pax(self):
        """Total de passageiros"""
        return self.qtd_inteira + self.qtd_meia + self.qtd_infantil
    
    @property
    def qtd_infantil_isentas(self):
        """Retorna quantas crianças estão isentas por idade"""
        idades = self.get_idades_lista()
        if not idades:
            return 0
        
        if not self.subcategoria:
            return 0
        
        idade_min = self.subcategoria.idade_isencao_min
        idade_max = self.subcategoria.idade_isencao_max
        
        if idade_min is None or idade_max is None:
            return 0
        
        count = 0
        for idade in idades:
            if idade_min <= idade <= idade_max:
                count += 1
        
        return count
    
    @property
    def qtd_infantil_pagas(self):
        """Retorna quantas crianças são pagas (não isentas)"""
        return self.qtd_infantil - self.qtd_infantil_isentas
    
    @property
    def qtd_infantil_pagam_inteira(self):
        """
        Retorna quantas crianças pagam valor de inteira.
        Crianças pagam inteira quando:
        1. Não estão isentas E
        2. Estão fora da faixa infantil OU o serviço não permite infantil OU não aceita meia
        """
        if not self.subcategoria:
            return 0
        
        # Se não aceita meia entrada, todas as crianças não isentas pagam inteira
        if not self.subcategoria.aceita_meia_entrada:
            return self.qtd_infantil_pagas
        
        # Se aceita meia mas não permite infantil, todas as crianças não isentas pagam inteira
        if not self.subcategoria.permite_infantil:
            return self.qtd_infantil_pagas
        
        # Contar crianças fora da faixa infantil
        count = 0
        idades = self.get_idades_lista()
        
        # Crianças isentas
        idade_isencao_min = self.subcategoria.idade_isencao_min
        idade_isencao_max = self.subcategoria.idade_isencao_max
        
        # Faixa infantil
        idade_infantil_min = self.subcategoria.idade_minima_infantil
        idade_infantil_max = self.subcategoria.idade_maxima_infantil
        
        for idade in idades:
            # Pular se está isenta
            if self.subcategoria.possui_isencao and idade_isencao_min <= idade <= idade_isencao_max:
                continue
            
            # Se não está na faixa infantil, paga inteira
            if idade < idade_infantil_min or idade > idade_infantil_max:
                count += 1
        
        return count
    
    @property
    def qtd_infantil_pagam_infantil(self):
        """
        Retorna quantas crianças pagam valor infantil.
        Crianças pagam infantil quando:
        1. Não estão isentas E
        2. Estão dentro da faixa infantil E
        3. O serviço permite infantil E aceita meia
        """
        if not self.subcategoria:
            return 0
        
        # Se não aceita meia ou não permite infantil, ninguém paga infantil
        if not self.subcategoria.aceita_meia_entrada or not self.subcategoria.permite_infantil:
            return 0
        
        # Contar crianças dentro da faixa infantil
        count = 0
        idades = self.get_idades_lista()
        
        # Crianças isentas
        idade_isencao_min = self.subcategoria.idade_isencao_min
        idade_isencao_max = self.subcategoria.idade_isencao_max
        
        # Faixa infantil
        idade_infantil_min = self.subcategoria.idade_minima_infantil
        idade_infantil_max = self.subcategoria.idade_maxima_infantil
        
        for idade in idades:
            # Pular se está isenta
            if self.subcategoria.possui_isencao and idade_isencao_min <= idade <= idade_isencao_max:
                continue
            
            # Se está na faixa infantil, paga infantil
            if idade_infantil_min <= idade <= idade_infantil_max:
                count += 1
        
        return count
    
    @property
    def valor_total(self):
        """
        Calcula o valor total do serviço.
        Considera 3 tipos de preços para crianças:
        1. ISENTAS (R$ 0,00) - dentro da faixa de isenção
        2. INFANTIL - dentro da faixa infantil (se serviço permite infantil e aceita meia)
        3. INTEIRA - fora das faixas acima ou quando serviço não permite infantil/meia
        Inclui valores de transfers (ida + volta)
        """
        total = Decimal('0.00')
        
        # Adultos inteira
        total += self.qtd_inteira * self.valor_unit_inteira
        
        # Adultos meia
        total += self.qtd_meia * self.valor_unit_meia
        
        # Crianças que pagam INFANTIL
        total += self.qtd_infantil_pagam_infantil * self.valor_unit_infantil
        
        # Crianças que pagam INTEIRA
        total += self.qtd_infantil_pagam_inteira * self.valor_unit_inteira
        
        # Crianças isentas não somam (R$ 0,00)
        # NOTA: Transfers agora são vinculados à OS via TransferOS, não aos lançamentos individuais
        
        return total
    
    def save(self, *args, **kwargs):
        """Sobrescreve save para capturar valores unitários da subcategoria"""
        if not self.pk:  # Apenas na criação
            if self.subcategoria:
                self.valor_unit_inteira = self.subcategoria.valor_inteira
                self.valor_unit_meia = self.subcategoria.valor_meia
                self.valor_unit_infantil = self.subcategoria.valor_infantil
        super().save(*args, **kwargs)
    
    def gerar_texto_whatsapp(self):
        """Gera texto formatado para envio via WhatsApp"""
        data_formatada = self.data_servico.strftime('%d/%m/%Y')
        
        # Montar detalhes das quantidades
        detalhes_pax = []
        if self.qtd_inteira > 0:
            detalhes_pax.append(f"{self.qtd_inteira} inteira(s)")
        if self.qtd_meia > 0:
            if self.tipos_meia_entrada:
                tipos = [tipo.strip() for tipo in self.tipos_meia_entrada.split('\n') if tipo.strip()]
                tipos_texto = ", ".join(tipos)
                detalhes_pax.append(f"{self.qtd_meia} meia(s) ({tipos_texto})")
            else:
                detalhes_pax.append(f"{self.qtd_meia} meia(s)")
        if self.qtd_infantil > 0:
            idades = self.get_idades_lista()
            if idades and len(idades) > 0:
                idades_texto = f" - Idades: {', '.join(map(str, idades))}"
                # Adicionar informação sobre isenções
                qtd_isentas = self.qtd_infantil_isentas
                if qtd_isentas > 0:
                    idades_texto += f" ({qtd_isentas} isenta(s))"
            else:
                idades_texto = ""
            detalhes_pax.append(f"{self.qtd_infantil} infantil(is){idades_texto}")
        
        pax_texto = ", ".join(detalhes_pax) if detalhes_pax else "Sem passageiros"
        
        # Montar observações públicas
        obs_texto = f"\n📝 Detalhes: {self.obs_publica}" if self.obs_publica else ""
        
        # Texto final
        texto = f"""Olá! Segue confirmação do serviço:

🗓 *Data:* {data_formatada}
📍 *Serviço:* {self.subcategoria.nome} ({self.categoria.nome})
👥 *Pax:* {self.total_pax} pessoa(s) - {pax_texto}{obs_texto}
💰 *Valor Total:* R$ {self.valor_total:,.2f}

Aguardamos você! 🎉"""
        
        return texto
    
    def clean(self):
        """Validações customizadas"""
        from django.core.exceptions import ValidationError
        errors = {}
        
        # Validar que pelo menos uma quantidade foi informada
        if self.qtd_inteira == 0 and self.qtd_meia == 0 and self.qtd_infantil == 0:
            errors['__all__'] = 'Informe ao menos uma quantidade (Inteira, Meia ou Infantil)'
        
        # Validar se o serviço aceita meia entrada
        if self.qtd_meia > 0 and self.subcategoria:
            if not self.subcategoria.aceita_meia_entrada:
                errors['qtd_meia'] = 'Este serviço não aceita meia entrada'
        
        # Validar tipo de meia entrada obrigatório quando qtd_meia > 0
        if self.qtd_meia > 0:
            # Verificar se há tipos de meia entrada associados
            if self.pk:  # Só verifica se já foi salvo
                tipos_count = self.tipos_meia_entrada.count()
                if tipos_count != self.qtd_meia:
                    errors['qtd_meia'] = f'Quantidade de tipos de meia ({tipos_count}) não corresponde à quantidade de meias ({self.qtd_meia})'
        
        # Validar que subcategoria pertence à categoria selecionada
        if self.categoria and self.subcategoria:
            if self.subcategoria.categoria != self.categoria:
                errors['subcategoria'] = 'O serviço selecionado não pertence à categoria escolhida'
        
        # Validar idades das crianças quando qtd_infantil > 0
        if self.qtd_infantil > 0:
            if not self.idades_criancas:
                errors['__all__'] = 'Informe as idades das crianças'
            else:
                # Obter lista de idades (pode ser string CSV ou lista)
                idades = self.get_idades_lista()
                
                if not idades:
                    errors['__all__'] = 'Formato inválido para idades das crianças'
                else:
                    # Verificar se a quantidade de idades corresponde à quantidade de crianças
                    if len(idades) != self.qtd_infantil:
                        errors['__all__'] = f'Quantidade de idades ({len(idades)}) não corresponde à quantidade de crianças ({self.qtd_infantil})'
                    
                    # Validar se todas as idades são positivas e não ultrapassam 17 anos
                    for idade in idades:
                        if idade <= 0:
                            errors['__all__'] = 'Todas as idades devem ser números positivos'
                            break
                        if idade > 17:
                            errors['__all__'] = f'A idade máxima permitida para infantil é 17 anos. Idade informada: {idade} anos.'
                            break
                    
                    # Validar idade mínima do serviço
                    if self.subcategoria and self.subcategoria.tem_idade_minima and self.subcategoria.idade_minima > 0:
                        for idade in self.idades_criancas:
                            if idade < self.subcategoria.idade_minima:
                                errors['__all__'] = f'Este serviço exige idade mínima de {self.subcategoria.idade_minima} anos. Criança com {idade} anos não atende o requisito.'
                                break
        
        if errors:
            raise ValidationError(errors)

