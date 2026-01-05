# ✅ WebReceptivo - Deployment Checklist

## 📌 Status Atual: 100% PRONTO

```
████████████████████████████████████████ 100%
✅ Preparação Completa | ✅ Código Pronto | ✅ Documentação Feita
```

---

## 📦 Arquivos Criados

### 🎯 Configurações Essenciais
- ✅ `production_requirements.txt` (566 bytes)
- ✅ `.env.production` (template de variáveis)
- ✅ `webreceptivo/settings_production.py` (4793 bytes)
- ✅ `nginx.production.conf` (5 KB)

### 🚀 Scripts de Automação
- ✅ `scripts/deploy_vps.sh` (7.3 KB) - Deploy automatizado
- ✅ `scripts/monitor.sh` (4.3 KB) - Monitoramento com auto-restart
- ✅ `scripts/backup.sh` (1.5 KB) - Backup automático

### 📚 Documentação
- ✅ `DEPLOY_GUIDE.md` (9.3 KB) - Guia passo-a-passo
- ✅ `SECURITY.md` (7.0 KB) - Segurança e hardening
- ✅ `READY_FOR_PRODUCTION.md` (8.6 KB) - Resumo visual
- ✅ `DEPLOYMENT_CHECKLIST.md` (este arquivo)

---

## 🎯 Pré-Deploy Checklist

### Repositório GitHub
- [ ] Repositório criado e público
- [ ] README.md com instruções
- [ ] Todos os commits feitos
- [ ] Código está em `main` branch

**Status GitHub:** ✅ PRONTO
```
Último commit: d3c7a08 - Adiciona READY_FOR_PRODUCTION.md
Branch: main
Remote: https://github.com/download2t/webReceptivo.git
```

### VPS Setup
- [ ] VPS contratada (recomendado: Contabo, Vultr, DigitalOcean)
- [ ] Mínimo 1GB RAM (você vai usar ~800MB)
- [ ] Mínimo 40GB SSD (você tem!)
- [ ] Ubuntu 22.04+ ou Debian 12+
- [ ] Acesso SSH com chave pública

**Sugestões de Providers Brasileiros:**
- Contabo (€2,99/mês - 1GB RAM)
- Vultr (Datacenter SP - $3,50/mês)
- DigitalOcean (BR-São Paulo - $4/mês)

### Domínio
- [ ] Domínio registrado (.com.br, .com, etc)
- [ ] DNS apontado para IP da VPS
  ```
  A record: seu-dominio.com.br → IP_DA_VPS
  A record: www.seu-dominio.com.br → IP_DA_VPS
  ```
- [ ] Propagação DNS confirmada (pode levar 1h)

### Email
- [ ] Provedor de email escolhido (Gmail, SendGrid, Mailgun)
- [ ] SMTP credentials guardados
- [ ] Se Gmail: App Password gerada
- [ ] Testar envio antes de deploy

---

## 🚀 Deploy em 6 Passos

### Passo 1️⃣: Verificar Git (2 min)
```bash
# Seu PC Windows
git status                          # Tudo commitado?
git log --oneline | head -5         # Últimos commits OK?
git push origin main                # Enviou para GitHub?
```

**Esperado:**
```
✅ "working tree clean"
✅ Commits: d3c7a08, 9aaa7f7, b561930, ...
✅ "Everything up-to-date"
```

---

### Passo 2️⃣: SSH na VPS (3 min)
```bash
# Terminal/PowerShell do seu PC
ssh root@seu-ip-vps
# Ou se configurou usuário: ssh seu-usuario@seu-ip-vps

# Verificar:
uname -a                            # Linux version
free -h                             # RAM disponível (>1GB?)
df -h /                             # Espaço disco (>40GB?)
```

**Esperado:**
```
✅ Ubuntu 22.04 LTS ou Debian 12
✅ RAM: ~1GB
✅ Disco: 40GB+
```

---

### Passo 3️⃣: Clone e Deploy (10-15 min) ⭐ CRÍTICO
```bash
# Na VPS:
cd /tmp
git clone https://github.com/download2t/webReceptivo.git webreceptivo
cd webreceptivo

# Execute o script de deploy:
bash scripts/deploy_vps.sh
```

