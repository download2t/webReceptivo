# WebReceptivo

Um sistema web desenvolvido em Django para gestão receptiva.

## Configuração do Ambiente

### Pré-requisitos
- Python 3.12+
- Git

### Instalação

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
