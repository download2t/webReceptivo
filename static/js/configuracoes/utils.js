/**
 * ============================================
 * CONFIGURAÇÕES - FUNÇÕES JAVASCRIPT COMUNS
 * ============================================
 */

class SettingsUtils {
    
    // ========== ESTADOS DE LOADING ========== //
    static showLoading(button) {
        if (!button) return;
        
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="loading-spinner"></span> Processando...';
        button.disabled = true;
        button.dataset.originalText = originalText;
    }
    
    static hideLoading(button) {
        if (!button || !button.dataset.originalText) return;
        
        button.innerHTML = button.dataset.originalText;
        button.disabled = false;
        delete button.dataset.originalText;
    }
    
    // ========== NOTIFICAÇÕES TOAST ========== //
    static showToast(message, type = 'success') {
        const toastContainer = this.getToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        const iconMap = {
            'success': 'check-circle',
            'error': 'times-circle',
            'danger': 'times-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        
        const icon = iconMap[type] || 'info-circle';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${icon} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Inicializa o toast do Bootstrap
        if (window.bootstrap) {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            // Remove o elemento após ser escondido
            toast.addEventListener('hidden.bs.toast', () => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            });
        }
    }
    
    static getToastContainer() {
        let container = document.getElementById('toastContainer');
        
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        
        return container;
    }
    
    // ========== CONFIRMAÇÕES ========== //
    static confirmAction(message, callback) {
        if (confirm(message)) {
            callback();
        }
    }
    
    static async confirmActionAsync(message) {
        return new Promise((resolve) => {
            const result = confirm(message);
            resolve(result);
        });
    }
    
    // ========== FORMATAÇÃO DE DADOS ========== //
    static formatCNPJ(value) {
        const cleaned = value.replace(/\D/g, '');
        return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }
    
    static formatCPF(value) {
        const cleaned = value.replace(/\D/g, '');
        return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }
    
    static formatCEP(value) {
        const cleaned = value.replace(/\D/g, '');
        return cleaned.replace(/(\d{5})(\d{3})/, '$1-$2');
    }
    
    static formatPhone(value) {
        const cleaned = value.replace(/\D/g, '');
        
        if (cleaned.length <= 10) {
            return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        } else {
            return cleaned.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        }
    }
    
    static formatCurrency(value) {
        const number = parseFloat(value.replace(/[^\d,.-]/g, '').replace(',', '.'));
        
        if (isNaN(number)) return 'R$ 0,00';
        
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(number);
    }
    
    // ========== VALIDAÇÕES ========== //
    static validateCNPJ(cnpj) {
        const cleaned = cnpj.replace(/\D/g, '');
        
        if (cleaned.length !== 14) return false;
        if (/^(\d)\1+$/.test(cleaned)) return false;
        
        // Algoritmo de validação do CNPJ
        let sum = 0;
        let weight = 5;
        
        for (let i = 0; i < 12; i++) {
            sum += parseInt(cleaned[i]) * weight;
            weight = weight === 2 ? 9 : weight - 1;
        }
        
        let remainder = sum % 11;
        let digit1 = remainder < 2 ? 0 : 11 - remainder;
        
        if (parseInt(cleaned[12]) !== digit1) return false;
        
        sum = 0;
        weight = 6;
        
        for (let i = 0; i < 13; i++) {
            sum += parseInt(cleaned[i]) * weight;
            weight = weight === 2 ? 9 : weight - 1;
        }
        
        remainder = sum % 11;
        let digit2 = remainder < 2 ? 0 : 11 - remainder;
        
        return parseInt(cleaned[13]) === digit2;
    }
    
    static validateCPF(cpf) {
        const cleaned = cpf.replace(/\D/g, '');
        
        if (cleaned.length !== 11) return false;
        if (/^(\d)\1+$/.test(cleaned)) return false;
        
        // Algoritmo de validação do CPF
        let sum = 0;
        
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cleaned[i]) * (10 - i);
        }
        
        let remainder = sum % 11;
        let digit1 = remainder < 2 ? 0 : 11 - remainder;
        
        if (parseInt(cleaned[9]) !== digit1) return false;
        
        sum = 0;
        
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cleaned[i]) * (11 - i);
        }
        
        remainder = sum % 11;
        let digit2 = remainder < 2 ? 0 : 11 - remainder;
        
        return parseInt(cleaned[10]) === digit2;
    }
    
    static validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }
    
    static validateCEP(cep) {
        const cleaned = cep.replace(/\D/g, '');
        return cleaned.length === 8;
    }
    
    // ========== UTILITÁRIOS DE FORMULÁRIO ========== //
    static clearForm(formId) {
        const form = document.getElementById(formId);
        if (form) {
            form.reset();
            
            // Remove classes de validação
            const inputs = form.querySelectorAll('.is-invalid, .is-valid');
            inputs.forEach(input => {
                input.classList.remove('is-invalid', 'is-valid');
            });
        }
    }
    
    static serializeForm(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }
    
    static setFormValues(formId, data) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    input.checked = Boolean(data[key]);
                } else {
                    input.value = data[key] || '';
                }
            }
        });
    }
    
    // ========== UTILITÁRIOS AJAX ========== //
    static async fetchJSON(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    }
    
    static getCSRFToken() {
        const cookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        
        if (cookie) {
            return cookie.split('=')[1];
        }
        
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        return input ? input.value : '';
    }
    
    // ========== UTILITÁRIOS DE INTERFACE ========== //
    static fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        const start = performance.now();
        
        function animate(currentTime) {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = progress;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    }
    
    static fadeOut(element, duration = 300) {
        const start = performance.now();
        const initialOpacity = parseFloat(getComputedStyle(element).opacity);
        
        function animate(currentTime) {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            element.style.opacity = initialOpacity * (1 - progress);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.style.display = 'none';
            }
        }
        
        requestAnimationFrame(animate);
    }
    
    // ========== DEBOUNCE E THROTTLE ========== //
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    static throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// ========== FUNÇÕES GLOBAIS (COMPATIBILIDADE) ========== //
function showLoading(button) { SettingsUtils.showLoading(button); }
function hideLoading(button) { SettingsUtils.hideLoading(button); }
function showToast(message, type) { SettingsUtils.showToast(message, type); }
function confirmAction(message, callback) { SettingsUtils.confirmAction(message, callback); }
function formatCNPJ(value) { return SettingsUtils.formatCNPJ(value); }
function formatCEP(value) { return SettingsUtils.formatCEP(value); }
function formatPhone(value) { return SettingsUtils.formatPhone(value); }

// ========== INICIALIZAÇÃO ========== //
document.addEventListener('DOMContentLoaded', function() {
    // Configurar máscaras automaticamente se jQuery estiver disponível
    if (window.jQuery) {
        // Máscaras para inputs com data-mask
        $('[data-mask="cnpj"]').mask('00.000.000/0000-00');
        $('[data-mask="cpf"]').mask('000.000.000-00');
        $('[data-mask="cep"]').mask('00000-000');
        $('[data-mask="phone"]').mask('(00) 00000-0000');
        $('[data-mask="currency"]').mask('#.##0,00', {reverse: true});
    }
    
    // Auto-formatação em tempo real
    const cnpjInputs = document.querySelectorAll('input[data-format="cnpj"]');
    cnpjInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            e.target.value = SettingsUtils.formatCNPJ(e.target.value);
        });
    });
    
    const cepInputs = document.querySelectorAll('input[data-format="cep"]');
    cepInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            e.target.value = SettingsUtils.formatCEP(e.target.value);
        });
    });
});
