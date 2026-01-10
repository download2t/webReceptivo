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
from .models import Categoria, SubCategoria, TipoMeiaEntrada, LancamentoServico, Transfer, OrdemServico, TransferOS
from .forms import CategoriaForm, SubCategoriaForm, TipoMeiaEntradaForm, LancamentoServicoForm, TransferForm
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
    """Lista Ordens de Serviço (OS) com seus lançamentos agrupados"""
    ordens = OrdemServico.objects.select_related('criado_por').prefetch_related(
        'lancamentos__categoria',
        'lancamentos__subcategoria'
    ).all().order_by('-data_criacao')
    
    # Filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    
    if search:
        ordens = ordens.filter(
            Q(numero_os__icontains=search) |
            Q(lancamentos__subcategoria__nome__icontains=search) |
            Q(roteiro__icontains=search)
        ).distinct()
    
    if categoria_id:
        ordens = ordens.filter(lancamentos__categoria_id=categoria_id).distinct()
    
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

# Alias para retrocompatibilidade
lancamento_list = ordem_servico_list


@require_permission('servicos.add_ordemservico')
def ordem_servico_create(request):
    """Cria novo lançamento / ordem de serviço com múltiplos serviços"""
    import json
    from decimal import Decimal
    from django.utils import timezone
    
    if request.method == 'POST':
        # Verificar se é JSON (múltiplos serviços)
        if request.content_type == 'application/json':
            try:
                dados = json.loads(request.body)
                servicos = dados.get('servicos', [])
                roteiro = dados.get('roteiro', '')
                
                if not servicos:
                    return JsonResponse({'error': 'Nenhum serviço informado'}, status=400)
                
                # CRIAR UMA ORDEM DE SERVIÇO PRIMEIRO
                ordem = OrdemServico.objects.create(
                    cliente=None,  # Sem cliente por enquanto
                    roteiro=roteiro,
                    status='confirmado',
                    criado_por=request.user
                )
                
                # OS criada com sucesso
                
                # Criar todos os lançamentos vinculados a esta OS
                lancamentos_criados = []
                
                for servico_data in servicos:
                    # Extrair dados
                    data_servico = servico_data['data']
                    servico_id = servico_data['servico_id']
                    qtd_inteira = int(servico_data.get('qtd_inteira') or 0)
                    qtd_meia = int(servico_data.get('qtd_meia') or 0)
                    qtd_infantil = int(servico_data.get('qtd_infantil') or 0)
                    # Converter idades para int, ignorando valores vazios
                    idades_raw = servico_data.get('idades', [])
                    idades = [int(i) for i in idades_raw if i and str(i).strip()]
                    tipos_meia = servico_data.get('tipos_meia', [])
                    descricao = servico_data.get('descricao', '')
                    
                    # Buscar serviço
                    servico = SubCategoria.objects.get(pk=servico_id)
                    
                    # Criar lançamento vinculado à OS
                    lancamento = LancamentoServico.objects.create(
                        ordem_servico=ordem,  # VINCULAR À OS
                        data_servico=data_servico,
                        categoria=servico.categoria,
                        subcategoria=servico,
                        qtd_inteira=qtd_inteira,
                        qtd_meia=qtd_meia,
                        qtd_infantil=qtd_infantil,
                        idades_criancas=','.join(map(str, idades)) if idades else '',
                        obs_publica=descricao,
                        criado_por=request.user,
                        # Snapshot dos valores
                        valor_unit_inteira=servico.valor_inteira,
                        valor_unit_meia=servico.valor_meia,
                        valor_unit_infantil=servico.valor_infantil,
                    )
                    
                    # Lançamento criado com sucesso
                    
                    # Associar tipos de meia
                    if tipos_meia:
                        tipos_texto = '\n'.join([t.get('tipo', t.get('nome', '')) for t in tipos_meia])
                        lancamento.tipos_meia_entrada = tipos_texto
                        lancamento.save()
                    
                    # Criar transfers deste serviço específico
                    transfers_servico = servico_data.get('transfers', [])
                    for transfer_data in transfers_servico:
                        transfer_obj = Transfer.objects.get(pk=transfer_data['transfer_id'])
                        valor_transfer = Decimal(str(transfer_data.get('valor', 0)))
                        
                        transfer_os = TransferOS.objects.create(
                            ordem_servico=ordem,
                            lancamento_servico=lancamento,  # VINCULAR AO LANÇAMENTO
                            transfer=transfer_obj,
                            data_transfer=transfer_data['data'],
                            quantidade=transfer_data.get('quantidade', 1),
                            valor=valor_transfer
                        )
                        # Transfer vinculado
                    
                    lancamentos_criados.append(lancamento)
                
                # Atualizar totais da OS
                ordem.calcular_total()
                
                messages.success(request, f'Ordem de Serviço #{ordem.numero_os} criada com {len(lancamentos_criados)} serviço(s)!')
                return JsonResponse({
                    'success': True, 
                    'message': f'Ordem de Serviço #{ordem.numero_os} criada com sucesso',
                    'ordem_id': ordem.id,
                    'numero_os': ordem.numero_os
                })
                
            except Exception as e:
                import traceback
                error_msg = str(e)
                traceback.print_exc()
                print(f"ERRO AO SALVAR OS: {error_msg}")
                return JsonResponse({'error': error_msg}, status=500, json_dumps_params={'ensure_ascii': False})
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
        return render(request, 'servicos/os/ordem_servico_form.html', context)

