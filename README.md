# � WebReceptivo

[![Versão](https://img.shields.io/badge/versão-1.2.0-blue.svg)](https://github.com/your-repo/WebReceptivo/releases)
[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org/)

Sistema web profissional para gestão receptiva desenvolvido em **Django 5.2.7**, com interface moderna, sistema completo de usuários e permissões hierárquicas.🏢 WebReceptivo

Sistema web profissional para gestão receptiva desenvolvido em **Django 5.2.7**, com interface moderna, sistema completo de usuários e permissões ## 🚀 Próximas Funcionalidades

### ✅ **Implementadas na v1.2.0**
- [x] **Sistema de Tema Personalizado**: Preferência individual de tema por usuário
- [x] **Melhorias nos Avatares**: Exibição consistente em todo o sistema
- [x] **Segurança Aprimorada**: Remoção da exclusão permanente de usuários
- [x] **Admin Integrado**: Unificação completa entre admin e site principal

### ✅ **Implementadas na v1.3.0 (NOVO!)**
- [x] **📊 Sistema de Auditoria Completo**: Rastreamento total de todas as ações do sistema
- [x] **🔍 Dashboard de Monitoramento**: Estatísticas em tempo real com gráficos dinâmicos
- [x] **📈 Relatórios Avançados**: Filtros, busca e exportação de dados de auditoria
- [x] **👤 Histórico Individual**: Perfil completo de atividades por usuário
- [x] **⚡ Performance Otimizada**: Comandos automáticos de manutenção e limpeza

### 📋 **Roadmap Futuro**
- [ ] API REST para integração com outros sistemas
- [ ] Sistema de notificações internas em tempo real
- [ ] Workflow de aprovação para criação de grupos
- [ ] Alertas automáticos para ações suspeitas
- [ ] Integração com sistemas SIEM externos
- [ ] Machine Learning para detecção de anomaliasquicas.

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

## � Últimas Atualizações (v1.2.0)

### 🎨 **Sistema de Tema Personalizado**
- **Tema Automático por Usuário**: Cada usuário tem sua preferência salva (claro/escuro/auto)
- **Aplicação Instantânea**: Tema aplicado automaticamente ao fazer login
- **Sincronização Inteligente**: Mudanças salvas em tempo real no perfil do usuário
- **Modo Auto**: Segue automaticamente a preferência do sistema operacional
- **Limpeza Automática**: Reset para tema do sistema após logout

### 👤 **Melhorias nos Avatares**
- **Menu Principal**: Avatar do usuário exibido ao lado do nome na navbar
- **Lista de Usuários**: Miniaturas dos avatares na listagem de usuários
- **Avatar Padrão**: Fallback elegante para usuários sem foto
- **Consistência Visual**: Mesmo estilo entre admin e site principal

### 🔒 **Segurança Aprimorada**
- **Exclusão Removida**: Funcionalidade de exclusão permanente de usuários desabilitada
- **Apenas Inativação**: Preservação da integridade dos dados com inativação segura
- **Política Documentada**: Avisos claros sobre política de não-exclusão
- **Proteção de Dados**: Manutenção do histórico e relacionamentos

### 🎯 **Organização de Código**
- **CSS Modularizado**: Separação do CSS de grupos em arquivo dedicado (`static/css/groups.css`)
- **Templates Limpos**: Remoção de CSS inline dos templates
- **Manutenibilidade**: Estrutura mais organizada e fácil de manter
- **Temas Unificados**: Suporte completo a temas claro/escuro em todos os componentes

### 🔧 **Integração Admin-Site**
- **Menu Unificado**: Admin Django usa exatamente o mesmo menu do site principal
- **Tema Sincronizado**: Sistema de tema compartilhado entre admin e site
- **Avatar Consistente**: Exibição de avatar idêntica em ambos os contextos
- **Zero Duplicação**: Eliminação completa de código duplicado

### 📊 **Sistema de Auditoria (NOVO na v1.3.0)**
- **🔍 Monitoramento Total**: Captura automática de todas as ações via signals Django
- **📈 Dashboard Interativo**: Estatísticas em tempo real com gráficos Chart.js
- **🎯 Rastreamento Detalhado**: IP, User-Agent, sessão, alterações antes/depois
- **👤 Perfis Individuais**: Histórico completo de ações por usuário
- **🔎 Busca Avançada**: Filtros por ação, usuário, data, status com exportação CSV
- **⚡ Performance Otimizada**: Índices de banco, resumos pré-calculados, limpeza automática
- **🛡️ Segurança Total**: Logs somente-leitura, acesso controlado apenas para staff
- **🔧 Extensível**: Decoradores e signals para auditoria de novos módulos
- **📱 Interface Responsiva**: CSS modular com suporte completo a temas

## �🏗️ Arquitetura

### 🔧 Backend
- **Django 5.2.7** com Python 3.12+
- **Apps Modulares**: `accounts`, `core`, `user_management`, `audit_system`
- **PostgreSQL** (produção) / **SQLite** (desenvolvimento)
- **Sistema de Permissões**: Regras hierárquicas customizadas com proteção de usuários críticos
- **Sistema de Auditoria**: Captura automática via signals, middleware de contexto, comandos de manutenção

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
