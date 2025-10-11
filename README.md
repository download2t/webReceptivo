# WebReceptivo

Um sistema web desenvolvido em Django para gestão receptiva.

## Configuração do Ambiente

### Pré-requisitos
- Python 3.12+
- Git
- Docker e Docker Compose (para execução em containers)

### Instalação Local

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd WebReceptivo
```

2. Crie um ambiente virtual:
```bash
python -m venv .venv
```

3. Ative o ambiente virtual:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Execute as migrações do banco de dados:
```bash
python manage.py migrate
```

6. Crie um superusuário (opcional):
```bash
python manage.py createsuperuser
```

7. Execute o servidor de desenvolvimento:
```bash
python manage.py runserver
```

O sistema estará disponível em `http://127.0.0.1:8000/`

### Instalação com Docker

**Certifique-se de que o Docker Desktop está executando antes de continuar.**

#### Desenvolvimento
```bash
# Construir e executar os containers
docker-compose up --build

# Executar em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar os containers
docker-compose down
```

#### Produção
```bash
# Executar em produção
docker-compose -f docker-compose.prod.yml up --build -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Parar os containers
docker-compose -f docker-compose.prod.yml down
```

O sistema estará disponível em:
- **Desenvolvimento**: `http://localhost:8000`
- **Produção**: `http://localhost` (porta 80)

### Comandos Docker Úteis

```bash
# Executar comandos Django no container
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic

# Acessar o shell do container
docker-compose exec web bash

# Reconstruir apenas um serviço
docker-compose up --build web

# Ver logs de um serviço específico
docker-compose logs -f web

# Limpar volumes (cuidado - remove dados do banco)
docker-compose down -v
```

## Estrutura do Projeto

```
WebReceptivo/
├── manage.py
├── webreceptivo/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
├── .gitignore
├── .dockerignore
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── nginx.conf
├── entrypoint.sh
└── README.md
```

## Desenvolvimento

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT.
