# 📘 Guia Operacional - Servidor VPS WebReceptivo

**Servidor:** 31.97.254.220  
**Domínio:** mydevsystem.site  
**Sistema:** LiteSpeed Web Server + Django 5.2.7

---

## 1️⃣ Conectar ao Servidor SSH

### Via Terminal (Windows PowerShell, Mac ou Linux)

```bash
ssh root@31.97.254.220
```

**Responder com a senha do servidor quando solicitado.**

### Via PuTTY (Windows GUI)
1. Abrir PuTTY
2. **Host Name:** `31.97.254.220`
3. **Port:** `22`
4. **Connection type:** SSH
5. Clicar em "Open"
6. Login: `root`
7. Senha: *[sua senha]*

---

## 2️⃣ Estrutura de Pastas

```
/usr/local/lsws/Example/html/demo/webReceptivo/
├── manage.py                          # Gerenciador Django
├── requirements.txt                   # Dependências Python
├── db.sqlite3                         # Banco de dados
├── .env                               # Variáveis de ambiente
├── venv/                              # Ambiente virtual Python
├── webreceptivo/                      # Projeto Django
│   ├── settings.py                    # Settings desenvolvimento
│   ├── settings_production.py         # Settings produção
│   ├── wsgi.py                        # WSGI desenvolvimento
│   └── wsgi_production.py             # WSGI produção
├── litespeed_wsgi.py                  # Arquivo WSGI para LiteSpeed
└── staticfiles/                       # Arquivos estáticos (CSS, JS)
```

---

## 3️⃣ Verificar Status do Servidor

### Status do LiteSpeed

```bash
# Ver se está rodando
sudo /usr/local/lsws/bin/lswsctrl status

# Exemplo de saída:
# [OK] LiteSpeed Web Server is running with PID 946
```

### Testar conexão HTTP

```bash
# Testar via IP
curl -I http://31.97.254.220/admin/

# Testar via domínio
curl -I http://mydevsystem.site/admin/

# Ver resposta completa
curl http://31.97.254.220/
```

### Ver logs em tempo real

```bash
# Logs de erro do LiteSpeed
tail -f /usr/local/lsws/logs/error.log

# Pressione CTRL+C para sair
```

---

## 4️⃣ Iniciar o Servidor

### Opção A: Iniciar LiteSpeed (Recomendado para Produção)

```bash
# Iniciar
sudo /usr/local/lsws/bin/lswsctrl start

# Verificar se iniciou
sudo /usr/local/lsws/bin/lswsctrl status
```

### Opção B: Iniciar Django em Modo Desenvolvimento

```bash
cd /usr/local/lsws/Example/html/demo/webReceptivo

# Ativar ambiente virtual
source venv/bin/activate

# Iniciar servidor Django (porta 8000)
python manage.py runserver 0.0.0.0:8000 --settings=webreceptivo.settings_production

# Acessar em: http://31.97.254.220:8000/admin/
```

---

## 5️⃣ Reiniciar o Servidor

### Reiniciar LiteSpeed (Melhor opção)

```bash
# Reiniciar gracefully (sem desconectar usuários ativos)
sudo /usr/local/lsws/bin/lswsctrl restart

# Esperar alguns segundos e verificar status
sleep 3
sudo /usr/local/lsws/bin/lswsctrl status
```

### Recarregar configuração (sem derrubar)

```bash
# Recarrega config sem interromper conexões
sudo /usr/local/lsws/bin/lswsctrl reload
```

### Reiniciar após mudanças no código

```bash
cd /usr/local/lsws/Example/html/demo/webReceptivo

# 1. Atualizar código
git pull origin main

# 2. Instalar/atualizar dependências (se necessário)
source venv/bin/activate
pip install -r requirements.txt

# 3. Aplicar migrações do banco (se houver)
python manage.py migrate --settings=webreceptivo.settings_production

# 4. Coletar arquivos estáticos
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production

# 5. Reiniciar LiteSpeed
sudo /usr/local/lsws/bin/lswsctrl restart
```

---

## 6️⃣ Parar o Servidor (Offline)

### Parar LiteSpeed

```bash
# Parar completamente
sudo /usr/local/lsws/bin/lswsctrl stop

# Verificar se parou
sudo /usr/local/lsws/bin/lswsctrl status

# Resultado esperado:
# [Error] Failed to connect to LiteSpeed Web Server!
```

### Parar Django (se rodando manualmente)

```bash
# Pressionar CTRL+C no terminal onde o runserver está rodando
# Ou matar o processo:
pkill -f "python manage.py runserver"
```

---

## 7️⃣ Comandos Django Essenciais

### Executar no servidor remoto

```bash
cd /usr/local/lsws/Example/html/demo/webReceptivo
source venv/bin/activate
```

### Criar superusuário (admin)

```bash
python manage.py createsuperuser --settings=webreceptivo.settings_production
```

### Criar grupos de permissões

```bash
python manage.py criar_grupos --settings=webreceptivo.settings_production
python manage.py setup_groups --settings=webreceptivo.settings_production
```

### Aplicar migrações do banco

```bash
python manage.py migrate --settings=webreceptivo.settings_production
```

### Coletar arquivos estáticos

```bash
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production
```

### Verificar erros de configuração

```bash
python manage.py check --settings=webreceptivo.settings_production
```

### Acessar shell Django

```bash
python manage.py shell --settings=webreceptivo.settings_production

# Exemplos:
# from django.contrib.auth.models import User
# User.objects.all()
# exit()
```

---

## 8️⃣ Backup e Manutenção

### Fazer backup do banco de dados

