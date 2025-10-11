#!/bin/bash

# Script de Restauração do Banco de Dados  
# Uso: ./scripts/restore_db.sh caminho/para/backup.sql

if [ $# -eq 0 ]; then
    echo "❌ Erro: Especifique o arquivo de backup"
    echo "📖 Uso: $0 <arquivo_backup.sql>"
    echo "📁 Backups disponíveis:"
    ls -la backups/
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Erro: Arquivo '$BACKUP_FILE' não encontrado"
    exit 1
fi

echo "⚠️  ATENÇÃO: Esta operação irá substituir todos os dados atuais!"
echo "📂 Arquivo: $BACKUP_FILE"
read -p "🤔 Deseja continuar? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Restaurando banco de dados..."
    
    # Parar aplicação
    docker-compose stop web
    
    # Dropar e recriar banco
    docker-compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS webreceptivo;"
    docker-compose exec db psql -U postgres -c "CREATE DATABASE webreceptivo;"
    
    # Restaurar dados
    if [[ $BACKUP_FILE == *.gz ]]; then
        zcat "$BACKUP_FILE" | docker-compose exec -T db psql -U postgres -d webreceptivo
    else
        cat "$BACKUP_FILE" | docker-compose exec -T db psql -U postgres -d webreceptivo
    fi
    
    # Reiniciar aplicação
    docker-compose start web
    
    echo "✅ Restauração concluída!"
else
    echo "❌ Operação cancelada"
fi
