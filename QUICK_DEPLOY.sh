#!/bin/bash
# 🚀 QUICK DEPLOYMENT REFERENCE
# Copy-paste friendly commands for fast VPS deployment

# ==================== PASSO 1: SEU PC (Windows/Mac/Linux) ====================
# Verificar tudo está commitado e fazer push

git status                                  # Ver se há mudanças
git add .                                   # Adicionar tudo (se houver)
git commit -m "Pre-deploy final"            # Commit (se houver)
git push origin main                        # Enviar para GitHub


# ==================== PASSO 2: VPS - SSH ====================
# Acessar a VPS

ssh root@seu-ip-vps
# OU
ssh seu-usuario@seu-ip-vps -i ~/.ssh/chave_privada


# ==================== PASSO 3: VPS - CLONE E DEPLOY ====================
# Executar o deploy automático

cd /tmp
git clone https://github.com/download2t/webReceptivo.git webreceptivo
cd webreceptivo

# Executar o script de deploy completo (vai levar 10-15 minutos)
bash scripts/deploy_vps.sh

# Acompanhar logs em tempo real (em outro terminal SSH):
tail -f /var/www/webreceptivo/deploy.log


# ==================== PASSO 4: VPS - CONFIGURAR VARIÁVEIS ====================
# Editar arquivo .env com valores reais

sudo nano /var/www/webreceptivo/.env

# Preencher:
# SECRET_KEY=gera-uma-chave-aleatoria-de-50-caracteres
# ALLOWED_HOSTS=seu-dominio.com.br,www.seu-dominio.com.br
# EMAIL_HOST_USER=seu-email@gmail.com
# EMAIL_HOST_PASSWORD=sua-app-password
# DEBUG=0  (SEM aspas)

# Salvar: Ctrl+X → Y → Enter


# ==================== PASSO 5: VPS - GERAR SECRET_KEY ====================
# Se precisar gerar um novo SECRET_KEY

python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Copiar a saída e colar no .env


# ==================== PASSO 6: VPS - CONFIGURAR SSL (HTTPS) ====================
# Certbot irá configurar Nginx automaticamente

sudo certbot --nginx -d seu-dominio.com.br -d www.seu-dominio.com.br

# Responder:
# 1. Email: seu-email@gmail.com
# 2. Agree to terms: Y
# 3. Share email: N (ou Y se quiser)
# 4. Redirect HTTP to HTTPS: 2 (recomendado)


# ==================== PASSO 7: VPS - VERIFICAÇÃO FINAL ====================
# Checar se tudo está funcionando

sudo systemctl status webreceptivo        # Deve estar "active (running)"
sudo systemctl status nginx              # Deve estar "active (running)"
sudo systemctl status postgresql         # Deve estar "active (running)"

# Testar conexão HTTPS
curl -I https://seu-dominio.com.br       # Deve retornar "200 OK"

# Ver logs de erros
tail -20 /var/www/webreceptivo/logs/django.log
sudo tail -20 /var/log/nginx/error.log


# ==================== PASSO 8: VPS - ACESSAR O SITE ====================

# Site principal: https://seu-dominio.com.br
# Admin: https://seu-dominio.com.br/admin
# Usuário: admin
# Senha: admin123

# ⚠️ MUDE A SENHA APÓS PRIMEIRO LOGIN!
# Menu: Admin → Users → admin → Change password


# ==================== MANUTENÇÃO DIÁRIA ====================

# Ver status em tempo real
/var/www/webreceptivo/scripts/monitor.sh

# Ou monitoramento contínuo (60s intervals)
/var/www/webreceptivo/scripts/monitor.sh --continuous

# Ver logs em tempo real
sudo journalctl -u webreceptivo -f
sudo tail -f /var/log/nginx/error.log
tail -f /var/www/webreceptivo/logs/django.log

# Fazer backup manual
/var/www/webreceptivo/scripts/backup.sh

# Verificar espaço em disco
df -h /

# Verificar uso de RAM
free -h

# Reiniciar Gunicorn (se necessário)
sudo systemctl restart webreceptivo

# Reiniciar Nginx (se necessário)
sudo systemctl restart nginx


# ==================== ATUALIZAR CÓDIGO ====================

