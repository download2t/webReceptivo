# 📘 Guia Operacional Completo - WebReceptivo

**Versão:** 2.0  
**Última Atualização:** 06/01/2026  
**Framework:** Django 5.2.7 + Python 3.12  
**Servidor Produção:** LiteSpeed 1.8.4 OpenSource

---

## 🚀 SUBIR A APLICAÇÃO DO ZERO (PRODUÇÃO)

### Passo 1: Conectar ao Servidor

```bash
ssh root@31.97.254.220
```

### Passo 2: Ir para o diretório do projeto

```bash
cd /usr/local/lsws/Example/html/demo/webReceptivo
```

### Passo 3: Ativar ambiente virtual

```bash
source venv/bin/activate
```

### Passo 4: Aplicar migrações do banco

```bash
# Usando manage_production.py (recomendado)
export DJANGO_ENV=production
python manage_production.py migrate

# OU usando manage.py tradicional
python manage.py migrate --settings=webreceptivo.settings_production
```

### Passo 5: Criar superusuário (se não existir)

```bash
# Usando manage_production.py
export DJANGO_ENV=production
python manage_production.py createsuperuser

# OU tradicional
python manage.py createsuperuser --settings=webreceptivo.settings_production
```

### Passo 6: Criar grupos de permissões

```bash
# Usando manage_production.py
export DJANGO_ENV=production
python manage_production.py criar_grupos
python manage_production.py setup_groups

# OU tradicional
python manage.py criar_grupos --settings=webreceptivo.settings_production
python manage.py setup_groups --settings=webreceptivo.settings_production
```

### Passo 7: Coletar arquivos estáticos

```bash
# Usando manage_production.py
export DJANGO_ENV=production
python manage_production.py collectstatic --noinput

# OU tradicional
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production
```

### Passo 8: Configurar permissões (CRÍTICO!)

```bash
# Permissões gerais do projeto
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/

# Banco de dados precisa ser gravável
chmod 666 /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3

# Media (uploads) precisa de permissões totais
chmod -R 777 /usr/local/lsws/Example/html/demo/webReceptivo/media/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/media/

# Staticfiles apenas leitura
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/staticfiles/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/staticfiles/
```

### Passo 9: Iniciar LiteSpeed

```bash
sudo /usr/local/lsws/bin/lswsctrl start
```

### Passo 10: Verificar se subiu

```bash
# Ver status
sudo /usr/local/lsws/bin/lswsctrl status

# Testar com curl
curl -I http://mydevsystem.site/admin/

# Ver logs em tempo real
tail -f /usr/local/lsws/logs/error.log
```

### Passo 11: Acessar no navegador

- **Site:** https://mydevsystem.site
- **Admin:** https://mydevsystem.site/admin/
- **Configurações:** https://mydevsystem.site/configuracoes/

---

## 🔄 ATUALIZAR CÓDIGO E REINICIAR (DIA A DIA)

### Script Completo (Copie tudo de uma vez)

```bash
#!/bin/bash
# Sequência completa para atualizar aplicação

cd /usr/local/lsws/Example/html/demo/webReceptivo

# 1. Puxar código atualizado
git pull origin main

# 2. Ativar ambiente virtual
source venv/bin/activate

# 3. Instalar/atualizar dependências
pip install -r requirements.txt

# 4. Configurar variável de ambiente
export DJANGO_ENV=production

# 5. Aplicar migrações
python manage_production.py migrate

# 6. Coletar estáticos
python manage_production.py collectstatic --noinput

# 7. Corrigir permissões
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/
chmod 666 /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3
chmod -R 777 /usr/local/lsws/Example/html/demo/webReceptivo/media/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/

# 8. Reiniciar LiteSpeed
sudo /usr/local/lsws/bin/lswsctrl restart

# 9. Verificar status
sleep 2
sudo /usr/local/lsws/bin/lswsctrl status

echo "✅ Aplicação atualizada e reiniciada!"
```

### Versão Passo a Passo

