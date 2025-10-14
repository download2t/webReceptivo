# ⚙️ Setup e Configuração - WebReceptivo

## 🚀 Instalação e Setup

### 1️⃣ **Dependências**
```bash
# Instalar dependências
pip install -r requirements.txt

# Principais pacotes:
# - requests>=2.28.0 (para validação CEP)
# - pytz (para fusos horários)
# - django>=5.0.9
```

### 2️⃣ **Migrações do Banco**
```bash
# Criar migrações
python manage.py makemigrations company_settings

# Aplicar migrações
python manage.py migrate company_settings

# Verificar status
python manage.py showmigrations company_settings
```

### 3️⃣ **Dados Iniciais**
```bash
# Popular dados demo
python setup_demo.py

# Criar superusuário (se necessário)
python manage.py createsuperuser
```

### 4️⃣ **Configuração no settings.py**
```python
# Adicionar ao INSTALLED_APPS
INSTALLED_APPS = [
    # ... outros apps
    'company_settings',
]

# Adicionar middleware (opcional - para SMTP dinâmico)
MIDDLEWARE = [
    # ... outros middlewares
    'company_settings.middleware.DynamicSMTPMiddleware',
]
```

### 5️⃣ **URLs do Projeto**
```python
# webreceptivo/urls.py
urlpatterns = [
    # ... outras URLs
    path('configuracoes/', include('company_settings.urls')),
]
```

## 🐳 Docker - Comandos Essenciais

### 📦 **Container Management**
```bash
# Verificar containers ativos
docker ps

# Executar comando no container
docker exec -it webreceptivo python manage.py migrate

# Executar setup demo no Docker
docker exec -it webreceptivo python setup_demo.py

# Ver logs do container
docker logs webreceptivo -f
```

### 🔄 **Atualizações no Docker**
```bash
# Parar container
docker-compose down

# Reconstruir com mudanças
docker-compose up --build -d

# Aplicar migrações
docker exec -it webreceptivo python manage.py migrate

# Coletar arquivos estáticos
docker exec -it webreceptivo python manage.py collectstatic --noinput
```

## 📧 Configuração SMTP Avançada

### 🔑 **Senhas de App (Gmail)**
1. Ativar verificação em 2 etapas na conta Google
2. Ir em "Senhas de app" nas configurações Google
3. Gerar uma senha específica para o Django
4. Usar essa senha no campo "Senha SMTP"

### 🌐 **Provedores Populares**

#### **Gmail**
```
Servidor: smtp.gmail.com
Porta: 587
Segurança: TLS
E-mail: seuemail@gmail.com
Senha: senha_de_app_do_google
```

#### **Outlook/Hotmail**
```
Servidor: smtp-mail.outlook.com
Porta: 587
Segurança: TLS
E-mail: seuemail@outlook.com
Senha: senha_normal_da_conta
```

#### **Yahoo**
```
Servidor: smtp.mail.yahoo.com
Porta: 587
Segurança: TLS
E-mail: seuemail@yahoo.com
Senha: senha_de_app_do_yahoo
```

### 🧪 **Teste de Configuração SMTP**
```bash
# Via comando Django
python manage.py apply_smtp --test

# Via interface web
# Acesse: /configuracoes/smtp/
# Preencha dados → "Enviar E-mail de Teste"

# Verificar logs de e-mail (desenvolvimento)
# No console aparecerão os e-mails simulados
```

## 🔐 Configuração de Segurança

### 👤 **Usuários Administradores**
```bash
# Criar superusuário
python manage.py createsuperuser

# Tornar usuário existente admin
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='usuario')
>>> user.is_staff = True
>>> user.is_superuser = True
>>> user.save()
```

### 🛡️ **Permissões de Acesso**
- Apenas usuários `is_staff=True` podem acessar configurações
- Verificação automática via decorator `@user_passes_test(is_admin_user)`
- Redirecionamento automático para login se não autenticado