# Quando fizer novo commit no GitHub:
cd /var/www/webreceptivo
git pull origin main
source venv/bin/activate
pip install -r production_requirements.txt
python manage.py migrate --settings=webreceptivo.settings_production
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production
sudo systemctl restart webreceptivo


# ==================== AGENDAR BACKUP AUTOMÁTICO ====================

# Configurar backup diário às 2am
sudo crontab -e

# Adicionar esta linha:
# 0 2 * * * /var/www/webreceptivo/scripts/backup.sh

# Salvar: Ctrl+X → Y → Enter

# Verificar se foi criado:
sudo crontab -l


# ==================== TROUBLESHOOTING ====================

# Problema: 502 Bad Gateway
# Solução:
sudo systemctl restart webreceptivo
sudo systemctl status webreceptivo

# Problema: RAM > 90%
# Solução: O script monitor.sh vai auto-restart, ou manual:
sudo systemctl restart webreceptivo

# Problema: SSL não funciona
# Verificar DNS:
nslookup seu-dominio.com.br
dig seu-dominio.com.br

# Problema: Migrations falhando
# Rodar manualmente:
cd /var/www/webreceptivo
source venv/bin/activate
python manage.py migrate --settings=webreceptivo.settings_production

# Problema: Estáticos não carregam (CSS/JS)
# Regenerar:
python manage.py collectstatic --noinput --settings=webreceptivo.settings_production
sudo systemctl restart nginx

# Ver erro completo:
sudo systemctl status webreceptivo -l


# ==================== TESTES DE PRODUÇÃO ====================

# Teste HTTP → HTTPS redirect
curl -I http://seu-dominio.com.br

# Teste SSL válido
openssl s_client -connect seu-dominio.com.br:443

# Teste página carregando
curl -s https://seu-dominio.com.br | head -20

# Teste admin
curl -I https://seu-dominio.com.br/admin/

# Teste estáticos (CSS)
curl -I https://seu-dominio.com.br/static/css/style.css

# Teste estáticos (JS)
curl -I https://seu-dominio.com.br/static/js/bootstrap.bundle.min.js


# ==================== REMOVER SEGURO (⚠️ CUIDADO!) ====================

# Se precisar deletar tudo (última resort):
sudo systemctl stop webreceptivo
sudo rm -rf /var/www/webreceptivo
sudo rm /etc/systemd/system/webreceptivo.service
sudo rm /etc/nginx/sites-available/webreceptivo
sudo rm /etc/nginx/sites-enabled/webreceptivo
sudo drop database webreceptivo_prod;  # Em PostgreSQL


# ==================== DICAS FINAIS ====================

# 1. Sempre faça backup antes de atualizar
#    /var/www/webreceptivo/scripts/backup.sh

# 2. Mantenha logs limpos (evita encher disco)
#    Use logrotate (já configurado)

# 3. Monitore RAM regularmente
#    free -h && ps aux | grep gunicorn

# 4. Atualizar sistema (weekly)
#    sudo apt update && sudo apt upgrade

# 5. Verificar certificado SSL (antes de expirar)
#    sudo certbot certificates

# 6. Teste de carga antes de ir pro ar
#    curl -s https://seu-dominio.com.br/static/

# 7. Documentar mudanças
#    git log --oneline | head

# 8. Fazer backup externo (Amazon S3, Google Drive, etc)
#    scripts/backup.sh && rclone copy /var/backups/webreceptivo gdrive:backups/


# ==================== REFERÊNCIAS ====================

# Documentação completa:
# - DEPLOY_GUIDE.md (guia detalhado)
# - SECURITY.md (segurança e hardening)
# - DEPLOYMENT_CHECKLIST.md (checklist passo-a-passo)
# - READY_FOR_PRODUCTION.md (resumo visual)

# Comandos úteis:
# - systemctl: gerenciar serviços
# - journalctl: ver logs systemd
# - top: monitorar processos
# - htop: versão melhorada do top (instalar se precisar)
# - netstat: conexões ativas
# - du -sh: tamanho de diretórios

echo "✅ Quick reference criado! Salve este arquivo."
echo "📖 Para instruções completas, veja DEPLOYMENT_CHECKLIST.md"