```bash
# 1. Ir para o projeto
cd /usr/local/lsws/Example/html/demo/webReceptivo

# 2. Atualizar código
git pull origin main

# 3. Ativar venv
source venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Exportar variável
export DJANGO_ENV=production

# 6. Migrar banco
python manage_production.py migrate

# 7. Coletar estáticos
python manage_production.py collectstatic --noinput

# 8. Permissões
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/
chmod 666 /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3
chmod -R 777 /usr/local/lsws/Example/html/demo/webReceptivo/media/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/

# 9. Reiniciar
sudo /usr/local/lsws/bin/lswsctrl restart
```

---

## 🎛️ COMANDOS LITESPEED

### Controle Básico

```bash
# Iniciar
sudo /usr/local/lsws/bin/lswsctrl start

# Parar
sudo /usr/local/lsws/bin/lswsctrl stop

# Reiniciar
sudo /usr/local/lsws/bin/lswsctrl restart

# Recarregar configuração (sem derrubar)
sudo /usr/local/lsws/bin/lswsctrl reload

# Ver status
sudo /usr/local/lsws/bin/lswsctrl status
```

### Ver Logs

```bash
# Logs de erro em tempo real
tail -f /usr/local/lsws/logs/error.log

# Últimas 100 linhas
tail -100 /usr/local/lsws/logs/error.log

# Logs de acesso
tail -f /usr/local/lsws/logs/access.log

# Buscar erro específico
grep "error" /usr/local/lsws/logs/error.log | tail -50
```

### Processos

```bash
# Ver processos LiteSpeed
ps aux | grep lsws

# Ver processos Python/Django
ps aux | grep python

# Matar LiteSpeed forçadamente (emergência)
sudo pkill -9 lsws
```

---

## 🐍 COMANDOS DJANGO (manage_production.py)

### Modo Correto de Usar

```bash
# SEMPRE exportar DJANGO_ENV antes
export DJANGO_ENV=production

# Então rodar comandos
python manage_production.py [comando]
```

### Comandos Essenciais

```bash
# Shell Django
export DJANGO_ENV=production
python manage_production.py shell

# Verificar configuração
export DJANGO_ENV=production
python manage_production.py check

# Criar migrações (após alterar models)
export DJANGO_ENV=production
python manage_production.py makemigrations

# Aplicar migrações
export DJANGO_ENV=production
python manage_production.py migrate

# Coletar estáticos
export DJANGO_ENV=production
python manage_production.py collectstatic --noinput

# Criar superusuário
export DJANGO_ENV=production
python manage_production.py createsuperuser

# Criar grupos
export DJANGO_ENV=production
python manage_production.py criar_grupos
python manage_production.py setup_groups

# Executar testes
export DJANGO_ENV=production
python manage_production.py test
```

### Modo Tradicional (alternativa)

```bash
# Se não quiser usar DJANGO_ENV, usar --settings
python manage.py migrate --settings=webreceptivo.settings_production
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production
python manage.py createsuperuser --settings=webreceptivo.settings_production
```

---

## 🔐 PERMISSÕES DETALHADAS

### Entendendo as Permissões

**chmod 755** (rwxr-xr-x):
- Dono: leitura, escrita, execução (7)
- Grupo: leitura, execução (5)
- Outros: leitura, execução (5)
- **Uso:** Pastas do projeto, staticfiles

**chmod 666** (rw-rw-rw-):
- Todos: leitura, escrita (6)
- **Uso:** db.sqlite3 (Django precisa escrever)

**chmod 777** (rwxrwxrwx):
- Todos: leitura, escrita, execução (7)
- **Uso:** Pasta media/ (uploads de usuários)

### Script Completo de Permissões

```bash
#!/bin/bash
# Salve como fix_permissions.sh

PROJECT_DIR="/usr/local/lsws/Example/html/demo/webReceptivo"

echo "🔧 Corrigindo permissões..."

# Permissões gerais (755)
chmod -R 755 $PROJECT_DIR/
chown -R nobody:nogroup $PROJECT_DIR/

# Banco de dados (666 - gravável)
chmod 666 $PROJECT_DIR/db.sqlite3
echo "✅ db.sqlite3: 666 (rw-rw-rw-)"

# Media (777 - uploads)
chmod -R 777 $PROJECT_DIR/media/
chown -R nobody:nogroup $PROJECT_DIR/media/
echo "✅ media/: 777 (rwxrwxrwx)"

# Staticfiles (755 - apenas leitura)
chmod -R 755 $PROJECT_DIR/staticfiles/
chown -R nobody:nogroup $PROJECT_DIR/staticfiles/
echo "✅ staticfiles/: 755 (rwxr-xr-x)"

# Venv não precisa (já é do root)
echo "✅ venv/: sem mudanças"

echo "🎉 Permissões corrigidas!"
```

