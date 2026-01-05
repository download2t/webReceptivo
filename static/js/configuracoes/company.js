/**
 * Formulário de Dados da Empresa
 * Gerencia validação de CNPJ e busca de CEP
 */

// Setup logo preview on file selection
function setupLogoPreview() {
    const logoInput = document.getElementById('id_logo');
    const logoActionsRow = document.getElementById('logoActionsRow');
    const logoPreviewContainer = document.getElementById('logoPreviewContainer');
    const clearCheckbox = document.getElementById('logo-clear_id');
    
    if (!logoInput) return;
    
    logoInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        
        if (file) {
            // Validate file type
            const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/jpg'];
            if (!validTypes.includes(file.type)) {
                alert('Formato não suportado. Use JPEG, PNG, GIF ou WebP.');
                logoInput.value = '';
                return;
            }
            
            // Validate file size (5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('Arquivo muito grande. Máximo 5MB.');
                logoInput.value = '';
                return;
            }
            
            // Uncheck clear checkbox if exists
            if (clearCheckbox) {
                clearCheckbox.checked = false;
            }
            
            // Show preview
            const reader = new FileReader();
            reader.onload = function(event) {
                if (logoPreviewContainer) {
                    logoPreviewContainer.innerHTML = `<img src="${event.target.result}" alt="Nova Logo">`;
                }
                if (logoActionsRow) {
                    logoActionsRow.style.display = 'flex';
                }
            };
            reader.readAsDataURL(file);
        }
    });
}

// Clear logo function
function clearLogo() {
    const clearCheckbox = document.getElementById('logo-clear_id');
    const logoActionsRow = document.getElementById('logoActionsRow');
    const logoInput = document.getElementById('id_logo');
    
    // Mark for deletion
    if (clearCheckbox) {
        clearCheckbox.checked = true;
        console.log('Logo marcada para remoção');
    } else {
        console.error('Checkbox logo-clear_id não encontrado!');
        return;
    }
    
    // Clear file input
    if (logoInput) {
        logoInput.value = '';
    }
    
    // Hide preview and button
    if (logoActionsRow) {
        logoActionsRow.style.display = 'none';
    }
}

// CEP search functionality
function setupCEPSearch() {
    const cepInput = document.getElementById('id_zip_code');
    const searchButton = document.getElementById('searchCEP');
    const addressFields = {
        address: document.getElementById('id_street'),
        district: document.getElementById('id_neighborhood'),
        city: document.getElementById('id_city'),
        state: document.getElementById('id_state')
    };

    if (!searchButton || !cepInput) return;

    searchButton.addEventListener('click', function() {
        const cep = cepInput.value.replace(/\D/g, '');
        
        if (cep.length < 8) {
            showToast('Digite um CEP válido com 8 dígitos.', 'warning');
            cepInput.focus();
            return;
        }

        searchCEP(cep, addressFields, searchButton);
    });

    // Search on Enter key
    cepInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            searchButton.click();
        }
    });

    // Auto-search when CEP is complete
    cepInput.addEventListener('input', function() {
        const cep = this.value.replace(/\D/g, '');
        if (cep.length === 8) {
            setTimeout(() => {
                searchCEP(cep, addressFields, searchButton);
            }, 500);
        }
    });
}

// CEP search function
function searchCEP(cep, fields, button) {
    showLoading(button);
    
    // Add loading class to address container
    const addressContainer = fields.address?.closest('.content-card');
    if (addressContainer) {
        addressContainer.classList.add('address-loading');
    }

    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrfToken) {
        hideLoading(button);
        if (addressContainer) addressContainer.classList.remove('address-loading');
        showToast('Erro: Token CSRF não encontrado.', 'error');
        return;
    }

    fetch('/configuracoes/ajax/validate-cep/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ cep: cep })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading(button);
        if (addressContainer) {
            addressContainer.classList.remove('address-loading');
        }

        if (data.success) {
            // Fill address fields
            if (data.logradouro && fields.address) fields.address.value = data.logradouro;
            if (data.bairro && fields.district) fields.district.value = data.bairro;
            if (data.localidade && fields.city) fields.city.value = data.localidade;
            if (data.uf && fields.state) {
                // Find and select the state option
                const stateSelect = fields.state;
                for (let option of stateSelect.options) {
                    if (option.value === data.uf) {
                        option.selected = true;
                        break;
                    }
                }
            }
            
            showToast('Endereço preenchido automaticamente!', 'success');
            
            // Focus on number field
            const numberField = document.getElementById('id_number');
            if (numberField) numberField.focus();
            
        } else {
            showToast(data.error || 'CEP não encontrado. Verifique o CEP digitado.', 'warning');
        }
    })
    .catch(error => {
        hideLoading(button);
        if (addressContainer) {
            addressContainer.classList.remove('address-loading');
        }
        console.error('Error:', error);
        showToast('Erro ao buscar CEP. Tente novamente.', 'error');
    });
}

// CNPJ validation (optional - can be removed if not needed)
function validateCNPJ() {
    const cnpjInput = document.getElementById('id_cnpj_cpf');
    if (!cnpjInput) return;
    
    const cnpj = cnpjInput.value;
    
    if (!cnpj) {
        showToast('Digite um CNPJ/CPF para validar.', 'warning');
        return;
    }
    
    showToast('CNPJ/CPF aceito!', 'success');
    cnpjInput.classList.remove('is-invalid');
    cnpjInput.classList.add('is-valid');
}

// Helper functions
function showLoading(button) {
    if (!button) return;
    button.disabled = true;
    const originalHtml = button.innerHTML;
    button.dataset.originalHtml = originalHtml;
    button.innerHTML = '<span class="loading-spinner"></span>Buscando...';
}

function hideLoading(button) {
    if (!button) return;
    button.disabled = false;
    if (button.dataset.originalHtml) {
        button.innerHTML = button.dataset.originalHtml;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    setupLogoPreview();
    setupCEPSearch();
    
    // Form validation on submit
    const form = document.getElementById('companyForm');
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showToast('Por favor, preencha todos os campos obrigatórios.', 'warning');
            }
            form.classList.add('was-validated');
        });
    }
});
