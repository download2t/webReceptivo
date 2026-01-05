// WebReceptivo - Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all components
    initializeForms();
    initializeAnimations();
    initializeTooltips();
    initializeTheme();
    initializeNavigation();
    
    console.log('WebReceptivo initialized successfully');
});

/**
 * Form Enhancement Functions
 */
function initializeForms() {
    // Add loading state to form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                addLoadingState(submitBtn);
            }
        });
    });
    
    // Auto-focus first input in forms
    const firstInput = document.querySelector('form input:first-of-type');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Real-time form validation feedback
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearValidation);
    });
}

function addLoadingState(button) {
    const originalText = button.innerHTML;
    const loadingText = button.dataset.loading || 'Processando...';
    
    button.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status">
            <span class="visually-hidden">Loading...</span>
        </span>
        ${loadingText}
    `;
    button.disabled = true;
    
    // Restore after 10 seconds as fallback
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 10000);
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    
    // Remove previous validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Basic validation rules
    if (field.required && !value) {
        field.classList.add('is-invalid');
        showFieldError(field, 'Este campo é obrigatório');
        return false;
    }
    
    if (field.type === 'email' && value && !isValidEmail(value)) {
        field.classList.add('is-invalid');
        showFieldError(field, 'Digite um e-mail válido');
        return false;
    }
    
    if (field.minLength && value.length < field.minLength) {
        field.classList.add('is-invalid');
        showFieldError(field, `Mínimo ${field.minLength} caracteres`);
        return false;
    }
    
    // Field is valid
    field.classList.add('is-valid');
    hideFieldError(field);
    return true;
}

function clearValidation(e) {
    const field = e.target;
    field.classList.remove('is-valid', 'is-invalid');
    hideFieldError(field);
}

function showFieldError(field, message) {
    hideFieldError(field); // Remove existing error
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    errorDiv.dataset.field = field.name;
    
    field.parentNode.appendChild(errorDiv);
}

function hideFieldError(field) {
    const existingError = field.parentNode.querySelector(`[data-field="${field.name}"]`);
    if (existingError) {
        existingError.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Animation Functions
 */
function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Add slide-in animation to alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.classList.add('slide-in');
        
        // Auto-dismiss apenas para alertas de sucesso e info (não para erro/warning)
        if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
            setTimeout(() => {
                if (alert.querySelector('.btn-close')) {
                    alert.querySelector('.btn-close').click();
                }
            }, 5000);
        }
    });
}

/**
 * Bootstrap Tooltips & Popovers
 */
function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Theme Management
 */
function initializeTheme() {
    const isAuthenticated = document.querySelector('meta[name="user-theme-preference"]') !== null;
    const userThemePreference = getUserThemePreference();
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    
    let theme;
    
    if (isAuthenticated) {
        // User is authenticated - ALWAYS use their preference from database
        if (userThemePreference === 'auto') {
            theme = systemTheme;
        } else {
            theme = userThemePreference;
        }
        // Clear any local storage theme when user is authenticated
        localStorage.removeItem('theme');
    } else {
        // User is not authenticated - use system preference only
        theme = systemTheme;
    }
    
    setTheme(theme);
    
    // Listen for system theme changes (only for auto preference)
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!isAuthenticated || userThemePreference === 'auto') {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

function getUserThemePreference() {
    // Get user theme preference from meta tag
    const themePreference = document.querySelector('meta[name="user-theme-preference"]');
    return themePreference ? themePreference.content : 'auto';
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    
    // Log theme change for debugging
    console.log('Theme set to:', theme);
}

/**
 * Funções removidas: showThemeNotification, updateThemeTooltip, toggleTheme, saveThemePreference
 * O tema agora é controlado exclusivamente pela preferência do usuário no perfil
 */

/**
 * Utility Functions
 */

// CSRF Token for AJAX requests
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Show notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show slide-in`;
    alertDiv.innerHTML = `
        <i class="bi bi-${getIconForType(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.querySelector('.btn-close')) {
            alertDiv.querySelector('.btn-close').click();
        }
    }, 5000);
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Smooth scroll to element
function scrollToElement(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Format currency (Brazilian Real)
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Format date (Brazilian format)
function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
}

// Debounce function for search inputs
function debounce(func, wait) {
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

/**
 * Navigation Enhancement Functions
 */
function initializeNavigation() {
    // Function to enhance avatar display
    function enhanceAvatarDisplay() {
        // Enhance avatar display in navigation
        const avatarImages = document.querySelectorAll('.navbar .rounded-circle');
        avatarImages.forEach(img => {
            // Add error handling for avatar images
            img.onerror = function() {
                this.src = '/static/images/default-avatar.svg';
            };
            
            // Add loading class while image loads
            img.classList.add('loading');
            img.onload = function() {
                this.classList.remove('loading');
            };
        });
    }
    // Enhance avatar display in navigation
    enhanceAvatarDisplay();
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        const navbar = document.querySelector('.navbar-collapse');
        const navbarToggler = document.querySelector('.navbar-toggler');
        const isClickInsideNav = navbar && navbar.contains(e.target);
        const isClickOnToggler = navbarToggler && navbarToggler.contains(e.target);
        
        if (!isClickInsideNav && !isClickOnToggler && navbar && navbar.classList.contains('show')) {
            // Use Bootstrap's collapse instance to hide the menu
            const bsCollapse = bootstrap.Collapse.getInstance(navbar);
            if (bsCollapse) {
                bsCollapse.hide();
            }
        }
    });
    
    // Close mobile menu when clicking on menu items
    const navLinks = document.querySelectorAll('.navbar-nav .dropdown-item');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            const navbar = document.querySelector('.navbar-collapse');
            if (navbar && navbar.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbar);
                if (bsCollapse) {
                    setTimeout(() => bsCollapse.hide(), 100); // Small delay for better UX
                }
            }
        });
    });
    
    // Let Bootstrap handle dropdown behavior naturally
    
    // Add smooth animations for navbar collapse
    const navbarCollapse = document.querySelector('.navbar-collapse');
    if (navbarCollapse) {
        navbarCollapse.addEventListener('show.bs.collapse', function() {
            this.style.transition = 'height 0.35s ease';
        });
        
        navbarCollapse.addEventListener('hide.bs.collapse', function() {
            this.style.transition = 'height 0.35s ease';
        });
    }
}

// Export functions for use in other scripts
window.WebReceptivo = {
    showNotification,
    scrollToElement,
    formatCurrency,
    formatDate,
    debounce,
    getCSRFToken,
    initializeNavigation
};
