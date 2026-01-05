#!/bin/bash

# ================================================
# SCRIPT DE DEPLOY WEBRECEPTIVO EM VPS
# Otimizado para 1GB RAM
# ================================================

set -e  # Exit on error

echo "=================================================="
echo "🚀 DEPLOY WEBRECEPTIVO - VPS 1GB"
echo "=================================================="

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ===== 1. PREPARAR AMBIENTE =====
echo -e "${YELLOW}1. Preparando ambiente...${NC}"

# Update sistema
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx supervisor

# Criar diretório do projeto
PROJECT_DIR="/var/www/webreceptivo"
sudo mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

echo -e "${GREEN}✅ Ambiente preparado${NC}"

# ===== 2. CLONAR REPOSITÓRIO =====
echo -e "${YELLOW}2. Clonando repositório...${NC}"

if [ -d ".git" ]; then
    git pull origin main
else
    git clone https://github.com/seu-usuario/webreceptivo.git .
fi

echo -e "${GREEN}✅ Repositório atualizado${NC}"

# ===== 3. CONFIGURAR PYTHON =====
echo -e "${YELLOW}3. Configurando Python virtual environment...${NC}"

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r production_requirements.txt

echo -e "${GREEN}✅ Dependências instaladas${NC}"

# ===== 4. CONFIGURAR DATABASE =====
echo -e "${YELLOW}4. Configurando PostgreSQL...${NC}"

sudo -u postgres psql << EOF
CREATE USER webreceptivo WITH PASSWORD 'SENHA_FORTE_AQUI';
CREATE DATABASE webreceptivo_prod OWNER webreceptivo;
ALTER ROLE webreceptivo SET client_encoding TO 'utf8';
ALTER ROLE webreceptivo SET default_transaction_isolation TO 'read committed';
ALTER ROLE webreceptivo SET default_transaction_deferrable TO on;
ALTER ROLE webreceptivo SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE webreceptivo_prod TO webreceptivo;
EOF

echo -e "${GREEN}✅ PostgreSQL configurado${NC}"

# ===== 5. CONFIGURAR .env =====
echo -e "${YELLOW}5. Configurando arquivo .env...${NC}"

cp .env.production .env
echo "Edite .env com suas configurações reais!"

echo -e "${GREEN}✅ .env criado (EDITE AGORA!)${NC}"

# ===== 6. APLICAR MIGRATIONS =====
echo -e "${YELLOW}6. Aplicando migrations...${NC}"

export DJANGO_SETTINGS_MODULE=webreceptivo.settings_production
python manage.py migrate

echo -e "${GREEN}✅ Migrations aplicadas${NC}"

# ===== 7. COLLECTSTATIC =====
echo -e "${YELLOW}7. Coletando arquivos estáticos...${NC}"

python manage.py collectstatic --noinput

echo -e "${GREEN}✅ Arquivos estáticos coletados${NC}"

# ===== 8. CRIAR SUPERUSER (se não existir) =====
echo -e "${YELLOW}8. Criando superuser...${NC}"

python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@webreceptivo.com', 'SENHA_AQUI')
    print("Superuser criado!")
else:
    print("Superuser já existe")
EOF

echo -e "${GREEN}✅ Superuser configurado${NC}"

# ===== 9. CONFIGURAR GUNICORN =====
echo -e "${YELLOW}9. Configurando Gunicorn...${NC}"

sudo tee /etc/systemd/system/webreceptivo.service > /dev/null <<EOF
[Unit]
Description=WebReceptivo Gunicorn Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
    --workers 3 \\
    --worker-class sync \\
    --worker-connections 1000 \\
    --max-requests 1000 \\
    --max-requests-jitter 50 \\
    --timeout 30 \\
    --bind unix:$PROJECT_DIR/webreceptivo.sock \\
    webreceptivo.wsgi:application

Restart=always
RestartSec=10

# Limites de memória
MemoryLimit=512M

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable webreceptivo
sudo systemctl start webreceptivo

echo -e "${GREEN}✅ Gunicorn configurado${NC}"

# ===== 10. CONFIGURAR NGINX =====
echo -e "${YELLOW}10. Configurando Nginx...${NC}"

sudo tee /etc/nginx/sites-available/webreceptivo > /dev/null <<EOF
server {
    listen 80;
    server_name seu-dominio.com.br www.seu-dominio.com.br;

    client_max_body_size 5M;

    # Redirecionar HTTP para HTTPS (descomentar após SSL)
    # return 301 https://$server_name$request_uri;

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/webreceptivo.sock;
        
        # Timeouts otimizados para 1GB RAM
        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/json application/javascript;
    gzip_min_length 1000;
}
EOF

sudo ln -sf /etc/nginx/sites-available/webreceptivo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo -e "${GREEN}✅ Nginx configurado${NC}"

# ===== 11. CONFIGURAR CERTBOT (SSL) =====
echo -e "${YELLOW}11. Configurando SSL com Certbot...${NC}"

sudo apt install -y certbot python3-certbot-nginx

# Descomentar quando domínio estiver pronto
# sudo certbot --nginx -d seu-dominio.com.br -d www.seu-dominio.com.br

echo -e "${GREEN}✅ Certbot instalado (configure depois)${NC}"

# ===== 12. CONFIGURAR LOGS =====
echo -e "${YELLOW}12. Configurando logs...${NC}"

mkdir -p $PROJECT_DIR/logs
sudo chown www-data:www-data $PROJECT_DIR/logs

echo -e "${GREEN}✅ Logs configurados${NC}"

# ===== 13. CRIAR SCRIPT DE MONITORAMENTO =====
echo -e "${YELLOW}13. Criando script de monitoramento...${NC}"

sudo tee /usr/local/bin/monitor_webreceptivo.sh > /dev/null <<'MONITOR'
#!/bin/bash
# Script de monitoramento

while true; do
    RAM_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
    DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}')
    
    echo "[$(date)] RAM: ${RAM_USAGE}% | DISK: ${DISK_USAGE}"
    
    # Se RAM > 90%, reiniciar serviço
    if (( $(echo "$RAM_USAGE > 90" | bc -l) )); then
        echo "⚠️  ALERTA: RAM acima de 90%!"
        systemctl restart webreceptivo
    fi
    
    sleep 300  # A cada 5 minutos
done
MONITOR

sudo chmod +x /usr/local/bin/monitor_webreceptivo.sh

echo -e "${GREEN}✅ Monitoramento configurado${NC}"

# ===== RESUMO FINAL =====
echo ""
echo -e "${GREEN}=================================================="
echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "==================================================${NC}"
echo ""
echo "📝 PRÓXIMOS PASSOS:"
echo "1. Edite .env com suas configurações reais"
echo "2. Configure SSL: sudo certbot --nginx"
echo "3. Inicie monitoramento: sudo /usr/local/bin/monitor_webreceptivo.sh &"
echo "4. Acesse: http://seu-dominio.com.br"
echo ""
echo "📊 STATUS:"
echo "  Gunicorn: sudo systemctl status webreceptivo"
echo "  Nginx: sudo systemctl status nginx"
echo "  PostgreSQL: sudo systemctl status postgresql"
echo ""
echo "📋 LOGS:"
echo "  Django: tail -f $PROJECT_DIR/logs/django.log"
echo "  Nginx: sudo tail -f /var/log/nginx/error.log"
echo "  Gunicorn: sudo journalctl -u webreceptivo -f"
echo ""
