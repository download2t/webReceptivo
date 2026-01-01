// Ordem de Serviço - Sistema de Múltiplos Serviços
(function() {
    'use strict';

    // Configuração e dados Django
    let djangoData = {};
    let servicosAdicionados = [];
    let servicoAtualInfo = null;
    let contadorTransfers = 0;
    let editandoId = null;

    // Inicialização quando DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function() {
        carregarDadosDjango();
        inicializarEventos();
        
        // Se estiver editando, carregar TODOS os lançamentos
        if (djangoData.editando && djangoData.lancamentosData && djangoData.lancamentosData.length > 0) {
            carregarLancamentosParaEdicao(djangoData.lancamentosData, djangoData.roteiro);
        }
    });

    function carregarDadosDjango() {
        const scriptData = document.getElementById('django-data');
        if (scriptData) {
            try {
                djangoData = JSON.parse(scriptData.textContent);
                console.log('=== DADOS DJANGO CARREGADOS ===');
                console.log('Editando?', djangoData.editando);
                console.log('Lançamentos:', djangoData.lancamentosData);
                console.log('Roteiro:', djangoData.roteiro);
                console.log('URLs:', djangoData.urls);
            } catch (e) {
                console.error('Erro ao parsear dados Django:', e);
                console.error('Conteúdo do script:', scriptData.textContent);
            }
        } else {
            console.error('Script #django-data não encontrado!');
        }
    }

    function inicializarEventos() {
        // Eventos de mudança de select
        document.getElementById('categoria').addEventListener('change', aoMudarCategoria);
        document.getElementById('servico').addEventListener('change', aoMudarServico);
        
        // Eventos de quantidade
        document.getElementById('qtdInfantil').addEventListener('input', aoMudarQtdInfantil);
        document.getElementById('qtdMeia').addEventListener('input', aoMudarQtdMeia);
        
        // Botões principais
        document.getElementById('btnAddTransfer').addEventListener('click', adicionarTransferOpcao);
        document.getElementById('btnAdicionarServico').addEventListener('click', adicionarServicoALista);
        document.getElementById('btnLimparForm').addEventListener('click', limparFormulario);
        document.getElementById('btnCopiarRoteiro').addEventListener('click', copiarRoteiro);
        document.getElementById('btnSalvarOS').addEventListener('click', salvarOrdemServico);
        document.getElementById('btnVerRegras').addEventListener('click', exibirRegrasNovamente);
    }

    function aoMudarCategoria() {
        const categoriaId = this.value;
        const servicoSelect = document.getElementById('servico');
        
        console.log('Categoria selecionada:', categoriaId);
        
        if (!categoriaId) {
            servicoSelect.innerHTML = '<option value="">Primeiro selecione uma categoria</option>';
            servicoSelect.disabled = true;
            document.getElementById('camposServico').classList.remove('show');
            return;
        }
        
        const url = '/servicos/ajax/subcategorias/?categoria_id=' + categoriaId;
        console.log('Buscando serviços:', url);
        
        fetch(url)
            .then(function(response) {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(function(data) {
                console.log('Serviços recebidos:', data);
                servicoSelect.innerHTML = '<option value="">Selecione o serviço...</option>';
                data.forEach(function(servico) {
                    const option = document.createElement('option');
                    option.value = servico.id;
                    option.textContent = servico.nome;
                    servicoSelect.appendChild(option);
                });
                servicoSelect.disabled = false;
            })
            .catch(function(error) {
                console.error('Erro ao carregar serviços:', error);
                alert('Erro ao carregar serviços: ' + error.message);
            });
    }

    function aoMudarServico() {
        const servicoId = this.value;
        
        if (!servicoId) {
            document.getElementById('camposServico').classList.remove('show');
            return;
        }
        
        const url = '/servicos/ajax/servico-info/?servico_id=' + servicoId;
        
        fetch(url)
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                servicoAtualInfo = data;
                console.log('Dados do serviço recebidos:', data);
                console.log('idade_isencao_min:', data.idade_isencao_min, 'tipo:', typeof data.idade_isencao_min);
                console.log('idade_isencao_max:', data.idade_isencao_max, 'tipo:', typeof data.idade_isencao_max);
                mostrarCamposServico(data);
            })
            .catch(function(error) {
                console.error('Erro ao carregar informações do serviço:', error);
                alert('Erro ao carregar informações do serviço');
            });
    }

    function mostrarCamposServico(info) {
        // Mostrar container
        document.getElementById('camposServico').classList.add('show');
        
        // Resetar campos
        document.getElementById('qtdInteira').value = 0;
        document.getElementById('qtdMeia').value = 0;
        document.getElementById('qtdInfantil').value = 0;
        document.getElementById('containerIdades').innerHTML = '';
        document.getElementById('containerTiposMeia').innerHTML = '';
        document.getElementById('containerTransfers').innerHTML = '';
        document.getElementById('descricaoServico').value = '';
        contadorTransfers = 0;
        
        // Mostrar/Ocultar campos baseado nas flags
        const campoMeia = document.getElementById('campoQtdMeia');
        const campoInfantil = document.getElementById('campoQtdInfantil');
        
        if (info.aceita_meia_entrada) {
            campoMeia.style.display = 'block';
        } else {
            campoMeia.style.display = 'none';
        }
        
        // Mostrar campo de infantil se permite infantil OU se tem isenção (para validar idades)
        if (info.permite_infantil || info.possui_isencao) {
            campoInfantil.style.display = 'block';
            // Mudar o label se não permite infantil mas tem isenção
            const labelInfantil = campoInfantil.querySelector('label');
            if (labelInfantil) {
                if (info.permite_infantil) {
                    labelInfantil.textContent = 'Qtd Infantil';
                } else {
                    labelInfantil.textContent = 'Qtd Crianças';
                }
            }
        } else {
            campoInfantil.style.display = 'none';
        }
        
        // Montar legenda de regras com validações aprimoradas
        atualizarRegrasServico(info);
        
        // Scroll suave para os campos
        document.getElementById('camposServico').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function aoMudarQtdInfantil() {
        const qtd = parseInt(this.value) || 0;
        // Sempre gerar campos de idade se há quantidade de crianças (para validar isenção)
        gerarCamposIdades(qtd);
    }

    function aoMudarQtdMeia() {
        const qtd = parseInt(this.value) || 0;
        gerarCamposTiposMeia(qtd);
    }

    function gerarCamposIdades(qtd) {
        const container = document.getElementById('containerIdades');
        const campoIdades = document.getElementById('campoIdades');
        
        container.innerHTML = '';
        
        if (qtd > 0) {
            campoIdades.style.display = 'block';
            
            // Se tem isenção mas não permite infantil, mostrar aviso
            if (servicoAtualInfo && servicoAtualInfo.possui_isencao && !servicoAtualInfo.permite_infantil) {
                const avisoDiv = document.createElement('div');
                avisoDiv.className = 'alert alert-warning py-2 mb-2';
                const idadeMin = servicoAtualInfo.idade_isencao_min !== undefined ? servicoAtualInfo.idade_isencao_min : '?';
                const idadeMax = servicoAtualInfo.idade_isencao_max !== undefined ? servicoAtualInfo.idade_isencao_max : '?';
                avisoDiv.innerHTML = '<small><i class="bi bi-info-circle me-1"></i>' +
                    '<strong>Atenção:</strong> Crianças na faixa de isenção (' + 
                    idadeMin + ' a ' + idadeMax + 
                    ' anos) <strong>NÃO PAGAM</strong>. Crianças fora desta faixa pagam <strong>INTEIRA</strong>.</small>';
                container.appendChild(avisoDiv);
            }
            for (let i = 1; i <= qtd; i++) {
                const col = document.createElement('div');
                col.className = 'col-md-3';
                
                const input = document.createElement('input');
                input.type = 'number';
                input.className = 'form-control idade-input';
                input.placeholder = 'Idade ' + i;
                input.min = '0';
                input.max = '120';
                input.required = true;
                input.addEventListener('input', validarIdade);
                
                col.appendChild(input);
                container.appendChild(col);
            }
        } else {
            campoIdades.style.display = 'none';
        }
    }

    function validarIdade(event) {
        const input = event.target;
        const idade = parseInt(input.value);
        
        console.log('validarIdade chamada para idade:', idade);
        console.log('servicoAtualInfo:', servicoAtualInfo);
        
        if (!servicoAtualInfo || isNaN(idade)) {
            input.classList.remove('isento', 'infantil', 'inteira', 'invalido');
            return;
        }
        
        // Limpar classes anteriores
        input.classList.remove('isento', 'infantil', 'inteira', 'invalido');
        
        // Validar idade mínima
        if (servicoAtualInfo.tem_idade_minima && idade < servicoAtualInfo.idade_minima) {
            input.classList.add('invalido');
            input.title = 'Idade abaixo da mínima permitida (' + servicoAtualInfo.idade_minima + ' anos)';
            return;
        }
        
        // Verificar isenção
        console.log('Verificando isenção:', {
            possui_isencao: servicoAtualInfo.possui_isencao,
            idade_isencao_min: servicoAtualInfo.idade_isencao_min,
            idade_isencao_max: servicoAtualInfo.idade_isencao_max,
            idade: idade,
            condicao: idade >= servicoAtualInfo.idade_isencao_min && idade <= servicoAtualInfo.idade_isencao_max
        });
        
        if (servicoAtualInfo.possui_isencao && 
            servicoAtualInfo.idade_isencao_min !== undefined && 
            servicoAtualInfo.idade_isencao_max !== undefined &&
            idade >= servicoAtualInfo.idade_isencao_min && 
            idade <= servicoAtualInfo.idade_isencao_max) {
            console.log('APLICANDO CLASSE ISENTO');
            input.classList.add('isento');
            input.title = 'Isento (grátis)';
            return;
        }
        
        // Verificar infantil
        if (servicoAtualInfo.permite_infantil && 
            idade >= servicoAtualInfo.idade_minima_infantil && 
            idade <= servicoAtualInfo.idade_maxima_infantil) {
            input.classList.add('infantil');
            input.title = 'Paga Infantil (R$ ' + parseFloat(servicoAtualInfo.valor_infantil).toFixed(2) + ')';
            return;
        }
        
        // Senão, paga inteira
        console.log('APLICANDO CLASSE INTEIRA');
        input.classList.add('inteira');
        input.title = 'Paga Inteira (R$ ' + parseFloat(servicoAtualInfo.valor_inteira).toFixed(2) + ')';
    }

    function gerarCamposTiposMeia(qtd) {
        const container = document.getElementById('containerTiposMeia');
        const campoTiposMeia = document.getElementById('campoTiposMeia');
        
        container.innerHTML = '';
        
        if (qtd > 0) {
            campoTiposMeia.style.display = 'block';
            
            fetch('/servicos/ajax/tipos-meia/')
                .then(function(response) {
                    return response.json();
                })
                .then(function(tipos) {
                    for (let i = 1; i <= qtd; i++) {
                        const col = document.createElement('div');
                        col.className = 'col-md-6';
                        
                        const select = document.createElement('select');
                        select.className = 'form-select tipo-meia-select';
                        select.required = true;
                        
                        const optDefault = document.createElement('option');
                        optDefault.value = '';
                        optDefault.textContent = 'Tipo Meia ' + i;
                        select.appendChild(optDefault);
                        
                        tipos.forEach(function(tipo) {
                            const opt = document.createElement('option');
                            opt.value = tipo.id;
                            opt.textContent = tipo.nome;
                            select.appendChild(opt);
                        });
                        
                        col.appendChild(select);
                        container.appendChild(col);
                    }
                })
                .catch(function(error) {
                    console.error('Erro ao carregar tipos de meia:', error);
                });
        } else {
            campoTiposMeia.style.display = 'none';
        }
    }

    function adicionarTransferOpcao() {
        contadorTransfers++;
        const container = document.getElementById('containerTransfers');
        const templateSelect = document.getElementById('transferTemplate');
        
        const div = document.createElement('div');
        div.className = 'transfer-opcao';
        
        const wrapper = document.createElement('div');
        wrapper.className = 'd-flex align-items-center gap-2';
        
        const label = document.createElement('label');
        label.className = 'form-label small mb-0';
        label.textContent = 'Opção ' + contadorTransfers;
        
        const selectClone = templateSelect.cloneNode(true);
        selectClone.id = '';
        selectClone.style.display = '';
        selectClone.className = 'form-select form-select-sm flex-grow-1 transfer-select';
        selectClone.setAttribute('data-transfer', contadorTransfers);
        
        const btnRemove = document.createElement('button');
        btnRemove.type = 'button';
        btnRemove.className = 'btn btn-sm btn-outline-danger';
        btnRemove.innerHTML = '<i class="bi bi-trash"></i>';
        btnRemove.addEventListener('click', function() {
            div.remove();
            contadorTransfers--;
        });
        
        wrapper.appendChild(label);
        wrapper.appendChild(selectClone);
        wrapper.appendChild(btnRemove);
        div.appendChild(wrapper);
        container.appendChild(div);
    }

    function adicionarServicoALista() {
        // Validações básicas
        const dataServico = document.getElementById('dataServico').value;
        const categoriaId = document.getElementById('categoria').value;
        const servicoId = document.getElementById('servico').value;
        const servicoNome = document.getElementById('servico').selectedOptions[0].textContent;
        
        if (!dataServico || !categoriaId || !servicoId) {
            alert('Por favor, preencha data, categoria e serviço');
            return;
        }
        
        if (!servicoAtualInfo) {
            alert('Informações do serviço não carregadas');
            return;
        }
        
        // Coletar quantidades
        const qtdInteira = parseInt(document.getElementById('qtdInteira').value) || 0;
        const qtdMeia = parseInt(document.getElementById('qtdMeia').value) || 0;
        const qtdInfantil = parseInt(document.getElementById('qtdInfantil').value) || 0;
        
        if (qtdInteira === 0 && qtdMeia === 0 && qtdInfantil === 0) {
            alert('Adicione ao menos uma quantidade (Inteira, Meia ou Infantil)');
            return;
        }
        
        // Validar idades se houver infantil
        let idades = [];
        if (qtdInfantil > 0) {
            const idadesInputs = document.querySelectorAll('#containerIdades input.idade-input');
            if (idadesInputs.length !== qtdInfantil) {
                alert('Preencha as idades de todas as crianças');
                return;
            }
            
            let temInvalido = false;
            idadesInputs.forEach(function(input) {
                const idade = parseInt(input.value);
                if (isNaN(idade)) {
                    temInvalido = true;
                } else if (input.classList.contains('invalido')) {
                    temInvalido = true;
                }
                idades.push(idade);
            });
            
            if (temInvalido) {
                alert('Existem idades inválidas (vermelho). Por favor, corrija.');
                return;
            }
        }
        
        // Validar tipos de meia se houver meia
        let tiposMeia = [];
        if (qtdMeia > 0) {
            const tiposSelects = document.querySelectorAll('#containerTiposMeia select.tipo-meia-select');
            if (tiposSelects.length !== qtdMeia) {
                alert('Preencha os tipos de meia entrada');
                return;
            }
            
            let temVazio = false;
            tiposSelects.forEach(function(select) {
                if (!select.value) {
                    temVazio = true;
                } else {
                    tiposMeia.push({
                        id: select.value,
                        tipo: select.selectedOptions[0].textContent
                    });
                }
            });
            
            if (temVazio) {
                alert('Selecione todos os tipos de meia entrada');
                return;
            }
        }
        
        // Coletar transfers
        let transfers = [];
        let valorTransferIda = 0;
        let valorTransferVolta = 0;
        
        const transferSelects = document.querySelectorAll('.transfer-select');
        transferSelects.forEach(function(select) {
            if (select.value) {
                const option = select.selectedOptions[0];
                const transferNome = option.getAttribute('data-nome');
                const transferValor = parseFloat(option.getAttribute('data-valor'));
                
                transfers.push({
                    transfer_id: select.value,  // ID do transfer
                    nome: transferNome,
                    data: dataServico,  // Usar a mesma data do serviço
                    quantidade: 1,  // Padrão 1
                    valor: transferValor
                });
                
                // Determinar se é ida ou volta (simplificado: primeiro = ida, segundo = volta)
                if (transfers.length === 1) {
                    valorTransferIda = transferValor;
                } else {
                    valorTransferVolta += transferValor;
                }
            }
        });
        
        // Descrição
        let descricao = document.getElementById('descricaoServico').value.trim();
        if (!descricao) {
            descricao = servicoNome;
            if (qtdInteira > 0) descricao += ' - ' + qtdInteira + ' Inteira(s)';
            if (qtdMeia > 0) descricao += ' - ' + qtdMeia + ' Meia(s)';
            if (qtdInfantil > 0) descricao += ' - ' + qtdInfantil + ' Infantil(is)';
        }
        
        // Criar objeto do serviço
        const servico = {
            id: editandoId || Date.now(),
            data: dataServico,
            categoria_id: categoriaId,
            servico_id: servicoId,
            servico_nome: servicoNome,
            qtd_inteira: qtdInteira,
            qtd_meia: qtdMeia,
            qtd_infantil: qtdInfantil,
            idades: idades,
            tipos_meia: tiposMeia,
            transfers: transfers,
            valor_transfer_ida: valorTransferIda,
            valor_transfer_volta: valorTransferVolta,
            descricao: descricao,
            info: servicoAtualInfo
        };
        
        // Adicionar ou atualizar
        if (editandoId) {
            const index = servicosAdicionados.findIndex(function(s) {
                return s.id === editandoId;
            });
            if (index !== -1) {
                servicosAdicionados[index] = servico;
            }
            editandoId = null;
        } else {
            servicosAdicionados.push(servico);
        }
        
        // Atualizar UI
        atualizarListaServicos();
        atualizarRoteiro();
        limparFormulario(false); // false = não limpar data/categoria
        
        // Scroll suave para o select de serviço
        document.getElementById('servico').scrollIntoView({ behavior: 'smooth', block: 'center' });
        document.getElementById('servico').focus();
    }

    function editarServico(id) {
        const servico = servicosAdicionados.find(function(s) {
            return s.id === id;
        });
        
        if (!servico) return;
        
        editandoId = id;
        
        // Preencher form
        document.getElementById('dataServico').value = servico.data;
        document.getElementById('categoria').value = servico.categoria_id;
        
        // Disparar evento para carregar serviços
        const categoriaSelect = document.getElementById('categoria');
        categoriaSelect.dispatchEvent(new Event('change'));
        
        // Aguardar carregamento dos serviços
        setTimeout(function() {
            document.getElementById('servico').value = servico.servico_id;
            document.getElementById('servico').dispatchEvent(new Event('change'));
            
            // Aguardar carregamento das infos do serviço
            setTimeout(function() {
                document.getElementById('qtdInteira').value = servico.qtd_inteira;
                document.getElementById('qtdMeia').value = servico.qtd_meia;
                document.getElementById('qtdInfantil').value = servico.qtd_infantil;
                
                // Gerar campos de idades
                if (servico.qtd_infantil > 0) {
                    gerarCamposIdades(servico.qtd_infantil);
                    setTimeout(function() {
                        const idadesInputs = document.querySelectorAll('#containerIdades input.idade-input');
                        idadesInputs.forEach(function(input, idx) {
                            input.value = servico.idades[idx];
                            input.dispatchEvent(new Event('input'));
                        });
                    }, 100);
                }
                
                // Gerar campos de tipos de meia
                if (servico.qtd_meia > 0) {
                    gerarCamposTiposMeia(servico.qtd_meia);
                    setTimeout(function() {
                        const tiposSelects = document.querySelectorAll('#containerTiposMeia select.tipo-meia-select');
                        tiposSelects.forEach(function(select, idx) {
                            select.value = servico.tipos_meia[idx].id;
                        });
                    }, 100);
                }
                
                // Adicionar transfers
                servico.transfers.forEach(function() {
                    adicionarTransferOpcao();
                });
                
                setTimeout(function() {
                    const transferSelects = document.querySelectorAll('.transfer-select');
                    transferSelects.forEach(function(select, idx) {
                        if (servico.transfers[idx]) {
                            select.value = servico.transfers[idx].transfer_id || servico.transfers[idx].id;
                        }
                    });
                }, 100);
                
                document.getElementById('descricaoServico').value = servico.descricao;
                
                // Scroll para o formulário
                document.getElementById('camposServico').scrollIntoView({ behavior: 'smooth' });
            }, 500);
        }, 500);
    }

    function removerServico(id) {
        if (!confirm('Deseja realmente remover este serviço?')) return;
        
        servicosAdicionados = servicosAdicionados.filter(function(s) {
            return s.id !== id;
        });
        
        atualizarListaServicos();
        atualizarRoteiro();
    }

    function atualizarListaServicos() {
        const container = document.getElementById('listaServicos');
        
        if (servicosAdicionados.length === 0) {
            container.innerHTML = '<div class="text-center text-muted py-4">' +
                '<i class="bi bi-inbox display-4 d-block mb-2"></i>' +
                '<p>Nenhum serviço adicionado ainda</p>' +
                '</div>';
            return;
        }
        
        container.innerHTML = '';
        
        servicosAdicionados.forEach(function(servico) {
            const div = document.createElement('div');
            div.className = 'servico-adicionado';
            
            let html = '<div class="d-flex justify-content-between align-items-start mb-2">' +
                '<div>' +
                '<h6 class="mb-1"><i class="bi bi-calendar-event me-1"></i>' + formatarData(servico.data) + '</h6>' +
                '<p class="mb-1"><strong>' + servico.servico_nome + '</strong></p>' +
                '</div>' +
                '<div class="btn-group">' +
                '<button class="btn btn-sm btn-outline-primary" onclick="window.editarServico(' + servico.id + ')">' +
                '<i class="bi bi-pencil"></i>' +
                '</button>' +
                '<button class="btn btn-sm btn-outline-danger" onclick="window.removerServico(' + servico.id + ')">' +
                '<i class="bi bi-trash"></i>' +
                '</button>' +
                '</div>' +
                '</div>';
            
            html += '<div class="small">';
            if (servico.qtd_inteira > 0) html += '<span class="badge bg-primary me-1">' + servico.qtd_inteira + ' Inteira</span>';
            if (servico.qtd_meia > 0) html += '<span class="badge bg-info me-1">' + servico.qtd_meia + ' Meia</span>';
            if (servico.qtd_infantil > 0) html += '<span class="badge bg-success me-1">' + servico.qtd_infantil + ' Infantil (idades: ' + servico.idades.join(', ') + ')</span>';
            html += '</div>';
            
            if (servico.transfers.length > 0) {
                html += '<div class="small mt-1"><i class="bi bi-bus-front me-1"></i>';
                servico.transfers.forEach(function(t, idx) {
                    html += t.nome;
                    if (idx < servico.transfers.length - 1) html += ', ';
                });
                html += '</div>';
            }
            
            div.innerHTML = html;
            container.appendChild(div);
        });
        
        // Atualizar resumo de totais
        atualizarResumoTotais();
    }
    
    // Função para atualizar o resumo detalhado (tipo nota fiscal)
    function atualizarResumoTotais() {
        const container = document.getElementById('resumoDetalhado');
        const totalPaxEl = document.getElementById('totalPaxGeral');
        const valorTotalEl = document.getElementById('valorTotalGeral');
        
        if (!container || !totalPaxEl || !valorTotalEl) {
            console.warn('Elementos do resumo não encontrados no DOM');
            return;
        }
        
        if (servicosAdicionados.length === 0) {
            container.innerHTML = '<div class="text-center text-muted py-3"><small>Nenhum serviço adicionado</small></div>';
            totalPaxEl.textContent = '0';
            valorTotalEl.textContent = 'R$ 0,00';
            return;
        }
        
        let totalGeral = 0;
        let totalPaxGeral = 0;
        let html = '<div class="list-group list-group-flush">';
        
        servicosAdicionados.forEach(function(servico, index) {
            const info = servico.info || {};
            const nomeServico = info.nome || 'Serviço sem nome';
            const data = servico.data || '';
            
            // Calcula valores do serviço
            const qtdInteira = parseInt(servico.qtd_inteira) || 0;
            const qtdMeia = parseInt(servico.qtd_meia) || 0;
            const qtdInfantil = parseInt(servico.qtd_infantil) || 0;
            
            const valorInteira = parseFloat(info.valor_inteira || 0);
            const valorMeia = parseFloat(info.valor_meia || 0);
            const valorInfantil = parseFloat(info.valor_infantil || 0);
            
            const subtotalInteira = qtdInteira * valorInteira;
            const subtotalMeia = qtdMeia * valorMeia;
            const subtotalInfantil = qtdInfantil * valorInfantil;
            
            // Transfer - somar todos os transfers do array
            let totalTransfer = 0;
            if (servico.transfers && servico.transfers.length > 0) {
                servico.transfers.forEach(function(transfer) {
                    totalTransfer += parseFloat(transfer.valor || 0);
                });
            }
            
            const subtotalServico = subtotalInteira + subtotalMeia + subtotalInfantil + totalTransfer;
            totalGeral += subtotalServico;
            totalPaxGeral += qtdInteira + qtdMeia + qtdInfantil;
            
            html += '<div class="list-group-item p-2">';
            html += '<div class="d-flex justify-content-between align-items-start mb-2">';
            html += '<div class="flex-grow-1">';
            html += '<strong class="d-block">' + (index + 1) + '. ' + nomeServico + '</strong>';
            html += '<small class="text-muted">' + formatarDataBrasileira(data) + '</small>';
            html += '</div>';
            html += '<span class="badge bg-secondary">' + (qtdInteira + qtdMeia + qtdInfantil) + ' PAX</span>';
            html += '</div>';
            
            // Detalhes dos valores
            html += '<div class="small ms-3">';
            
            if (qtdInteira > 0) {
                html += '<div class="d-flex justify-content-between">';
                html += '<span class="text-primary">• ' + qtdInteira + ' Inteira(s) × R$ ' + valorInteira.toFixed(2).replace('.', ',') + '</span>';
                html += '<span class="text-primary">R$ ' + subtotalInteira.toFixed(2).replace('.', ',') + '</span>';
                html += '</div>';
            }
            
            if (qtdMeia > 0) {
                html += '<div class="d-flex justify-content-between">';
                html += '<span class="text-info">• ' + qtdMeia + ' Meia(s) × R$ ' + valorMeia.toFixed(2).replace('.', ',') + '</span>';
                html += '<span class="text-info">R$ ' + subtotalMeia.toFixed(2).replace('.', ',') + '</span>';
                html += '</div>';
            }
            
            if (qtdInfantil > 0) {
                html += '<div class="d-flex justify-content-between">';
                html += '<span class="text-success">• ' + qtdInfantil + ' Infantil(is) × R$ ' + valorInfantil.toFixed(2).replace('.', ',') + '</span>';
                html += '<span class="text-success">R$ ' + subtotalInfantil.toFixed(2).replace('.', ',') + '</span>';
                html += '</div>';
            }
            
            // Transfers - mostrar cada um com seu nome
            if (servico.transfers && servico.transfers.length > 0) {
                servico.transfers.forEach(function(transfer) {
                    const valorTransfer = parseFloat(transfer.valor || 0);
                    if (valorTransfer > 0) {
                        html += '<div class="d-flex justify-content-between">';
                        html += '<span class="text-warning">• ' + transfer.nome + '</span>';
                        html += '<span class="text-warning">R$ ' + valorTransfer.toFixed(2).replace('.', ',') + '</span>';
                        html += '</div>';
                    }
                });
            }
            
            html += '</div>';
            
            // Subtotal do serviço
            html += '<div class="d-flex justify-content-end mt-2 pt-2 border-top">';
            html += '<strong>Subtotal: <span class="text-dark">R$ ' + subtotalServico.toFixed(2).replace('.', ',') + '</span></strong>';
            html += '</div>';
            
            html += '</div>';
        });
        
        html += '</div>';
        
        container.innerHTML = html;
        totalPaxEl.textContent = totalPaxGeral;
        valorTotalEl.textContent = 'R$ ' + totalGeral.toFixed(2).replace('.', ',');
    }
    
    // Função auxiliar para formatar data
    function formatarDataBrasileira(data) {
        if (!data) return '';
        const partes = data.split('-');
        if (partes.length === 3) {
            return partes[2] + '/' + partes[1] + '/' + partes[0];
        }
        return data;
    }

    function atualizarRoteiro() {
        const preview = document.getElementById('roteiroPreview');
        
        if (servicosAdicionados.length === 0) {
            preview.innerHTML = '<div class="text-center text-muted">' +
                '<i class="bi bi-file-earmark-text display-3 d-block mb-3"></i>' +
                '<p>Adicione serviços para visualizar o roteiro</p>' +
                '</div>';
            return;
        }
        
        // Agrupar por data
        const porData = {};
        servicosAdicionados.forEach(function(servico) {
            if (!porData[servico.data]) {
                porData[servico.data] = [];
            }
            porData[servico.data].push(servico);
        });
        
        // Ordenar datas
        const datasOrdenadas = Object.keys(porData).sort();
        
        // Gerar roteiro
        let roteiro = '=== ROTEIRO ===\n\n';
        
        datasOrdenadas.forEach(function(data) {
            roteiro += '📅 ' + formatarData(data) + '\n';
            roteiro += '─'.repeat(50) + '\n\n';
            
            porData[data].forEach(function(servico, idx) {
                roteiro += 'Opção ' + (idx + 1) + '\n';
                roteiro += servico.descricao + '\n';
                
                if (servico.qtd_inteira > 0) roteiro += '  • ' + servico.qtd_inteira + ' Inteira(s)\n';
                if (servico.qtd_meia > 0) roteiro += '  • ' + servico.qtd_meia + ' Meia(s)\n';
                if (servico.qtd_infantil > 0) roteiro += '  • ' + servico.qtd_infantil + ' Infantil(is) (idades: ' + servico.idades.join(', ') + ')\n';
                
                if (servico.transfers.length > 0) {
                    roteiro += '  🚌 Transfers:\n';
                    servico.transfers.forEach(function(t) {
                        roteiro += '     - ' + t.nome + ' (R$ ' + parseFloat(t.valor).toFixed(2) + ')\n';
                    });
                }
                
                roteiro += '\n';
            });
            
            roteiro += '\n';
        });
        
        preview.textContent = roteiro;
    }

    function formatarData(data) {
        const partes = data.split('-');
        return partes[2] + '/' + partes[1] + '/' + partes[0];
    }

    function limparFormulario(limparTudo) {
        if (limparTudo !== false) {
            document.getElementById('dataServico').value = '';
            document.getElementById('categoria').value = '';
            document.getElementById('servico').value = '';
            document.getElementById('servico').disabled = true;
            document.getElementById('camposServico').classList.remove('show');
        } else {
            // Manter data e categoria, apenas resetar o serviço
            document.getElementById('servico').value = '';
            // Não ocultar os campos, apenas limpar os valores
        }
        
        document.getElementById('qtdInteira').value = 0;
        document.getElementById('qtdMeia').value = 0;
        document.getElementById('qtdInfantil').value = 0;
        document.getElementById('containerIdades').innerHTML = '';
        document.getElementById('containerTiposMeia').innerHTML = '';
        document.getElementById('containerTransfers').innerHTML = '';
        document.getElementById('descricaoServico').value = '';
        
        // Ocultar campos condicionais
        document.getElementById('campoIdades').style.display = 'none';
        document.getElementById('campoTiposMeia').style.display = 'none';
        document.getElementById('campoQtdMeia').style.display = 'none';
        document.getElementById('campoQtdInfantil').style.display = 'none';
        document.getElementById('regrasServico').style.display = 'none';
        
        servicoAtualInfo = null;
        contadorTransfers = 0;
        editandoId = null;
    }

    function copiarRoteiro() {
        const texto = document.getElementById('roteiroPreview').textContent;
        
        if (!texto || texto.includes('Adicione serviços')) {
            alert('Nenhum roteiro para copiar');
            return;
        }
        
        navigator.clipboard.writeText(texto)
            .then(function() {
                alert('Roteiro copiado para a área de transferência!');
            })
            .catch(function(error) {
                console.error('Erro ao copiar:', error);
                alert('Erro ao copiar roteiro');
            });
    }

    function salvarOrdemServico() {
        if (servicosAdicionados.length === 0) {
            alert('Adicione ao menos um serviço');
            return;
        }
        
        const dados = {
            servicos: servicosAdicionados,
            roteiro: document.getElementById('roteiroPreview').textContent
        };
        
        // URL varia se está editando ou criando
        let url = djangoData.urls.ordemServicoCreate || djangoData.urls.lancamentoCreate;
        
        if (djangoData.editando && djangoData.lancamentosData && djangoData.lancamentosData.length > 0) {
            // Pegar o ID do primeiro lançamento (todos pertencem à mesma OS)
            const primeiroLancamentoId = djangoData.lancamentosData[0].id;
            url = '/servicos/lancamentos/' + primeiroLancamentoId + '/editar/';
        }
        
        console.log('URL de salvamento:', url);
        console.log('Editando?', djangoData.editando);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': djangoData.csrfToken
            },
            body: JSON.stringify(dados)
        })
        .then(function(response) {
            if (response.ok) {
                alert('Ordem de Serviço salva com sucesso!');
                window.location.href = djangoData.urls.ordemServicoList || djangoData.urls.lancamentoList;
            } else {
                return response.json().then(function(data) {
                    alert('Erro ao salvar: ' + (data.error || 'Erro desconhecido'));
                });
            }
        })
        .catch(function(error) {
            console.error('Erro:', error);
            alert('Erro ao salvar ordem de serviço');
        });
    }

    function carregarLancamentosParaEdicao(lancamentos, roteiro) {
        console.log('=== CARREGANDO LANÇAMENTOS PARA EDIÇÃO ===');
        console.log('Quantidade de lançamentos:', lancamentos ? lancamentos.length : 0);
        console.log('Roteiro:', roteiro);
        
        // Carregar TODOS os lançamentos da OS
        if (lancamentos && lancamentos.length > 0) {
            servicosAdicionados = []; // Limpar array primeiro
            
            lancamentos.forEach(function(lancamento, index) {
                console.log('Carregando lançamento ' + (index + 1) + ':', lancamento);
                
                // Garantir que o objeto tem todas as propriedades necessárias
                const servicoCompleto = {
                    id: lancamento.id || Date.now() + index,
                    data: lancamento.data,
                    categoria_id: lancamento.categoria_id,
                    servico_id: lancamento.servico_id,
                    servico_nome: lancamento.servico_nome,
                    qtd_inteira: parseInt(lancamento.qtd_inteira) || 0,
                    qtd_meia: parseInt(lancamento.qtd_meia) || 0,
                    qtd_infantil: parseInt(lancamento.qtd_infantil) || 0,
                    idades: lancamento.idades || [],
                    tipos_meia: lancamento.tipos_meia || [],
                    transfers: lancamento.transfers || [],
                    valor_transfer_ida: parseFloat(lancamento.valor_transfer_ida) || 0,
                    valor_transfer_volta: parseFloat(lancamento.valor_transfer_volta) || 0,
                    descricao: lancamento.descricao || '',
                    info: lancamento.info || {}
                };
                
                servicosAdicionados.push(servicoCompleto);
                console.log('Serviço adicionado:', servicoCompleto);
            });
            
            console.log('Total de serviços carregados:', servicosAdicionados.length);
            console.log('Array servicosAdicionados:', servicosAdicionados);
            
            // Atualizar a UI
            atualizarListaServicos();
            
            // Se há roteiro salvo, definir no preview
            if (roteiro) {
                const roteiroElement = document.getElementById('roteiroPreview');
                if (roteiroElement) {
                    roteiroElement.textContent = roteiro;
                    console.log('Roteiro carregado no preview');
                }
            } else {
                console.log('Gerando roteiro automaticamente...');
                atualizarRoteiro();
            }
            
            console.log('=== CARREGAMENTO CONCLUÍDO ===');
        } else {
            console.warn('Nenhum lançamento para carregar ou array vazio');
        }
    }

