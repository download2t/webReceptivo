/**
 * ============================================
 * SIDEBAR - GERENCIADOR DE ESTADO
 * JavaScript profissional e bem estruturado
 * ============================================
 */

// Variável global para acesso à instância
let sidebarInstance = null;

/**
 * Função global para toggle (compatibilidade com onclick no HTML)
 * @return {void}
 */
function toggleSidebar() {
    if (sidebarInstance) {
        sidebarInstance.toggle();
    }
}

/**
 * ============================================
 * CLASSE: SettingsSidebar
 * Gerencia o estado e comportamento da sidebar
 * ============================================
 */

class SettingsSidebar {
    /**
     * Construtor
     * @constructor
     */
    constructor() {
        this.sidebar = null;
        this.overlay = null;
        this.toggleBtn = null;
        this.closeBtn = null;
        this.collapseBtn = null;
        this.timeDisplay = null;

        // Estado
        this.isOpen = false;
        this.isCollapsed = true;
        this.isMobile = window.innerWidth < 992;
        this.timeUpdateInterval = null;
        this.justToggled = false;

        this.init();
    }

    /**
     * Inicializa a sidebar quando o DOM estiver pronto
     * @return {void}
     */
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    /**
     * Configura elementos, event listeners e estado inicial
     * @return {void}
     */
    setup() {
        this.cacheElements();

        if (!this.sidebar) {
            console.warn('SettingsSidebar: Elemento sidebar não encontrado');
            return;
        }

        this.bindEvents();
        this.initTimeUpdate();
        this.handleInitialState();
    }

    /**
     * Cache de elementos do DOM
     * @return {void}
     */
    cacheElements() {
        this.sidebar = document.getElementById('settingsSidebar');
        this.overlay = document.getElementById('sidebarOverlay');
        this.toggleBtn = document.querySelector('.sidebar-mobile-toggle');
        this.closeBtn = document.querySelector('.sidebar-toggle');
        this.collapseBtn = document.querySelector('.sidebar-collapse-toggle');
        this.timeDisplay = document.getElementById('timeDisplay');
    }

    /**
     * Vincula event listeners
     * @return {void}
     */
    bindEvents() {
        // Botão toggle mobile
        if (this.toggleBtn) {
            this.toggleBtn.addEventListener('click', (e) => this.handleToggleClick(e));
        }

        // Botão fechar mobile (X)
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', (e) => this.handleCloseClick(e));
        }

        // Botão colapsar/expandir desktop
        if (this.collapseBtn) {
            this.collapseBtn.addEventListener('click', (e) => this.handleCollapseClick(e));
        }

        // Overlay mobile
        if (this.overlay) {
            this.overlay.addEventListener('click', (e) => this.handleOverlayClick(e));
        }

        // Fechar com ESC
        document.addEventListener('keydown', (e) => this.handleEscKey(e));

        // Clique fora da sidebar
        document.addEventListener('click', (e) => this.handleOutsideClick(e));

        // Redimensionamento da janela
        window.addEventListener('resize', () => this.handleResize());

        // Clique no sidebar para expandir (desktop)
        this.sidebar.addEventListener('click', (e) => this.handleSidebarClick(e));

