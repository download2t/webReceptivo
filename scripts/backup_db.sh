#!/bin/bash

# Script de Backup do Banco de Dados
# Uso: ./scripts/backup_db.sh

# Criar diretório de backups se não existir
mkdir -p backups

# Nome do arquivo com timestamp
BACKUP_FILE="backups/webreceptivo_backup_$(date +%Y%m%d_%H%M%S).sql"

# Fazer backup
docker-compose exec -T db pg_dump -U postgres -d webreceptivo > "$BACKUP_FILE"

# Compactar backup
gzip "$BACKUP_FILE"

echo "✅ Backup criado: ${BACKUP_FILE}.gz"
echo "📁 Localização: $(pwd)/${BACKUP_FILE}.gz"

# Manter apenas os 10 backups mais recentes
ls -t backups/webreceptivo_backup_*.sql.gz | tail -n +11 | xargs -r rm

echo "🧹 Backups antigos removidos (mantidos os 10 mais recentes)"
