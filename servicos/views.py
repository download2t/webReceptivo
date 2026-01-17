"""
Views para gerenciamento de serviços turísticos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.views.decorators.http import require_http_methods
from .models import Categoria, SubCategoria, TipoMeiaEntrada, LancamentoServico, Transfer, OrdemServico, TransferOrdemServico
from .forms import CategoriaForm, SubCategoriaForm, TipoMeiaEntradaForm, LancamentoServicoForm, TransferForm, OrdemServicoForm
from .permissions import require_permission


# ==================== VIEWS DE CATEGORIA ====================

@require_permission('servicos.view_categoria')
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
    return render(request, 'servicos/categorias/categoria_list.html', context)


@require_permission('servicos.add_categoria')
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
    return render(request, 'servicos/categorias/categoria_form.html', context)


@require_permission('servicos.change_categoria')
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
    return render(request, 'servicos/categorias/categoria_form.html', context)


@require_permission('servicos.delete_categoria')
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
    return render(request, 'servicos/categorias/categoria_confirm_delete.html', context)


# ==================== VIEWS DE SUBCATEGORIA (SERVIÇOS) ====================

@require_permission('servicos.view_subcategoria')
def servico_list(request):
    """Lista todos os serviços"""
    servicos = SubCategoria.objects.select_related('categoria').all()
    
    # Filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    
    if search:
        servicos = servicos.filter(
            Q(nome__icontains=search) |
            Q(descricao__icontains=search)
        )
    
    if categoria_id:
        servicos = servicos.filter(categoria_id=categoria_id)
    
    # Paginação
    paginator = Paginator(servicos, 20)
    page = request.GET.get('page')
    servicos = paginator.get_page(page)
    
    categorias = Categoria.objects.filter(ativo=True)
    
    context = {
        'servicos': servicos,
        'categorias': categorias,
        'search': search,
        'categoria_filter': categoria_id,
        'title': 'Serviços Turísticos'
    }
    return render(request, 'servicos/servicos/servico_list.html', context)


@require_permission('servicos.add_subcategoria')
def servico_create(request):
    """Cria novo serviço"""
    if request.method == 'POST':
        form = SubCategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço criado com sucesso!')
            return redirect('servicos:servico_list')
    else:
        form = SubCategoriaForm()
    
    context = {
        'form': form,
        'title': 'Novo Serviço',
        'action': 'Criar'
    }
    return render(request, 'servicos/servicos/servico_form.html', context)


@require_permission('servicos.change_subcategoria')
def servico_edit(request, pk):
    """Edita serviço existente"""
    subcategoria = get_object_or_404(SubCategoria, pk=pk)
    
    if request.method == 'POST':
        form = SubCategoriaForm(request.POST, instance=subcategoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Serviço atualizado com sucesso!')
            return redirect('servicos:servico_list')
    else:
        form = SubCategoriaForm(instance=subcategoria)
    
    context = {
        'form': form,
        'servico': subcategoria,
        'title': f'Editar {subcategoria.nome}',
        'action': 'Atualizar'
    }
    return render(request, 'servicos/servicos/servico_form.html', context)


@require_permission('servicos.delete_subcategoria')
def servico_delete(request, pk):
    """Deleta serviço"""
    subcategoria = get_object_or_404(SubCategoria, pk=pk)
    
    if request.method == 'POST':
        try:
            subcategoria.delete()
            messages.success(request, f'Serviço "{subcategoria.nome}" deletado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao deletar serviço: {str(e)}')
        return redirect('servicos:servico_list')
    
    context = {
        'servico': subcategoria,
        'title': f'Deletar {subcategoria.nome}'
    }
    return render(request, 'servicos/servicos/servico_confirm_delete.html', context)


# ==================== VIEWS DE TIPO DE MEIA ENTRADA ====================

@require_permission('servicos.view_tipomeiaentrada')
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
    return render(request, 'servicos/meias/tipo_meia_list.html', context)


@require_permission('servicos.add_tipomeiaentrada')
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
    return render(request, 'servicos/meias/tipo_meia_form.html', context)


@require_permission('servicos.change_tipomeiaentrada')
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
    return render(request, 'servicos/meias/tipo_meia_form.html', context)


@require_permission('servicos.delete_tipomeiaentrada')
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
    return render(request, 'servicos/meias/tipo_meia_confirm_delete.html', context)


# ==================== VIEWS DE ORDEM DE SERVIÇO ====================

@require_permission('servicos.view_ordemservico')
def ordem_servico_list(request):
    # Listagem e filtros de Ordens de Serviço
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    ordens = OrdemServico.objects.all()

    if search:
        ordens = ordens.filter(
            Q(numero_os__icontains=search) |
            Q(lancamentos__subcategoria__nome__icontains=search) |
            Q(criado_por__username__icontains=search) |
            Q(criado_por__first_name__icontains=search) |
            Q(criado_por__last_name__icontains=search)
        ).distinct()
    if categoria_id:
        ordens = ordens.filter(lancamentos__subcategoria__categoria_id=categoria_id).distinct()
    if data_inicio:
        ordens = ordens.filter(lancamentos__data_servico__gte=data_inicio).distinct()
    if data_fim:
        ordens = ordens.filter(lancamentos__data_servico__lte=data_fim).distinct()

    # Estatísticas
    stats = {
        'total_ordens': ordens.count(),
        'total_servicos': sum(os.lancamentos.count() for os in ordens),
    }

    # Paginação
    paginator = Paginator(ordens, 20)
    page = request.GET.get('page')
    ordens = paginator.get_page(page)

    categorias = Categoria.objects.filter(ativo=True)

    # Debug: Verificar permissões do usuário
    has_add_perm = request.user.has_perm('servicos.add_ordemservico')

    context = {
        'ordens': ordens,
        'categorias': categorias,
        'stats': stats,
        'search': search,
        'categoria_filter': categoria_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'title': 'Ordens de Serviço',
        'debug_has_add_perm': has_add_perm,  # Debug
    }
    return render(request, 'servicos/os/ordem_servico_list.html', context)
    # Estatísticas
    stats = {
        'total_ordens': ordens.count(),
        'total_servicos': sum(os.lancamentos.count() for os in ordens),
    }
    
    # Paginação
    paginator = Paginator(ordens, 20)
    page = request.GET.get('page')
    ordens = paginator.get_page(page)
    
    categorias = Categoria.objects.filter(ativo=True)
    
    # Debug: Verificar permissões do usuário
    has_add_perm = request.user.has_perm('servicos.add_ordemservico')
    
    context = {
        'ordens': ordens,
        'categorias': categorias,
        'stats': stats,
        'search': search,
        'categoria_filter': categoria_id,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'title': 'Ordens de Serviço',
        'debug_has_add_perm': has_add_perm,  # Debug
    }
    return render(request, 'servicos/os/ordem_servico_list.html', context)

# Alias para retrocompatibilidade
lancamento_list = ordem_servico_list


@require_permission('servicos.add_ordemservico')
@require_permission('servicos.add_ordemservico')
def ordem_servico_create(request):
    """Cria novo lançamento / ordem de serviço com múltiplos serviços"""
    import json
    from decimal import Decimal
    from django.utils import timezone
    # Inicializa variáveis para GET
    form = OrdemServicoForm()
    categorias = Categoria.objects.filter(ativo=True)
    transfers = Transfer.objects.filter(ativo=True) if hasattr(Transfer, 'ativo') else Transfer.objects.all()
                        # DEBUG: Logar transfers recebidos

    if request.method == 'POST':
        if request.content_type == 'application/json':
            import traceback
            try:
                data = json.loads(request.body)
                # DEBUG: Logar transfers recebidos
                import logging
                logger = logging.getLogger('django')
                logger.warning('DEBUG transfers/transfers_json recebidos: transfers=%s transfers_json=%s', data.get('transfers'), data.get('transfers_json'))
                # Criação da OS
                form_data = {
                    'clientes': data.get('clientes', ''),
                    'hospedagem': data.get('hospedagem', ''),
                    'roteiro': data.get('roteiro', ''),
                    'status': data.get('status', 'orcamento'),
                }
                form = OrdemServicoForm(form_data)
                if form.is_valid():
                    ordem = form.save(commit=False)
                    ordem.criado_por = request.user
                    cliente_id = data.get('cliente')
                    if cliente_id:
                        try:
                            from .models import Cliente
                            ordem.cliente = Cliente.objects.get(pk=cliente_id)
                        except Exception:
                            pass
                    ordem.save()

                    servicos = data.get('servicos', [])
                    from .models import LancamentoServico
                    # Antes de adicionar novos transfers, remover todos os transfers antigos da OS (garante remoção ao editar)
                    ordem.transfers.all().delete()
                    for s in servicos:
                        if s.get('__transfer_avulso'):
                            # Para cada transfer avulso, criar TransferOrdemServico
                            for transfer_data in s.get('transfers', []):
                                transfer_id = transfer_data.get('transfer_id')
                                transfer_valor = transfer_data.get('valor', 0)
                                try:
                                    transfer_id = int(transfer_id)
                                except Exception:
                                    continue
                                try:
                                    transfer_obj = Transfer.objects.get(pk=transfer_id)
                                except Transfer.DoesNotExist:
                                    return JsonResponse({
                                        'error': 'Transfer não encontrado',
                                        'transfer_id': transfer_id
                                    }, status=400)
                                TransferOrdemServico.objects.create(
                                    ordem_servico=ordem,
                                    transfer=transfer_obj,
                                    valor=transfer_valor
                                )
                        else:
                            # Só cria lançamento se houver serviço válido
                            if s.get('servico_id') and s.get('categoria_id') and s.get('data'):
                                lancamento = LancamentoServico(
                                    ordem_servico=ordem,
                                    categoria_id=s.get('categoria_id'),
                                    subcategoria_id=s.get('servico_id'),
                                    data_servico=s.get('data'),
                                    obs_publica=s.get('descricao', ''),
                                    qtd_inteira=s.get('qtd_inteira', 0),
                                    qtd_meia=s.get('qtd_meia', 0),
                                    qtd_infantil=s.get('qtd_infantil', 0),
                                    idades_criancas=','.join(str(i) for i in s.get('idades', [])),
                                    tipos_meia_entrada='\n'.join(str(tm.get('tipo')) for tm in s.get('tipos_meia', [])),
                                    valor_unit_inteira=s['info'].get('valor_inteira', 0) if s.get('info') else 0,
                                    valor_unit_meia=s['info'].get('valor_meia', 0) if s.get('info') else 0,
                                    valor_unit_infantil=s['info'].get('valor_infantil', 0) if s.get('info') else 0,
                                )
                                lancamento.save()
                    ordem.calcular_total()
                    ordem.save()
                    return JsonResponse({'success': True, 'ordem_id': ordem.id})
                else:
                    return JsonResponse({'error': 'Dados inválidos', 'form_errors': form.errors}, status=400)
            except Exception as e:
                return JsonResponse({
                    'error': 'Erro inesperado',
                    'exception': str(e),
                    'traceback': traceback.format_exc()
                }, status=500)

    return render(request, 'servicos/os/ordem_servico_form.html', {
        'form': form,
        'editando': False,
        'title': 'Nova Ordem de Serviço',
        'categorias': categorias,
        'transfers': transfers,
        # ...outros contextos necessários...
    })

# Alias para retrocompatibilidade
lancamento_create = ordem_servico_create

@require_permission('servicos.change_ordemservico')
def ordem_servico_edit(request, pk):
    """Edita Ordem de Serviço existente - usa mesmo template de criação"""
    ordem = get_object_or_404(OrdemServico, pk=pk)
    
    if request.method == 'POST' and request.content_type == 'application/json':
        import json as _json
        import traceback
        try:
            data = _json.loads(request.body)
            form_data = {
                'clientes': data.get('clientes', ''),
                'hospedagem': data.get('hospedagem', ''),
                'roteiro': data.get('roteiro', ''),
                'status': data.get('status', ordem.status if hasattr(ordem, 'status') else 'orcamento'),
            }
            form = OrdemServicoForm(form_data, instance=ordem)
            if form.is_valid():
                ordem = form.save()
                # Remover todos os lançamentos e transfers antigos
                ordem.lancamentos.all().delete()
                ordem.transfers.all().delete()
                servicos = data.get('servicos', [])
                for s in servicos:
                    if s.get('__transfer_avulso'):
                        for transfer_data in s.get('transfers', []):
                            transfer_id = transfer_data.get('transfer_id')
                            transfer_valor = transfer_data.get('valor', 0)
                            try:
                                transfer_id = int(transfer_id)
                            except Exception:
                                continue
                            try:
                                transfer_obj = Transfer.objects.get(pk=transfer_id)
                            except Transfer.DoesNotExist:
                                return JsonResponse({
                                    'error': 'Transfer não encontrado',
                                    'transfer_id': transfer_id
                                }, status=400)
                            TransferOrdemServico.objects.create(
                                ordem_servico=ordem,
                                transfer=transfer_obj,
                                valor=transfer_valor
                            )
                    else:
                        if s.get('servico_id') and s.get('categoria_id') and s.get('data'):
                            lancamento = LancamentoServico(
                                ordem_servico=ordem,
                                categoria_id=s.get('categoria_id'),
                                subcategoria_id=s.get('servico_id'),
                                data_servico=s.get('data'),
                                obs_publica=s.get('descricao', ''),
                                qtd_inteira=s.get('qtd_inteira', 0),
                                qtd_meia=s.get('qtd_meia', 0),
                                qtd_infantil=s.get('qtd_infantil', 0),
                                idades_criancas=','.join(str(i) for i in s.get('idades', [])),
                                tipos_meia_entrada='\n'.join(str(tm.get('tipo')) for tm in s.get('tipos_meia', [])),
                                valor_unit_inteira=s['info'].get('valor_inteira', 0) if s.get('info') else 0,
                                valor_unit_meia=s['info'].get('valor_meia', 0) if s.get('info') else 0,
                                valor_unit_infantil=s['info'].get('valor_infantil', 0) if s.get('info') else 0,
                            )
                            lancamento.save()
                ordem.calcular_total()
                ordem.save()
                return JsonResponse({'success': True, 'ordem_id': ordem.id})
            else:
                return JsonResponse({'error': 'Dados inválidos', 'form_errors': form.errors}, status=400)
        except Exception as e:
            return JsonResponse({
                'error': 'Erro inesperado',
                'exception': str(e),
                'traceback': traceback.format_exc()
            }, status=500)
    elif request.method == 'POST':
        form = OrdemServicoForm(request.POST, instance=ordem)
        if form.is_valid():
            ordem = form.save()
            messages.success(request, 'Ordem de Serviço atualizada com sucesso!')
            return redirect('servicos:ordem_servico_list')
    else:
        form = OrdemServicoForm(instance=ordem)
    import json
    categorias = Categoria.objects.filter(ativo=True)
    transfers = Transfer.objects.filter(ativo=True) if hasattr(Transfer, 'ativo') else Transfer.objects.all()
    # Serializar lançamentos e transfers para o JS
    lancamentos_data = []
    datas_servicos = [l.data_servico for l in ordem.lancamentos.all()]
    menor_data = min(datas_servicos).strftime('%Y-%m-%d') if datas_servicos else ''
    for l in ordem.lancamentos.all():
        lancamentos_data.append({
            'id': l.id,
            'data': l.data_servico.strftime('%Y-%m-%d'),
            'categoria_id': l.categoria_id,
            'servico_id': l.subcategoria_id,
            'servico_nome': l.subcategoria.nome,
            'qtd_inteira': l.qtd_inteira,
            'qtd_meia': l.qtd_meia,
            'qtd_infantil': l.qtd_infantil,
            'idades': [int(i) for i in l.idades_criancas.split(',') if i.strip()] if l.idades_criancas else [],
            'tipos_meia': [{'tipo': t} for t in l.tipos_meia_entrada.split('\n') if t.strip()],
            'descricao': l.obs_publica,
            'valor_transfer_ida': float(l.valor_transfer_ida),
            'valor_transfer_volta': float(l.valor_transfer_volta),
            'transfers': [],
            'info': {
                'id': l.subcategoria_id,
                'nome': l.subcategoria.nome,
                'descricao': l.subcategoria.descricao,
                'categoria_nome': l.categoria.nome,
                'valor_inteira': float(l.valor_unit_inteira),
                'valor_meia': float(l.valor_unit_meia),
                'valor_infantil': float(l.valor_unit_infantil),
                'aceita_meia_entrada': getattr(l.subcategoria, 'aceita_meia_entrada', False),
                'regras_meia_entrada': getattr(l.subcategoria, 'regras_meia_entrada', ''),
                'permite_infantil': getattr(l.subcategoria, 'permite_infantil', False),
                'idade_minima_infantil': getattr(l.subcategoria, 'idade_minima_infantil', 0),
                'idade_maxima_infantil': getattr(l.subcategoria, 'idade_maxima_infantil', 0),
                'possui_isencao': getattr(l.subcategoria, 'possui_isencao', False),
                'idade_isencao_min': getattr(l.subcategoria, 'idade_isencao_min', 0),
                'idade_isencao_max': getattr(l.subcategoria, 'idade_isencao_max', 0),
                'texto_isencao': getattr(l.subcategoria, 'texto_isencao', ''),
                'tem_idade_minima': getattr(l.subcategoria, 'tem_idade_minima', False),
                'idade_minima': getattr(l.subcategoria, 'idade_minima', 0),
            }
        })

    # Transfers avulsos enviados separadamente e também como __transfer_avulso em lancamentos_json (para roteiro/resumo)
    transfers_data = []
    for t in ordem.transfers.all():
        transfer_dict = {
            'transfer_id': str(t.transfer_id),
            'nome': t.transfer.nome,
            'valor': float(t.valor)
        }
        transfers_data.append(transfer_dict)
        lancamentos_data.append({
            'id': f'transfer_avulso_{t.id}',
            'data': menor_data,
            'servico_nome': t.transfer.nome,
            'descricao': t.transfer.nome,
            'qtd_inteira': 0,
            'qtd_meia': 0,
            'qtd_infantil': 0,
            'idades': [],
            'tipos_meia': [],
            'transfers': [transfer_dict],
            'valor_transfer_ida': float(t.valor),
            'valor_transfer_volta': 0,
            'info': {},
            '__transfer_avulso': True,
            '__nao_exibir_card': True
        })

    # Gerar roteiro exatamente como no cadastro
    # Reutiliza a mesma lógica do JS para garantir consistência
    # Agrupa por data, inclui transfers por data, e gera texto igual ao preview
    por_data = {}
    for l in ordem.lancamentos.all():
        data = l.data_servico.strftime('%Y-%m-%d')
        if data not in por_data:
            por_data[data] = []
        por_data[data].append(l)
    transfers_por_data = {}
    for t in ordem.transfers.all():
        data = menor_data
        if data not in transfers_por_data:
            transfers_por_data[data] = []
        transfers_por_data[data].append(t)
    datas_ordenadas = sorted(por_data.keys())
    roteiro = '=== ROTEIRO ===\n\n'
    resumo_servicos = []
    for data in datas_ordenadas:
        roteiro += f'📅 {data[8:10]}/{data[5:7]}/{data[0:4]}\n'
        roteiro += '─' * 15 + '\n'
        for l in por_data[data]:
            roteiro += f'\n{l.obs_publica or l.subcategoria.nome}\n'
            if l.qtd_inteira > 0:
                roteiro += f'  • {l.qtd_inteira} Inteira(s)\n'
            if l.qtd_meia > 0:
                roteiro += f'  • {l.qtd_meia} Meia(s)\n'
            if l.qtd_infantil > 0:
                idades = [i for i in l.idades_criancas.split(",") if i.strip()]
                roteiro += f'  • {l.qtd_infantil} Infantil(is) (idades: {", ".join(idades)})\n'
            info = l.subcategoria
            valor_inteira = float(getattr(info, 'valor_inteira', 0))
            valor_meia = float(getattr(info, 'valor_meia', 0))
            valor_infantil = float(getattr(info, 'valor_infantil', 0))
            subtotal_ingressos = (l.qtd_inteira * valor_inteira) + (l.qtd_meia * valor_meia) + (l.qtd_infantil * valor_infantil)
            resumo_servicos.append({
                'nome': l.subcategoria.nome,
                'valorIngressos': subtotal_ingressos
            })
        # Transfers deste dia
        if data in transfers_por_data and transfers_por_data[data]:
            roteiro += '\n 🚌 Transfers:\n'
            for t in transfers_por_data[data]:
                roteiro += f'     - 🚕 {t.transfer.nome} (R$ {float(t.valor):.2f})\n'
        roteiro += '\n'
    roteiro += '─' * 15 + '\n'
    roteiro += '💰 RESUMO DE VALORES\n'
    for item in resumo_servicos:
        if item['valorIngressos'] > 0:
            roteiro += f'\n🎫 {item["nome"]} - Ingresso: R$ {item["valorIngressos"]:.2f}'.replace('.', ',')
    roteiro += '\n' + '─' * 15 + '\n'

    return render(request, 'servicos/os/ordem_servico_form.html', {
        'form': form,
        'editando': True,
        'title': f'Editar Ordem de Serviço #{ordem.numero_os}',
        'categorias': categorias,
        'transfers': transfers,
        'lancamentos_json': json.dumps(lancamentos_data),
        'transfers_json': json.dumps(transfers_data),
        'roteiro': roteiro,
        # ...outros contextos necessários...
    })
# ...existing code...

@require_permission('servicos.delete_ordemservico')
def ordem_servico_delete(request, pk):
    """Deleta Ordem de Serviço inteira com todos os lançamentos"""
    ordem = get_object_or_404(OrdemServico, pk=pk)
    if request.method == 'POST':
        try:
            numero_os = ordem.numero_os
            qtd_servicos = ordem.lancamentos.count()
            ordem.delete()
            messages.success(request, f'Ordem de Serviço #{numero_os} deletada com sucesso ({qtd_servicos} serviço(s))!')
        except Exception as e:
            messages.error(request, f'Erro ao deletar: {str(e)}')
        return redirect('servicos:ordem_servico_list')
    lancamentos = ordem.lancamentos.all()
    context = {
        'ordem': ordem,
        'lancamentos': lancamentos,
        'title': f'Deletar OS #{ordem.numero_os}'
    }
    return render(request, 'servicos/os/ordem_servico_confirm_delete.html', context)



@require_permission('servicos.view_ordemservico')
def ordem_servico_detail(request, pk):
    """Visualiza detalhes completos da Ordem de Serviço"""
    from .models import OrdemServico
    ordem = get_object_or_404(OrdemServico, pk=pk)
    todos_lancamentos = ordem.lancamentos.select_related('categoria', 'subcategoria').all()
    transfers = ordem.transfers.select_related('transfer').all()
    context = {
        'ordem': ordem,
        'todos_lancamentos': todos_lancamentos,
        'transfers': transfers,
        'title': f'OS #{ordem.numero_os}'
    }
    return render(request, 'servicos/os/ordem_servico_detail.html', context)

# Alias para retrocompatibilidade  
lancamento_detail = ordem_servico_detail


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
    return JsonResponse(list(tipos), safe=False)


# ==================== VIEWS DE TRANSFER ====================

@require_permission('servicos.view_transfer')
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
    return render(request, 'servicos/transfers/transfer_list.html', context)


@require_permission('servicos.add_transfer')
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
    return render(request, 'servicos/transfers/transfer_form.html', context)


@require_permission('servicos.change_transfer')
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
    return render(request, 'servicos/transfers/transfer_form.html', context)


@require_permission('servicos.delete_transfer')
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
    return render(request, 'servicos/transfers/transfer_confirm_delete.html', context)


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


# ==================== TRADUÇÃO COM ARGOS ====================



@require_permission('servicos.view_ordemservico')
@require_http_methods(["POST"])
def translate_text(request):
    """Endpoint para tradução usando Argos Translate com preservação de formatação"""
    import json
    import re
    import argostranslate.package
    import argostranslate.translate
    
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'en')
        
        if not text:
            return JsonResponse({'error': 'Texto não fornecido'}, status=400)
        
        # Mapeamento de códigos de idioma
        lang_map = {
            'en': 'en',
            'es': 'es',
            'fr': 'fr'
        }
        
        target_code = lang_map.get(target_lang, 'en')
        
        # Dicionário de traduções customizadas para termos turísticos
        custom_translations = {
            'en': {
                # Termos gerais
                'CATARATAS': 'WATERFALLS',
                'Cataratas': 'Waterfalls',
                'cataratas': 'waterfalls',
                'Inteira': 'Full',
                'Inteira(s)': 'Full',
                'Meia': 'Half',
                'Meia(s)': 'Half',
                'Infantil': 'Child',
                'Transfer': 'Transfer',
                'Transfers': 'Transfers',
                'Ingresso': 'Ticket',
                'Ingressos': 'Tickets',
                'Roteiro': 'Itinerary',
                'ROTEIRO': 'ITINERARY',
                'Opção': 'Option',
                'OPÇÃO': 'OPTION',
                'RESUMO DOS VALORES': 'SUMMARY OF VALUES',
                'Resumo dos Valores': 'Summary of Values',
                'leva e trás': 'round trip',
                'leva e traz': 'round trip',
                'horário livre': 'flexible schedule',
                
                # Atrativos específicos
                'CATARATAS BR': 'WATERFALLS BR',
                'Cataratas BR': 'Waterfalls BR',
                'PARQUE DAS AVES': 'BIRD PARK',
                'Parque das Aves': 'Bird Park',
                'ITAIPU PANORAMICA': 'ITAIPU PANORAMIC',
                'Itaipu Panoramica': 'Itaipu Panoramic',
                'ITAIPU ESPECIAL': 'ITAIPU SPECIAL',
                'Itaipu Especial': 'Itaipu Special',
                'REFUGIO BIOLÓGICO': 'BIOLOGICAL REFUGE',
                'Refugio Biológico': 'Biological Refuge',
                'ILUMINADA ESPECIAL': 'ILLUMINATED SPECIAL',
                'Iluminada Especial': 'Illuminated Special',
                'ILUMINADA': 'ILLUMINATED',
                'Iluminada': 'Illuminated',
                'MARCO DAS TRÊS FRONTEIRAS': 'THREE BORDERS LANDMARK',
                'Marco das Três Fronteiras': 'Three Borders Landmark',
                'RODA GIGANTE': 'FERRIS WHEEL',
                'Roda Gigante': 'Ferris Wheel',
                'DREAMLAND COMBO 6': 'DREAMLAND COMBO 6',
                'DREAMLAND COMBO 5': 'DREAMLAND COMBO 5',
                'DREAMLAND QUARTETO': 'DREAMLAND QUARTET',
                'Dreamland Quarteto': 'Dreamland Quartet',
                'DREAMLAND TRIO NATUREZA': 'DREAMLAND NATURE TRIO',
                'Dreamland Trio Natureza': 'Dreamland Nature Trio',
                'TRIO BY NIGHT': 'TRIO BY NIGHT',
                'TRIO AVENTURA': 'ADVENTURE TRIO',
                'Trio Aventura': 'Adventure Trio',
                'MUSEU': 'MUSEUM',
                'Museu': 'Museum',
                'DREAM ECO PARK': 'DREAM ECO PARK',
                'TIROLEZA': 'ZIPLINE',
                'Tiroleza': 'Zipline',
                'MOVIE CARS': 'MOVIE CARS',
                'SHOW DAS ÁGUAS': 'WATER SHOW',
                'Show das Águas': 'Water Show',
                'COMBO MOVIE E SHOW': 'MOVIE AND SHOW COMBO',
                'Combo Movie e Show': 'Movie and Show Combo',
                'RAFAIN CHURRASCARIA SHOW': 'RAFAIN STEAKHOUSE SHOW',
                'Rafain Churrascaria Show': 'Rafain Steakhouse Show',
                'KATTAMARAM': 'CATAMARAN',
                'Kattamaram': 'Catamaran',
                'MACUCO SAFARI': 'MACUCO SAFARI',
                'IGUASSU SECRET FALLS ALL DAY': 'IGUASSU SECRET FALLS ALL DAY',
                'Iguassu Secret Falls All Day': 'Iguassu Secret Falls All Day',
                'IGUASSU SECRET MEIO PERIODO': 'IGUASSU SECRET HALF DAY',
                'Iguassu Secret Meio Periodo': 'Iguassu Secret Half Day',
                'IGUASSU SECRET TRILHA ÚNICA': 'IGUASSU SECRET SINGLE TRAIL',
                'Iguassu Secret Trilha Única': 'Iguassu Secret Single Trail',
                'LA ARIPUCA': 'LA ARIPUCA',
                'RUINAS SAN IGNACIO': 'SAN IGNACIO RUINS',
                'Ruinas San Ignacio': 'San Ignacio Ruins',
                'MINAS DE WANDA': 'WANDA MINES',
                'Minas de Wanda': 'Wanda Mines',
                'MESQUITA MULÇUMANA': 'MUSLIM MOSQUE',
                'Mesquita Mulçumana': 'Muslim Mosque',
            },
            'es': {
                # Termos gerais
                'CATARATAS': 'CATARATAS',
                'Cataratas': 'Cataratas',
                'cataratas': 'cataratas',
                'Inteira': 'Entera',
                'Inteira(s)': 'Entera(s)',
                'Meia': 'Media',
                'Meia(s)': 'Media(s)',
                'Infantil': 'Infantil',
                'Transfer': 'Transfer',
                'Transfers': 'Transfers',
                'Ingresso': 'Entrada',
                'Ingressos': 'Entradas',
                'Roteiro': 'Itinerario',
                'ROTEIRO': 'ITINERARIO',
                'Opção': 'Opción',
                'OPÇÃO': 'OPCIÓN',
                'RESUMO DOS VALORES': 'RESUMEN DE VALORES',
                'Resumo dos Valores': 'Resumen de Valores',
                'leva e trás': 'ida y vuelta',
                'leva e traz': 'ida y vuelta',
                'horário livre': 'horario libre',
                
                # Atrativos específicos
                'CATARATAS BR': 'CATARATAS BR',
                'Cataratas BR': 'Cataratas BR',
                'PARQUE DAS AVES': 'PARQUE DE LAS AVES',
                'Parque das Aves': 'Parque de las Aves',
                'ITAIPU PANORAMICA': 'ITAIPU PANORÁMICA',
                'Itaipu Panoramica': 'Itaipu Panorámica',
                'ITAIPU ESPECIAL': 'ITAIPU ESPECIAL',
                'Itaipu Especial': 'Itaipu Especial',
                'REFUGIO BIOLÓGICO': 'REFUGIO BIOLÓGICO',
                'Refugio Biológico': 'Refugio Biológico',
                'ILUMINADA ESPECIAL': 'ILUMINADA ESPECIAL',
                'Iluminada Especial': 'Iluminada Especial',
                'ILUMINADA': 'ILUMINADA',
                'Iluminada': 'Iluminada',
                'MARCO DAS TRÊS FRONTEIRAS': 'HITO DE LAS TRES FRONTERAS',
                'Marco das Três Fronteiras': 'Hito de las Tres Fronteras',
                'RODA GIGANTE': 'RUEDA GIGANTE',
                'Roda Gigante': 'Rueda Gigante',
                'DREAMLAND COMBO 6': 'DREAMLAND COMBO 6',
                'DREAMLAND COMBO 5': 'DREAMLAND COMBO 5',
                'DREAMLAND QUARTETO': 'DREAMLAND CUARTETO',
                'Dreamland Quarteto': 'Dreamland Cuarteto',
                'DREAMLAND TRIO NATUREZA': 'DREAMLAND TRÍO NATURALEZA',
                'Dreamland Trio Natureza': 'Dreamland Trío Naturaleza',
                'TRIO BY NIGHT': 'TRÍO BY NIGHT',
                'TRIO AVENTURA': 'TRÍO AVENTURA',
                'Trio Aventura': 'Trío Aventura',
                'MUSEU': 'MUSEO',
                'Museu': 'Museo',
                'DREAM ECO PARK': 'DREAM ECO PARK',
                'TIROLEZA': 'TIROLESA',
                'Tiroleza': 'Tirolesa',
                'MOVIE CARS': 'MOVIE CARS',
                'SHOW DAS ÁGUAS': 'SHOW DE LAS AGUAS',
                'Show das Águas': 'Show de las Aguas',
                'COMBO MOVIE E SHOW': 'COMBO MOVIE Y SHOW',
                'Combo Movie e Show': 'Combo Movie y Show',
                'RAFAIN CHURRASCARIA SHOW': 'RAFAIN PARRILLA SHOW',
                'Rafain Churrascaria Show': 'Rafain Parrilla Show',
                'KATTAMARAM': 'CATAMARÁN',
                'Kattamaram': 'Catamarán',
                'MACUCO SAFARI': 'MACUCO SAFARI',
                'IGUASSU SECRET FALLS ALL DAY': 'IGUASSU SECRET FALLS TODO EL DÍA',
                'Iguassu Secret Falls All Day': 'Iguassu Secret Falls Todo el Día',
                'IGUASSU SECRET MEIO PERIODO': 'IGUASSU SECRET MEDIO DÍA',
                'Iguassu Secret Meio Periodo': 'Iguassu Secret Medio Día',
                'IGUASSU SECRET TRILHA ÚNICA': 'IGUASSU SECRET SENDERO ÚNICO',
                'Iguassu Secret Trilha Única': 'Iguassu Secret Sendero Único',
                'LA ARIPUCA': 'LA ARIPUCA',
                'RUINAS SAN IGNACIO': 'RUINAS SAN IGNACIO',
                'Ruinas San Ignacio': 'Ruinas San Ignacio',
                'MINAS DE WANDA': 'MINAS DE WANDA',
                'Minas de Wanda': 'Minas de Wanda',
                'MESQUITA MULÇUMANA': 'MEZQUITA MUSULMANA',
                'Inteira(s)': 'Plein(s)',
                'Meia': 'Demi',
                'Meia(s)': 'Demi(s)',
                'Infantil': 'Enfant',
                'Transfer': 'Transfert',
                'Transfers': 'Transferts',
                'Ingresso': 'Billet',
                'Ingressos': 'Billets',
                'Roteiro': 'Itinéraire',
                'ROTEIRO': 'ITINÉRAIRE',
                'Opção': 'Option',
                'OPÇÃO': 'OPTION',
                'RESUMO DOS VALORES': 'RÉSUMÉ DES VALEURS',
                'Resumo dos Valores': 'Résumé des Valeurs',
                'leva e trás': 'aller-retour',
                'leva e traz': 'aller-retour',
                'horário livre': 'horaire libre',
                'Inteira': 'Plein',
                'Inteira(s)': 'Plein(s)',
                'Meia': 'Demi',
                'Meia(s)': 'Demi(s)',
                'Infantil': 'Enfant',
                'Transfer': 'Transfert',
                'Transfers': 'Transferts',
                'Ingresso': 'Billet',
                'Ingressos': 'Billets',
                
                # Atrativos específicos
                'CATARATAS BR': 'CHUTES D\'EAU BR',
                'Cataratas BR': 'Chutes d\'eau BR',
                'PARQUE DAS AVES': 'PARC DES OISEAUX',
                'Parque das Aves': 'Parc des Oiseaux',
                'ITAIPU PANORAMICA': 'ITAIPU PANORAMIQUE',
                'Itaipu Panoramica': 'Itaipu Panoramique',
                'ITAIPU ESPECIAL': 'ITAIPU SPÉCIAL',
                'Itaipu Especial': 'Itaipu Spécial',
                'REFUGIO BIOLÓGICO': 'REFUGE BIOLOGIQUE',
                'Refugio Biológico': 'Refuge Biologique',
                'ILUMINADA ESPECIAL': 'ILLUMINÉE SPÉCIALE',
                'Iluminada Especial': 'Illuminée Spéciale',
                'ILUMINADA': 'ILLUMINÉE',
                'Iluminada': 'Illuminée',
                'MARCO DAS TRÊS FRONTEIRAS': 'BORNE DES TROIS FRONTIÈRES',
                'Marco das Três Fronteiras': 'Borne des Trois Frontières',
                'RODA GIGANTE': 'GRANDE ROUE',
                'Roda Gigante': 'Grande Roue',
                'DREAMLAND COMBO 6': 'DREAMLAND COMBO 6',
                'DREAMLAND COMBO 5': 'DREAMLAND COMBO 5',
                'DREAMLAND QUARTETO': 'DREAMLAND QUATUOR',
                'Dreamland Quarteto': 'Dreamland Quatuor',
                'DREAMLAND TRIO NATUREZA': 'DREAMLAND TRIO NATURE',
                'Dreamland Trio Natureza': 'Dreamland Trio Nature',
                'TRIO BY NIGHT': 'TRIO BY NIGHT',
                'TRIO AVENTURA': 'TRIO AVENTURE',
                'Trio Aventura': 'Trio Aventure',
                'MUSEU': 'MUSÉE',
                'Museu': 'Musée',
                'DREAM ECO PARK': 'DREAM ECO PARK',
                'TIROLEZA': 'TYROLIENNE',
                'Tiroleza': 'Tyrolienne',
                'MOVIE CARS': 'MOVIE CARS',
                'SHOW DAS ÁGUAS': 'SPECTACLE DES EAUX',
                'Show das Águas': 'Spectacle des Eaux',
                'COMBO MOVIE E SHOW': 'COMBO MOVIE ET SHOW',
                'Combo Movie e Show': 'Combo Movie et Show',
                'RAFAIN CHURRASCARIA SHOW': 'RAFAIN RESTAURANT SHOW',
                'Rafain Churrascaria Show': 'Rafain Restaurant Show',
                'KATTAMARAM': 'CATAMARAN',
                'Kattamaram': 'Catamaran',
                'MACUCO SAFARI': 'MACUCO SAFARI',
                'IGUASSU SECRET FALLS ALL DAY': 'IGUASSU SECRET FALLS JOURNÉE COMPLÈTE',
                'Iguassu Secret Falls All Day': 'Iguassu Secret Falls Journée Complète',
                'IGUASSU SECRET MEIO PERIODO': 'IGUASSU SECRET DEMI-JOURNÉE',
                'Iguassu Secret Meio Periodo': 'Iguassu Secret Demi-Journée',
                'IGUASSU SECRET TRILHA ÚNICA': 'IGUASSU SECRET SENTIER UNIQUE',
                'Iguassu Secret Trilha Única': 'Iguassu Secret Sentier Unique',
                'LA ARIPUCA': 'LA ARIPUCA',
                'RUINAS SAN IGNACIO': 'RUINES SAN IGNACIO',
                'Ruinas San Ignacio': 'Ruines San Ignacio',
                'MINAS DE WANDA': 'MINES DE WANDA',
                'Minas de Wanda': 'Mines de Wanda',
                'MESQUITA MULÇUMANA': 'MOSQUÉE MUSULMANE',
                'Mesquita Mulçumana': 'Mosquée Musulmane',
            }
        }
        
        try:
            # Dicionário de proteção para elementos que não devem ser traduzidos
            protected = {}
            placeholder_counter = 0
            
            def protect_element(match):
                nonlocal placeholder_counter
                placeholder = f"PROTECT{placeholder_counter}PROTECT"
                protected[placeholder] = match.group(0)
                placeholder_counter += 1
                return placeholder
            
            # Proteger elementos antes da tradução
            text_protected = text
            
            # 1. Proteger linhas decorativas (═══, ───, etc)
            text_protected = re.sub(r'[─═]{3,}', protect_element, text_protected)
            
            # 2. Proteger emojis e símbolos especiais
            emoji_pattern = r'[📅🚌💰🎫📍⏰✈️🏨🍽️🎭🎨🏛️🌊🌲🦋🐦🌅🌄🎢🎡🎪🚁🚢⛵🏖️🗿🏰🎭📸🎬🎵🎸🎹🎺🎻🎤🎧🎮🎯🎲🎰🎳🏀⚽🏈🏉🎾🏐🏓🏸🥊🥋⛳🏹🎣🥅🥌🛷🎿⛷️🏂🏋️🤸🤼🤽🤾🤺🏇🏌️🧘🏃🚴🏊🤹]'
            text_protected = re.sub(emoji_pattern, protect_element, text_protected)
            
            # 3. Proteger bullets e caracteres especiais de lista
            text_protected = re.sub(r'[•◦▪▫]', protect_element, text_protected)
            
            # 4. Proteger valores monetários (R$ 000,00)
            text_protected = re.sub(r'R\$\s*[\d.,]+', protect_element, text_protected)
            
            # 5. Proteger datas (dd/mm/aaaa ou dd/mm)
            text_protected = re.sub(r'\d{2}/\d{2}(?:/\d{4})?', protect_element, text_protected)
            
            # 6. Proteger números entre parênteses (1 pax)
            text_protected = re.sub(r'\(\d+\s*pax\)', protect_element, text_protected)
            
            # 7. Proteger linhas que são apenas símbolos/espaços
            lines = text_protected.split('\n')
            protected_lines = []
            for line in lines:
                if re.match(r'^[\s─═•\-]+$', line) or not line.strip():
                    placeholder = f"PROTECTLINE{placeholder_counter}PROTECT"
                    protected[placeholder] = line
                    placeholder_counter += 1
                    protected_lines.append(placeholder)
                else:
                    protected_lines.append(line)
            text_protected = '\n'.join(protected_lines)
            
            # Aplicar traduções customizadas ANTES da tradução automática
            if target_code in custom_translations:
                for pt_term, translated_term in custom_translations[target_code].items():
                    # Usar placeholder numérico único que não será traduzido
                    placeholder = f"XYZTERM{placeholder_counter}XYZ"
                    protected[placeholder] = translated_term
                    placeholder_counter += 1
                    # Substituir termo português pelo placeholder
                    text_protected = text_protected.replace(pt_term, placeholder)
            
            # Traduzir texto com elementos protegidos
            if target_code == 'fr':
                intermediate_text = argostranslate.translate.translate(text_protected, "pt", "en")
                translated_text = argostranslate.translate.translate(intermediate_text, "en", "fr")
            else:
                translated_text = argostranslate.translate.translate(text_protected, "pt", target_code)
            
            # Restaurar elementos protegidos
            for placeholder, original in protected.items():
                translated_text = translated_text.replace(placeholder, original)
            
            return JsonResponse({
                'success': True,
                'translated_text': translated_text,
                'source_lang': 'pt',
                'target_lang': target_code
            })
            
        except Exception as e:
            return JsonResponse({
                'error': f'Erro na tradução: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
