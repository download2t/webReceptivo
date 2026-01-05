#!/bin/bash
# Deploy Manual Rápido para WebReceptivo

set -e

echo "=========================================="
echo "🚀 DEPLOY MANUAL - WEBRECEPTIVO"
echo "=========================================="
echo ""

# PASSO 1
echo "1️⃣  Preparando diretório..."
cd /var/www/webreceptivo
rm -rf .git .gitignore
echo "✓ OK"

# PASSO 2
echo ""
echo "2️⃣  Baixando repositório..."
cd /tmp
wget -q https://github.com/download2t/webReceptivo/archive/refs/heads/main.zip 2>/dev/null || {
    echo "❌ Erro ao baixar. Usando git clone..."
    git clone -q https://github.com/download2t/webReceptivo.git web-temp
    mv web-temp/* /var/www/webreceptivo/
    rm -rf web-temp
}
unzip -q main.zip 2>/dev/null || true
[ -d "webReceptivo-main" ] && mv webReceptivo-main/* /var/www/webreceptivo/ && rm -rf webReceptivo-main
rm -f main.zip
echo "✓ OK"

# PASSO 3
echo ""
echo "3️⃣  Configurando Python..."
cd /var/www/webreceptivo
python3.12 -m venv venv 2>/dev/null || python3 -m venv venv
source venv/bin/activate
pip install --quiet --upgrade pip setuptools wheel 2>/dev/null || true
pip install --quiet -r production_requirements.txt 2>/dev/null || {
    echo "⚠ Instalação com requirements falhou. Instalando pacotes básicos..."
    pip install Django==5.2.7 gunicorn psycopg2-binary whitenoise django-cors-headers
}
echo "✓ OK"

# PASSO 4
echo ""
echo "4️⃣  Criando arquivo .env..."
cat > .env << 'EOF'
DEBUG=0
SECRET_KEY=temporary-key-change-me-to-random-50-chars
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
echo "✓ OK"

# PASSO 5
echo ""
echo "5️⃣  Aplicando migrations..."
source venv/bin/activate
python manage.py migrate --settings=webreceptivo.settings_production --noinput 2>&1 | grep -E "Applying|OK|Running|Creating table" || echo "✓ Migrations executadas"

# PASSO 6
echo ""
echo "6️⃣  Coletando estáticos..."
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production 2>&1 | tail -1
echo "✓ OK"

# PASSO 7
echo ""
echo "7️⃣  Configurando permissões..."
sudo chown -R www-data:www-data /var/www/webreceptivo
sudo chmod -R 755 /var/www/webreceptivo
echo "✓ OK"

# PASSO 8
echo ""
echo "8️⃣  Criando serviço systemd..."
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
echo "✓ OK"

# PASSO 9
echo ""
echo "9️⃣  Iniciando serviço..."
sudo systemctl daemon-reload
sudo systemctl enable webreceptivo 2>/dev/null || true
sudo systemctl restart webreceptivo
sleep 2
echo "✓ OK"

# PASSO 10
echo ""
echo "=========================================="
echo "✅ DEPLOY COMPLETO!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Editar SECRET_KEY:"
echo "   nano /var/www/webreceptivo/.env"
echo ""
echo "2. Ver status:"
echo "   sudo systemctl status webreceptivo"
echo ""
echo "3. Ver logs:"
echo "   sudo journalctl -u webreceptivo -f"
echo ""
echo "4. Testar site (quando DNS propagar):"
echo "   curl https://mydevsystem.site"
echo ""
