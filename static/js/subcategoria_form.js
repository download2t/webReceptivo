/**
 * subcategoria_form.js
 * JavaScript para o formulário de subcategorias
 * Controla a exibição condicional de campos baseada em checkboxes
 */

document.addEventListener('DOMContentLoaded', function() {
    const aceitaMeiaCheck = document.getElementById('id_aceita_meia_entrada');
    const meiaEntradaFields = document.getElementById('meiaEntradaFields');
    
    const permiteInfantilCheck = document.getElementById('id_permite_infantil');
    const infantilFields = document.getElementById('infantilFields');
    
    const possuiIsencaoCheck = document.getElementById('id_possui_isencao');
    const isencaoFields = document.getElementById('isencaoFields');
    
    const temIdadeMinimaCheck = document.getElementById('id_tem_idade_minima');
    const idadeMinimaFields = document.getElementById('idadeMinimaFields');
    
    // Função para mostrar/ocultar campos de meia entrada
    function toggleMeiaEntrada() {
        if (aceitaMeiaCheck.checked) {
            meiaEntradaFields.style.display = 'block';
        } else {
            meiaEntradaFields.style.display = 'none';
            // Limpar valores quando desativado
            document.getElementById('id_valor_meia').value = '0.00';
            document.getElementById('id_regras_meia_entrada').value = '';
        }
    }
    
    // Função para mostrar/ocultar campos infantis
    function toggleInfantil() {
        if (permiteInfantilCheck.checked) {
            infantilFields.style.display = 'block';
        } else {
            infantilFields.style.display = 'none';
            // Limpar valores quando desativado
            document.getElementById('id_valor_infantil').value = '0.00';
            document.getElementById('id_idade_minima_infantil').value = '0';
            document.getElementById('id_idade_maxima_infantil').value = '17';
        }
    }
    
    // Função para mostrar/ocultar campos de isenção
    function toggleIsencao() {
        if (possuiIsencaoCheck.checked) {
            isencaoFields.style.display = 'block';
        } else {
            isencaoFields.style.display = 'none';
            // Limpar valores quando desativado
            document.getElementById('id_idade_isencao_min').value = '0';
            document.getElementById('id_idade_isencao_max').value = '0';
            document.getElementById('id_texto_isencao').value = '';
        }
    }
    
    // Função para mostrar/ocultar campos de idade mínima
    function toggleIdadeMinima() {
        if (temIdadeMinimaCheck.checked) {
            idadeMinimaFields.style.display = 'block';
        } else {
            idadeMinimaFields.style.display = 'none';
            // Limpar valores quando desativado
            document.getElementById('id_idade_minima').value = '0';
        }
    }
    
    // Eventos
    aceitaMeiaCheck.addEventListener('change', toggleMeiaEntrada);
    permiteInfantilCheck.addEventListener('change', toggleInfantil);
    possuiIsencaoCheck.addEventListener('change', toggleIsencao);
    temIdadeMinimaCheck.addEventListener('change', toggleIdadeMinima);
    
    // Estado inicial
    toggleMeiaEntrada();
    toggleInfantil();
    toggleIsencao();
    toggleIdadeMinima();
});
