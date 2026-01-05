#!/bin/bash
# 🚀 Deploy Alternativo Mais Leve
# Usar se deploy_vps.sh ficar muito lento

set -e

echo "=================================================="
echo "🚀 DEPLOY WEBRECEPTIVO - VERSÃO LEVE"
echo "=================================================="
echo ""

# 1. Diretório base
WEBRECEPTIVO_DIR="/var/www/webreceptivo"
mkdir -p $WEBRECEPTIVO_DIR
cd $WEBRECEPTIVO_DIR

# 2. Se já existe git, atualizar
if [ -d ".git" ]; then
    echo "✓ Repositório já existe. Atualizando..."
    git pull origin main
else
    echo "✓ Clonando repositório..."
    cd /tmp
    git clone https://github.com/download2t/webReceptivo.git .webreceptivo-temp
    mv .webreceptivo-temp/* $WEBRECEPTIVO_DIR/
    cd $WEBRECEPTIVO_DIR
fi

echo ""
echo "=================================================="
echo "2. Preparando Python e venv"
echo "=================================================="

# Criar venv se não existir
if [ ! -d "venv" ]; then
    python3.12 -m venv venv
fi

source venv/bin/activate

# 3. Instalar dependências (já feito no deploy_vps.sh, pular se venv ativo)
if ! pip show gunicorn >/dev/null 2>&1; then
    echo "✓ Instalando dependências..."
    pip install --no-cache-dir -r production_requirements.txt
fi

echo ""
echo "=================================================="
echo "3. Configurando Django"
echo "=================================================="

# Migrations
echo "✓ Aplicando migrations..."
python manage.py migrate --settings=webreceptivo.settings_production || echo "⚠ Migrations podem ter falhado"

# Collectstatic
echo "✓ Coletando estáticos..."
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production

echo ""
echo "=================================================="
echo "4. Verificando arquivo .env"
echo "=================================================="

if [ ! -f ".env" ]; then
    echo "✓ Criando arquivo .env..."
    cat > .env << 'EOF'
DEBUG=0
SECRET_KEY=change-me-to-random-string-of-50-chars
ALLOWED_HOSTS=localhost,127.0.0.1,31.97.254.220,mydevsystem.site,www.mydevsystem.site
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
    echo "⚠  Arquivo .env criado. MUDE os valores reais!"
else
    echo "✓ Arquivo .env já existe"
fi

echo ""
echo "=================================================="
echo "5. Configurando Systemd Service"
echo "=================================================="

if [ ! -f "/etc/systemd/system/webreceptivo.service" ]; then
    echo "✓ Criando serviço systemd..."
    sudo tee /etc/systemd/system/webreceptivo.service > /dev/null << EOF
[Unit]
Description=WebReceptivo Gunicorn Service
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=$WEBRECEPTIVO_DIR
ExecStart=$WEBRECEPTIVO_DIR/venv/bin/gunicorn \
    --workers 3 \
    --worker-class sync \
    --bind unix:$WEBRECEPTIVO_DIR/gunicorn.sock \
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
    
    sudo systemctl daemon-reload
    sudo systemctl enable webreceptivo
else
    echo "✓ Serviço já existe"
fi

echo ""
echo "=================================================="
echo "6. Iniciando Serviço"
echo "=================================================="

sudo systemctl restart webreceptivo
sudo systemctl status webreceptivo --no-pager

echo ""
echo "=================================================="
echo "✅ DEPLOY COMPLETO!"
echo "=================================================="
echo ""
echo "Próximas etapas:"
echo "1. Editar .env com valores reais:"
echo "   sudo nano /var/www/webreceptivo/.env"
echo ""
echo "2. Gerar SECRET_KEY:"
echo "   python3 -c \"import secrets; print(secrets.token_urlsafe(50))\""
echo ""
echo "3. Verificar status:"
echo "   sudo systemctl status webreceptivo"
echo ""
echo "4. Ver logs:"
echo "   sudo journalctl -u webreceptivo -f"
echo ""
