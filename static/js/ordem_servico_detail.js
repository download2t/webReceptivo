/**
 * ordem_servico_detail.js
 * JavaScript para a página de detalhes da ordem de serviço
 */

function copiarRoteiro() {
    const text = document.getElementById('roteiroText').textContent;
    const btn = document.getElementById('copyRoteiroBtn');
    
    // Usar a API moderna do Clipboard
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            // Feedback visual
            const originalHTML = btn.innerHTML;
            btn.classList.remove('btn-success');
            btn.classList.add('btn-success', 'disabled');
            btn.innerHTML = '<i class="fas fa-check"></i> Copiado!';
            
            // Resetar após 2 segundos
            setTimeout(() => {
                btn.classList.remove('disabled');
                btn.innerHTML = originalHTML;
            }, 2000);
        }).catch(err => {
            console.error('Erro ao copiar:', err);
            alert('Erro ao copiar para a área de transferência. Por favor, copie manualmente.');
        });
    } else {
        // Fallback para navegadores antigos
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            document.execCommand('copy');
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i> Copiado!';
            
            setTimeout(() => {
                btn.innerHTML = originalHTML;
            }, 2000);
        } catch (err) {
            console.error('Erro ao copiar:', err);
            alert('Erro ao copiar. Por favor, copie manualmente.');
        }
        
        document.body.removeChild(textArea);
    }
}
