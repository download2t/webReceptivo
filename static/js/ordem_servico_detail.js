/**
 * ordem_servico_detail.js
 * JavaScript para a página de detalhes da ordem de serviço
 */

// Cache de traduções para evitar chamadas repetidas
const translationCache = {};

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
            btn.innerHTML = '<i class="bi bi-check"></i> Copiado!';
            
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
            btn.innerHTML = '<i class="bi bi-check"></i> Copiado!';
            
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

async function traduzirRoteiro() {
    const languageSelector = document.getElementById('languageSelector');
    const targetLang = languageSelector.value;
    const roteiroText = document.getElementById('roteiroText');
    const loadingDiv = document.getElementById('loadingTranslation');
    const translateBtn = document.getElementById('translateBtn');
    
    // Se for português, restaurar original
    if (targetLang === 'pt') {
        roteiroText.textContent = roteiroOriginal;
        return;
    }
    
    // Verificar cache
    const cacheKey = `${targetLang}_${roteiroOriginal}`;
    if (translationCache[cacheKey]) {
        roteiroText.textContent = translationCache[cacheKey];
        return;
    }
    
    // Mostrar loading
    loadingDiv.style.display = 'block';
    translateBtn.disabled = true;
    
    try {
        // Usar endpoint Django com Argos Translate
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                         document.querySelector('meta[name="csrf-token"]')?.content;
        
        const response = await fetch('/servicos/ajax/translate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                text: roteiroOriginal,
                target_lang: targetLang
            })
        });
        
        // Verificar se a resposta é JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const errorText = await response.text();
            console.error('Resposta não é JSON:', errorText);
            throw new Error('Servidor retornou resposta inválida. Verifique se o serviço de tradução está configurado.');
        }
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            const translatedText = data.translated_text;
            
            // Salvar no cache
            translationCache[cacheKey] = translatedText;
            
            // Atualizar display
            roteiroText.textContent = translatedText;
        } else {
            const errorMsg = data.error || 'Erro desconhecido';
            console.error('Erro na tradução:', errorMsg);
            alert('Erro ao traduzir: ' + errorMsg);
        }
        
    } catch (error) {
        console.error('Erro na tradução:', error);
        alert('Erro ao traduzir: ' + error.message + '\n\nVerifique o console para mais detalhes.');
    } finally {
        loadingDiv.style.display = 'none';
        translateBtn.disabled = false;
    }
}