**O que o script faz:**
- ✅ Instala Python 3.12, PostgreSQL, Nginx, Supervisor
- ✅ Cria usuário `webreceptivo` e diretórios
- ✅ Configura banco de dados PostgreSQL
- ✅ Instala dependências Python
- ✅ Roda migrations Django
- ✅ Coleta arquivos estáticos
- ✅ Configura Gunicorn (3 workers)
- ✅ Configura Nginx reverse proxy
- ✅ Instala Certbot para SSL

**Monitorar:**
```bash
# Se quiser ver em tempo real (abra outro SSH):
tail -f /var/www/webreceptivo/deploy.log
```

**Esperado:**
```
✅ Deploy script completed successfully!
✅ Seu servidor está rodando em: http://seu-ip
✅ Arquivo .env criado em /var/www/webreceptivo/.env
```

---

### Passo 4️⃣: Configurar Variáveis Reais (5 min) ⚠️ IMPORTANTE
```bash
# Na VPS:
sudo nano /var/www/webreceptivo/.env
```

**Edite:**
```ini
# ✏️ MUDE ESTAS LINHAS:

SECRET_KEY=mude-isso-para-uma-chave-segura-de-50-caracteres
# Gerar: python3 -c "import secrets; print(secrets.token_urlsafe(50))"

ALLOWED_HOSTS=seu-dominio.com.br,www.seu-dominio.com.br

EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-app-password-do-gmail

EMAIL_FROM=noreply@seu-dominio.com.br

# Opcional (deixe como está se não quiser Redis):
# CACHE_URL=redis://localhost:6379/1
```

**Salvar:** `Ctrl+X` → `Y` → `Enter`

---

### Passo 5️⃣: Configurar SSL (5 min)
```bash
# Na VPS:
sudo certbot --nginx -d seu-dominio.com.br -d www.seu-dominio.com.br

# Responder:
# - Email: seu-email@gmail.com
# - Agree to terms: Y
# - Share email: N (opcional)
# - Redirect HTTP to HTTPS: 2 (recomendado)
```

**Esperado:**
```
✅ Congratulations! Your certificate has been issued.
✅ Seu site agora está HTTPS
```

---

### Passo 6️⃣: Verificação Final (5 min)
```bash
# Na VPS - Verificar status:
sudo systemctl status webreceptivo      # Deve estar "active (running)"
sudo systemctl status nginx             # Deve estar "active (running)"
sudo systemctl status postgresql        # Deve estar "active (running)"

# Testar acesso:
curl -I https://seu-dominio.com.br      # Deve retornar "200 OK"

# Verificar logs:
tail -20 /var/www/webreceptivo/logs/django.log
```

**Esperado:**
```
✅ webreceptivo: active (running)
✅ nginx: active (running)
✅ postgresql: active (running)
✅ HTTP/2 200 OK
✅ Sem erros em django.log
```

---

## 🌐 Acessar o Site

| URL | O que é |
|-----|---------|
| `https://seu-dominio.com.br` | Site principal |
| `https://seu-dominio.com.br/admin` | Painel admin |
| `https://seu-dominio.com.br/health/` | Health check |

**Login Admin:**
```
Usuário: admin
Senha: admin123   # ⚠️ MUDE APÓS PRIMEIRO LOGIN!
```

---

## 📊 Verificações Pós-Deploy

### Performance
```bash
# Na VPS:
free -h                            # RAM usage (deve estar <80%)
df -h /                            # Disk usage
ps aux | grep gunicorn             # Ver 3 workers rodar
```

### Logs
```bash
# Ver erros em tempo real:
sudo journalctl -u webreceptivo -f

# Ver Nginx:
sudo tail -f /var/log/nginx/error.log

# Ver Django:
tail -f /var/www/webreceptivo/logs/django.log
```

### Monitoring
```bash
# Rodar monitoria contínua (60s interval):
/var/www/webreceptivo/scripts/monitor.sh --continuous

# Apenas uma verificação:
/var/www/webreceptivo/scripts/monitor.sh
```

---

## 🔧 Manutenção Diária