# Alias para retrocompatibilidade
lancamento_create = ordem_servico_create

@require_permission('servicos.change_ordemservico')
def ordem_servico_edit(request, pk):
    """Edita lançamento existente - usa mesmo template de criação"""
    lancamento = get_object_or_404(LancamentoServico, pk=pk)
    ordem = lancamento.ordem_servico
    
    if request.method == 'POST':
        # Se for JSON (salvamento do formulário novo)
        if request.content_type == 'application/json':
            import json
            from decimal import Decimal
            try:
                dados = json.loads(request.body)
                servicos = dados.get('servicos', [])
                roteiro = dados.get('roteiro', '')
                
                if not servicos:
                    return JsonResponse({'error': 'Nenhum serviço informado'}, status=400)
                
                # Atualizar roteiro da OS
                if ordem:
                    ordem.roteiro = roteiro
                    ordem.save()
                    
                    # Remover todos os lançamentos e transfers antigos da OS
                    ordem.lancamentos.all().delete()
                    ordem.transfers_os.all().delete()
                    
                    # Criar novos lançamentos com seus transfers
                    for servico_data in servicos:
                        # Extrair dados
                        data_servico = servico_data['data']
                        servico_id = servico_data['servico_id']
                        qtd_inteira = int(servico_data.get('qtd_inteira') or 0)
                        qtd_meia = int(servico_data.get('qtd_meia') or 0)
                        qtd_infantil = int(servico_data.get('qtd_infantil') or 0)
                        idades_raw = servico_data.get('idades', [])
                        idades = [int(i) for i in idades_raw if i and str(i).strip()]
                        tipos_meia = servico_data.get('tipos_meia', [])
                        descricao = servico_data.get('descricao', '')
                        
                        # Buscar serviço
                        servico = SubCategoria.objects.get(pk=servico_id)
                        
                        # Criar novo lançamento vinculado à OS
                        novo_lancamento = LancamentoServico.objects.create(
                            ordem_servico=ordem,
                            data_servico=data_servico,
                            categoria=servico.categoria,
                            subcategoria=servico,
                            qtd_inteira=qtd_inteira,
                            qtd_meia=qtd_meia,
                            qtd_infantil=qtd_infantil,
                            idades_criancas=','.join(map(str, idades)) if idades else '',
                            obs_publica=descricao,
                            criado_por=request.user,
                            valor_unit_inteira=servico.valor_inteira,
                            valor_unit_meia=servico.valor_meia,
                            valor_unit_infantil=servico.valor_infantil,
                        )
                        
                        # Associar tipos de meia
                        if tipos_meia:
                            tipos_texto = '\n'.join([t.get('tipo', t.get('nome', '')) for t in tipos_meia])
                            novo_lancamento.tipos_meia_entrada = tipos_texto
                            novo_lancamento.save()
                        
                        # Criar transfers deste serviço específico
                        transfers_servico = servico_data.get('transfers', [])
                        for transfer_data in transfers_servico:
                            transfer_obj = Transfer.objects.get(pk=transfer_data['transfer_id'])
                            valor_transfer = Decimal(str(transfer_data.get('valor', 0)))
                            
                            TransferOS.objects.create(
                                ordem_servico=ordem,
                                lancamento_servico=novo_lancamento,  # VINCULAR AO LANÇAMENTO
                                transfer=transfer_obj,
                                data_transfer=transfer_data['data'],
                                quantidade=transfer_data.get('quantidade', 1),
                                valor=valor_transfer
                            )
                    
                    # Atualizar totais da OS
                    ordem.calcular_total()
                    
                    messages.success(request, f'Ordem de Serviço #{ordem.numero_os} atualizada com {len(servicos)} serviço(s)!')
                    return JsonResponse({
                        'success': True, 
                        'message': f'Ordem de Serviço #{ordem.numero_os} atualizada com sucesso',
                        'ordem_id': ordem.id,
                        'numero_os': ordem.numero_os
                    })
                else:
                    return JsonResponse({'error': 'Lançamento não possui Ordem de Serviço vinculada'}, status=400)
                
            except Exception as e:
                import traceback
                error_msg = str(e)
                traceback.print_exc()
                print(f"ERRO AO EDITAR OS: {error_msg}")
                return JsonResponse({'error': error_msg}, status=500, json_dumps_params={'ensure_ascii': False})
        else:
            # Form tradicional (fallback)
            form = LancamentoServicoForm(request.POST, instance=lancamento)
            if form.is_valid():
                form.save()
                messages.success(request, 'Lançamento atualizado com sucesso!')
                return redirect('servicos:lancamento_list')
    
    # GET - preparar dados para o JavaScript
    categorias = Categoria.objects.filter(ativo=True)
    transfers = Transfer.objects.filter(ativo=True)
    
    # Converter TODOS os lançamentos da OS para formato JavaScript
    import json
    
    # Pegar todos os lançamentos da mesma OS
    if ordem:
        todos_lancamentos = ordem.lancamentos.all().order_by('id')
        roteiro = ordem.roteiro
    else:
        todos_lancamentos = [lancamento]
        roteiro = ""
    
    lancamentos_data = []
    
    for lanc in todos_lancamentos:
        idades = []
        if lanc.idades_criancas:
            idades = [int(i.strip()) for i in lanc.idades_criancas.split(',') if i.strip()]
        
        tipos_meia = []
        if lanc.tipos_meia_entrada:
            # Buscar todos os tipos de meia disponíveis para fazer o mapeamento
            todos_tipos_meia = TipoMeiaEntrada.objects.filter(ativo=True)
            mapa_tipos = {t.nome: t.id for t in todos_tipos_meia}
            
            for tipo_texto in lanc.tipos_meia_entrada.split('\n'):
                tipo_texto = tipo_texto.strip()
                if tipo_texto:
                    # Tentar encontrar o ID real pelo nome
                    tipo_id = mapa_tipos.get(tipo_texto)
                    if tipo_id:
                        tipos_meia.append({
                            'id': tipo_id,
                            'tipo': tipo_texto,
                            'nome': tipo_texto
                        })
                    else:
                        # Se não encontrar, usar o primeiro tipo disponível como fallback
                        primeiro_tipo = todos_tipos_meia.first()
                        if primeiro_tipo:
                            tipos_meia.append({
                                'id': primeiro_tipo.id,
                                'tipo': tipo_texto,
                                'nome': tipo_texto
                            })
        
        # Coletar transfers deste lançamento usando o vínculo direto
        transfers_lista = []
        if ordem:
            # Usar o related_name 'transfers_vinculados' do campo lancamento_servico
            for transfer_os in lanc.transfers_vinculados.all():
                transfers_lista.append({
                    'id': transfer_os.id,
                    'transfer_id': transfer_os.transfer.id,
                    'nome': transfer_os.transfer.nome,
                    'data': transfer_os.data_transfer.strftime('%Y-%m-%d'),
                    'quantidade': transfer_os.quantidade,
                    'valor': float(transfer_os.valor)
                })
        
        lancamentos_data.append({
            'id': lanc.id,
            'data': lanc.data_servico.strftime('%Y-%m-%d'),
            'categoria_id': lanc.categoria.id,
            'servico_id': lanc.subcategoria.id,
            'servico_nome': lanc.subcategoria.nome,
            'qtd_inteira': lanc.qtd_inteira,
            'qtd_meia': lanc.qtd_meia,
            'qtd_infantil': lanc.qtd_infantil,
            'idades': idades,
            'tipos_meia': tipos_meia,
            'transfers': transfers_lista,
            'valor_transfer_ida': float(lanc.valor_transfer_ida),
            'valor_transfer_volta': float(lanc.valor_transfer_volta),
            'descricao': lanc.obs_publica or lanc.subcategoria.nome,
            'info': {
                'id': lanc.subcategoria.id,
                'nome': lanc.subcategoria.nome,
                'valor_inteira': float(lanc.subcategoria.valor_inteira),
                'valor_meia': float(lanc.subcategoria.valor_meia),
                'valor_infantil': float(lanc.subcategoria.valor_infantil),
                'aceita_meia_entrada': lanc.subcategoria.aceita_meia_entrada,
                'permite_infantil': lanc.subcategoria.permite_infantil,
                'possui_isencao': lanc.subcategoria.possui_isencao,
                'tem_idade_minima': lanc.subcategoria.tem_idade_minima,
                'idade_minima': lanc.subcategoria.idade_minima,
                'idade_minima_infantil': lanc.subcategoria.idade_minima_infantil,
                'idade_maxima_infantil': lanc.subcategoria.idade_maxima_infantil,
                'idade_minima_isencao': lanc.subcategoria.idade_isencao_min,
                'idade_maxima_isencao': lanc.subcategoria.idade_isencao_max,
            }
        })
    
    context = {
        'categorias': categorias,
        'transfers': transfers,
        'title': f'Editar OS #{ordem.numero_os if ordem else lancamento.id}',
        'editando': True,
        'lancamentos_json': json.dumps(lancamentos_data),
        'roteiro': roteiro,
    }
    return render(request, 'servicos/os/ordem_servico_form.html', context)