// Função para atualizar e exibir regras do serviço de forma detalhada
    function atualizarRegrasServico(info) {
        const regrasDiv = document.getElementById('regrasServico');
        const listaRegras = document.getElementById('listaRegras');
        listaRegras.innerHTML = '';
        
        let temRegras = false;
        
        // 1. REGRAS DE ISENÇÃO (mais importante - aparece primeiro)
        if (info.possui_isencao) {
            const li = document.createElement('li');
            li.className = 'mb-2';
            const idadeMin = info.idade_isencao_min !== undefined ? info.idade_isencao_min : '?';
            const idadeMax = info.idade_isencao_max !== undefined ? info.idade_isencao_max : '?';
            li.innerHTML = '<i class="bi bi-gift text-success me-2"></i>' +
                '<strong class="text-success">ISENÇÃO:</strong> Crianças de ' + 
                idadeMin + ' a ' + idadeMax + ' anos são <strong>GRATUITAS</strong>' +
                '<br><small class="text-muted ms-4">Estas crianças não pagam nada</small>';
            listaRegras.appendChild(li);
            temRegras = true;
        }
        
        // 2. REGRAS DE INFANTIL
        if (info.permite_infantil) {
            const li = document.createElement('li');
            li.className = 'mb-2';
            li.innerHTML = '<i class="bi bi-check-circle text-info me-2"></i>' +
                '<strong class="text-info">INFANTIL:</strong> Crianças de ' + 
                info.idade_minima_infantil + ' a ' + info.idade_maxima_infantil + ' anos' +
                '<br><small class="text-muted ms-4">Valor: <strong>R$ ' + parseFloat(info.valor_infantil).toFixed(2) + '</strong> por criança</small>';
            listaRegras.appendChild(li);
            temRegras = true;
        }
        
        // 3. IDADE MÍNIMA (alerta se existir)
        if (info.tem_idade_minima) {
            const li = document.createElement('li');
            li.className = 'mb-2';
            li.innerHTML = '<i class="bi bi-exclamation-triangle-fill text-danger me-2"></i>' +
                '<strong class="text-danger">IDADE MÍNIMA:</strong> ' + info.idade_minima + ' anos' +
                '<br><small class="text-muted ms-4">⚠️ Crianças abaixo desta idade <strong>NÃO podem participar</strong></small>';
            listaRegras.appendChild(li);
            temRegras = true;
        }
        
        // 4. MEIA ENTRADA
        if (info.aceita_meia_entrada) {
            const li = document.createElement('li');
            li.className = 'mb-2';
            const regrasTexto = info.regras_meia_entrada ? 
                '<br><small class="text-muted ms-4">📋 ' + info.regras_meia_entrada + '</small>' : '';
            li.innerHTML = '<i class="bi bi-ticket-perforated text-warning me-2"></i>' +
                '<strong class="text-warning">MEIA ENTRADA:</strong> Aceita' +
                '<br><small class="text-muted ms-4">Valor: <strong>R$ ' + parseFloat(info.valor_meia).toFixed(2) + '</strong> por pessoa</small>' +
                regrasTexto;
            listaRegras.appendChild(li);
            temRegras = true;
        } else {
            const li = document.createElement('li');
            li.className = 'mb-2';
            li.innerHTML = '<i class="bi bi-x-circle text-secondary me-2"></i>' +
                '<span class="text-secondary">Não aceita meia entrada neste serviço</span>';
            listaRegras.appendChild(li);
            temRegras = true;
        }
        
        // 5. VALOR INTEIRA (sempre mostrar destacado)
        const li = document.createElement('li');
        li.className = 'mb-2';
        li.innerHTML = '<i class="bi bi-cash-coin text-primary me-2"></i>' +
            '<strong class="text-primary">VALOR INTEIRA:</strong> R$ ' + parseFloat(info.valor_inteira).toFixed(2) +
            '<br><small class="text-muted ms-4">Valor padrão para adultos e crianças fora das faixas especiais</small>';
        listaRegras.appendChild(li);
        temRegras = true;
        
        // 6. RESUMO DAS FAIXAS (tabela visual)
        const resumo = document.createElement('li');
        resumo.className = 'mb-0 mt-3';
        let tabelaHTML = '<div class="border-top pt-2">' +
            '<strong class="d-block mb-2"><i class="bi bi-table me-2"></i>Resumo de Faixas Etárias:</strong>' +
            '<div class="table-responsive">' +
            '<table class="table table-sm table-bordered mb-0" style="font-size: 0.85rem;">' +
            '<thead class="table-light">' +
            '<tr>' +
            '<th>Faixa</th>' +
            '<th>Idade</th>' +
            '<th>Valor</th>' +
            '</tr>' +
            '</thead>' +
            '<tbody>';
        
        // Ordenar faixas por idade
        let faixas = [];
        
        // Determinar a faixa inteira corretamente
        let idadeInteiraTexto = '';
        if (info.permite_infantil) {
            // Se permite infantil, inteira é acima da idade máxima infantil
            idadeInteiraTexto = 'Acima de ' + info.idade_maxima_infantil + ' anos';
        } else if (info.possui_isencao) {
            // Se não permite infantil mas tem isenção, inteira é acima da isenção
            idadeInteiraTexto = 'Acima de ' + info.idade_isencao_max + ' anos';
        } else if (info.tem_idade_minima) {
            // Se só tem idade mínima, inteira é a partir da idade mínima
            idadeInteiraTexto = 'A partir de ' + info.idade_minima + ' anos';
        } else {
            // Caso genérico
            idadeInteiraTexto = 'Todas as idades';
        }
        
        if (info.possui_isencao) {
            const idadeMin = info.idade_isencao_min !== undefined ? info.idade_isencao_min : '?';
            const idadeMax = info.idade_isencao_max !== undefined ? info.idade_isencao_max : '?';
            faixas.push({
                nome: '🎁 Isento',
                idade: idadeMin + ' - ' + idadeMax + ' anos',
                valor: 'Grátis',
                classe: 'table-success'
            });
        }
        
        if (info.permite_infantil) {
            faixas.push({
                nome: '👶 Infantil',
                idade: info.idade_minima_infantil + ' - ' + info.idade_maxima_infantil + ' anos',
                valor: 'R$ ' + parseFloat(info.valor_infantil).toFixed(2),
                classe: 'table-info'
            });
        }
        
        faixas.push({
            nome: '👤 Inteira',
            idade: idadeInteiraTexto,
            valor: 'R$ ' + parseFloat(info.valor_inteira).toFixed(2),
            classe: 'table-warning'
        });
        
        faixas.forEach(function(faixa) {
            tabelaHTML += '<tr class="' + faixa.classe + '">' +
                '<td><strong>' + faixa.nome + '</strong></td>' +
                '<td>' + faixa.idade + '</td>' +
                '<td><strong>' + faixa.valor + '</strong></td>' +
                '</tr>';
        });
        
        tabelaHTML += '</tbody></table></div></div>';
        resumo.innerHTML = tabelaHTML;
        listaRegras.appendChild(resumo);
        
        // Exibir ou ocultar
        if (temRegras) {
            regrasDiv.style.display = 'block';
            regrasDiv.className = 'alert alert-light border shadow-sm'; // Melhor visualização
            
            // Mostrar botão "Ver Regras" para consulta rápida
            const btnVerRegras = document.getElementById('btnVerRegras');
            if (btnVerRegras) {
                btnVerRegras.style.display = 'inline-block';
            }
        } else {
            regrasDiv.style.display = 'none';
            const btnVerRegras = document.getElementById('btnVerRegras');
            if (btnVerRegras) {
                btnVerRegras.style.display = 'none';
            }
        }
        
        // Scroll suave para as regras
        setTimeout(function() {
            regrasDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }
    
    // Função para reexibir regras quando o usuário clicar no botão
    function exibirRegrasNovamente() {
        const regrasDiv = document.getElementById('regrasServico');
        if (regrasDiv && regrasDiv.style.display !== 'none') {
            regrasDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Efeito de destaque
            regrasDiv.style.animation = 'none';
            setTimeout(function() {
                regrasDiv.style.animation = 'pulse 0.5s ease-in-out';
            }, 10);
        } else if (servicoAtualInfo) {
            // Se as regras estão ocultas, mas temos info do serviço, reexibir
            atualizarRegrasServico(servicoAtualInfo);
        } else {
            alert('⚠️ Por favor, selecione um serviço primeiro para ver as regras de negócio.');
        }
    }

    // Expor funções globalmente para uso nos botões
    window.editarServico = editarServico;
    window.removerServico = removerServico;
})();
