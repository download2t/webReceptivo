#!/bin/bash

# ================================================
# SCRIPT DE MONITORAMENTO - WebReceptivo
# Monitora RAM, CPU, Disk e status dos serviços
# ================================================

PROJECT_DIR="/var/www/webreceptivo"
LOG_FILE="$PROJECT_DIR/logs/monitor.log"

# Cores
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# ===== FUNÇÃO DE LOG =====
log_event() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# ===== FUNCTION: CHECK RAM =====
check_ram() {
    local ram_usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')
    
    if [ $ram_usage -gt 90 ]; then
        echo -e "${RED}❌ RAM CRÍTICA: ${ram_usage}%${NC}"
        log_event "ALERT: RAM usage at ${ram_usage}%"
        restart_service
    elif [ $ram_usage -gt 80 ]; then
        echo -e "${YELLOW}⚠️  RAM ALTA: ${ram_usage}%${NC}"
        log_event "WARNING: RAM usage at ${ram_usage}%"
    else
        echo -e "${GREEN}✅ RAM OK: ${ram_usage}%${NC}"
    fi
}

# ===== FUNCTION: CHECK DISK =====
check_disk() {
    local disk_usage=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ $disk_usage -gt 90 ]; then
        echo -e "${RED}❌ DISCO CRÍTICO: ${disk_usage}%${NC}"
        log_event "ALERT: Disk usage at ${disk_usage}%"
    elif [ $disk_usage -gt 80 ]; then
        echo -e "${YELLOW}⚠️  DISCO ALTO: ${disk_usage}%${NC}"
        log_event "WARNING: Disk usage at ${disk_usage}%"
    else
        echo -e "${GREEN}✅ DISCO OK: ${disk_usage}%${NC}"
    fi
}

# ===== FUNCTION: CHECK CPU =====
check_cpu() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{printf("%.0f", 100 - $1)}')
    
    if [ $cpu_usage -gt 90 ]; then
        echo -e "${RED}❌ CPU CRÍTICA: ${cpu_usage}%${NC}"
        log_event "ALERT: CPU usage at ${cpu_usage}%"
    elif [ $cpu_usage -gt 70 ]; then
        echo -e "${YELLOW}⚠️  CPU ALTA: ${cpu_usage}%${NC}"
        log_event "WARNING: CPU usage at ${cpu_usage}%"
    else
        echo -e "${GREEN}✅ CPU OK: ${cpu_usage}%${NC}"
    fi
}

# ===== FUNCTION: CHECK SERVICES =====
check_services() {
    echo ""
    echo "=== SERVIÇOS ==="
    
    if systemctl is-active --quiet webreceptivo; then
        echo -e "${GREEN}✅ Gunicorn: ATIVO${NC}"
    else
        echo -e "${RED}❌ Gunicorn: INATIVO${NC}"
        log_event "ERROR: Gunicorn is down"
        restart_service
    fi
    
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✅ Nginx: ATIVO${NC}"
    else
        echo -e "${RED}❌ Nginx: INATIVO${NC}"
        log_event "ERROR: Nginx is down"
        systemctl restart nginx
    fi
    
    if systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}✅ PostgreSQL: ATIVO${NC}"
    else
        echo -e "${RED}❌ PostgreSQL: INATIVO${NC}"
        log_event "ERROR: PostgreSQL is down"
        systemctl restart postgresql
    fi
}

# ===== FUNCTION: RESTART SERVICE =====
restart_service() {
    log_event "Restarting Gunicorn..."
    systemctl restart webreceptivo
    sleep 5
    if systemctl is-active --quiet webreceptivo; then
        log_event "Gunicorn restarted successfully"
        echo -e "${GREEN}✅ Gunicorn reiniciado${NC}"
    else
        log_event "ERROR: Failed to restart Gunicorn"
        echo -e "${RED}❌ Falha ao reiniciar Gunicorn${NC}"
    fi
}

# ===== FUNCTION: CHECK UPTIME =====
check_uptime() {
    local uptime=$(uptime -p 2>/dev/null || echo "unknown")
    echo "Sistema online há: $uptime"
}

# ===== MAIN LOOP =====
main() {
    clear
    
    echo "=================================================="
    echo "📊 MONITORAMENTO WEBRECEPTIVO"
    echo "=================================================="
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    echo "=== RECURSOS ==="
    check_ram
    check_disk
    check_cpu
    
    check_services
    
    echo ""
    check_uptime
    
    echo ""
    echo "=================================================="
}

# ===== INICIAR MONITORAMENTO =====
if [ "$1" == "--continuous" ]; then
    echo "Monitoramento contínuo ativo. Pressione Ctrl+C para parar."
    while true; do
        main
        sleep 60  # A cada 1 minuto
        clear
    done
else
    main
fi
