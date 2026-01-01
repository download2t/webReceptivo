"""
Views para gerenciamento de serviços turísticos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from .models import Categoria, SubCategoria, TipoMeiaEntrada, LancamentoServico, Transfer
from .forms import CategoriaForm, SubCategoriaForm, TipoMeiaEntradaForm, LancamentoServicoForm, TransferForm


# ==================== VIEWS DE CATEGORIA ====================

@login_required
def categoria_list(request):
    """Lista todas as categorias"""
    categorias = Categoria.objects.all()
    
    # Busca
    search = request.GET.get('search', '')
    if search:
        categorias = categorias.filter(
            Q(nome__icontains=search)
        )
    
    context = {
        'categorias': categorias,
        'search': search,
        'title': 'Categorias de Serviços'
    }
    return render(request, 'servicos/categoria_list.html', context)


@login_required
def categoria_create(request):
    """Cria nova categoria"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('servicos:categoria_list')
    else:
        form = CategoriaForm()
    
    context = {
        'form': form,
        'title': 'Nova Categoria',
        'action': 'Criar'
    }
    return render(request, 'servicos/categoria_form.html', context)


@login_required
def categoria_edit(request, pk):
    """Edita categoria existente"""
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('servicos:categoria_list')
    else:
        form = CategoriaForm(instance=categoria)
    
    context = {
        'form': form,
        'categoria': categoria,
        'title': f'Editar {categoria.nome}',
        'action': 'Atualizar'
    }
    return render(request, 'servicos/categoria_form.html', context)


@login_required
def categoria_delete(request, pk):
    """Deleta categoria"""
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        try:
            categoria.delete()
            messages.success(request, f'Categoria "{categoria.nome}" deletada com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao deletar categoria: {str(e)}')
        return redirect('servicos:categoria_list')
    
    context = {
        'categoria': categoria,
        'title': f'Deletar {categoria.nome}'
    }
    return render(request, 'servicos/categoria_confirm_delete.html', context)


# ==================== VIEWS DE SUBCATEGORIA (SERVIÇOS) ====================

@login_required
def subcategoria_list(request):
    """Lista todos os serviços"""
    subcategorias = SubCategoria.objects.select_related('categoria').all()
    
    # Filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    
    if search:
        subcategorias = subcategorias.filter(
            Q(nome__icontains=search) |
            Q(descricao__icontains=search)
        )
    
    if categoria_id:
        subcategorias = subcategorias.filter(categoria_id=categoria_id)
    
    # Paginação
    paginator = Paginator(subcategorias, 20)
    page = request.GET.get('page')
    subcategorias = paginator.get_page(page)
    
    categorias = Categoria.objects.filter(ativo=True)
    
    context = {
        'subcategorias': subcategorias,
        'categorias': categorias,
        'search': search,
        'categoria_filter': categoria_id,
        'title': 'Serviços Turísticos'
    }
    return render(request, 'servicos/subcategoria_list.html', context)


@login_required
def subcategoria_create(request):
    """Cria novo serviço"""
    if request.method == 'POST':
        form = SubCategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço criado com sucesso!')
            return redirect('servicos:subcategoria_list')
    else:
        form = SubCategoriaForm()
    
    context = {
        'form': form,
        'title': 'Novo Serviço',
        'action': 'Criar'
    }
    return render(request, 'servicos/subcategoria_form.html', context)


