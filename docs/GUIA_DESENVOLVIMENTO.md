# 📘 Guia de Desenvolvimento - WebReceptivo

**Versão:** 1.0  
**Último Update:** 06/01/2026  
**Framework:** Django 5.2.7 + Python 3.12

---

## 1️⃣ Instalar Dependências

```bash
# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
source venv/bin/activate      # Mac/Linux

# Instalar pacotes
pip install -r requirements.txt
```

---

## 2️⃣ Configurar Banco de Dados

```bash
# Aplicar migrações
python manage.py migrate

# Criar superusuário (admin)
python manage.py createsuperuser

# Criar grupos de permissões
python manage.py criar_grupos
python manage.py setup_groups
```

---

## 3️⃣ Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

---

## 4️⃣ Iniciar o Servidor Django

```bash
python manage.py runserver
```

Acesso em: **http://localhost:8000**  
Admin em: **http://localhost:8000/admin**

---

## 5️⃣ Subir Novamente o Servidor (Após Parada/Reinicialização)

### Opção A: Inicialização Completa (Recomendado após mudanças)

```bash
# 1. Entrar na pasta do projeto
cd E:\PROJETOS\WebReceptivo

# 2. Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1

# 3. Atualizar código (se necessário)
git pull origin main

# 4. Instalar/atualizar dependências
pip install -r requirements.txt

# 5. Aplicar migrações
python manage.py migrate

# 6. Coletar estáticos
python manage.py collectstatic --noinput

# 7. Iniciar servidor
python manage.py runserver
```

### Opção B: Inicialização Rápida (Sem mudanças no código)

```bash
# 1. Entrar na pasta
cd E:\PROJETOS\WebReceptivo

# 2. Ativar venv
.\.venv\Scripts\Activate.ps1

# 3. Rodar servidor
python manage.py runserver
```

---

## 6️⃣ Shell Django (Testes/Debug)

```bash
python manage.py shell

# Exemplos:
from django.contrib.auth.models import User
User.objects.all()
exit()
```

---

## 7️⃣ Executar Testes

```bash
# Todos os testes
python manage.py test

# Testes específicos de um app
python manage.py test accounts
python manage.py test user_management
```

---

## 8️⃣ Verificar Erros de Configuração

```bash
python manage.py check
```

---

## 9️⃣ Troubleshooting

### Erro: "ModuleNotFoundError"

```bash
# Reinstalar dependências
pip install -r requirements.txt

# Verificar se venv está ativado
which python  # Mac/Linux
where python  # Windows
```

### Erro: "No such table" (Banco corrompido)

```bash
# Apagar banco
rm db.sqlite3

# Recriar migrações
python manage.py migrate

# Recriar grupos
python manage.py criar_grupos
python manage.py setup_groups
```

### Porta 8000 já em uso

```bash
# Usar outra porta
python manage.py runserver 8001
```

### Arquivos estáticos não carregam

```bash
# Limpar e re-coletar
python manage.py collectstatic --clear --noinput
```

---

## 🔟 Cheat Sheet Rápido

```bash
# ✅ Setup completo
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py criar_grupos
python manage.py runserver

# ✅ Iniciar rapidinho
.\.venv\Scripts\Activate.ps1
python manage.py runserver

# ✅ Checar config
python manage.py check

# ✅ Criar grupo de teste
python manage.py shell
from django.contrib.auth.models import Group, User
g = Group.objects.create(name="Teste")
exit()

# ✅ Ver logs/erros
tail -f /path/to/logs/  # Mac/Linux

# ✅ Desativar venv
deactivate
```

---

## 1️⃣1️⃣ Dicas Úteis

### Desenvolvimento mais rápido com auto-reload

Django já recarrega automaticamente quando você salva arquivos. Se não recarregar:

```bash
# Force reload pressionando CTRL+R no navegador
# ou restartar o servidor: CTRL+C e rodar novamente
```

### Debug com print (desenvolvimento)

```python
# No seu código
print("Debug:", variavel)

# Aparecerá no terminal onde o servidor está rodando
```

### Usar DEBUG=True (Já está ativo por padrão em desenvolvimento)

Isso mostra erro completo no navegador quando algo falha.

---

## 📞 Estrutura do Projeto

```
WebReceptivo/
├── manage.py                    # Gerenciador Django
├── requirements.txt             # Dependências
├── db.sqlite3                   # Banco de dados
├── .env                         # Variáveis de ambiente
├── .venv/                       # Ambiente virtual
├── docs/                        # Documentação
├── webreceptivo/                # Projeto Django (settings, urls, wsgi)
├── user_management/             # App de usuários
├── accounts/                    # App de contas/perfil
├── servicos/                    # App de serviços
├── audit_system/                # Sistema de auditoria
├── company_settings/            # Configurações da empresa
├── core/                        # App core/dashboard
├── static/                      # Arquivos CSS, JS, imagens
├── staticfiles/                 # Arquivos coletados (collectstatic)
├── templates/                   # Templates HTML
└── media/                       # Uploads de usuários
```

---

**Última atualização:** 06/01/2026  
**Mantido por:** Equipe de Desenvolvimento