# Alias para retrocompatibilidade
lancamento_edit = ordem_servico_edit

@require_permission('servicos.delete_ordemservico')
def ordem_servico_delete(request, pk):
    """Deleta Ordem de Serviço inteira com todos os lançamentos"""
    lancamento = get_object_or_404(LancamentoServico, pk=pk)
    ordem = lancamento.ordem_servico
    
    if request.method == 'POST':
        try:
            if ordem:
                numero_os = ordem.numero_os
                qtd_servicos = ordem.lancamentos.count()
                # Deletar a OS inteira (cascade vai deletar os lançamentos)
                ordem.delete()
                messages.success(request, f'Ordem de Serviço #{numero_os} deletada com sucesso ({qtd_servicos} serviço(s))!')
            else:
                # Lançamento sem OS, deletar só ele
                lancamento.delete()
                messages.success(request, 'Lançamento deletado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao deletar: {str(e)}')
        return redirect('servicos:lancamento_list')
    
    # Buscar todos os lançamentos da OS
    lancamentos = ordem.lancamentos.all() if ordem else [lancamento]
    
    context = {
        'lancamento': lancamento,
        'ordem': ordem,
        'lancamentos': lancamentos,
        'title': f'Deletar OS #{ordem.numero_os if ordem else lancamento.id}'
    }
    return render(request, 'servicos/os/ordem_servico_confirm_delete.html', context)


