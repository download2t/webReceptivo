# WebReceptivo

Aplicação Django focada em operação receptiva: cadastros de serviços e ordens, gestão de usuários com regras hierárquicas e trilha completa de auditoria. Este projeto agora é **local-only** (SQLite), sem dependências de Docker ou servidores externos.

## Requisitos
- Python 3.12+
- pip
- Windows: use PowerShell; recomendo virtualenv (`python -m venv .venv`).

## Como rodar localmente
1. Ative o ambiente virtual
	- `python -m venv .venv`
	- `.venv\Scripts\activate`
2. Instale dependências: `pip install -r requirements.txt`
3. Aplique migrações: `python manage.py migrate`
4. Crie um superusuário (opcional, mas recomendado): `python manage.py createsuperuser`
5. Configure grupos iniciais (ambos podem ser executados em qualquer ordem):
	- Permissões do módulo de serviços: `python manage.py criar_grupos`
	- Hierarquia do módulo de usuários: `python manage.py setup_groups`
6. Suba o servidor: `python manage.py runserver`

## URLs úteis (local)
- Admin Django: http://127.0.0.1:8000/admin/
- Configurações da empresa: http://127.0.0.1:8000/configuracoes/
- Auditoria: http://127.0.0.1:8000/audit/
- Gestão de usuários: http://127.0.0.1:8000/usuarios/

## Regras e módulos (resumo)
- **Permissões de serviços**: quatro grupos padrão (`Operador`, `Coordenador`, `Gestor de Cadastros`, `Gerente`) controlam criação/edição de categorias, serviços, transfers e ordens. Veja [docs/PERMISSOES.md](docs/PERMISSOES.md).
- **Hierarquia de usuários**: níveis protegidos (Admin Principal, Administradores, Gerentes, Operadores, Usuários Básicos) com restrições claras para visualizar/editar/excluir. Veja [docs/PERMISSIONS_DOCUMENTATION.md](docs/PERMISSIONS_DOCUMENTATION.md).
- **Configurações da empresa**: módulo para dados da empresa, fuso horário, SMTP com teste e aplicação dinâmica. Veja [docs/COMPANY_SETTINGS_GUIDE.md](docs/COMPANY_SETTINGS_GUIDE.md) e [docs/SETUP_CONFIG.md](docs/SETUP_CONFIG.md).
- **Auditoria**: dashboard, busca e exportação de logs; todas as ações relevantes são registradas. Veja [docs/RESUMO_EXECUTIVO_AUDITORIA.md](docs/RESUMO_EXECUTIVO_AUDITORIA.md) e [docs/SISTEMA_AUDITORIA_COMPLETO.md](docs/SISTEMA_AUDITORIA_COMPLETO.md).

## Fluxo recomendado para novo ambiente
- Criar superusuário e fazer login no admin.
- Executar os comandos de grupos (`criar_grupos` e `setup_groups`).
- Cadastrar dados da empresa e SMTP em /configuracoes/.
- Criar usuários operacionais e atribuir grupos.
- Validar auditoria acessando /audit/ para confirmar registros.

## Manutenção rápida
- Sincronizar modelo: `python manage.py makemigrations` e `python manage.py migrate` quando alterar modelos.
- Coletar estáticos (se precisar servir fora do runserver): `python manage.py collectstatic`.

## Documentação
- **[Guia de Desenvolvimento](docs/GUIA_DESENVOLVIMENTO.md)** - Passo a passo para rodar o servidor Django, troubleshooting e dicas rápidas
- Permissões do módulo de serviços: [docs/PERMISSOES.md](docs/PERMISSOES.md)
- Hierarquia de usuários: [docs/PERMISSIONS_DOCUMENTATION.md](docs/PERMISSIONS_DOCUMENTATION.md)
- Configurações da empresa: [docs/COMPANY_SETTINGS_GUIDE.md](docs/COMPANY_SETTINGS_GUIDE.md)
- Setup técnico e SMTP: [docs/SETUP_CONFIG.md](docs/SETUP_CONFIG.md)
- Auditoria (executivo): [docs/RESUMO_EXECUTIVO_AUDITORIA.md](docs/RESUMO_EXECUTIVO_AUDITORIA.md)
- Auditoria (completo): [docs/SISTEMA_AUDITORIA_COMPLETO.md](docs/SISTEMA_AUDITORIA_COMPLETO.md)
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
*Desenvolvido utilizandp Django 5.2.7 e Bootstrap 5*


##Conectar o PC ao servidor SSH

Criar chave SSH ( chave pública e privada).
```
ssh-keygen -t rsa -b 4096 -C "mtduarte.b@gmail.com"
```

exibir o conteudo da chave pública
cat ~/.ssh/id_rsa.pub