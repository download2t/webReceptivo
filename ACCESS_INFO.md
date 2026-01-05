# 🎯 INFORMAÇÕES DE ACESSO - mydevsystem.site

## 📌 Credenciais VPS

```
IP:              31.97.254.220
Provedor:        Hostinger
Usuario:         root
```

### Como conectar:

```bash
ssh root@31.97.254.220
# Digite a senha de root
```

---

## 💻 Aplicação Django

```
Diretório:       /var/www/webreceptivo
Venv:            /var/www/webreceptivo/venv
Arquivo .env:    /var/www/webreceptivo/.env
Database:        PostgreSQL (webreceptivo_prod)
```

### Iniciar Django:

```bash
cd /var/www/webreceptivo
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000 --settings=webreceptivo.settings_production
```

### Ver Logs:

```bash
sudo journalctl -u webreceptivo -f
```

---

## 🌐 Domínio & Cloudflare

```
Domínio:         mydevsystem.site
Cloudflare:      Configurado
Nameservers:     ns1.cloudflare.com, ns2.cloudflare.com
Status DNS:      ⏳ Aguardando propagação
```

### Test DNS:

```bash
nslookup mydevsystem.site
dig mydevsystem.site
```

---

## 🔐 Arquivo .env Exemplo

Localização: `/var/www/webreceptivo/.env`

```ini
DEBUG=0
SECRET_KEY=your-secret-key-50-chars-here
ALLOWED_HOSTS=mydevsystem.site,www.mydevsystem.site,31.97.254.220
DATABASE_URL=postgres://webreceptivo:webreceptivo@localhost:5432/webreceptivo_prod
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-app-password
DEFAULT_FROM_EMAIL=noreply@mydevsystem.site
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Gerar SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 📊 Serviços Rodando

```
Nginx:           Port 80, 443 (reverse proxy)
Gunicorn:        Unix socket /var/www/webreceptivo/gunicorn.sock
PostgreSQL:      Port 5432 (localhost)
Supervisor:      Process manager
Fail2Ban:        Brute force protection
```

### Ver Status:

```bash
sudo systemctl status webreceptivo
sudo systemctl status nginx
sudo systemctl status postgresql
```

### Reiniciar:

```bash
sudo systemctl restart webreceptivo  # Django/Gunicorn
sudo systemctl restart nginx         # Web Server
sudo systemctl restart postgresql    # Database
```

---

## 📈 URLs do Site

```
HTTP:            http://31.97.254.220
HTTPS:           https://31.97.254.220
Domínio HTTP:    http://mydevsystem.site (após DNS propagar)
Domínio HTTPS:   https://mydevsystem.site (após SSL)
Admin:           https://mydevsystem.site/admin
```

### Login Admin:

```
Usuário:  admin
Senha:    admin123  (⚠️ MUDE APÓS PRIMEIRO LOGIN)
```

---

## 🔧 Comandos Úteis

### Django

```bash
# Migrations
python manage.py migrate --settings=webreceptivo.settings_production

# Collectstatic
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production

# Criar superuser
python manage.py createsuperuser --settings=webreceptivo.settings_production

# Shell Django
python manage.py shell --settings=webreceptivo.settings_production
```

### Database

```bash
# Conectar ao PostgreSQL
psql -U webreceptivo -d webreceptivo_prod

# Ver tabelas
\dt

# Sair
\q
```

### Nginx

```bash
# Ver config
cat /etc/nginx/sites-available/webreceptivo

# Testar config
sudo nginx -t

# Ver logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 📋 Checklist de Próximas Etapas

- [ ] VPS respondendo
- [ ] Migrations executadas
- [ ] Estáticos coletados
- [ ] Serviço systemd criado
- [ ] Gunicorn rodando
- [ ] Testar via curl localhost:8000
- [ ] Testar via curl https://31.97.254.220
- [ ] DNS propagado
- [ ] Testar via https://mydevsystem.site
- [ ] Mudar senha admin
- [ ] Configurar email real
- [ ] Fazer backup inicial

---

## 🆘 Troubleshooting Rápido

### VPS não responde SSH
```bash
# Verifique painel Hostinger - VPS pode estar reiniciando
# Aguarde 5-10 minutos
```

### Django não inicia
```bash
# Ver erro
sudo journalctl -u webreceptivo -n 50

# Reiniciar
sudo systemctl restart webreceptivo
```

### PostgreSQL erro
```bash
# Verificar status
sudo systemctl status postgresql

# Ver logs
sudo tail -f /var/log/postgresql/postgresql.log
```

### Nginx 502
```bash
# Verificar socket
ls -lah /var/www/webreceptivo/gunicorn.sock

# Reiniciar Gunicorn
sudo systemctl restart webreceptivo
```

### DNS não funciona
```bash
# Verificar registros
nslookup mydevsystem.site @ns1.cloudflare.com

# Propagar pode levar até 48h
```

---

## 📞 Suporte

Documentação disponível no GitHub:
- CLOUDFLARE_QUICK_START.md
- DEPLOYMENT_PROGRESS.md
- DEPLOY_GUIDE.md
- SECURITY.md

---

**Status:** 🟡 Deployment em progresso  
**Próximo:** Aguardar VPS responder e completar migrations  
**ETA:** ~45 minutos para site online

