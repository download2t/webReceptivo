#!/bin/bash

# ================================================
# SCRIPT DE BACKUP - WebReceptivo
# Faz backup de BD, arquivos e código
# ================================================

PROJECT_DIR="/var/www/webreceptivo"
BACKUP_DIR="/var/backups/webreceptivo"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="webreceptivo_backup_$DATE.tar.gz"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "=================================================="
echo "🔄 INICIANDO BACKUP"
echo "=================================================="

# Criar diretório de backup
sudo mkdir -p $BACKUP_DIR
cd $BACKUP_DIR

# ===== BACKUP DATABASE =====
echo "📦 Fazendo backup do banco de dados..."
sudo -u postgres pg_dump webreceptivo_prod | gzip > webreceptivo_db_$DATE.sql.gz

# ===== BACKUP FILES =====
echo "📦 Fazendo backup dos arquivos..."
sudo tar -czf $BACKUP_FILE \
    -C $PROJECT_DIR \
    --exclude=venv \
    --exclude=.git \
    --exclude=__pycache__ \
    --exclude=.pytest_cache \
    --exclude=.env \
    static/ media/ logs/

# ===== PERMISSÕES =====
sudo chown postgres:postgres $BACKUP_DIR/*
sudo chmod 600 $BACKUP_DIR/*

# ===== TAMANHOS =====
echo ""
echo "=== RESUMO DO BACKUP ==="
du -sh $BACKUP_DIR/*

# ===== LIMPEZA (manter últimos 7 dias) =====
echo ""
echo "🧹 Removendo backups com mais de 7 dias..."
find $BACKUP_DIR -name "webreceptivo_*" -mtime +7 -delete

echo ""
echo -e "${GREEN}✅ BACKUP CONCLUÍDO!${NC}"
echo ""
echo "📍 Local: $BACKUP_DIR"
echo "📝 Arquivo: $BACKUP_FILE"
echo ""
