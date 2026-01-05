# 🔐 Guia de Segurança - WebReceptivo Produção

## 1️⃣ Checklist de Segurança Pré-Deploy

### Django Security
- [ ] `DEBUG = False` em production
- [ ] `SECRET_KEY` aleatória e segura (50+ chars)
- [ ] `ALLOWED_HOSTS` configurado corretamente
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_HSTS_SECONDS = 31536000`

### Database Security
- [ ] PostgreSQL com senha forte
- [ ] Permissões mínimas para usuário BD
- [ ] Backups criptografados
- [ ] Conexão SSL entre Django e PostgreSQL

### Sistema Operacional
- [ ] Firewall ativo (UFW)
- [ ] Apenas portas necessárias abertas (22, 80, 443)
- [ ] SSH com chave pública (não senha)
- [ ] Updates de segurança instaladas
- [ ] fail2ban para proteção contra brute force

### Aplicação
- [ ] HTTPS/SSL configurado
- [ ] CORS configurado corretamente
- [ ] Rate limiting ativo
- [ ] Sanitização de inputs
- [ ] Validação de uploads

---

## 2️⃣ Configurar Firewall (UFW)

```bash
# Instalar
sudo apt install ufw

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP e HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Ativar
sudo ufw enable

# Verificar regras
sudo ufw status
```

---

## 3️⃣ SSH Security

```bash
# Gerar chave SSH (no seu PC)
ssh-keygen -t ed25519 -C "seu-email@gmail.com"

# Copiar chave pública para VPS
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@seu-ip

# Desabilitar login por senha em /etc/ssh/sshd_config
sudo nano /etc/ssh/sshd_config
```

Modificar:
```bash
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

Reiniciar SSH:
```bash
sudo systemctl restart sshd
```

---

## 4️⃣ Fail2Ban (Proteção contra Brute Force)

```bash
# Instalar
sudo apt install fail2ban

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

Configurar para nginx:
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
maxretry = 3

[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true

[nginx-ratelimit]
enabled = true
```

Iniciar:
```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status
```

---

## 5️⃣ Certificado SSL (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot --nginx -d seu-dominio.com.br -d www.seu-dominio.com.br

# Auto-renew (já vem configurado)
sudo systemctl enable certbot.timer
```

---

## 6️⃣ Secrets Management

### Gerar SECRET_KEY Segura
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Armazenar em .env (nunca em código!)
```bash
# .env (NUNCA versionado)
SECRET_KEY=seu-super-secret-key-aqui

# .env.example (pode versionado)
SECRET_KEY=CHANGE_ME
```

---

## 7️⃣ Database Security

### Senha forte para PostgreSQL
```bash
# Gerar senha (20+ chars)
openssl rand -base64 32
```

### Limitar acesso ao PostgreSQL
```bash
sudo nano /etc/postgresql/15/main/postgresql.conf

# Comentar ou remover listen_addresses
listen_addresses = 'localhost'

# Reiniciar
sudo systemctl restart postgresql
```

---

## 8️⃣ Monitoramento de Segurança

### Verificar tentativas de login falhadas
```bash
sudo tail -f /var/log/auth.log | grep sshd
```

### Ver IPs banidos pelo Fail2Ban
```bash
sudo fail2ban-client status sshd
```

### Verificar conexões ativas
```bash
sudo netstat -tunlap
```

---

## 9️⃣ Headers de Segurança (Nginx)

Já configurado em `nginx.production.conf`:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

---

## 🔟 Rate Limiting

Já configurado em `nginx.production.conf`:
```nginx
# Limite 10 requests por segundo da mesma IP
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

# Limite 5 logins por minuto
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
```

---

## 1️⃣1️⃣ Backup & Recovery

### Criptografar backups
```bash
# Gerar chave
openssl rand -base64 32 > /etc/backup.key

# Criptografar backup
tar czf - /var/www/webreceptivo | openssl enc -aes-256-cbc -salt -in /var/backups/webreceptivo_encrypted.tar.gz

# Descriptografar
openssl enc -d -aes-256-cbc -in /var/backups/webreceptivo_encrypted.tar.gz | tar xz
```

### Backup externo (S3, Drive, etc)
```bash
# Instalar rclone
sudo apt install rclone

# Configurar
rclone config

# Sincronizar backups
rclone sync /var/backups/webreceptivo remote:backups/webreceptivo --backup-dir=remote:backups/archive
```

---

## 1️⃣2️⃣ Logging & Auditoria

### Verificar logs de acesso
```bash
# Django
tail -f /var/www/webreceptivo/logs/django.log

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Sistema
tail -f /var/log/syslog
```

### Arquivar logs antigos
```bash
# Setup logrotate (automático)
sudo nano /etc/logrotate.d/nginx
```

```
/var/log/nginx/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
}
```

---

## 1️⃣3️⃣ Atualizações de Segurança

### Ativar actualizações automáticas
```bash
# Instalar unattended-upgrades
sudo apt install unattended-upgrades apt-listchanges

# Habilitar
sudo dpkg-reconfigure -plow unattended-upgrades

# Verificar
cat /etc/apt/apt.conf.d/50unattended-upgrades
```

---

## 1️⃣4️⃣ Teste de Segurança

### OWASP Security Test
```bash
# Verificar headers
curl -I https://seu-dominio.com.br

# Verificar SSL
echo | openssl s_client -servername seu-dominio.com.br -connect seu-dominio.com.br:443
```

### Scan de vulnerabilidades
```bash
# Trivy (container scanning)
trivy image seu-docker-image

# OWASP ZAP
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://seu-dominio.com.br
```

---

## 1️⃣5️⃣ Resposta a Incidentes

### Se detectar invasão:
1. **Desconectar:** `sudo systemctl stop webreceptivo nginx`
2. **Investigar:** Ver todos os logs
3. **Backup:** Cópia dos dados para análise
4. **Limpar:** Mudar passwords, rechaves
5. **Deploy:** Versão limpa da aplicação

---

## ✅ Checklist Final

- [ ] Firewall ativo
- [ ] SSH com chave pública
- [ ] Fail2Ban instalado
- [ ] SSL/HTTPS configurado
- [ ] SECRET_KEY segura
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configurado
- [ ] Backups criptografados
- [ ] Logs monitorados
- [ ] Atualizações automáticas ativas

---

**Última atualização:** 2026-01-05

