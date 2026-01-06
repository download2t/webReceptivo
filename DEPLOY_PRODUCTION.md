# Guia de Deploy para Produção - WebReceptivo
# IP: 31.97.254.220
# Domínio: mydevsystem.site

## 1. No servidor VPS (via SSH)

### 1.1 Atualizar código do repositório
```bash
cd /usr/local/lsws/Example/html/demo/webReceptivo
git pull origin main
```

### 1.2 Criar arquivo .env (IMPORTANTE - primeira vez)
```bash
# Gerar SECRET_KEY segura
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Criar arquivo .env
nano .env
```

Conteúdo do .env:
```
SECRET_KEY=COLE-AQUI-A-CHAVE-GERADA-ACIMA
DEBUG=False
ALLOWED_HOSTS=31.97.254.220,mydevsystem.site,www.mydevsystem.site
DATABASE_URL=
```

### 1.3 Ativar ambiente virtual
```bash
source venv/bin/activate
```

### 1.4 Instalar dependências (se houver mudanças)
```bash
pip install -r requirements.txt
```

### 1.5 Coletar arquivos estáticos
```bash
export DJANGO_SETTINGS_MODULE=webreceptivo.settings_production
python manage.py collectstatic --noinput
```

### 1.6 Aplicar migrações
```bash
python manage.py migrate --settings=webreceptivo.settings_production
```

### 1.7 Criar grupos de permissões (primeira vez)
```bash
python manage.py criar_grupos --settings=webreceptivo.settings_production
python manage.py setup_groups --settings=webreceptivo.settings_production
```

### 1.8 Criar superusuário (primeira vez)
```bash
python manage.py createsuperuser --settings=webreceptivo.settings_production
```

## 2. Configurar LiteSpeed Web Server

### 2.1 Criar arquivo de configuração WSGI
Caminho: `/usr/local/lsws/Example/html/demo/webReceptivo/litespeed_wsgi.py`

```python
import sys
import os

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, '/usr/local/lsws/Example/html/demo/webReceptivo')

# Configurar Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'webreceptivo.settings_production'

# Importar a aplicação WSGI
from webreceptivo.wsgi_production import application
```

### 2.2 Configurar Virtual Host no LiteSpeed

No painel de administração do LiteSpeed (http://31.97.254.220:7080):

1. **Virtual Hosts → Add**
   - Virtual Host Name: `webreceptivo`
   - Virtual Host Root: `/usr/local/lsws/Example/html/demo/webReceptivo/`
   - Config File: `$VH_ROOT/conf/vhconf.conf`

2. **General → Context**
   - Type: `WSGI`
   - URI: `/`
   - Location: `/usr/local/lsws/Example/html/demo/webReceptivo/litespeed_wsgi.py`
   - Python WSGI: `application`

3. **General → Static Files Context**
   - URI: `/static/`
   - Location: `/usr/local/lsws/Example/html/demo/webReceptivo/staticfiles/`
   - Accessible: `Yes`

4. **General → Static Files Context (Media)**
   - URI: `/media/`
   - Location: `/usr/local/lsws/Example/html/demo/webReceptivo/media/`
   - Accessible: `Yes`

### 2.3 Configurar domínio
1. **Listeners → Add**
   - Name: `HTTP`
   - IP Address: `31.97.254.220`
   - Port: `80`

2. **Listeners → Add**
   - Name: `HTTPS`
   - IP Address: `31.97.254.220`
   - Port: `443`
   - Secure: `Yes`

3. **Virtual Host Mappings**
   - Virtual Host: `webreceptivo`
   - Domains: `mydevsystem.site, www.mydevsystem.site, 31.97.254.220`

## 3. Configurar Firewall (UFW)
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 7080/tcp  # Painel LiteSpeed (opcional, apenas se necessário)
sudo ufw status
```

## 4. Configurar SSL/HTTPS (Certbot - Let's Encrypt)
```bash
# Instalar certbot
sudo apt update
sudo apt install certbot python3-certbot-apache -y

# Gerar certificado SSL
sudo certbot certonly --webroot -w /usr/local/lsws/Example/html/demo/webReceptivo/staticfiles -d mydevsystem.site -d www.mydevsystem.site

# Certificados serão salvos em:
# /etc/letsencrypt/live/mydevsystem.site/fullchain.pem
# /etc/letsencrypt/live/mydevsystem.site/privkey.pem
```

No painel LiteSpeed, configure o SSL:
1. **Virtual Hosts → webreceptivo → SSL**
   - Private Key File: `/etc/letsencrypt/live/mydevsystem.site/privkey.pem`
   - Certificate File: `/etc/letsencrypt/live/mydevsystem.site/fullchain.pem`
   - Chained Certificate: `Yes`

## 5. Reiniciar LiteSpeed
```bash
sudo /usr/local/lsws/bin/lswsctrl restart
```

## 6. Verificar deployment
- HTTP: http://mydevsystem.site
- HTTPS: https://mydevsystem.site
- Admin: https://mydevsystem.site/admin/

## 7. Comandos úteis para manutenção

### Atualizar código e reiniciar
```bash
cd /usr/local/lsws/Example/html/demo/webReceptivo
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=webreceptivo.settings_production
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production
sudo /usr/local/lsws/bin/lswsctrl restart
```

### Ver logs
```bash
# Logs do LiteSpeed
tail -f /usr/local/lsws/logs/error.log

# Logs do Django (configurar no settings)
tail -f /usr/local/lsws/Example/html/demo/webReceptivo/logs/django.log
```

### Backup do banco de dados
```bash
cp /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3 /root/backups/db_$(date +%Y%m%d_%H%M%S).sqlite3
```

## 8. Checklist pós-deploy
- [ ] Site carrega em http://mydevsystem.site
- [ ] Site carrega em https://mydevsystem.site
- [ ] Admin acessível em /admin/
- [ ] Arquivos estáticos carregam (CSS/JS)
- [ ] Login funciona
- [ ] Auditoria registra ações
- [ ] Configurações da empresa acessíveis
- [ ] SMTP configurado (se necessário)

## Troubleshooting

### Erro 500 - Internal Server Error
```bash
# Ver logs detalhados
tail -f /usr/local/lsws/logs/error.log

# Verificar permissões
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo
```

### Static files não carregam
```bash
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production
sudo /usr/local/lsws/bin/lswsctrl restart
```

### Banco de dados não encontrado
```bash
# Verificar se db.sqlite3 existe
ls -la /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3

# Se não existir, criar:
python manage.py migrate --settings=webreceptivo.settings_production
```
