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

> **🚀 Melhorias Implementadas**: O entrypoint foi otimizado para aguardar automaticamente o PostgreSQL estar disponível antes de executar migrações, eliminando erros de conexão durante o startup.

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

## Melhorias Técnicas

### Entrypoint Inteligente
O arquivo `entrypoint.sh` foi aprimorado com:

- **🔍 Verificação Robusta**: Usa `netcat` para verificar se a porta PostgreSQL (5432) está aberta
- **🔄 Fallback Python**: Se `netcat` não estiver disponível, usa verificação Python nativa
- **⏱️ Timing Otimizado**: Aguarda tempo adicional após porta abrir para garantir readiness completo
- **📝 Logs Informativos**: Fornece feedback claro sobre o processo de inicialização

### Benefícios
- ✅ **Zero Erros de Conexão**: Elimina erros de timing durante startup
- ✅ **Startup Confiável**: Garante que migrações só executem quando banco estiver pronto  
- ✅ **Compatibilidade**: Funciona com ou sem netcat instalado
- ✅ **Desenvolvimento Suave**: Experiência consistente ao subir containers

## Troubleshooting

### Problemas Comuns

#### Container não consegue conectar ao PostgreSQL
**Solução**: O entrypoint já resolve este problema automaticamente aguardando o banco estar disponível.

#### Erro "database is being accessed by other users"
```bash
# Parar todos os containers e remover volumes
docker-compose down -v
docker-compose up --build
```

#### Ver logs detalhados
```bash
# Logs de todos os serviços
docker-compose logs -f

# Logs apenas do Django
docker-compose logs -f web

# Logs apenas do PostgreSQL
docker-compose logs -f db
```

#### Resetar banco de dados completamente
```bash
docker-compose down -v
docker volume rm webreceptivo_postgres_data
docker-compose up --build
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
