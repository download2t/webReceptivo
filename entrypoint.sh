#!/bin/bash

# Função para esperar o banco de dados ficar disponível
wait_for_db() {
    echo "Aguardando o banco de dados ficar disponível..."
    
    # Tentar usar nc se disponível, senão usar Python
    if command -v nc >/dev/null 2>&1; then
        until nc -z db 5432; do
            echo "Banco de dados não está pronto ainda. Aguardando..."
            sleep 1
        done
    else
        # Usar Python como alternativa
        until python -c "
import socket
import sys
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('db', 5432))
    sock.close()
    if result != 0:
        sys.exit(1)
except:
    sys.exit(1)
" 2>/dev/null; do
            echo "Banco de dados não está pronto ainda. Aguardando..."
            sleep 1
        done
    fi
    
    echo "PostgreSQL porta está aberta!"
    
    # Aguardar mais um pouco para o banco estar completamente pronto
    echo "Aguardando PostgreSQL estar completamente pronto..."
    sleep 3
    echo "Banco de dados deve estar disponível agora!"
}

# Chamar a função para aguardar o banco
wait_for_db

# Executar migrações
echo "Executando migrações do banco de dados..."
python manage.py migrate

# Coletar arquivos estáticos em produção
if [ "$DEBUG" = "0" ]; then
    echo "Coletando arquivos estáticos..."
    python manage.py collectstatic --noinput
fi

# Executar o comando passado como argumento
exec "$@"