### 🔒 **Dados Sensíveis**
- Senhas SMTP são criptografadas no banco
- Campos de senha não aparecem em logs de auditoria
- CSRF protection em todos os formulários

## 🗃️ Estrutura do Banco de Dados

### 📊 **Tabelas Criadas**
```sql
-- Configurações da empresa
company_settings_companysettings (
    id, company_name, cnpj_cpf, state_registration,
    street, number, complement, neighborhood, city, state,
    zip_code, phone, email, logo, created_at, updated_at, updated_by_id
)

-- Configurações do sistema
company_settings_systemsettings (
    id, date_format, time_format, timezone,
    created_at, updated_at, updated_by_id
)

-- Configurações SMTP (simplificado)
company_settings_smtpsettings (
    id, email_backend, smtp_server, smtp_port, connection_security,
    email, smtp_password, use_authentication, timeout, is_active,
    last_test_date, last_test_success, last_test_message,
    created_at, updated_at, updated_by_id
)
```

## 🔍 Validações Especiais

### 🆔 **CNPJ da Empresa WebReceptivo**
```python
# CNPJ especial aceito pelo sistema
COMPANY_CNPJ = "77.766.483/0001-64"

# Todos os outros CNPJs devem passar pela validação matemática:
def validate_cnpj(cnpj):
    # Remove formatação
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Verifica se é o CNPJ da empresa (exceção)
    if cnpj == "77766483000164":
        return True
    
    # Validação matemática normal para outros CNPJs
    # ... algoritmo de validação
```

### 🏠 **Validação CEP (ViaCEP)**
```python
def validate_cep(cep):
    """Busca dados do CEP via API ViaCEP"""
    try:
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        if response.status_code == 200:
            data = response.json()
            if 'erro' not in data:
                return {
                    'street': data.get('logradouro', ''),
                    'neighborhood': data.get('bairro', ''),
                    'city': data.get('localidade', ''),
                    'state': data.get('uf', '')
                }
    except Exception:
        pass
    return None
```

## 🛠️ Troubleshooting

### 🚨 **Problemas Comuns**

#### **Erro: "relation does not exist"**
```bash
# Solução: Aplicar migrações
python manage.py migrate company_settings
```

#### **SMTP não funciona**
```bash
# Verificar configurações
python manage.py shell
>>> from company_settings.models import SMTPSettings
>>> smtp = SMTPSettings.get_settings()
>>> print(smtp.email, smtp.smtp_server)

# Testar manualmente
python manage.py apply_smtp --test
```

#### **CEP não preenche endereço**
```bash
# Verificar conexão internet
curl https://viacep.com.br/ws/01310-100/json/

# Verificar logs do navegador (F12 → Console)
```

### 📝 **Logs e Debug**
```bash
# Ver logs Django (desenvolvimento)
python manage.py runserver --verbosity=2

# Logs de auditoria
# Acesse: /audit/logs/

# Debug SMTP
# Adicione no settings.py:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## 📋 Checklist de Implantação

### ✅ **Antes de ir para Produção**
- [ ] Migrações aplicadas
- [ ] Dados demo populados ou configurações reais inseridas
- [ ] Teste SMTP funcionando
- [ ] Usuário admin criado
- [ ] Menu "Configurações" aparece para admins
- [ ] Validações funcionando (CNPJ, CEP, e-mail)
- [ ] Docker funcionando (se aplicável)
- [ ] Arquivos estáticos coletados
- [ ] Backup do banco de dados

### 🔄 **Manutenção Regular**
- [ ] Verificar logs de auditoria mensalmente
- [ ] Testar SMTP periodicamente
- [ ] Atualizar dependências quando necessário
- [ ] Monitorar espaço de upload de logos
- [ ] Fazer backup das configurações

---

**🔧 Documento Técnico**: Setup e Configuração  
**📅 Atualizado**: Outubro 2025  
**🏗️ Versão Django**: 5.0.9  
**🐍 Versão Python**: 3.12+