### Atualizar Código
```bash
ssh seu-usuario@seu-ip-vps
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

### Automatizar Backup Diário
```bash
# Na VPS:
sudo crontab -e

# Adicionar linha:
0 2 * * * /var/www/webreceptivo/scripts/backup.sh
# (Roda todo dia às 2am)
```

---

## 🚨 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| **502 Bad Gateway** | `sudo systemctl restart webreceptivo` |
| **RAM acima de 90%** | Script auto-restart, ou manual: `sudo systemctl restart webreceptivo` |
| **SSL não funciona** | Verificar DNS: `nslookup seu-dominio.com.br` |
| **Certbot erro** | Verificar porta 80 aberta: `sudo ufw allow 80` |
| **Migrations falhando** | Ver log: `python manage.py migrate --settings=webreceptivo.settings_production` |

---

## 📋 Testes de Produção

```bash
# 1. Teste HTTP → HTTPS redirect
curl -I http://seu-dominio.com.br      # Deve redirecionar

# 2. Teste SSL válido
openssl s_client -connect seu-dominio.com.br:443

# 3. Teste página carregando
curl -s https://seu-dominio.com.br | grep -o "title.*title" | head -1

# 4. Teste admin
curl -I https://seu-dominio.com.br/admin/

# 5. Teste estáticos (CSS/JS)
curl -I https://seu-dominio.com.br/static/css/style.css
```

---

## 📊 Recursos Estimados

### RAM Usage (1GB total)
```
PostgreSQL:     ~100-150MB
Nginx:          ~20-30MB
Gunicorn (3x):  ~500-600MB (200MB cada worker)
Sistema:        ~100MB livre
─────────────────────────────
Total:          ~800MB (safe margin para 1GB)
```

### CPU Usage
```
Idle:           <5%
Com usuários:   5-20%
Pico:           50-70%
```

### Bandwidth
```
Estimado: 100-500MB/dia
Recomendado: Plano com 500GB+/mês
```

---

## 🎯 Próximos Passos (Após Deploy)

1. **Mudar senha admin**
   ```
   Acessar: https://seu-dominio.com.br/admin/
   Usuários → admin → Change password
   ```

2. **Configurar email real**
   - Testar envio em /admin/email/
   - Verificar logs se houver erro

3. **Agendar backups**
   ```bash
   sudo crontab -e
   # Adicionar: 0 2 * * * /var/www/webreceptivo/scripts/backup.sh
   ```

4. **Configurar fail2ban** (opcional, segurança)
   ```bash
   sudo fail2ban-client status
   ```

5. **Monitorar em tempo real** (opcional)
   ```bash
   /var/www/webreceptivo/scripts/monitor.sh --continuous
   ```

---

## 📞 Suporte & Documentação

| Doc | Quando Usar |
|-----|------------|
| `DEPLOY_GUIDE.md` | Instruções detalhadas de deploy |
| `SECURITY.md` | Hardening, firewall, SSL, etc |
| `READY_FOR_PRODUCTION.md` | Resumo visual e FAQ |

---

## ✅ Final Checklist

- [ ] Repositório GitHub atualizado
- [ ] SSH acessível na VPS
- [ ] DNS apontando para VPS
- [ ] `scripts/deploy_vps.sh` executado com sucesso
- [ ] `.env.production` configurado com valores reais
- [ ] SSL certificado instalado (Certbot)
- [ ] Site acessível em HTTPS
- [ ] Admin funcionando
- [ ] Estáticos carregando
- [ ] Logs sem erros críticos
- [ ] Senha admin alterada
- [ ] Backup agendado
- [ ] Email testado

---

## 🎉 Parabéns!

**Seu WebReceptivo está 100% online em produção! 🚀**

Tempo total estimado: **30-45 minutos**

### Status Final
```
✅ Django 5.2.7 rodando
✅ PostgreSQL 15 conectado
✅ Nginx com SSL ativado
✅ Gunicorn 3 workers
✅ Monitoramento ativo
✅ Backups agendados
✅ Segurança implementada
```

---

**Última atualização:** 2026-01-05  
**Versão:** 1.0 - Pronto para Deploy  
**Suporte:** Veja DEPLOY_GUIDE.md e SECURITY.md para detalhes