@require_permission('servicos.view_ordemservico')
def ordem_servico_detail(request, pk):
    """Visualiza detalhes completos da Ordem de Serviço"""
    lancamento = get_object_or_404(
        LancamentoServico.objects.select_related(
            'categoria', 'subcategoria', 'criado_por', 'ordem_servico'
        ),
        pk=pk
    )
    
    ordem = lancamento.ordem_servico
    
    # Pegar todos os lançamentos da OS
    if ordem:
        todos_lancamentos = ordem.lancamentos.select_related('categoria', 'subcategoria').all()
    else:
        todos_lancamentos = [lancamento]
    
    context = {
        'lancamento': lancamento,
        'ordem': ordem,
        'todos_lancamentos': todos_lancamentos,
        'title': f'OS #{ordem.numero_os if ordem else lancamento.id}'
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
    """Endpoint para tradução usando argostranslate + dicionário customizado"""
    import json
    import re
    from .translations import CUSTOM_TRANSLATIONS  # Seu dicionário customizado
    
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'en')
        
        if not text:
            return JsonResponse({'error': 'Texto não fornecido'}, status=400, json_dumps_params={'ensure_ascii': False})
        
        # Mapear códigos de idioma do frontend para argostranslate
        lang_map = {
            'pt': 'pt',  # Português
            'en': 'en',  # Inglês
            'es': 'es',  # Espanhol
            'fr': 'fr',  # Francês
            'de': 'de',  # Alemão
            'it': 'it',  # Italiano
        }
        
        source_code = 'pt'
        target_code = lang_map.get(target_lang, 'en')
        
        if source_code == target_code:
            return JsonResponse({
                'success': True,
                'translated_text': text,
                'source_lang': source_code,
                'target_lang': target_code,
                'method': 'no_translation_needed'
            }, json_dumps_params={'ensure_ascii': False})
        
        # Proteger elementos que NÃO devem ser traduzidos
        protected = {}
        counter = 0
        
        def protect(match):
            nonlocal counter
            key = f"__PROTECT_{counter:04d}__"
            protected[key] = match.group(0)
            counter += 1
            return key
        
        text_protected = text
        
        # 1. Proteger datas completas (dd/mm/yyyy)
        text_protected = re.sub(r'\b\d{1,2}/\d{1,2}/\d{4}\b', protect, text_protected)
        
        # 2. Proteger valores monetários (R$ 1.234,56)
        text_protected = re.sub(r'R\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?', protect, text_protected)
        
        # 3. Proteger códigos específicos (OS-2024-001, CAT-123)
        text_protected = re.sub(r'\b(?:OS|CAT|TRF|CLI)-\d{4}-\d{3,}\b', protect, text_protected, flags=re.IGNORECASE)
        
        # 4. Proteger nomes próprios de atrações (em maiúsculas seguidas)
        text_protected = re.sub(r'\b([A-Z]{2,}(?:\s+[A-Z]{2,}){1,3})\b(?![a-z])', protect, text_protected)
        
        # 5. Proteger horários (09h30, 14:00)
        text_protected = re.sub(r'\b\d{1,2}(?:h|:)\d{2}\b', protect, text_protected)
        
        # 6. Proteger números entre parênteses
        text_protected = re.sub(r'\(\s*\d+(?:\s*(?:pax|anos?|idades?|hora?s?|pessoas?))\s*\)', protect, text_protected, flags=re.IGNORECASE)
        
        # APLICAR DICIONÁRIO CUSTOMIZADO PRIMEIRO
        # (para termos específicos do seu domínio)
        custom_dict = CUSTOM_TRANSLATIONS.get(target_lang, CUSTOM_TRANSLATIONS.get('en', {}))
        
        # Ordenar por comprimento (mais longo primeiro) para evitar sobreposições
        sorted_custom = sorted(custom_dict.items(), key=lambda x: -len(x[0]))
        
        for pt_term, custom_translation in sorted_custom:
            # Usar substituição com word boundaries para palavras completas
            if pt_term.isalpha():
                pattern = r'\b' + re.escape(pt_term) + r'\b'
                text_protected = re.sub(pattern, custom_translation, text_protected, flags=re.IGNORECASE)
            else:
                # Para frases ou termos com espaços
                text_protected = text_protected.replace(pt_term, custom_translation)
        
        # AGORA USAR ARGOSTRANSLATE PARA O RESTO
        try:
            import argostranslate.translate
            import argostranslate.package
            import argostranslate.models
            
            # Verificar se o pacote de tradução está instalado
            installed_languages = argostranslate.translate.get_installed_languages()
            from_lang = next((lang for lang in installed_languages if lang.code == source_code), None)
            to_lang = next((lang for lang in installed_languages if lang.code == target_code), None)
            
            if from_lang and to_lang:
                # Traduzir com argostranslate
                translation = from_lang.get_translation(to_lang)
                text_translated = translation.translate(text_protected)
            else:
                # Fallback para tradução simples se não houver pacote
                text_translated = text_protected
                print(f"Aviso: Pacote de tradução {source_code}->{target_code} não encontrado")
        except Exception as e:
            print(f"Erro argostranslate: {e}")
            text_translated = text_protected  # Fallback
            
        # RESTAURAR ELEMENTOS PROTEGIDOS
        # Ordem inversa para evitar conflitos
        for i in range(counter-1, -1, -1):
            key = f"__PROTECT_{i:04d}__"
            if key in protected:
                text_translated = text_translated.replace(key, protected[key])
        
        return JsonResponse({
            'success': True,
            'translated_text': text_translated,
            'source_lang': source_code,
            'target_lang': target_code,
            'method': 'argostranslate_with_custom_dict',
            'custom_terms_applied': len(custom_dict)
        }, json_dumps_params={'ensure_ascii': False})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        print(f"ERRO TRADUÇÃO: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500, json_dumps_params={'ensure_ascii': False})