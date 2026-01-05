# 🚀 Deploy Manual Rápido (Quando VPS Responder)

Se o deploy automático ficar lento, use este método rápido:

## PASSO 1: Conectar na VPS

```bash
ssh root@31.97.254.220
```

## PASSO 2: Preparar Diretório

```bash
cd /var/www/webreceptivo
rm -rf .git .gitignore
```

## PASSO 3: Download do ZIP do GitHub

```bash
cd /tmp
wget https://github.com/download2t/webReceptivo/archive/refs/heads/main.zip
unzip main.zip
mv webReceptivo-main/* /var/www/webreceptivo/
cd /var/www/webreceptivo
rm -rf /tmp/webReceptivo-main /tmp/main.zip
```

## PASSO 4: Criar Python Venv

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r production_requirements.txt
```

## PASSO 5: Criar Arquivo .env

```bash
cat > .env << 'EOF'
DEBUG=0
SECRET_KEY=seu-secret-key-aqui-50-caracteres-aleatorios
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
EOF
```

### Gerar SECRET_KEY Real:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copie a saída e edite:
```bash
nano .env
```

Procure `SECRET_KEY=seu-secret-key` e mude para a chave gerada.

## PASSO 6: Migrations e Collectstatic

```bash
source venv/bin/activate
python manage.py migrate --settings=webreceptivo.settings_production
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production
```

## PASSO 7: Criar Serviço Systemd

```bash
sudo tee /etc/systemd/system/webreceptivo.service > /dev/null << 'EOF'
[Unit]
Description=WebReceptivo Gunicorn Service
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/webreceptivo
ExecStart=/var/www/webreceptivo/venv/bin/gunicorn \
    --workers 3 \
    --worker-class sync \
    --bind unix:/var/www/webreceptivo/gunicorn.sock \
    --timeout 30 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    webreceptivo.wsgi

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

## PASSO 8: Permissões

```bash
sudo chown -R www-data:www-data /var/www/webreceptivo
sudo chmod -R 755 /var/www/webreceptivo
```

## PASSO 9: Iniciar Serviço

```bash
sudo systemctl daemon-reload
sudo systemctl enable webreceptivo
sudo systemctl start webreceptivo
sudo systemctl status webreceptivo
```

## PASSO 10: Verificar

```bash
curl http://localhost:8000/
# Deve retornar HTML do site

sudo journalctl -u webreceptivo -f
# Ver logs em tempo real
```

## PASSO 11: Testar HTTPS (depois que DNS propagar)

```bash
curl -I https://mydevsystem.site
# Deve retornar 200 OK
```

---

## ⏱️ Tempo Total: ~5 minutos

Se tudo funcionar, seu site estará online quando o DNS propagar!