        // Links de navegação
        this.bindNavigationLinks();
    }

    /**
     * Vincula event listeners aos links de navegação
     * @return {void}
     */
    bindNavigationLinks() {
        const navLinks = this.sidebar.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => this.handleNavLinkClick(e));
        });
    }

    /**
     * Handler: Clique no botão toggle mobile
     * @param {Event} e
     * @return {void}
     */
    handleToggleClick(e) {
        e.preventDefault();
        e.stopPropagation();
        this.toggle();
    }

    /**
     * Handler: Clique no botão fechar mobile
     * @param {Event} e
     * @return {void}
     */
    handleCloseClick(e) {
        e.preventDefault();
        e.stopPropagation();
        this.close();
    }

    /**
     * Handler: Clique no botão colapsar/expandir desktop
     * @param {Event} e
     * @return {void}
     */
    handleCollapseClick(e) {
        e.preventDefault();
        e.stopPropagation();
        this.toggleCollapse();
    }

    /**
     * Handler: Clique no overlay mobile
     * @param {Event} e
     * @return {void}
     */
    handleOverlayClick(e) {
        e.stopPropagation();
        this.close();
    }

    /**
     * Handler: Tecla ESC
     * @param {KeyboardEvent} e
     * @return {void}
     */
    handleEscKey(e) {
        if (e.key === 'Escape' && this.isOpen) {
            this.close();
        }
    }

    /**
     * Handler: Clique fora da sidebar
     * @param {Event} e
     * @return {void}
     */
    handleOutsideClick(e) {
        // Flag para evitar múltiplos cliques
        if (this.justToggled) {
            this.justToggled = false;
            return;
        }

        const isClickInsideSidebar = this.sidebar && this.sidebar.contains(e.target);
        const isClickOnToggle = this.toggleBtn && this.toggleBtn.contains(e.target);

        if (this.isMobile) {
            // Mobile: fechar ao clicar fora
            if (this.isOpen && !isClickInsideSidebar && !isClickOnToggle) {
                this.close();
            }
        } else {
            // Desktop: colapsar ao clicar fora
            if (!isClickInsideSidebar && !this.collapseBtn.contains(e.target)) {
                this.collapse();
            }
        }
    }

    /**
     * Handler: Redimensionamento da janela
     * @return {void}
     */
    handleResize() {
        const newIsMobile = window.innerWidth < 992;

        if (newIsMobile !== this.isMobile) {
            this.isMobile = newIsMobile;
            this.handleBreakpointChange();
        }
    }

    /**
     * Handler: Mudança de breakpoint
     * @return {void}
     */
    handleBreakpointChange() {
        if (this.isMobile) {
            // Mudou para mobile
            this.sidebar.classList.remove('active');
            this.sidebar.classList.remove('is-collapsed');
            if (this.overlay) {
                this.overlay.classList.remove('active');
            }
            document.body.style.overflow = 'auto';
            this.isOpen = false;
            this.isCollapsed = false;
        } else {
            // Mudou para desktop
            this.sidebar.classList.remove('active');
            if (this.overlay) {
                this.overlay.classList.remove('active');
            }
            document.body.style.overflow = 'auto';
            this.isOpen = false;
            this.collapse();
        }
    }

    /**
     * Handler: Clique no sidebar (para expandir no desktop)
     * @param {Event} e
     * @return {void}
     */
    handleSidebarClick(e) {
        if (this.isMobile) return;

        if (this.isCollapsed) {
            const clickedLink = e.target.closest('.nav-link');
            if (clickedLink) {
                this.expand();
            }
        }
    }

    /**
     * Handler: Clique em link de navegação
     * @param {Event} e
     * @return {void}
     */
    handleNavLinkClick(e) {
        // Mobile: fechar após clique
        if (this.isMobile && this.isOpen) {
            setTimeout(() => this.close(), 150);
            this.justToggled = true;
        }
    }

    /**
     * Abre a sidebar (mobile)
     * @return {void}
     */
    open() {
        if (this.isOpen) return;

        this.sidebar.classList.add('active');
        if (this.overlay) {
            this.overlay.classList.add('active');
        }

        document.body.style.overflow = 'hidden';

        if (this.toggleBtn) {
            this.toggleBtn.setAttribute('aria-expanded', 'true');
            const icon = this.toggleBtn.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-times';
            }
        }

        this.isOpen = true;
        this.dispatchEvent('sidebarOpened');
    }

    /**
     * Fecha a sidebar (mobile)
     * @return {void}
     */
    close() {
        if (!this.isOpen) return;

        this.sidebar.classList.remove('active');
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }

        document.body.style.overflow = 'auto';

        if (this.toggleBtn) {
            this.toggleBtn.setAttribute('aria-expanded', 'false');
            const icon = this.toggleBtn.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-bars';
            }
        }

        this.isOpen = false;
        this.dispatchEvent('sidebarClosed');
    }

    /**
     * Toggle: Abre ou fecha a sidebar
     * @return {void}
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Expande a sidebar (desktop)
     * @return {void}
     */
    expand() {
        if (this.isMobile) return;

        this.sidebar.classList.remove('is-collapsed');
        this.isCollapsed = false;
        this.updateCollapseButton();
        this.dispatchEvent('sidebarExpanded');
    }

    /**
     * Colapspa a sidebar (desktop)
     * @return {void}
     */
    collapse() {
        if (this.isMobile) return;

        this.sidebar.classList.add('is-collapsed');
        this.isCollapsed = true;
        this.updateCollapseButton();
        this.dispatchEvent('sidebarCollapsed');
    }

    /**
     * Toggle: Expande ou colapspa a sidebar
     * @return {void}
     */
    toggleCollapse() {
        if (this.isCollapsed) {
            this.expand();
        } else {
            this.collapse();
        }
    }

    /**
     * Atualiza o ícone do botão colapsar
     * @return {void}
     */
    updateCollapseButton() {
        if (!this.collapseBtn) return;

        const icon = this.collapseBtn.querySelector('i');
        if (icon) {
            if (this.isCollapsed) {
                icon.className = 'fas fa-angle-double-right';
                this.collapseBtn.setAttribute('title', 'Expandir menu');
                this.collapseBtn.setAttribute('aria-label', 'Expandir menu');
            } else {
                icon.className = 'fas fa-angle-double-left';
                this.collapseBtn.setAttribute('title', 'Recolher menu');
                this.collapseBtn.setAttribute('aria-label', 'Recolher menu');
            }
        }
    }

    /**
     * Define o estado inicial da sidebar baseado no tamanho da tela
     * @return {void}
     */
    handleInitialState() {
        this.isMobile = window.innerWidth < 992;

        if (this.isMobile) {
            this.sidebar.classList.remove('is-collapsed');
            this.isCollapsed = false;
        } else {
            this.sidebar.classList.add('is-collapsed');
            this.isCollapsed = true;
            this.updateCollapseButton();
        }
    }

    /**
     * ========== GERENCIAMENTO DE TEMPO ==========
     */

    /**
     * Inicializa a atualização de hora
     * @return {void}
     */
    initTimeUpdate() {
        if (!this.timeDisplay) return;

        this.updateCurrentTime();

        // Atualiza a cada minuto (60000ms)
        this.timeUpdateInterval = setInterval(() => {
            this.updateCurrentTime();
        }, 60000);
    }

    /**
     * Atualiza a hora atual do servidor
     * @async
     * @return {Promise<void>}
     */
    async updateCurrentTime() {
        try {
            const response = await fetch('/configuracoes/current-datetime/');

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (this.timeDisplay && data.datetime) {
                this.timeDisplay.textContent = data.datetime;

                // Animação de atualização
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

    /**
     * ========== UTILITÁRIOS ==========
     */

    /**
     * Dispara evento customizado
     * @param {string} eventName - Nome do evento
     * @return {void}
     */
    dispatchEvent(eventName) {
        const event = new CustomEvent(eventName, {
            detail: { sidebar: this }
        });
        document.dispatchEvent(event);
    }

    /**
     * Retorna se a sidebar está aberta
     * @return {boolean}
     */
    isActive() {
        return this.isOpen;
    }

    /**
     * Define a aba/link ativo
     * @param {string} tabName - Nome da aba
     * @return {void}
     */
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

    /**
     * Limpeza: Remove listeners e reset
     * @return {void}
     */
    destroy() {
        if (this.timeUpdateInterval) {
            clearInterval(this.timeUpdateInterval);
        }

        document.body.style.overflow = 'auto';
    }
}

/**
 * ============================================
 * INICIALIZAÇÃO E SETUP GLOBAL
 * ============================================
 */

/**
 * Inicializa a sidebar quando o DOM está pronto
 */
document.addEventListener('DOMContentLoaded', function () {
    // Verifica se estamos em uma página de configurações
    if (document.querySelector('#settingsSidebar')) {
        sidebarInstance = new SettingsSidebar();

        // Event listeners para eventos customizados
        document.addEventListener('sidebarOpened', function (e) {
            console.log('Sidebar aberta');
        });

        document.addEventListener('sidebarClosed', function (e) {
            console.log('Sidebar fechada');
        });

        document.addEventListener('sidebarCollapsed', function (e) {
            console.log('Sidebar recolhida');
        });

        document.addEventListener('sidebarExpanded', function (e) {
            console.log('Sidebar expandida');
        });
    }
});

/**
 * Limpeza ao descarregar a página
 */
window.addEventListener('beforeunload', function () {
    if (sidebarInstance) {
        sidebarInstance.destroy();
    }
});
