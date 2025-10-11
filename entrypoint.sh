#!/bin/bash

# Função para esperar o banco de dados ficar disponível
wait_for_db() {
    echo "Aguardando o banco de dados ficar disponível..."
    while ! python manage.py dbshell --command="SELECT 1" > /dev/null 2>&1; do
        echo "Banco de dados não está pronto ainda. Aguardando..."
        sleep 1
    done
    echo "Banco de dados está disponível!"
}

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