### Executar Script

```bash
# Criar arquivo
nano fix_permissions.sh

# Colar o conteúdo acima, salvar (CTRL+X, Y, ENTER)

# Tornar executável
chmod +x fix_permissions.sh

# Executar
./fix_permissions.sh
```

### Correção Rápida (uma linha)

```bash
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/ && chmod 666 /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3 && chmod -R 777 /usr/local/lsws/Example/html/demo/webReceptivo/media/ && chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/ && echo "✅ Permissões OK!"
```

---

## 🛠️ TROUBLESHOOTING

### Erro 500 - Internal Server Error

```bash
# 1. Ver logs
tail -f /usr/local/lsws/logs/error.log

# 2. Corrigir permissões
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/
chmod 666 /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3
chmod -R 777 /usr/local/lsws/Example/html/demo/webReceptivo/media/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/

# 3. Reiniciar
sudo /usr/local/lsws/bin/lswsctrl restart

# 4. Ver novamente
tail -f /usr/local/lsws/logs/error.log
```

### Uploads não funcionam

```bash
# Permissões media devem ser 777
chmod -R 777 /usr/local/lsws/Example/html/demo/webReceptivo/media/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/media/
sudo /usr/local/lsws/bin/lswsctrl restart
```

### Erro de banco (Can't write to database)

```bash
# Banco precisa 666
chmod 666 /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3
sudo /usr/local/lsws/bin/lswsctrl restart
```

### CSS/JS não carregam

```bash
# Recoletar estáticos
cd /usr/local/lsws/Example/html/demo/webReceptivo
source venv/bin/activate
export DJANGO_ENV=production
python manage_production.py collectstatic --clear --noinput

# Permissões
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/staticfiles/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/staticfiles/

# Reiniciar
sudo /usr/local/lsws/bin/lswsctrl restart
```

### LiteSpeed não inicia

```bash
# Ver status detalhado
sudo /usr/local/lsws/bin/lswsctrl status

# Ver processos
ps aux | grep lsws

# Matar processo travado
sudo pkill -9 lsws

# Iniciar novamente
sudo /usr/local/lsws/bin/lswsctrl start

# Ver logs
tail -50 /usr/local/lsws/logs/error.log
```

### ModuleNotFoundError

```bash
# Reinstalar dependências
cd /usr/local/lsws/Example/html/demo/webReceptivo
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo /usr/local/lsws/bin/lswsctrl restart
```

### AttributeError: 'NoneType' object has no attribute 'id'

```bash
# Este foi o erro que corrigimos - atualizar código
cd /usr/local/lsws/Example/html/demo/webReceptivo
git pull origin main
sudo /usr/local/lsws/bin/lswsctrl restart
```

---

## 📋 CHEAT SHEET RÁPIDO

### Iniciar/Parar/Reiniciar

```bash
# Status
sudo /usr/local/lsws/bin/lswsctrl status

# Iniciar
sudo /usr/local/lsws/bin/lswsctrl start

# Parar
sudo /usr/local/lsws/bin/lswsctrl stop

# Reiniciar
sudo /usr/local/lsws/bin/lswsctrl restart

# Logs
tail -f /usr/local/lsws/logs/error.log
```

### Atualizar Aplicação (Completo)

```bash
cd /usr/local/lsws/Example/html/demo/webReceptivo
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
export DJANGO_ENV=production
python manage_production.py migrate
python manage_production.py collectstatic --noinput
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/
chmod 666 /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3
chmod -R 777 /usr/local/lsws/Example/html/demo/webReceptivo/media/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/
sudo /usr/local/lsws/bin/lswsctrl restart
```

### Comandos Django Rápidos

```bash
# Configurar ambiente
cd /usr/local/lsws/Example/html/demo/webReceptivo
source venv/bin/activate
export DJANGO_ENV=production

# Shell
python manage_production.py shell

# Migrar
python manage_production.py migrate

# Coletar estáticos
python manage_production.py collectstatic --noinput

# Criar superusuário
python manage_production.py createsuperuser
```

