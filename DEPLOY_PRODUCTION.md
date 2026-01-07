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
python manage_production.py criar_grupos
python manage_production.py setup_groups
```

### Passo 10: Criar categorias padrão

```bash
python manage_production.py criar_categorias
```

**Categorias criadas:**
- Atrativos
- Hospedagem
- Transporte
- Alimentação
- Passeios
- Eventos
- Outros

### Passo 11: Criar tipos de meia entrada padrão

```bash
python manage_production.py criar_tipos_meia_entrada
```

**Tipos criados:**
- PCD (Pessoa com Deficiência)
- DOADOR DE SANGUE
- IDOSO
- ESTUDANTE BR
- ESTUDANTE BR COM CARTEIRINHA
- PROFESSOR BR
- POLICIAL BR
- ACOMPANHANTE DE PCD
- PESSOA COM CANCER
- CRIANÇA
- ADOLESCENTE
- JOVEM

### Passo 12: Importar serviços iniciais (Foz do Iguaçu)

```bash
python manage_production.py importar_servicos_foz
```

**Serviços importados (31 atrativos):**
- Parque das Aves
- Itaipu Panorâmica / Especial / Iluminada
- Refúgio Biológico
- Marco das Três Fronteiras
- Dreamland (diversos combos)
- Shows e atrações
- E muito mais...

**Nota:** Os serviços serão vinculados à categoria "Atrativos" criada no Passo 10.

### Passo 13: Coletar arquivos estáticos

```bash
python manage_production.py collectstatic --noinput
```

### Passo 14: Criar arquivo WSGI para LiteSpeed

```bash
cat > litespeed_wsgi.py << 'EOF'
import sys
import os

sys.path.insert(0, '/usr/local/lsws/Example/html/demo/webReceptivo')
os.environ['DJANGO_SETTINGS_MODULE'] = 'webreceptivo.settings_production'

from webreceptivo.wsgi_production import application
EOF
```

### Passo 15: Configurar permissões do projeto

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

### Passo 16: Configurar LiteSpeed vhost

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

### Passo 17: Remover arquivo HTML padrão

```bash
mv /usr/local/lsws/Example/html/index.html /usr/local/lsws/Example/html/index.html.bak 2>/dev/null
```

### Passo 18: Iniciar LiteSpeed

```bash
sudo /usr/local/lsws/bin/lswsctrl start
```

### Passo 19: Verificar status

```bash
sudo /usr/local/lsws/bin/lswsctrl status

# Resultado esperado:
# [OK] LiteSpeed Web Server is running with PID XXXX
```

### Passo 20: Testar acesso

```bash
# Testar via IP
curl -I http://31.97.254.220/admin/

# Testar via domínio
curl -I http://mydevsystem.site/admin/

# Resultado esperado: HTTP/1.1 200 OK (ou redirecionado para login)
```

### Passo 21: Acessar no navegador

Abrir: `http://mydevsystem.site/admin/`

**Login:**
- Username: `admin`
- Password: [a senha que criou no Passo 8]

---

## 👥 SISTEMA DE PERMISSÕES E GRUPOS

O sistema possui 4 níveis de acesso:

### 🔷 Administradores (Controle Total)
- ✅ Gerenciar usuários e grupos
- ✅ CRUD completo de TUDO (categorias, serviços, transfers, tipos meia, ordens)

### 🔶 Gerentes (Gestão Operacional)
- ✅ Criar e editar usuários (não pode gerenciar grupos)
- ✅ CRUD completo de categorias, serviços, transfers, tipos meia, ordens

### 🔹 Operadores (Foco em Ordens de Serviço)
- ✅ CRUD completo de Ordens de Serviço
- 👁️ Apenas VISUALIZAR: categorias, serviços, transfers, tipos meia
- ❌ NÃO pode editar ou excluir cadastros
- ❌ NÃO pode acessar área de usuários (`/users/` retorna 403 Forbidden)

### 🔘 Usuários Básicos (Apenas Consulta)
- 👁️ Apenas VISUALIZAR: serviços e ordens de serviço
- ❌ NÃO pode criar, editar ou excluir NADA

**Ver detalhes completos:** [docs/GUIA_GRUPOS.md](docs/GUIA_GRUPOS.md)

**Atualizar permissões:**
```bash
python manage_production.py setup_groups
```

---

## 📦 ATUALIZAR APLICAÇÃO (Deploy de Novas Alterações)

Sempre que houver alterações no código, execute os comandos na sequência:

```bash
# 1. Conectar no servidor
ssh root@31.97.254.220

# 2. Navegar para o diretório do projeto
cd /usr/local/lsws/Example/html/demo/webReceptivo

# 3. Ativar ambiente virtual
source venv/bin/activate

# 4. Atualizar código do repositório
git pull origin main

# 5. Instalar novas dependências (se houver)
pip install -r requirements.txt

# 6. Aplicar migrações do banco
python manage_production.py migrate

# 7. Coletar arquivos estáticos
python manage_production.py collectstatic --noinput

# 8. Reiniciar LiteSpeed
sudo /usr/local/lsws/bin/lswsctrl restart
```

**Comando único (copiar e colar):**
```bash
cd /usr/local/lsws/Example/html/demo/webReceptivo && source venv/bin/activate && git pull origin main && pip install -r requirements.txt && python manage_production.py migrate && python manage_production.py collectstatic --noinput && sudo /usr/local/lsws/bin/lswsctrl restart
```

---

## 🔧 COMANDOS ÚTEIS DE GERENCIAMENTO

### Criar dados iniciais em novo ambiente

```bash
# Categorias padrão
python manage_production.py criar_categorias

# Tipos de meia entrada
python manage_production.py criar_tipos_meia_entrada

# Importar serviços de Foz do Iguaçu
python manage_production.py importar_servicos_foz

# Criar grupos de permissões
python manage_production.py setup_groups
```

**Ordem recomendada para setup inicial completo:**
1. `criar_categorias` - Cria categorias (Atrativos, Hospedagem, etc.)
2. `criar_tipos_meia_entrada` - Cria tipos de meia entrada (PCD, Idoso, etc.)
3. `importar_servicos_foz` - Importa 31 serviços de Foz vinculados à categoria "Atrativos"
4. `setup_groups` - Configura permissões de grupos

### Ver logs do sistema

```bash
# Logs do LiteSpeed
tail -f /usr/local/lsws/logs/error.log

# Logs de acesso
tail -f /usr/local/lsws/Example/logs/access.log
```

### Gerenciar LiteSpeed

```bash
# Status
sudo /usr/local/lsws/bin/lswsctrl status

# Iniciar
sudo /usr/local/lsws/bin/lswsctrl start

# Parar
sudo /usr/local/lsws/bin/lswsctrl stop

# Reiniciar
sudo /usr/local/lsws/bin/lswsctrl restart

# Recarregar configuração (sem downtime)
sudo /usr/local/lsws/bin/lswsctrl reload
```

### Backup do banco de dados

```bash
# Criar backup
cp /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3 /root/backups/db_$(date +%Y%m%d_%H%M%S).sqlite3

# Listar backups
ls -lh /root/backups/

# Restaurar backup
cp /root/backups/db_YYYYMMDD_HHMMSS.sqlite3 /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3
chmod 666 /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3
sudo /usr/local/lsws/bin/lswsctrl restart
```

### Gerenciar ambiente virtual

```bash
# Ativar
source /usr/local/lsws/Example/html/demo/webReceptivo/venv/bin/activate

# Desativar
deactivate

# Ver pacotes instalados
pip list

# Atualizar pip
pip install --upgrade pip
```

---

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
