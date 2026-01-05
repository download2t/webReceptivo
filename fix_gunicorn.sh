#!/bin/bash
# 🚀 Fix Gunicorn - Corrigir Permissões e Iniciar

echo "=== CORRIGINDO PERMISSÕES ==="
sudo chown -R www-data:www-data /var/www/webreceptivo
sudo chmod -R 755 /var/www/webreceptivo
echo "✓ Permissões ajustadas"

echo ""
echo "=== REINICIANDO GUNICORN ==="
sudo systemctl restart webreceptivo
sleep 3

echo ""
echo "=== STATUS ===" 
sudo systemctl status webreceptivo

echo ""
echo "=== PROCESSOS ==="
ps aux | grep gunicorn | grep -v grep

echo ""
echo "=== TESTANDO SOCKET ==="
ls -lah /var/www/webreceptivo/gunicorn.sock

echo ""
echo "✅ PRONTO!"
echo "Seu site deve estar funcionando agora!"