```bash
# Criar pasta de backups (primeira vez)
mkdir -p /root/backups

# Backup com data/hora
cp /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3 \
   /root/backups/db_$(date +%Y%m%d_%H%M%S).sqlite3

# Listar backups
ls -lah /root/backups/
```

### Restaurar backup

```bash
# Parar servidor
sudo /usr/local/lsws/bin/lswsctrl stop

# Restaurar arquivo
cp /root/backups/db_20260106_120000.sqlite3 \
   /usr/local/lsws/Example/html/demo/webReceptivo/db.sqlite3

# Reiniciar
sudo /usr/local/lsws/bin/lswsctrl start
```

### Limpeza de logs antigos

```bash
# Ver tamanho dos logs
du -sh /usr/local/lsws/logs/

# Limpar logs antigos (mantém últimos 7 dias)
find /usr/local/lsws/logs/ -name "*.log*" -mtime +7 -delete
```

---

## 9️⃣ URLs de Acesso

| Função | URL |
|--------|-----|
| **Admin Django** | http://mydevsystem.site/admin/ |
| **Configurações** | http://mydevsystem.site/configuracoes/ |
| **Auditoria** | http://mydevsystem.site/audit/ |
| **Usuários** | http://mydevsystem.site/usuarios/ |
| **Painel LiteSpeed** | http://31.97.254.220:7080/admin/ |

---

## 🔟 Troubleshooting

### Erro 500 - Internal Server Error

```bash
# Ver logs detalhados
tail -50 /usr/local/lsws/logs/error.log

# Verificar arquivo .env existe
cat /usr/local/lsws/Example/html/demo/webReceptivo/.env

# Verificar permissões
ls -la /usr/local/lsws/Example/html/demo/webReceptivo/
```

### Página 404 - Not Found

```bash
# Verificar se Django está respondendo
curl -v http://31.97.254.220/admin/

# Testar com IP direto
curl -I http://31.97.254.220/admin/

# Verificar ALLOWED_HOSTS no settings
grep -A 5 "ALLOWED_HOSTS" /usr/local/lsws/Example/html/demo/webReceptivo/webreceptivo/settings_production.py
```

### Banco de dados corrompido

```bash
# Fazer backup
cp db.sqlite3 db.sqlite3.corrupted

# Deletar migrations antigas
rm -rf webreceptivo/migrations/

# Recriar migrações
python manage.py makemigrations --settings=webreceptivo.settings_production

# Aplicar novamente
python manage.py migrate --settings=webreceptivo.settings_production
```

### Arquivos estáticos não carregam

```bash
# Coletar estáticos novamente
python manage.py collectstatic --noinput --clear --settings=webreceptivo.settings_production

# Verificar permissões
chmod -R 755 /usr/local/lsws/Example/html/demo/webReceptivo/staticfiles/

# Reiniciar
sudo /usr/local/lsws/bin/lswsctrl restart
```

---

## 1️⃣1️⃣ Rotina Diária Recomendada

### Manhã (ao iniciar trabalho)

```bash
# 1. Conectar ao servidor
ssh root@31.97.254.220

# 2. Verificar status
sudo /usr/local/lsws/bin/lswsctrl status

# 3. Verificar logs de erro
tail -20 /usr/local/lsws/logs/error.log

# 4. Verificar espaço em disco
df -h

# 5. Verificar processos
ps aux | grep python
```

### Antes de fazer alterações

```bash
# 1. Fazer backup do banco
cp db.sqlite3 db.sqlite3.$(date +%Y%m%d_%H%M%S)

# 2. Atualizar código
cd /usr/local/lsws/Example/html/demo/webReceptivo
git pull origin main

# 3. Aplicar migrações
python manage.py migrate --settings=webreceptivo.settings_production

# 4. Coletar estáticos
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production

# 5. Reiniciar
sudo /usr/local/lsws/bin/lswsctrl restart
```

### À noite (antes de sair)

```bash
# 1. Fazer backup final
cp db.sqlite3 /root/backups/db_$(date +%Y%m%d_%H%M%S).sqlite3

# 2. Verificar logs
tail -20 /usr/local/lsws/logs/error.log

# 3. Confirmar tudo está rodando
curl -I http://mydevsystem.site/admin/
```

---

## 1️⃣2️⃣ Cheat Sheet Rápido

```bash
# ✅ Iniciar tudo
ssh root@31.97.254.220
sudo /usr/local/lsws/bin/lswsctrl start

# ✅ Verificar status
sudo /usr/local/lsws/bin/lswsctrl status

# ✅ Reiniciar após mudanças
cd /usr/local/lsws/Example/html/demo/webReceptivo
git pull && python manage.py migrate --settings=webreceptivo.settings_production && python manage.py collectstatic --noinput --settings=webreceptivo.settings_production && sudo /usr/local/lsws/bin/lswsctrl restart

# ✅ Parar
sudo /usr/local/lsws/bin/lswsctrl stop

# ✅ Ver logs
tail -f /usr/local/lsws/logs/error.log

# ✅ Sair da conexão SSH
exit
```

---

## 📞 Suporte

Se encontrar problemas:
1. Verificar logs: `tail -50 /usr/local/lsws/logs/error.log`
2. Testar manualmente: `curl -v http://31.97.254.220/admin/`
3. Verificar .env: `cat /usr/local/lsws/Example/html/demo/webReceptivo/.env`
4. Reiniciar: `sudo /usr/local/lsws/bin/lswsctrl restart`

---

**Última atualização:** 06/01/2026  
**Versão:** 1.0  
**Sistema:** LiteSpeed 1.8.4 + Django 5.2.7 + Python 3.12