@login_required
def subcategoria_edit(request, pk):
    """Edita serviço existente"""
    subcategoria = get_object_or_404(SubCategoria, pk=pk)
    
    if request.method == 'POST':
        form = SubCategoriaForm(request.POST, instance=subcategoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço atualizado com sucesso!')
            return redirect('servicos:subcategoria_list')
    else:
        form = SubCategoriaForm(instance=subcategoria)
    
    context = {
        'form': form,
        'subcategoria': subcategoria,
        'title': f'Editar {subcategoria.nome}',
        'action': 'Atualizar'
    }
    return render(request, 'servicos/subcategoria_form.html', context)


@login_required
def subcategoria_delete(request, pk):
    """Deleta serviço"""
    subcategoria = get_object_or_404(SubCategoria, pk=pk)
    
    if request.method == 'POST':
        try:
            subcategoria.delete()
            messages.success(request, f'Serviço "{subcategoria.nome}" deletado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao deletar serviço: {str(e)}')
        return redirect('servicos:subcategoria_list')
    
    context = {
        'subcategoria': subcategoria,
        'title': f'Deletar {subcategoria.nome}'
    }
    return render(request, 'servicos/subcategoria_confirm_delete.html', context)


# ==================== VIEWS DE TIPO DE MEIA ENTRADA ====================

@login_required
def tipo_meia_list(request):
    """Lista tipos de meia entrada"""
    tipos = TipoMeiaEntrada.objects.all()
    
    search = request.GET.get('search', '')
    if search:
        tipos = tipos.filter(nome__icontains=search)
    
    context = {
        'tipos': tipos,
        'search': search,
        'title': 'Tipos de Meia Entrada'
    }
    return render(request, 'servicos/tipo_meia_list.html', context)


@login_required
def tipo_meia_create(request):
    """Cria novo tipo de meia entrada"""
    if request.method == 'POST':
        form = TipoMeiaEntradaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de meia entrada criado com sucesso!')
            return redirect('servicos:tipo_meia_list')
    else:
        form = TipoMeiaEntradaForm()
    
    context = {
        'form': form,
        'title': 'Novo Tipo de Meia Entrada',
        'action': 'Criar'
    }
    return render(request, 'servicos/tipo_meia_form.html', context)


@login_required
def tipo_meia_edit(request, pk):
    """Edita tipo de meia entrada"""
    tipo = get_object_or_404(TipoMeiaEntrada, pk=pk)
    
    if request.method == 'POST':
        form = TipoMeiaEntradaForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de meia entrada atualizado com sucesso!')
            return redirect('servicos:tipo_meia_list')
    else:
        form = TipoMeiaEntradaForm(instance=tipo)
    
    context = {
        'form': form,
        'tipo': tipo,
        'title': f'Editar {tipo.nome}',
        'action': 'Atualizar'
    }
    return render(request, 'servicos/tipo_meia_form.html', context)


@login_required
def tipo_meia_delete(request, pk):
    """Deleta tipo de meia entrada"""
    tipo = get_object_or_404(TipoMeiaEntrada, pk=pk)
    
    if request.method == 'POST':
        try:
            tipo.delete()
            messages.success(request, f'Tipo "{tipo.nome}" deletado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao deletar tipo: {str(e)}')
        return redirect('servicos:tipo_meia_list')
    
    context = {
        'tipo': tipo,
        'title': f'Deletar {tipo.nome}'
    }
    return render(request, 'servicos/tipo_meia_confirm_delete.html', context)


# ==================== VIEWS DE LANÇAMENTO DE SERVIÇO ====================

@login_required
def lancamento_list(request):
    """Lista lançamentos de serviços"""
    lancamentos = LancamentoServico.objects.select_related(
        'categoria', 'subcategoria', 'criado_por'
    ).prefetch_related('tipos_meia_entrada').all()
    
    # Filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    if search:
        lancamentos = lancamentos.filter(
            Q(subcategoria__nome__icontains=search) |
            Q(obs_publica__icontains=search)
        )
    
    if categoria_id:
        lancamentos = lancamentos.filter(categoria_id=categoria_id)
    
    if data_inicio:
        lancamentos = lancamentos.filter(data_servico__gte=data_inicio)
    
    if data_fim:
        lancamentos = lancamentos.filter(data_servico__lte=data_fim)
    
    # Estatísticas
    stats = lancamentos.aggregate(
        total_lancamentos=Count('id'),
        total_pax=Sum('qtd_inteira') + Sum('qtd_meia') + Sum('qtd_infantil')
    )
    
    # Paginação
    paginator = Paginator(lancamentos, 20)
    page = request.GET.get('page')
    lancamentos = paginator.get_page(page)
    
    categorias = Categoria.objects.filter(ativo=True)
    
    context = {
        'lancamentos': lancamentos,
        'categorias': categorias,
        'stats': stats,
        'search': search,
        'categoria_filter': categoria_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'title': 'Lançamentos de Serviços'
    }
    return render(request, 'servicos/lancamento_list.html', context)


@login_required
def lancamento_create(request):
    """Cria novo lançamento / ordem de serviço com múltiplos serviços"""
    import json
    from decimal import Decimal
    
    if request.method == 'POST':
        # Verificar se é JSON (múltiplos serviços)
        if request.content_type == 'application/json':
            try:
                dados = json.loads(request.body)
                servicos = dados.get('servicos', [])
                roteiro = dados.get('roteiro', '')
                
                if not servicos:
                    return JsonResponse({'error': 'Nenhum serviço informado'}, status=400)
                
                # Criar todos os lançamentos
                lancamentos_criados = []
                
                for servico_data in servicos:
                    # Extrair dados
                    data_servico = servico_data['data']
                    servico_id = servico_data['servico_id']
                    qtd_inteira = servico_data.get('qtd_inteira', 0)
                    qtd_meia = servico_data.get('qtd_meia', 0)
                    qtd_infantil = servico_data.get('qtd_infantil', 0)
                    idades = servico_data.get('idades', [])
                    tipos_meia = servico_data.get('tipos_meia', [])
                    descricao = servico_data.get('descricao', '')
                    
                    # Buscar serviço
                    servico = SubCategoria.objects.get(pk=servico_id)
                    
                    # Criar lançamento
                    lancamento = LancamentoServico.objects.create(
                        data_servico=data_servico,
                        categoria=servico.categoria,
                        subcategoria=servico,
                        qtd_inteira=qtd_inteira,
                        qtd_meia=qtd_meia,
                        qtd_infantil=qtd_infantil,
                        idades_criancas=','.join(map(str, idades)) if idades else '',
                        obs_publica=descricao,
                        criado_por=request.user
                    )
                    
                    # Associar tipos de meia (se usar ManyToMany - senão guardar como texto)
                    if tipos_meia:
                        tipos_texto = '\n'.join([t['nome'] for t in tipos_meia])
                        lancamento.tipos_meia_entrada_text = tipos_texto
                        lancamento.save()
                    
                    lancamentos_criados.append(lancamento)
                
                messages.success(request, f'{len(lancamentos_criados)} serviço(s) adicionado(s) com sucesso!')
                return JsonResponse({'success': True, 'message': 'Ordem de serviço criada com sucesso'})
                
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            # Formulário tradicional (manter compatibilidade)
            form = LancamentoServicoForm(request.POST)
            if form.is_valid():
                lancamento = form.save(commit=False)
                lancamento.criado_por = request.user
                lancamento.save()
                messages.success(request, 'Lançamento criado com sucesso!')
                return redirect('servicos:lancamento_list')
    else:
        # GET - mostrar formulário
        categorias = Categoria.objects.filter(ativo=True)
        transfers = Transfer.objects.filter(ativo=True)
        
        context = {
            'categorias': categorias,
            'transfers': transfers,
            'title': 'Nova Ordem de Serviço'
        }
        return render(request, 'servicos/lancamento_form.html', context)


@login_required
def lancamento_edit(request, pk):
    """Edita lançamento existente"""
    lancamento = get_object_or_404(LancamentoServico, pk=pk)
    
    if request.method == 'POST':
        form = LancamentoServicoForm(request.POST, instance=lancamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lançamento atualizado com sucesso!')
            return redirect('servicos:lancamento_list')
    else:
        form = LancamentoServicoForm(instance=lancamento)
    
    context = {
        'form': form,
        'lancamento': lancamento,
        'title': f'Editar Lançamento #{lancamento.id}',
        'action': 'Atualizar'
    }
    return render(request, 'servicos/lancamento_form.html', context)


@login_required
def lancamento_delete(request, pk):
    """Deleta lançamento"""
    lancamento = get_object_or_404(LancamentoServico, pk=pk)
    
    if request.method == 'POST':
        try:
            lancamento.delete()
            messages.success(request, 'Lançamento deletado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao deletar lançamento: {str(e)}')
        return redirect('servicos:lancamento_list')
    
    context = {
        'lancamento': lancamento,
        'title': f'Deletar Lançamento #{lancamento.id}'
    }
    return render(request, 'servicos/lancamento_confirm_delete.html', context)


@login_required
def lancamento_detail(request, pk):
    """Visualiza detalhes do lançamento"""
    lancamento = get_object_or_404(
        LancamentoServico.objects.select_related(
            'categoria', 'subcategoria', 'criado_por'
        ),
        pk=pk
    )
    
    # Gerar texto do WhatsApp
    texto_whatsapp = lancamento.gerar_texto_whatsapp()
    
    context = {
        'lancamento': lancamento,
        'texto_whatsapp': texto_whatsapp,
        'title': f'Lançamento #{lancamento.id}'
    }
    return render(request, 'servicos/lancamento_detail.html', context)


# ==================== AJAX VIEWS ====================

@login_required
def ajax_load_subcategorias(request):
    """Carrega subcategorias via AJAX baseado na categoria selecionada"""
    categoria_id = request.GET.get('categoria_id')
    
    if categoria_id:
        subcategorias = SubCategoria.objects.filter(
            categoria_id=categoria_id,
            ativo=True
        ).values(
            'id', 'nome', 
            'valor_inteira', 'valor_meia', 'valor_infantil',
            'aceita_meia_entrada', 'regras_meia_entrada',
            'idade_isencao_min', 'idade_isencao_max', 'texto_isencao'
        )
        return JsonResponse(list(subcategorias), safe=False)
    
    return JsonResponse([], safe=False)


@login_required
def ajax_get_subcategoria_valores(request):
    """Retorna valores de uma subcategoria específica via AJAX"""
    subcategoria_id = request.GET.get('subcategoria_id')
    
    if subcategoria_id:
        try:
            subcategoria = SubCategoria.objects.get(id=subcategoria_id)
            data = {
                'valor_inteira': float(subcategoria.valor_inteira),
                'valor_meia': float(subcategoria.valor_meia),
                'valor_infantil': float(subcategoria.valor_infantil),
                'aceita_meia_entrada': subcategoria.aceita_meia_entrada,
                'regras_meia_entrada': subcategoria.regras_meia_entrada,
                'permite_infantil': subcategoria.permite_infantil,
                'idade_minima_infantil': subcategoria.idade_minima_infantil,
                'idade_maxima_infantil': subcategoria.idade_maxima_infantil,
                'possui_isencao': subcategoria.possui_isencao,
                'idade_isencao_min': subcategoria.idade_isencao_min,
                'idade_isencao_max': subcategoria.idade_isencao_max,
                'texto_isencao': subcategoria.texto_isencao,
                'tem_idade_minima': subcategoria.tem_idade_minima,
                'idade_minima': subcategoria.idade_minima,
            }
            return JsonResponse(data)
        except SubCategoria.DoesNotExist:
            return JsonResponse({'error': 'Serviço não encontrado'}, status=404)
    
    return JsonResponse({'error': 'ID não fornecido'}, status=400)


@login_required
def ajax_load_tipos_meia(request):
    """Retorna lista de tipos de meia entrada ativos em JSON"""
    tipos = TipoMeiaEntrada.objects.filter(ativo=True).values('id', 'nome')
    return JsonResponse({'tipos': list(tipos)})


# ==================== VIEWS DE TRANSFER ====================

@login_required
def transfer_list(request):
    """Lista todos os transfers"""
    transfers = Transfer.objects.all()
    
    # Busca
    search = request.GET.get('search', '')
    if search:
        transfers = transfers.filter(
            Q(nome__icontains=search) | Q(descricao__icontains=search)
        )
    
    # Paginação
    paginator = Paginator(transfers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'title': 'Transfers'
    }
    return render(request, 'servicos/transfer_list.html', context)


@login_required
def transfer_create(request):
    """Cria novo transfer"""
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transfer criado com sucesso!')
            return redirect('servicos:transfer_list')
    else:
        form = TransferForm()
    
    context = {
        'form': form,
        'title': 'Novo Transfer',
        'button_text': 'Criar Transfer'
    }
    return render(request, 'servicos/transfer_form.html', context)


@login_required
def transfer_edit(request, pk):
    """Edita transfer existente"""
    transfer = get_object_or_404(Transfer, pk=pk)
    
    if request.method == 'POST':
        form = TransferForm(request.POST, instance=transfer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transfer atualizado com sucesso!')
            return redirect('servicos:transfer_list')
    else:
        form = TransferForm(instance=transfer)
    
    context = {
        'form': form,
        'transfer': transfer,
        'title': f'Editar Transfer: {transfer.nome}',
        'button_text': 'Salvar Alterações'
    }
    return render(request, 'servicos/transfer_form.html', context)


@login_required
def transfer_delete(request, pk):
    """Deleta transfer"""
    transfer = get_object_or_404(Transfer, pk=pk)
    
    if request.method == 'POST':
        nome = transfer.nome
        transfer.delete()
        messages.success(request, f'Transfer "{nome}" deletado com sucesso!')
        return redirect('servicos:transfer_list')
    
    context = {
        'transfer': transfer,
        'title': f'Deletar Transfer: {transfer.nome}'
    }
    return render(request, 'servicos/transfer_confirm_delete.html', context)


# ==================== ENDPOINT AJAX PARA INFORMAÇÕES DO SERVIÇO ====================

@login_required
def ajax_get_servico_info(request):
    """Retorna todas as informações e flags de um serviço"""
    servico_id = request.GET.get('servico_id')
    
    if not servico_id:
        return JsonResponse({'error': 'ID do serviço não informado'}, status=400)
    
    try:
        servico = SubCategoria.objects.get(pk=servico_id)
        
        data = {
            'id': servico.id,
            'nome': servico.nome,
            'descricao': servico.descricao,
            'categoria_nome': servico.categoria.nome,
            
            # Valores
            'valor_inteira': float(servico.valor_inteira),
            'valor_meia': float(servico.valor_meia),
            'valor_infantil': float(servico.valor_infantil),
            
            # Flags de meia entrada
            'aceita_meia_entrada': servico.aceita_meia_entrada,
            'regras_meia_entrada': servico.regras_meia_entrada,
            
            # Flags de infantil
            'permite_infantil': servico.permite_infantil,
            'idade_minima_infantil': servico.idade_minima_infantil,
            'idade_maxima_infantil': servico.idade_maxima_infantil,
            
            # Flags de isenção
            'possui_isencao': servico.possui_isencao,
            'idade_isencao_min': servico.idade_isencao_min,
            'idade_isencao_max': servico.idade_isencao_max,
            'texto_isencao': servico.texto_isencao,
            
            # Flags de idade mínima
            'tem_idade_minima': servico.tem_idade_minima,
            'idade_minima': servico.idade_minima,
        }
        
        return JsonResponse(data)
        
    except SubCategoria.DoesNotExist:
        return JsonResponse({'error': 'Serviço não encontrado'}, status=404)