### Corrigir Permissões (Rápido)

```bash
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/
chmod 666 /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3
chmod -R 777 /usr/local/lsws/Example/html/demo/webReceptivo/media/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/
sudo /usr/local/lsws/bin/lswsctrl restart
```

---

## 💻 DESENVOLVIMENTO LOCAL (Windows)

### Iniciar Servidor

```powershell
# Na pasta do projeto
.\start.ps1
```

**Acesso:**
- Site: http://localhost:8000
- Admin: http://localhost:8000/admin/

### Setup Inicial

```powershell
# Ativar venv
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Migrar banco
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Criar grupos
python manage.py criar_grupos
python manage.py setup_groups

# Coletar estáticos
python manage.py collectstatic --noinput

# Iniciar
.\start.ps1
```

### Atualizar Código

```powershell
git pull origin main
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
.\start.ps1
```

---

## 📁 ESTRUTURA DO PROJETO

```
/usr/local/lsws/Example/html/demo/webReceptivo/
├── manage.py                    # Gerenciador Django (dev)
├── manage_production.py         # Gerenciador Django (prod) ⭐
├── requirements.txt             # Dependências Python
├── db.sqlite3                   # Banco SQLite (chmod 666) ⭐
├── .env                         # Variáveis de ambiente
├── litespeed_wsgi.py            # Entry point LiteSpeed ⭐
├── start.ps1                    # Script Windows (dev)
│
├── venv/                        # Ambiente virtual Python
│
├── webreceptivo/                # Projeto Django
│   ├── settings.py              # Settings desenvolvimento
│   ├── settings_production.py  # Settings produção ⭐
│   ├── wsgi.py                  # WSGI dev
│   ├── wsgi_production.py       # WSGI produção ⭐
│   └── urls.py                  # URLs principais
│
├── user_management/             # App gestão de usuários
├── accounts/                    # App perfis e autenticação
├── servicos/                    # App serviços/ordens
├── audit_system/                # Sistema de auditoria
├── company_settings/            # Configurações empresa
├── core/                        # App core/dashboard
│
├── static/                      # Arquivos estáticos (fonte)
├── staticfiles/                 # Coletados (chmod 755) ⭐
├── templates/                   # Templates HTML
├── media/                       # Uploads (chmod 777) ⭐
│
└── docs/                        # Documentação
    ├── GUIA_DESENVOLVIMENTO.md  # Este arquivo
    └── DEPLOY_PRODUCTION.md     # Deploy completo
```

**⭐ = Arquivos/pastas críticos para produção**

---

## 📚 DOCUMENTAÇÃO ADICIONAL

- **[DEPLOY_PRODUCTION.md](../DEPLOY_PRODUCTION.md)** - Setup completo VPS do zero (18 passos)
- **[PERMISSOES.md](PERMISSOES.md)** - Sistema de permissões de serviços
- **[PERMISSIONS_DOCUMENTATION.md](PERMISSIONS_DOCUMENTATION.md)** - Hierarquia de usuários
- **[COMPANY_SETTINGS_GUIDE.md](COMPANY_SETTINGS_GUIDE.md)** - Configurações da empresa
- **[SISTEMA_AUDITORIA_COMPLETO.md](SISTEMA_AUDITORIA_COMPLETO.md)** - Sistema de auditoria

---

## 🔗 URLs de Acesso

### Produção
- **Site:** https://mydevsystem.site
- **Admin:** https://mydevsystem.site/admin/
- **Configurações:** https://mydevsystem.site/configuracoes/
- **Auditoria:** https://mydevsystem.site/audit/
- **Usuários:** https://mydevsystem.site/usuarios/
- **Painel LiteSpeed:** http://31.97.254.220:7080/admin/

### Desenvolvimento
- **Site:** http://localhost:8000
- **Admin:** http://localhost:8000/admin/

---

**Última atualização:** 06/01/2026  
**Mantido por:** Equipe de Desenvolvimento  
**Servidor:** LiteSpeed 1.8.4 + Django 5.2.7 + Python 3.12
