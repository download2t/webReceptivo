// Ordem de Serviço - Sistema de Múltiplos Serviços
(function() {
    'use strict';

    // Configuração e dados Django
    let djangoData = {};
    let servicosAdicionados = [];
    let servicoAtualInfo = null;
    let contadorTransfers = 0;
    let editandoId = null;
    let transferEditandoId = null;

    // Inicialização quando DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function() {
        carregarDadosDjango();
        inicializarEventos();

        // Preencher campos de texto OS ao editar
        if (djangoData.editando) {
            if (typeof djangoData.clientes === 'string' && document.getElementById('id_clientes')) {
                document.getElementById('id_clientes').value = djangoData.clientes;
            }
            if (typeof djangoData.hospedagem === 'string' && document.getElementById('id_hospedagem')) {
                document.getElementById('id_hospedagem').value = djangoData.hospedagem;
            }
        }

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
        const btnAddTransfer = document.getElementById('btnAddTransfer');
        const btnSalvarTransfer = document.getElementById('btnSalvarTransfer');
        const btnAdicionarServico = document.getElementById('btnAdicionarServico');
        const btnLimparForm = document.getElementById('btnLimparForm');
        const btnCopiarRoteiro = document.getElementById('btnCopiarRoteiro');
        const btnSalvarOS = document.getElementById('btnSalvarOS');
        const btnVerRegras = document.getElementById('btnVerRegras');
        
        if (btnAddTransfer) btnAddTransfer.addEventListener('click', adicionarTransferOpcao);
        if (btnSalvarTransfer) btnSalvarTransfer.addEventListener('click', confirmarEdicaoTransfer);
        if (btnAdicionarServico) btnAdicionarServico.addEventListener('click', adicionarServicoALista);
        if (btnLimparForm) btnLimparForm.addEventListener('click', limparFormulario);
        if (btnCopiarRoteiro) {
            console.log('Botão copiar roteiro encontrado, adicionando event listener');
            btnCopiarRoteiro.addEventListener('click', copiarRoteiro);
        } else {
            console.error('Botão btnCopiarRoteiro NÃO encontrado!');
        }
        if (btnSalvarOS) btnSalvarOS.addEventListener('click', salvarOrdemServico);
        if (btnVerRegras) btnVerRegras.addEventListener('click', exibirRegrasNovamente);
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

    function gerarCamposTiposMeia(qtd, callback) {
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
                    // Chamar callback após criar todos os campos
                    if (callback) callback();
                })
                .catch(function(error) {
                    console.error('Erro ao carregar tipos de meia:', error);
                    if (callback) callback();
                });
        } else {
            campoTiposMeia.style.display = 'none';
            if (callback) callback();
        }
    }

    function adicionarTransferOpcao(dadosPreenchimento) {
        const dados = dadosPreenchimento || {};
        contadorTransfers++;
        const container = document.getElementById('containerTransfers');
        const templateSelect = document.getElementById('transferTemplate');

        const div = document.createElement('div');
        div.className = 'transfer-opcao mb-2';

        const wrapper = document.createElement('div');
        wrapper.className = 'd-flex align-items-center gap-2';

        const label = document.createElement('label');
        label.className = 'form-label small mb-0';
        label.textContent = 'Opção ' + contadorTransfers;
        label.style.minWidth = '60px';

        // Campo select do transfer
        const selectClone = templateSelect.cloneNode(true);
        selectClone.id = '';
        selectClone.style.display = '';
        selectClone.className = 'form-select form-select-sm transfer-select';
        selectClone.setAttribute('data-transfer', contadorTransfers);
        selectClone.style.flex = '2';

        const nomeInput = document.createElement('input');
        nomeInput.type = 'text';
        nomeInput.className = 'form-control form-control-sm transfer-nome-input';
        nomeInput.placeholder = 'Nome na OS';
        nomeInput.style.flex = '2';
        nomeInput.style.minWidth = '180px';

        // Campo de valor editável
        const valorInput = document.createElement('input');
        valorInput.type = 'number';
        valorInput.step = '0.01';
        valorInput.min = '0';
        valorInput.className = 'form-control form-control-sm transfer-valor-input';
        valorInput.placeholder = 'Valor';
        valorInput.style.flex = '1';
        valorInput.style.minWidth = '100px';
        valorInput.value = '0.00';

        // Evento para preencher o valor automaticamente ao selecionar transfer
        selectClone.addEventListener('change', function() {
            if (this.value) {
                const option = this.selectedOptions[0];
                const transferValor = option.getAttribute('data-valor');
                const transferNome = option.getAttribute('data-nome') || '';
                nomeInput.value = transferNome;
                valorInput.value = parseFloat(transferValor).toFixed(2);
            } else {
                nomeInput.value = '';
                valorInput.value = '0.00';
            }
            // Adicionar transfer avulso ao roteiro imediatamente
            atualizarTransferAvulsoAoRoteiro();
        });

        nomeInput.addEventListener('input', function() {
            atualizarTransferAvulsoAoRoteiro();
        });

        // Adicionar transfer avulso ao roteiro ao digitar valor
        valorInput.addEventListener('input', function() {
            atualizarTransferAvulsoAoRoteiro();
        });

        const btnRemove = document.createElement('button');
        btnRemove.type = 'button';
        btnRemove.className = 'btn btn-sm btn-outline-danger';
        btnRemove.innerHTML = '<i class="bi bi-trash"></i>';
        btnRemove.addEventListener('click', function() {
            div.remove();
            atualizarTransferAvulsoAoRoteiro();
        });

        wrapper.appendChild(label);
        wrapper.appendChild(selectClone);
        wrapper.appendChild(nomeInput);
        wrapper.appendChild(valorInput);
        wrapper.appendChild(btnRemove);
        div.appendChild(wrapper);
        container.appendChild(div);

        if (dados.transfer_id) {
            selectClone.value = String(dados.transfer_id);
            selectClone.dispatchEvent(new Event('change'));
            if (dados.nome_personalizado !== undefined) {
                nomeInput.value = dados.nome_personalizado;
            }
            if (dados.valor !== undefined && dados.valor !== null && dados.valor !== '') {
                valorInput.value = parseFloat(dados.valor).toFixed(2);
            }
            atualizarTransferEdicaoUI();
            atualizarTransferAvulsoAoRoteiro();
        }

        // Função para adicionar transfer avulso ao roteiro
        function atualizarTransferAvulsoAoRoteiro() {
            // Preserva os itens já salvos e substitui apenas o transfer em edição, quando houver
            let itensBase = servicosAdicionados.filter(function(s) {
                return !s.__transfer_avulso || (transferEditandoId && s.id !== transferEditandoId);
            });

            // Coletar todos transfers do DOM
            const transferOpcoes = document.querySelectorAll('#containerTransfers .transfer-opcao');
            transferOpcoes.forEach(function(opcao, idx) {
                const select = opcao.querySelector('.transfer-select');
                const nomeInput = opcao.querySelector('.transfer-nome-input');
                const valorInput = opcao.querySelector('.transfer-valor-input');
                if (select && select.value && valorInput) {
                    const option = select.selectedOptions[0];
                    const transferNome = option.getAttribute('data-nome');
                    const nomePersonalizado = nomeInput ? nomeInput.value.trim() : '';
                    const transferValor = parseFloat(valorInput.value) || 0;
                    // Adiciona transfer avulso ao array
                    itensBase.push({
                        id: transferEditandoId || ('transfer_avulso_' + idx + '_' + Date.now()),
                        servico_nome: nomePersonalizado || transferNome,
                        descricao: nomePersonalizado || transferNome,
                        qtd_inteira: 0,
                        qtd_meia: 0,
                        qtd_infantil: 0,
                        idades: [],
                        tipos_meia: [],
                        transfers: [{
                            transfer_id: select.value,
                            nome: transferNome,
                            nome_personalizado: nomePersonalizado,
                            nome_exibicao: nomePersonalizado || transferNome,
                            valor: transferValor
                        }],
                        valor_transfer_ida: transferValor,
                        valor_transfer_volta: 0,
                        info: {},
                        __transfer_avulso: true
                    });
                }
            });
            servicosAdicionados = itensBase;
            atualizarListaServicos();
            atualizarRoteiro();
        }

        function atualizarTransferEdicaoUI() {
            const btnSalvarTransfer = document.getElementById('btnSalvarTransfer');
            if (!btnSalvarTransfer) return;
            if (transferEditandoId) {
                btnSalvarTransfer.style.display = 'inline-flex';
                btnSalvarTransfer.disabled = false;
                btnSalvarTransfer.innerHTML = '<i class="bi bi-check-circle me-2"></i>Confirmar Alteração do Transfer';
            } else {
                btnSalvarTransfer.style.display = 'none';
            }
        }
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
        
        // Coletar transfers APENAS do container de transfers
        let transfers = [];
        let valorTransferIda = 0;
        let valorTransferVolta = 0;
        
        const transferOpcoes = document.querySelectorAll('#containerTransfers .transfer-opcao');
        console.log('=== COLETANDO TRANSFERS ===');
        console.log('Quantidade de transfers encontrados:', transferOpcoes.length);
        transferOpcoes.forEach(function(opcao, idx) {
            const select = opcao.querySelector('.transfer-select');
            const valorInput = opcao.querySelector('.transfer-valor-input');
            
            console.log('Transfer #' + (idx + 1) + ':');
            console.log('  - Select encontrado:', !!select);
            console.log('  - Select value:', select ? select.value : 'N/A');
            console.log('  - Input valor encontrado:', !!valorInput);
            console.log('  - Input valor:', valorInput ? valorInput.value : 'N/A');
            
            if (select && select.value && valorInput) {
                const option = select.selectedOptions[0];
                const transferNome = option.getAttribute('data-nome');
                const transferValor = parseFloat(valorInput.value) || 0; // Usar o valor editável
                
                console.log('  ✅ Transfer adicionado:', transferNome, 'Valor: R$', transferValor);
                
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
            } else {
                console.log('  ❌ Transfer não adicionado (falta select, valor ou select vazio)');
            }
        });
        
        console.log('Total de transfers coletados:', transfers.length);
        console.log('Dados dos transfers:', JSON.stringify(transfers, null, 2));
        
        // Descrição
        let descricao = document.getElementById('descricaoServico').value.trim();
        if (!descricao) {
            descricao = servicoNome;
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
            atualizarTextoBotaoServico();
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
        atualizarTextoBotaoServico();
        
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
                if (servico.qtd_infantil > 0 && servico.idades && servico.idades.length > 0) {
                    gerarCamposIdades(servico.qtd_infantil);
                    setTimeout(function() {
                        const idadesInputs = document.querySelectorAll('#containerIdades input.idade-input');
                        idadesInputs.forEach(function(input, idx) {
                            if (servico.idades[idx] !== undefined) {
                                input.value = servico.idades[idx];
                                input.dispatchEvent(new Event('input'));
                            }
                        });
                    }, 100);
                }
                
                // Gerar campos de tipos de meia
                if (servico.qtd_meia > 0 && servico.tipos_meia && servico.tipos_meia.length > 0) {
                    console.log('=== CARREGANDO TIPOS DE MEIA ===');
                    console.log('Quantidade de meia:', servico.qtd_meia);
                    console.log('Tipos de meia salvos:', servico.tipos_meia);
                    
                    gerarCamposTiposMeia(servico.qtd_meia, function() {
                        console.log('Campos de tipos de meia criados');
                        const tiposSelects = document.querySelectorAll('#containerTiposMeia select.tipo-meia-select');
                        console.log('Selects encontrados:', tiposSelects.length);
                        
                        tiposSelects.forEach(function(select, idx) {
                            const tipoMeiaSalvo = servico.tipos_meia[idx];
                            if (tipoMeiaSalvo) {
                                const valorParaSelecionar = tipoMeiaSalvo.id || tipoMeiaSalvo.tipo || tipoMeiaSalvo.nome;
                                console.log('Definindo select', idx, 'para:', valorParaSelecionar, '- Dados:', tipoMeiaSalvo);
                                select.value = valorParaSelecionar;

                                if (!select.value && tipoMeiaSalvo.tipo) {
                                    const optionMatch = Array.from(select.options).find(function(option) {
                                        return option.textContent.trim() === String(tipoMeiaSalvo.tipo).trim();
                                    });
                                    if (optionMatch) {
                                        select.value = optionMatch.value;
                                    }
                                }
                            } else {
                                console.warn('Tipo de meia não encontrado para índice:', idx);
                            }
                        });
                    });
                }
                
                document.getElementById('descricaoServico').value = servico.descricao;
                
                // Scroll para o formulário
                document.getElementById('camposServico').scrollIntoView({ behavior: 'smooth' });
            }, 500);
        }, 500);
    }

    function atualizarTextoBotaoServico() {
        const btnAdicionarServico = document.getElementById('btnAdicionarServico');
        if (!btnAdicionarServico) return;
        
        if (editandoId) {
            btnAdicionarServico.innerHTML = '<i class="bi bi-check-circle me-2"></i>Salvar Alterações';
            btnAdicionarServico.classList.remove('btn-success');
            btnAdicionarServico.classList.add('btn-primary');
        } else {
            btnAdicionarServico.innerHTML = '<i class="bi bi-check-circle me-2"></i>Adicionar Serviço';
            btnAdicionarServico.classList.remove('btn-primary');
            btnAdicionarServico.classList.add('btn-success');
        }
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


        // Exibir serviços normais e transfers avulsos
        const servicosNormais = servicosAdicionados.filter(function(s) {
            return !s.__transfer_avulso && !s.__nao_exibir_card;
        });
        const transfersAvulsos = servicosAdicionados.filter(function(s) { return s.__transfer_avulso; });

        if (servicosNormais.length === 0 && transfersAvulsos.length === 0) {
            container.innerHTML = '<div class="text-center text-muted py-4">' +
                '<i class="bi bi-inbox display-4 d-block mb-2"></i>' +
                '<p>Nenhum serviço adicionado ainda</p>' +
                '</div>';
            return;
        }

        container.innerHTML = '';

        servicosNormais.forEach(function(servico) {
            const div = document.createElement('div');
            div.className = 'servico-adicionado';
            const idParam = (typeof servico.id === 'number' || !isNaN(Number(servico.id))) ? servico.id : `'${servico.id}'`;
            let html = '<div class="d-flex justify-content-between align-items-start mb-2">' +
                '<div>' +
                '<h6 class="mb-1"><i class="bi bi-calendar-event me-1"></i>' + formatarData(servico.data) + '</h6>' +
                '<p class="mb-1"><strong>' + servico.servico_nome + '</strong></p>' +
                '</div>' +
                '<div class="btn-group">' +
                '<button class="btn btn-sm btn-outline-primary" onclick="window.editarServico(' + idParam + ')">' +
                '<i class="bi bi-pencil"></i>' +
                '</button>' +
                '<button class="btn btn-sm btn-outline-danger" onclick="window.removerServico(' + idParam + ')">' +
                '<i class="bi bi-trash"></i>' +
                '</button>' +
                '</div>' +
                '</div>';
            html += '<div class="small">';
            if (servico.qtd_inteira > 0) html += '<span class="badge bg-primary me-1">' + servico.qtd_inteira + ' Inteira</span>';
            if (servico.qtd_meia > 0) html += '<span class="badge bg-info me-1">' + servico.qtd_meia + ' Meia</span>';
            if (servico.qtd_infantil > 0) html += '<span class="badge bg-success me-1">' + servico.qtd_infantil + ' Infantil (idades: ' + servico.idades.join(', ') + ')</span>';
            html += '</div>';
            div.innerHTML = html;
            container.appendChild(div);
        });

        // Exibir transfers avulsos com botão editar
        transfersAvulsos.forEach(function(transfer) {
            const div = document.createElement('div');
            div.className = 'servico-adicionado';
            const idParam = (typeof transfer.id === 'number' || !isNaN(Number(transfer.id))) ? transfer.id : `'${transfer.id}'`;
            let html = '<div class="d-flex justify-content-between align-items-start mb-2">' +
                '<div>' +
                '<h6 class="mb-1"><i class="bi bi-calendar-event me-1"></i>' + formatarData(transfer.data) + '</h6>' +
                '<p class="mb-1"><strong>' + transfer.servico_nome + '</strong></p>' +
                '</div>' +
                '<div class="btn-group">' +
                '<button class="btn btn-sm btn-outline-primary" onclick="window.editarTransfer(' + idParam + ')">' +
                '<i class="bi bi-pencil"></i>' +
                '</button>' +
                '<button class="btn btn-sm btn-outline-danger" onclick="window.removerServico(' + idParam + ')">' +
                '<i class="bi bi-trash"></i>' +
                '</button>' +
                '</div>' +
                '</div>';
            html += '<div class="small">';
            if (transfer.transfers && transfer.transfers.length > 0) {
                transfer.transfers.forEach(function(t) {
                    const nomeExibicao = t.nome_personalizado || t.nome_exibicao || t.nome;
                    html += '<span class="badge bg-warning text-dark me-1">Transfer: ' + nomeExibicao + ' - R$ ' + parseFloat(t.valor).toFixed(2).replace('.', ',') + '</span>';
                });
            }
            html += '</div>';
            div.innerHTML = html;
            container.appendChild(div);
        });
    }
    // Atualizar resumo de totais
    atualizarResumoTotais();

