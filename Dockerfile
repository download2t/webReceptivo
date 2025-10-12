# Use uma imagem base do Python
FROM python:3.12-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-openbsd \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria diretórios para media files
RUN mkdir -p /app/media/avatars \
    && mkdir -p /app/staticfiles

# Torna o script de entrada executável
RUN chmod +x entrypoint.sh

# Cria um usuário não-root para executar a aplicação
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expõe a porta 8000
EXPOSE 8000

# Define o script de entrada
ENTRYPOINT ["./entrypoint.sh"]

# Comando para executar a aplicação
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
