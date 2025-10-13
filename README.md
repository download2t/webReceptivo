# 🏢 WebReceptivo

Sistema web profissional para gestão receptiva desenvolvido em **Django 5.2.7**, com interface moderna, sistema completo de usuários e permissões hierárquicas.

## ✨ Principais Funcionalidades

### 👥 Sistema de Usuários e Permissões
- **5 Níveis Hierárquicos**: Admin Principal, Administradores, Gerentes, Operadores, Usuários Básicos
- **Gerenciamento Completo**: CRUD de usuários com regras de permissão robustas
- **Gerenciamento de Grupos**: Criação e edição de cargos/funções dinâmicos
- **Autenticação Segura**: Login/logout com validações server-side
- **Perfis Completos**: Dados pessoais, endereço, avatar e preferências

### 🎨 Interface Moderna
- **Design Responsivo**: Bootstrap 5.3.2 com tema claro/escuro
- **Mobile-First**: Otimizado para todos os dispositivos
- **Componentes Avançados**: Máscaras de input, upload de avatar, validação em tempo real
- **UX Profissional**: Mensagens de feedback, animações suaves, navegação intuitiva

## 🏗️ Arquitetura

### 🔧 Backend
- **Django 5.2.7** com Python 3.12+
- **Apps Modulares**: `accounts`, `core`, `user_management`
- **PostgreSQL** (produção) / **SQLite** (desenvolvimento)
- **Sistema de Permissões**: Regras hierárquicas customizadas com proteção de usuários críticos

### 🎨 Frontend  
- **Bootstrap 5.3.2** com **Bootstrap Icons**
- **JavaScript Vanilla** com funcionalidades modernas
- **CSS Customizado** com sistema de temas persistente

### 🐳 Infraestrutura
- **Docker** + **Docker Compose** para containerização
- **Entrypoint Inteligente** com verificação automática do banco
- **Configuração Otimizada** para desenvolvimento e produção

## ⚡ Instalação Rápida

### 🐳 Com Docker (Recomendado)
```bash
git clone <url-do-repositorio>
cd WebReceptivo
docker-compose up --build
```
**Acesse:** `http://localhost:8000`

### 🐍 Local (Python)
```bash
git clone <url-do-repositorio>
cd WebReceptivo
python -m venv .venv
.venv\Scripts\activate  # Windows | source .venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 🛠️ Comandos Úteis
```bash
# Setup inicial com grupos e usuários de teste
python manage.py setup_groups
python manage.py create_test_users

# Comandos Docker
docker-compose up -d              # Executar em background
docker-compose logs -f            # Ver logs
docker-compose down -v            # Parar e limpar volumes
```

## 📁 Estrutura do Projeto

```
WebReceptivo/
├── 📁 accounts/              # Autenticação e perfis
├── 📁 core/                  # Dashboard e funcionalidades principais
├── � user_management/       # Sistema completo de usuários e grupos
│   ├── 📄 permission_helpers.py    # Regras de permissão hierárquicas
│   ├── 📄 views.py                 # CRUD de usuários
│   ├── 📄 group_views.py           # CRUD de grupos/cargos
│   └── 📁 management/commands/     # Comandos de setup e teste
├── 📁 templates/             # Templates HTML responsivos
├── 📁 static/               # CSS, JS e assets
├── 📄 requirements.txt      # Dependências Python
├── 📄 docker-compose.yml    # Configuração Docker
└── 📄 entrypoint.sh        # Script de inicialização inteligente
```

## � Sistema de Permissões

### Hierarquia de Usuários
| Nível | Pode Gerenciar | Observações |
|-------|----------------|-------------|
| **Admin Principal (ID=1)** | 🌟 Todos | Protegido, intocável |
| **Administradores** | Gerentes, Operadores, Usuários | Não mexem entre si |
| **Gerentes** | Operadores, Usuários | Podem criar grupos customizados |
| **Operadores** | - | Acesso ao sistema operacional |
| **Usuários Básicos** | - | Acesso apenas ao próprio perfil |

### Grupos Protegidos vs Customizados
- **� Protegidos**: Administradores, Gerentes, Operadores, Usuários Básicos (não podem ser deletados)
- **✨ Customizados**: Criados dinamicamente pelos usuários com permissão (podem ser deletados)

## 📚 Documentação Adicional
- **[PERMISSIONS_DOCUMENTATION.md](./PERMISSIONS_DOCUMENTATION.md)** - Detalhes completos das permissões
- **[GUIA_GRUPOS.md](./GUIA_GRUPOS.md)** - Como usar o sistema de grupos
- **[ADMIN_INTEGRADO.md](./ADMIN_INTEGRADO.md)** - Admin Django integrado ao design
- **[CORRECAO_FINAL_UNION_ERROR.md](./CORRECAO_FINAL_UNION_ERROR.md)** - Histórico de correções técnicas

## ❓ FAQ & Troubleshooting

### Problemas Comuns
```bash
# Container não conecta ao PostgreSQL
# ✅ O entrypoint já resolve automaticamente

# Resetar banco completamente  
docker-compose down -v && docker-compose up --build

# Ver logs específicos
docker-compose logs -f web    # Django
docker-compose logs -f db     # PostgreSQL

# Testar sistema de permissões
python manage.py test_groups_queryset
```

## � Admin Django Integrado
- **🎨 Interface Unificada**: Admin Django com design do WebReceptivo
- **📊 Dashboard Personalizado**: Estatísticas e acesso rápido
- **🎨 Templates Customizados**: Formulários e listas com Bootstrap
- **🔐 Acesso Hierárquico**: Integração com sistema de permissões
- **📱 Responsivo**: Funciona perfeitamente em todos os dispositivos

## �🚀 Próximas Funcionalidades
- [ ] Sistema de logs/auditoria para alterações de usuários e grupos
- [ ] API REST para integração com outros sistemas
- [ ] Dashboard com relatórios de usuários ativos
- [ ] Sistema de notificações internas
- [ ] Workflow de aprovação para criação de grupos

## 📄 Licença
MIT License - Veja o arquivo LICENSE para mais detalhes.

---
*Desenvolvido com ❤️ usando Django 5.2.7 e Bootstrap 5*
