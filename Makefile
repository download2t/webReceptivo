.PHONY: help build up down logs shell migrate superuser collectstatic test clean

help: ## Mostra esta mensagem de ajuda
	@echo "Comandos disponíveis:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Constrói as imagens Docker
	docker-compose build

up: ## Inicia os containers em desenvolvimento
	docker-compose up

up-d: ## Inicia os containers em background
	docker-compose up -d

down: ## Para todos os containers
	docker-compose down

logs: ## Mostra os logs dos containers
	docker-compose logs -f

shell: ## Acessa o shell do container web
	docker-compose exec web bash

migrate: ## Executa as migrações do Django
	docker-compose exec web python manage.py migrate

superuser: ## Cria um superusuário
	docker-compose exec web python manage.py createsuperuser

collectstatic: ## Coleta arquivos estáticos
	docker-compose exec web python manage.py collectstatic --noinput

test: ## Executa os testes
	docker-compose exec web python manage.py test

clean: ## Remove containers, networks e volumes
	docker-compose down -v --remove-orphans
	docker system prune -f

# Comandos de produção
prod-up: ## Inicia em produção
	docker-compose -f docker-compose.prod.yml up -d --build

prod-down: ## Para containers de produção
	docker-compose -f docker-compose.prod.yml down

prod-logs: ## Logs de produção
	docker-compose -f docker-compose.prod.yml logs -f