// Função para atualizar o resumo detalhado (tipo nota fiscal)
function atualizarResumoTotais() {
        const container = document.getElementById('resumoDetalhado');
        const totalPaxEl = document.getElementById('totalPaxGeral');
        const valorTotalEl = document.getElementById('valorTotalGeral');
        if (!container || !totalPaxEl || !valorTotalEl) {
            console.warn('Elementos do resumo não encontrados no DOM');
            return;
        }
        // Serviços e transfers
        const servicosReais = servicosAdicionados.filter(s => !s.__transfer_avulso);
        const transfersAvulsos = servicosAdicionados.filter(s => s.__transfer_avulso);
        if (servicosReais.length === 0 && transfersAvulsos.length === 0) {
            container.innerHTML = '<div class="text-center text-muted py-3"><small>Nenhum serviço ou transfer adicionado</small></div>';
            totalPaxEl.textContent = '0';
            valorTotalEl.textContent = 'R$ 0,00';
            return;
        }
        let totalGeral = 0;
        let totalPaxGeral = 0;
        let html = '<div class="list-group list-group-flush">';
        let idx = 1;
        servicosReais.forEach(function(servico) {
            const info = servico.info || {};
            const nomeServico = info.nome || 'Serviço sem nome';
            const data = servico.data || '';
            const qtdInteira = parseInt(servico.qtd_inteira) || 0;
            const qtdMeia = parseInt(servico.qtd_meia) || 0;
            const qtdInfantil = parseInt(servico.qtd_infantil) || 0;
            const valorInteira = parseFloat(info.valor_inteira || 0);
            const valorMeia = parseFloat(info.valor_meia || 0);
            const valorInfantil = parseFloat(info.valor_infantil || 0);
            const subtotalInteira = qtdInteira * valorInteira;
            const subtotalMeia = qtdMeia * valorMeia;
            const subtotalInfantil = qtdInfantil * valorInfantil;
            const subtotalServico = subtotalInteira + subtotalMeia + subtotalInfantil;
            totalGeral += subtotalServico;
            totalPaxGeral += qtdInteira + qtdMeia + qtdInfantil;
            html += '<div class="list-group-item p-2">';
            html += '<div class="d-flex justify-content-between align-items-start mb-2">';
            html += '<div class="flex-grow-1">';
            html += '<strong class="d-block">' + (idx++) + '. ' + nomeServico + '</strong>';
            html += '<small class="text-muted">' + formatarDataBrasileira(data) + '</small>';
            html += '</div>';
            html += '<span class="badge bg-secondary">' + (qtdInteira + qtdMeia + qtdInfantil) + ' PAX</span>';
            html += '</div>';
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
            html += '<div class="d-flex justify-content-end mt-2 pt-2 border-top">';
            html += '<strong>Subtotal: <span class="text-dark">R$ ' + subtotalServico.toFixed(2).replace('.', ',') + '</span></strong>';
            html += '</div>';
            html += '</div>';
            html += '</div>';
        });
        // Detalhar transfers avulsos
        transfersAvulsos.forEach(function(transfer) {
            html += '<div class="list-group-item p-2">';
            html += '<div class="d-flex justify-content-between align-items-start mb-2">';
            html += '<div class="flex-grow-1">';
            html += '<strong class="d-block">' + (idx++) + '. Transfer</strong>';
            html += '<small class="text-muted">' + formatarDataBrasileira(transfer.data) + '</small>';
            html += '</div>';
            html += '<span class="badge bg-warning text-dark">Transfer</span>';
            html += '</div>';
            html += '<div class="small ms-3">';
            if (transfer.transfers && transfer.transfers.length > 0) {
                transfer.transfers.forEach(function(t) {
                    html += '<div class="d-flex justify-content-between">';
                    const nomeExibicao = t.nome_personalizado || t.nome_exibicao || t.nome;
                    html += '<span class="text-warning">• ' + nomeExibicao + '</span>';
                    html += '<span class="text-warning">R$ ' + parseFloat(t.valor).toFixed(2).replace('.', ',') + '</span>';
                    html += '</div>';
                    totalGeral += parseFloat(t.valor) || 0;
                });
            }
            html += '</div>';
            html += '</div>';
        });
        html += '</div>';
        container.innerHTML = html;
        totalPaxEl.textContent = totalPaxGeral;
        valorTotalEl.textContent = 'R$ ' + totalGeral.toFixed(2).replace('.', ',');
    }
        // Função para editar transfer avulso
        window.editarTransfer = function(id) {
            // Busca o transfer avulso pelo id
            const transfer = servicosAdicionados.find(function(s) { return s.id === id; });
            if (!transfer) return;
            transferEditandoId = id;
            // Preenche o containerTransfers com o transfer selecionado para edição
            // Limpa todos os transfers do DOM
            document.getElementById('containerTransfers').innerHTML = '';
            contadorTransfers = 0;
            const transferItens = (transfer.transfers && transfer.transfers.length > 0) ? transfer.transfers : [];
            if (transferItens.length === 0) {
                adicionarTransferOpcao();
            } else {
                transferItens.forEach(function(item) {
                    adicionarTransferOpcao({
                        transfer_id: item.transfer_id,
                        nome_personalizado: item.nome_personalizado || item.nome_exibicao || item.nome || '',
                        valor: item.valor
                    });
                });
            }
            const btnSalvarTransfer = document.getElementById('btnSalvarTransfer');
            if (btnSalvarTransfer) {
                btnSalvarTransfer.style.display = 'inline-flex';
                btnSalvarTransfer.disabled = false;
                btnSalvarTransfer.innerHTML = '<i class="bi bi-check-circle me-2"></i>Confirmar Alteração do Transfer';
            }
            atualizarListaServicos();
            atualizarRoteiro();
        }

    function confirmarEdicaoTransfer() {
            transferEditandoId = null;
            const btnSalvarTransfer = document.getElementById('btnSalvarTransfer');
            if (btnSalvarTransfer) {
                btnSalvarTransfer.style.display = 'none';
            }
            atualizarListaServicos();
            atualizarRoteiro();
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
        
        // Separar transfers avulsos dos serviços
        const transfersAvulsos = servicosAdicionados.filter(s => s.__transfer_avulso);
        const servicosNormais = servicosAdicionados.filter(s => !s.__transfer_avulso);

        // Agrupar serviços por data
        const porData = {};
        servicosNormais.forEach(function(servico) {
            if (!porData[servico.data]) {
                porData[servico.data] = [];
            }
            porData[servico.data].push(servico);
        });

        // Ordenar datas
        const datasOrdenadas = Object.keys(porData).sort();

        // Gerar roteiro
        let roteiro = '=== ROTEIRO ===\n\n';

        // Resumos separados para deixar a prévia mais clara
        const resumoIngressos = [];
        const resumoTransfers = [];
        let totalGeral = 0;

        function formatarMoeda(valor) {
            return new Intl.NumberFormat('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(valor);
        }

        datasOrdenadas.forEach(function(data) {
            roteiro += '📅 ' + formatarData(data) + '\n';
            roteiro += '─'.repeat(15) + '\n';

            porData[data].forEach(function(servico, idx) {
                roteiro += '\n' + (servico.descricao || '') + '\n';

                if (servico.qtd_inteira > 0) roteiro += '  • ' + servico.qtd_inteira + ' Inteira(s)\n';
                if (servico.qtd_meia > 0) roteiro += '  • ' + servico.qtd_meia + ' Meia(s)\n';
                if (servico.qtd_infantil > 0) roteiro += '  • ' + servico.qtd_infantil + ' Infantil(is) (idades: ' + servico.idades.join(', ') + ')\n';

                // Adicionar ao resumo
                const info = servico.info || {};
                const qtdInteira = parseInt(servico.qtd_inteira) || 0;
                const qtdMeia = parseInt(servico.qtd_meia) || 0;
                const qtdInfantil = parseInt(servico.qtd_infantil) || 0;
                const valorInteira = parseFloat(info.valor_inteira || 0);
                const valorMeia = parseFloat(info.valor_meia || 0);
                const valorInfantil = parseFloat(info.valor_infantil || 0);
                const subtotalIngressos = (qtdInteira * valorInteira) + (qtdMeia * valorMeia) + (qtdInfantil * valorInfantil);
                resumoIngressos.push({
                    nome: servico.servico_nome || servico.descricao,
                    valorIngressos: subtotalIngressos
                });
                totalGeral += subtotalIngressos;
            });

            roteiro += '\n';
        });

        if (datasOrdenadas.length === 0 && transfersAvulsos.length > 0) {
            roteiro += '🚌 Transfers:\n';
            roteiro += '─'.repeat(15) + '\n';
            transfersAvulsos.forEach(function(transfer) {
                if (transfer.transfers && transfer.transfers.length > 0) {
                    transfer.transfers.forEach(function(t) {
                        const nomeExibicao = t.nome_personalizado || t.nome_exibicao || t.nome || 'Transfer';
                        roteiro += '     - 🚕 ' + nomeExibicao + ' (R$ ' + formatarMoeda(parseFloat(t.valor) || 0) + ')\n';
                    });
                }
            });
            roteiro += '\n';
        }

        transfersAvulsos.forEach(function(transfer) {
            if (transfer.transfers && transfer.transfers.length > 0) {
                transfer.transfers.forEach(function(t) {
                    const valorTransfer = parseFloat(t.valor) || 0;
                    resumoTransfers.push({
                        nome: t.nome_personalizado || t.nome_exibicao || t.nome || 'Transfer',
                        valor: valorTransfer
                    });
                    totalGeral += valorTransfer;
                });
            }
        });

        roteiro += '─'.repeat(15) + '\n';
        roteiro += '💰 RESUMO DE VALORES\n';
        if (resumoTransfers.length > 0) {
            roteiro += '\n 🚌 Transfers:\n';
            resumoTransfers.forEach(function(item) {
                roteiro += '\t- 🚕 ' + item.nome + ' (R$ ' + formatarMoeda(item.valor) + ')\n';
            });
        }

        if (resumoIngressos.length > 0) {
            roteiro += '\n 🎫 TICKETS:\n';
            resumoIngressos.forEach(function(item) {
                if (item.valorIngressos > 0) {
                    roteiro += '\t- ' + item.nome + ' - Ingresso: R$ ' + formatarMoeda(item.valorIngressos) + '\n';
                }
            });
        }

        roteiro += ' 💰 TOTAL: R$ ' + formatarMoeda(totalGeral) + '\n';
        roteiro += '\n' + '─'.repeat(15) + '\n';

        preview.innerHTML = roteiro;
    }

    function formatarData(data) {
        if (!data || typeof data !== 'string' || !data.includes('-')) {
            return '';
        }
        const partes = data.split('-');
        if (partes.length !== 3) return data;
        return partes[2] + '/' + partes[1] + '/' + partes[0];
    }

    function copiarRoteiro() {
        console.log('Função copiarRoteiro chamada');
        const preview = document.getElementById('roteiroPreview');
        const btn = document.getElementById('btnCopiarRoteiro');
        
        if (!preview) {
            console.error('Elemento roteiroPreview não encontrado');
            alert('Erro: Preview do roteiro não encontrado.');
            return;
        }
        
        if (!btn) {
            console.error('Botão btnCopiarRoteiro não encontrado');
            return;
        }
        
        const texto = preview.textContent;
        console.log('Texto do roteiro:', texto);
        console.log('servicosAdicionados.length:', servicosAdicionados.length);
        
        // Verificar se há texto para copiar (ignora se array está vazio, pode ter roteiro carregado)
        if (!texto || texto.trim() === '') {
            alert('⚠️ Não há roteiro para copiar. Adicione serviços primeiro.');
            return;
        }
        
        // Usar textarea para garantir compatibilidade (funciona via IP)
        const textArea = document.createElement('textarea');
        textArea.value = texto;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        textArea.style.top = '0';
        document.body.appendChild(textArea);
        textArea.select();
        textArea.setSelectionRange(0, 99999); // Para dispositivos móveis
        
        try {
            const sucesso = document.execCommand('copy');
            document.body.removeChild(textArea);
            
            if (sucesso) {
                // Feedback visual
                const originalHTML = btn.innerHTML;
                btn.classList.add('btn-success');
                btn.classList.remove('btn-outline-success');
                btn.innerHTML = '<i class="bi bi-check"></i> Copiado!';
                btn.disabled = true;
                
                // Resetar após 2 segundos
                setTimeout(function() {
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-outline-success');
                    btn.innerHTML = originalHTML;
                    btn.disabled = false;
                }, 2000);
            } else {
                alert('Não foi possível copiar. Por favor, copie manualmente.');
            }
        } catch (err) {
            document.body.removeChild(textArea);
            console.error('Erro ao copiar:', err);
            alert('Erro ao copiar. Por favor, selecione e copie manualmente (CTRL+C).');
        }
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
        atualizarTextoBotaoServico();
    }

    function salvarOrdemServico() {
        if (servicosAdicionados.length === 0) {
            alert('Adicione ao menos um serviço ou transfer');
            return;
        }
        
        console.log('=== SALVANDO ORDEM DE SERVIÇO ===');
        console.log('Serviços a salvar:', servicosAdicionados.length);
        console.log('Dados completos:', JSON.stringify(servicosAdicionados, null, 2));
        
        const dados = {
            servicos: servicosAdicionados,
            roteiro: document.getElementById('roteiroPreview').textContent,
            clientes: document.getElementById('id_clientes') ? document.getElementById('id_clientes').value : '',
            hospedagem: document.getElementById('id_hospedagem') ? document.getElementById('id_hospedagem').value : ''
        };
        
        // URL varia se está editando ou criando
        let url = djangoData.urls.ordemServicoCreate || djangoData.urls.lancamentoCreate;
        // Se estiver editando, usar o id da Ordem de Serviço
        if (djangoData.editando && djangoData.ordemId) {
            url = '/servicos/ordens-servico/' + djangoData.ordemId + '/editar/';
        }
        
        console.log('URL de salvamento:', url);
        console.log('Editando?', djangoData.editando);
        console.log('Payload JSON:', JSON.stringify(dados, null, 2));
        
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
                console.log('  - tipos_meia recebidos:', lancamento.tipos_meia);
                console.log('  - idades recebidas:', lancamento.idades);
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
                // Se for transfer avulso, manter flags especiais
                if (lancamento.__transfer_avulso) servicoCompleto.__transfer_avulso = true;
                if (lancamento.__nao_exibir_card) servicoCompleto.__nao_exibir_card = true;
                servicosAdicionados.push(servicoCompleto);
                console.log('Serviço adicionado:', servicoCompleto);
            });
            
            console.log('Total de serviços carregados:', servicosAdicionados.length);
            console.log('Array servicosAdicionados:', servicosAdicionados);
            
            // Atualizar a UI
            atualizarListaServicos();
            atualizarResumoTotais();
            atualizarRoteiro();
            // Se há roteiro salvo, também exibe no preview (mas sempre atualiza resumo)
            if (roteiro) {
                const roteiroElement = document.getElementById('roteiroPreview');
                if (roteiroElement) {
                    roteiroElement.textContent = roteiro;
                    console.log('Roteiro carregado no preview');
                }
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
