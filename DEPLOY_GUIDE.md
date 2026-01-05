# 🚀 GUIA COMPLETO DE DEPLOY - WebReceptivo em VPS (1GB RAM)

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Arquivos Criados](#arquivos-criados)
4. [Processo de Deploy](#processo-de-deploy)
5. [Configuração Detalhada](#configuração-detalhada)
6. [Monitoramento](#monitoramento)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Este guia descreve como fazer deploy do **WebReceptivo** em uma VPS com **1GB de RAM** de forma otimizada.

### Tecnologias:
- **Framework:** Django 5.2.7
- **Database:** PostgreSQL 15
- **Web Server:** Nginx
- **Application Server:** Gunicorn (3 workers)
- **Python:** 3.12
- **Cache:** LocMemCache (ou Redis opcional)

### Otimizações para 1GB RAM:
- ✅ Gunicorn com 3 workers
- ✅ WhiteNoise para arquivos estáticos
- ✅ Gzip compression no Nginx
- ✅ Session cache em banco
- ✅ Monitoramento automático com auto-restart

---

## ✅ Pré-requisitos

### No seu computador:
- [ ] Repositório GitHub do projeto criado
- [ ] Chave SSH configurada no GitHub
- [ ] Domínio apontado para IP da VPS

### Na VPS:
- [ ] SSH acesso com permissões de sudo
- [ ] Python 3.12+
- [ ] 1GB RAM (mínimo)
- [ ] 40GB SSD (observado: você tem isso!)

---

## 📁 Arquivos Criados

### 1. **production_requirements.txt**
Dependências otimizadas para produção
```bash
pip install -r production_requirements.txt
```

### 2. **.env.production**
Template de variáveis de ambiente
```bash
cp .env.production .env  # Na VPS, preencher valores reais
```

### 3. **webreceptivo/settings_production.py**
Configurações Django para produção
- SSL/HTTPS forçado
- Debug = False
- Segurança máxima
- Logging completo
- Otimizações de memória

### 4. **scripts/deploy_vps.sh** ⭐ PRINCIPAL
Script completo de deploy (usa os arquivos abaixo)
```bash
bash scripts/deploy_vps.sh
```

### 5. **nginx.production.conf**
Configuração Nginx otimizada para 1GB RAM
- Rate limiting
- Gzip compression
- Cache HTTP
- SSL/HTTPS

### 6. **scripts/monitor.sh**
Monitoramento contínuo de recursos
```bash
# Uma vez
./scripts/monitor.sh

# Contínuo (a cada 1 min)
./scripts/monitor.sh --continuous
```

### 7. **scripts/backup.sh**
Backup automático de BD e arquivos
```bash
./scripts/backup.sh
```

---

## 🚀 Processo de Deploy

### Passo 1: Acessar VPS
```bash
ssh root@seu-ip-vps
```

### Passo 2: Clonar Repositório
```bash
cd /tmp
git clone https://github.com/seu-usuario/webreceptivo.git
cd webreceptivo
```

### Passo 3: Executar Deploy (AUTOMÁTICO)
```bash
bash scripts/deploy_vps.sh
```

O script vai:
- ✅ Instalar dependências do sistema
- ✅ Clonar/atualizar repositório
- ✅ Criar virtual environment Python
- ✅ Instalar dependências Python
- ✅ Configurar PostgreSQL
- ✅ Aplicar migrations
- ✅ Coletar arquivos estáticos
- ✅ Configurar Gunicorn
- ✅ Configurar Nginx
- ✅ Instalar Certbot (SSL)
- ✅ Criar superuser

### Passo 4: Configurar Variáveis Reais
```bash
nano /var/www/webreceptivo/.env
```

Preencher:
```ini
SECRET_KEY=gerar-chave-segura-de-50-chars
ALLOWED_HOSTS=seu-dominio.com.br,www.seu-dominio.com.br
DATABASE_URL=postgres://webreceptivo:SENHA@localhost:5432/webreceptivo_prod
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-app-password
```

### Passo 5: Gerar SECRET_KEY Segura
```bash
python3 << EOF
import secrets
print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))
EOF
```

### Passo 6: Configurar SSL com Certbot
```bash
sudo certbot --nginx -d seu-dominio.com.br -d www.seu-dominio.com.br
```

### Passo 7: Reiniciar Serviços
```bash
sudo systemctl restart nginx
sudo systemctl restart webreceptivo
```

### Passo 8: Verificar Status
```bash
sudo systemctl status webreceptivo
sudo systemctl status nginx
sudo systemctl status postgresql
```

---

## ⚙️ Configuração Detalhada

### Gunicorn - 3 Workers (Otimizado)
```ini
# /etc/systemd/system/webreceptivo.service
--workers 3              # 3 workers para 1GB RAM
--worker-class sync      # Sync é mais leve que async
--max-requests 1000      # Recicla worker a cada 1000 req
--timeout 30             # Timeout 30s
--bind unix:socket       # Socket local (não TCP)
```

**Por que 3 workers?**
- 1GB RAM ÷ 3 workers ≈ 333MB por worker
- Deixa ~100MB para nginx, postgresql, sistema

### Nginx - Rate Limiting & Compression
```nginx
gzip on;                 # Comprimir responses
gzip_min_length 1000;    # Apenas >1KB
limit_req_zone ...;      # Limitar requests maliciosos
proxy_buffering on;      # Buffer responses do Gunicorn
```

### PostgreSQL - Modo Econômico
```sql
-- Conexões limitadas
max_connections = 20      # Suficiente para 1GB
shared_buffers = 128MB    # Reduzido
work_mem = 4MB           # Reduzido
```

### Django - Cache em Memória
```python
# settings_production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'webreceptivo-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000  # Limitar a 1000 entradas
        }
    }
}
```

---

## 📊 Monitoramento

### Verificar Status (Uma Vez)
```bash
/var/www/webreceptivo/scripts/monitor.sh
```

### Monitoramento Contínuo
```bash
# Em background
nohup /var/www/webreceptivo/scripts/monitor.sh --continuous > /tmp/monitor.log 2>&1 &

# Ver logs
tail -f /tmp/monitor.log
```

### Ver Logs Detalhados

**Django:**
```bash
tail -f /var/www/webreceptivo/logs/django.log
```

**Nginx:**
```bash
sudo tail -f /var/log/nginx/error.log
```

**Gunicorn:**
```bash
sudo journalctl -u webreceptivo -f
```

**PostgreSQL:**
```bash
sudo journalctl -u postgresql -f
```

### Métricas Importantes

```bash
# RAM usage
free -h

# Disk usage
df -h

# CPU usage
top -b -n 1 | head -n 5

# Conexões PostgreSQL
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Conexões Nginx
netstat -an | grep ESTABLISHED | wc -l
```

---

## 🔧 Maintenance

### Atualizar Código
```bash
cd /var/www/webreceptivo
git pull origin main
source venv/bin/activate
pip install -r production_requirements.txt
python manage.py migrate --settings=webreceptivo.settings_production
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production
sudo systemctl restart webreceptivo
```

### Fazer Backup
```bash
/var/www/webreceptivo/scripts/backup.sh
```

Backups salvos em: `/var/backups/webreceptivo/`

### Limpar Cache
```bash
cd /var/www/webreceptivo
source venv/bin/activate
python manage.py shell --settings=webreceptivo.settings_production
>>> from django.core.cache import cache
>>> cache.clear()
>>> exit()
```

### Resetar Gunicorn (se travar)
```bash
sudo systemctl restart webreceptivo
```

---

## 🚨 Troubleshooting

### ❌ "Connection refused"
```bash
# Verificar se Gunicorn está rodando
sudo systemctl status webreceptivo

# Reiniciar
sudo systemctl restart webreceptivo

# Ver erro
sudo journalctl -u webreceptivo -n 50
```

### ❌ "Out of memory"
```bash
# Ver uso atual
free -h

# Aumentar swap (emergência)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Limpar cache Django
python manage.py shell --settings=webreceptivo.settings_production
>>> from django.core.cache import cache; cache.clear()
```

### ❌ "Static files not found"
```bash
# Recoletar
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production

# Verificar permissões
sudo chown -R www-data:www-data /var/www/webreceptivo/staticfiles
```

### ❌ "PostgreSQL connection error"
```bash
# Verificar status
sudo systemctl status postgresql

# Reiniciar
sudo systemctl restart postgresql

# Ver logs
sudo journalctl -u postgresql -n 50
```

### ❌ "Nginx 502 Bad Gateway"
```bash
# Verificar Gunicorn socket
ls -la /var/www/webreceptivo/webreceptivo.sock

# Verificar Gunicorn
sudo systemctl status webreceptivo

# Reiniciar ambos
sudo systemctl restart webreceptivo nginx
```

---

## 📞 Suporte

Para erros detalhados:

1. **Verificar logs:** `tail -f /var/www/webreceptivo/logs/django.log`
2. **Testar connectivity:** `curl localhost:8000`
3. **Verificar permissões:** `ls -la /var/www/webreceptivo/`

---

## 🎯 Checklist Pós-Deploy

- [ ] Acessível via domínio (https://seu-dominio.com.br)
- [ ] SSL funcionando (cadeado verde no browser)
- [ ] Admin acessível (/admin/)
- [ ] Database conectada
- [ ] Arquivos estáticos carregando
- [ ] Emails enviando corretamente
- [ ] Monitoramento ativo
- [ ] Backups agendados
- [ ] Logs sendo gravados

---

## 📈 Próximos Passos

Se crescer além de 1GB RAM:
1. Upgrade para 2-4GB RAM
2. Adicionar Redis para cache distribuído
3. Usar Celery para tarefas assíncronas
4. Setup de load balancing

---

**Última atualização:** 2026-01-05  
**Status:** ✅ Pronto para Deploy

