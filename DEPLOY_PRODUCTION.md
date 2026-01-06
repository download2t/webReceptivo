# 📘 Guia Completo de Deploy - WebReceptivo

**IP:** 31.97.254.220  
**Domínio:** mydevsystem.site  
**Web Server:** LiteSpeed 1.8.4  
**Framework:** Django 5.2.7 + Python 3.12

---

## 🚀 SETUP INICIAL COMPLETO (PRIMEIRA VEZ)

Execute **na sequência exata** para montar o servidor do zero:

### Passo 1: Conectar via SSH

```bash
ssh root@31.97.254.220
```

### Passo 2: Clonar repositório

```bash
cd /usr/local/lsws/Example/html/demo/
git clone https://github.com/download2t/webReceptivo.git
cd webReceptivo
```

### Passo 3: Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 4: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 5: Gerar SECRET_KEY

```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Copie a saída (exemplo: abc123xyz...)
```

### Passo 6: Criar arquivo .env

```bash
cat > .env << 'EOF'
SECRET_KEY=COLE-AQUI-A-CHAVE-GERADA-NO-PASSO-5
DEBUG=False
ALLOWED_HOSTS=31.97.254.220,mydevsystem.site,www.mydevsystem.site
DATABASE_URL=
EOF
```

Verificar:
```bash
cat .env
```

### Passo 7: Aplicar migrações

```bash
python manage.py migrate --settings=webreceptivo.settings_production
```

### Passo 8: Criar superusuário

```bash
python manage.py createsuperuser --settings=webreceptivo.settings_production

# Responder:
# Username: admin
# Email: seu@email.com
# Password: [sua senha segura]
```

### Passo 9: Criar grupos de permissões

```bash
python manage.py criar_grupos --settings=webreceptivo.settings_production
python manage.py setup_groups --settings=webreceptivo.settings_production
```

### Passo 10: Coletar arquivos estáticos

```bash
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production
```

### Passo 11: Criar arquivo WSGI para LiteSpeed

```bash
cat > litespeed_wsgi.py << 'EOF'
import sys
import os

sys.path.insert(0, '/usr/local/lsws/Example/html/demo/webReceptivo')
os.environ['DJANGO_SETTINGS_MODULE'] = 'webreceptivo.settings_production'

from webreceptivo.wsgi_production import application
EOF
```

### Passo 12: Configurar permissões do projeto

```bash
# Dar permissões corretas para LiteSpeed servir os arquivos
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/

# Permissões específicas para banco de dados
chmod 666 /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3

# Permissões para media (uploads)
chmod -R 777 /usr/local/lsws/Example/html/demo/webReceptivo/media/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/media/

# Permissões para staticfiles
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/staticfiles/
chown -R nobody:nogroup /usr/local/lsws/Example/html/demo/webReceptivo/staticfiles/
```

### Passo 13: Configurar LiteSpeed vhost

```bash
# Editar arquivo de configuração
nano /usr/local/lsws/conf/vhosts/Example/vhconf.conf
```

**Substituir todo o conteúdo por:**

```
docRoot                   $VH_ROOT/html/demo/webReceptivo/

enableGzip                1

errorlog $VH_ROOT/logs/error.log {
  useServer               1
  logLevel                DEBUG
  rollingSize             10M
}

accesslog $VH_ROOT/logs/access.log {
  useServer               0
  rollingSize             10M
  keepDays                7
  compressArchive         0
}

index  {
  useServer               0
  indexFiles              index.html, index.php
  autoIndex               0
  autoIndexURI            /_autoindex/default.php
}

errorpage 404 {
  url                     /error404.html
}

expires  {
  enableExpires           1
}

accessControl  {
  allow                   *
}

context /.well-known/ {
  location                /usr/local/lsws/Example/html/.well-known/
  allowBrowse             1
  addDefaultCharset       off
}

context /static/ {
  type                    null
  location                /usr/local/lsws/Example/html/demo/webReceptivo/staticfiles/
  allowBrowse             1
  addDefaultCharset       off
}

context /media/ {
  type                    null
  location                /usr/local/lsws/Example/html/demo/webReceptivo/media/
  allowBrowse             1
  addDefaultCharset       off
}

context / {
  type                    appserver
  location                /usr/local/lsws/Example/html/demo/webReceptivo/
  binPath                 /usr/local/lsws/fcgi-bin/lswsgi
  appType                 wsgi
  startupFile             litespeed_wsgi.py
  env                     PYTHONPATH=/usr/local/lsws/Example/html/demo/webReceptivo:/usr/local/lsws/Example/html/demo/webReceptivo/venv/lib/python3.12/site-packages
  env                     LS_PYTHONBIN=/usr/local/lsws/Example/html/demo/venv/bin/python
  addDefaultCharset       off
}

rewrite  {
  enable                  1
  autoLoadHtaccess        1
  logLevel                0
}
```

**Salvar:** `CTRL+X` → `Y` → `ENTER`

### Passo 14: Remover arquivo HTML padrão

```bash
mv /usr/local/lsws/Example/html/index.html /usr/local/lsws/Example/html/index.html.bak 2>/dev/null
```

### Passo 15: Iniciar LiteSpeed

```bash
sudo /usr/local/lsws/bin/lswsctrl start
```

### Passo 16: Verificar status

```bash
sudo /usr/local/lsws/bin/lswsctrl status

# Resultado esperado:
# [OK] LiteSpeed Web Server is running with PID XXXX
```

### Passo 17: Testar acesso

```bash
# Testar via IP
curl -I http://31.97.254.220/admin/

# Testar via domínio
curl -I http://mydevsystem.site/admin/

# Resultado esperado: HTTP/1.1 200 OK (ou redirecionado para login)
```

### Passo 18: Acessar no navegador

Abrir: `http://mydevsystem.site/admin/`

**Login:**
- Username: `admin`
- Password: [a senha que criou no Passo 8]

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
