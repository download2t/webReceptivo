// Variável global para a instância do sidebar
let sidebarInstance = null;

// Função global para toggle (usada pelos onclick no HTML)
function toggleSidebar() {
    if (sidebarInstance) {
        sidebarInstance.toggle();
    }
}

/**
 * ============================================
 * CONFIGURAÇÕES - SIDEBAR JAVASCRIPT
 * ============================================
 */

class SettingsSidebar {
    constructor() {
        this.sidebar = null;
        this.overlay = null;
        this.toggleBtn = null;
        this.timeDisplay = null;
        this.isOpen = false;
        this.timeUpdateInterval = null;
        this.justToggled = false; // Flag para prevenir fechamento imediato
        
        this.init();
    }

    init() {
        // Aguarda o DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Seleciona elementos
        this.sidebar = document.getElementById('settingsSidebar');
        this.overlay = document.getElementById('sidebarOverlay');
        this.toggleBtn = document.querySelector('.sidebar-mobile-toggle');
        this.closeBtn = document.querySelector('.sidebar-toggle'); // Botão X de fechar
        this.timeDisplay = document.getElementById('timeDisplay');

        if (!this.sidebar) {
            console.warn('SettingsSidebar: Elemento sidebar não encontrado');
            return;
        }

        this.bindEvents();
        this.initTimeUpdate();
        this.handleInitialState();
    }

    bindEvents() {
        // Event listeners
        if (this.toggleBtn) {
            this.toggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggle();
            });
        }

        // Botão de fechar (X) no header do sidebar
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.close();
            });
        }

        if (this.overlay) {
            this.overlay.addEventListener('click', (e) => {
                e.stopPropagation();
                this.close();
            });
        }

        // Fechar com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });

        // Fechar clicando fora (mobile) - só após o sidebar estar realmente aberto
        document.addEventListener('click', (e) => {
            if (this.justToggled) {
                this.justToggled = false;
                return;
            }
            this.handleOutsideClick(e);
        });

        // Redimensionamento da janela
        window.addEventListener('resize', () => this.handleResize());

        // Links de navegação
        this.bindNavigationLinks();
    }

    bindNavigationLinks() {
        const navLinks = this.sidebar.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                // Fecha o sidebar no mobile após clicar em um link
                if (window.innerWidth < 992) {
                    setTimeout(() => this.close(), 150);
        this.justToggled = true; // Marca que acabou de fazer toggle
                }
            });
        });
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        if (this.isOpen) return;

        this.sidebar.classList.add('active');
        if (this.overlay) {
            this.overlay.classList.add('active');
        }

        // Previne scroll do body no mobile
        if (window.innerWidth < 992) {
            document.body.style.overflow = 'hidden';
        }

        // Atualiza estado do botão
        if (this.toggleBtn) {
            this.toggleBtn.setAttribute('aria-expanded', 'true');
            const icon = this.toggleBtn.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-times';
            }
        }

        this.isOpen = true;
        this.sidebar.focus();

        // Dispara evento customizado
        this.dispatchEvent('sidebarOpened');
    }

    close() {
        if (!this.isOpen) return;

        this.sidebar.classList.remove('active');
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }

        // Restaura scroll do body
        document.body.style.overflow = 'auto';

        // Atualiza estado do botão
        if (this.toggleBtn) {
            this.toggleBtn.setAttribute('aria-expanded', 'false');
            const icon = this.toggleBtn.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-bars';
            }
        }

        this.isOpen = false;

        // Dispara evento customizado
        this.dispatchEvent('sidebarClosed');
    }

    handleOutsideClick(event) {
        if (window.innerWidth >= 992) return; // Apenas no mobile

        const isClickInsideSidebar = this.sidebar && this.sidebar.contains(event.target);
        const isClickOnToggle = this.toggleBtn && this.toggleBtn.contains(event.target);

        if (this.isOpen && !isClickInsideSidebar && !isClickOnToggle) {
            this.close();
        }
    }

    handleResize() {
        if (window.innerWidth >= 992) {
            // Desktop: sidebar sempre visível, sem overlay
            this.sidebar.classList.remove('active');
            if (this.overlay) {
                this.overlay.classList.remove('active');
            }
            document.body.style.overflow = 'auto';
            this.isOpen = false;

            if (this.toggleBtn) {
                this.toggleBtn.setAttribute('aria-expanded', 'false');
                this.toggleBtn.style.display = 'none';
            }
        } else {
            // Mobile/Tablet: mostrar botão toggle
            if (this.toggleBtn) {
                this.toggleBtn.style.display = 'flex';
            }
        }
    }

    handleInitialState() {
        // Estado inicial baseado no tamanho da tela
        this.handleResize();
    }

    // ========== ATUALIZAÇÃO DE TEMPO ========== //
    initTimeUpdate() {
        if (!this.timeDisplay) return;

        this.updateCurrentTime();
        
        // Atualiza a cada minuto
        this.timeUpdateInterval = setInterval(() => {
            this.updateCurrentTime();
        }, 60000);
    }

    async updateCurrentTime() {
        try {
            const response = await fetch('/configuracoes/current-datetime/');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            
            if (this.timeDisplay && data.datetime) {
                this.timeDisplay.textContent = data.datetime;
                
                // Adiciona animação de atualização
                this.timeDisplay.style.opacity = '0.7';
                setTimeout(() => {
                    this.timeDisplay.style.opacity = '1';
                }, 200);
            }
        } catch (error) {
            console.error('Erro ao atualizar horário:', error);
            
            if (this.timeDisplay) {
                this.timeDisplay.textContent = 'Erro ao carregar';
                this.timeDisplay.style.color = '#dc3545';
            }
        }
    }

    // ========== UTILITÁRIOS ========== //
    dispatchEvent(eventName) {
        const event = new CustomEvent(eventName, {
            detail: { sidebar: this }
        });
        document.dispatchEvent(event);
    }

    destroy() {
        // Limpeza
        if (this.timeUpdateInterval) {
            clearInterval(this.timeUpdateInterval);
        }

        document.body.style.overflow = 'auto';
    }

    // ========== API PÚBLICA ========== //
    isActive() {
        return this.isOpen;
    }

    setActiveTab(tabName) {
        const links = this.sidebar.querySelectorAll('.nav-link');
        links.forEach(link => {
            link.classList.remove('active');
        });

        const activeLink = this.sidebar.querySelector(`[data-tab="${tabName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }
}

// ========== INICIALIZAÇÃO ========== //
document.addEventListener('DOMContentLoaded', function() {
    // Só inicializa se estivermos em uma página de configurações
    if (document.querySelector('#settingsSidebar')) {
        sidebarInstance = new SettingsSidebar();

        // Event listeners para eventos customizados
        document.addEventListener('sidebarOpened', function(e) {
            console.log('Sidebar aberto');
        });

        document.addEventListener('sidebarClosed', function(e) {
            console.log('Sidebar fechado');
        });
    }
});

// ========== CLEANUP ========== //
window.addEventListener('beforeunload', function() {
    if (sidebarInstance) {
        sidebarInstance.destroy();
    }
});
