# Use uma imagem base do Python 3.12
FROM python:3.12-slim

# Define variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    netcat-openbsd \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    zlib1g-dev \
    libpcsclite-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria diretórios para media files e static files
RUN mkdir -p /app/media/avatars \
    && mkdir -p /app/staticfiles \
    && mkdir -p /app/backups

# Torna o script de entrada executável
RUN chmod +x entrypoint.sh || echo "entrypoint.sh não encontrado, usando comando padrão"

# Cria um usuário não-root para executar a aplicação
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

# Define permissões adequadas
RUN chmod -R 755 /app

USER app

# Expõe a porta 8000
EXPOSE 8000

# Comando padrão
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
