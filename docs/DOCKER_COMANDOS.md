# WebReceptivo - Comandos Seguros Docker

## ✅ COMANDOS SEGUROS (Preservam dados):

### Desenvolvimento Normal
```bash
# Reiniciar apenas a aplicação
docker-compose restart web

# Parar e subir novamente
docker-compose down && docker-compose up

# Rebuild por mudanças no código
docker-compose build && docker-compose up

# Ver logs
docker-compose logs -f
```

### Rebuild Completo (Seguro)
```bash
# Rebuild sem remover volumes
docker-compose down
docker-compose build --no-cache  
docker-compose up --force-recreate

# Ou tudo em uma linha
docker-compose up --build --force-recreate
```

### Backup e Manutenção
```bash
# Fazer backup
./scripts/backup_db.sh

# Ver espaço usado pelos volumes
docker system df

# Listar volumes
docker volume ls
```

## ❌ COMANDOS PERIGOSOS (Podem perder dados):

### NUNCA use estes comandos sem backup:
```bash
# ❌ Remove volumes (APAGA BANCO!)
docker-compose down -v

# ❌ Remove volume específico (APAGA BANCO!)
docker volume rm webreceptivo_postgres_data

# ❌ Limpa tudo incluindo volumes (APAGA TUDO!)
docker system prune --volumes

# ❌ Remove todos os volumes não utilizados
docker volume prune
```

## 🛡️ Comandos de Emergência:

### Se algo der errado:
```bash
# Parar tudo sem remover dados
docker-compose stop

# Verificar se volume existe
docker volume inspect webreceptivo_postgres_data

# Restaurar de backup
./scripts/restore_db.sh backups/arquivo_backup.sql.gz
```

## 💾 Backup e Restore

### Backup Manual
```bash
# Backup simples
docker-compose exec -T db pg_dump -U postgres -d webreceptivo > backups/backup_manual.sql

# Backup com timestamp
docker-compose exec -T db pg_dump -U postgres -d webreceptivo > "backups/backup_$(date +%Y%m%d_%H%M%S).sql"

# Windows PowerShell
docker-compose exec -T db pg_dump -U postgres -d webreceptivo > "backups\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
```

### Backup Automático
```bash
# Usar script criado
./scripts/backup_db.sh

# Programar backup semanal (Linux/Mac)
crontab -e
# Adicionar linha: 0 2 * * 0 /caminho/para/projeto/scripts/backup_db.sh
```

### Restore (Restauração)
```bash
# Restaurar de backup específico
./scripts/restore_db.sh backups/backup_20241011_142930.sql

# Restaurar arquivo compactado
./scripts/restore_db.sh backups/backup_20241011_142930.sql.gz

# Restore manual (Linux/Mac)
cat backups/backup.sql | docker-compose exec -T db psql -U postgres -d webreceptivo
```

## 🔍 Monitoramento e Debugging

### Status do Sistema
```bash
# Ver status dos containers
docker-compose ps

# Ver uso de espaço
docker system df

# Ver logs em tempo real
docker-compose logs -f

# Logs apenas do banco
docker-compose logs -f db

# Logs apenas da aplicação
docker-compose logs -f web
```

### Informações do Volume
```bash
# Listar todos os volumes
docker volume ls

# Detalhes do volume do PostgreSQL
docker volume inspect webreceptivo_postgres_data

# Ver tamanho do volume
docker system df -v | grep webreceptivo_postgres_data
```

### Acesso Direto ao Banco
```bash
# Conectar no PostgreSQL via psql
docker-compose exec db psql -U postgres -d webreceptivo

# Executar comando SQL direto
docker-compose exec db psql -U postgres -d webreceptivo -c "SELECT COUNT(*) FROM auth_user;"

# Ver tabelas do Django
docker-compose exec db psql -U postgres -d webreceptivo -c "\dt"
```

## 📋 Rotinas Recomendadas

### Desenvolvimento Diário
```bash
# 1. Verificar status
docker-compose ps

# 2. Ver logs se necessário
docker-compose logs -f web

# 3. Reiniciar após mudanças no código
docker-compose restart web

# 4. Aplicar migrações se necessário
docker-compose exec web python manage.py migrate
```

### Manutenção Semanal
```bash
# 1. Fazer backup
./scripts/backup_db.sh

# 2. Verificar espaço usado
docker system df

# 3. Limpar imagens não utilizadas (sem volumes!)
docker image prune -f

# 4. Ver logs por erros
docker-compose logs --tail=100 | grep -i error
```

### Antes de Grandes Mudanças
```bash
# 1. SEMPRE fazer backup antes
./scripts/backup_db.sh

# 2. Testar em branch separada
git checkout -b feature/nova-funcionalidade

# 3. Documentar mudanças
git commit -m "backup: antes de implementar nova funcionalidade"

# 4. Proceder com as alterações
```

## 🚨 Troubleshooting

### Problemas Comuns

#### Container não inicia
```bash
# Ver logs de erro
docker-compose logs db
docker-compose logs web

# Verificar portas em uso
netstat -tulpn | grep :5432
netstat -tulpn | grep :8000

# Forçar recriação
docker-compose up --force-recreate
```

#### Erro de conexão com banco
```bash
# Verificar se PostgreSQL está rodando
docker-compose exec db pg_isready -U postgres

# Testar conexão
docker-compose exec web python manage.py dbshell

# Reiniciar apenas o banco
docker-compose restart db
```

#### Volume corrompido (EXTREMO)
```bash
# 1. FAZER BACKUP se possível
docker-compose exec -T db pg_dump -U postgres -d webreceptivo > backup_emergencia.sql

# 2. Parar containers
docker-compose down

# 3. Remover volume corrompido (PERIGOSO!)
docker volume rm webreceptivo_postgres_data

# 4. Recriar e restaurar
docker-compose up -d db
sleep 30
cat backup_emergencia.sql | docker-compose exec -T db psql -U postgres -d webreceptivo
docker-compose up web
```

## 📝 Notas Importantes

### ⚠️ LEMBRE-SE:
- **SEMPRE** faça backup antes de operações arriscadas
- **NUNCA** use `docker-compose down -v` sem backup
- **Volume `webreceptivo_postgres_data` contém TODOS os seus dados**
- **Scripts estão em `./scripts/` para automatizar tarefas**

### 📞 Em Caso de Emergência:
1. **NÃO ENTRE EM PÂNICO**
2. **Verificar se volume existe**: `docker volume inspect webreceptivo_postgres_data`
3. **Procurar backup mais recente**: `ls -la backups/`
4. **Restaurar**: `./scripts/restore_db.sh backups/backup_mais_recente.sql`

### 💡 Dicas de Performance:
```bash
# Limpar logs antigos (não afeta dados)
docker-compose logs --tail=0 -f > /dev/null &

# Verificar uso de memória
docker stats

# Otimizar PostgreSQL (se necessário)
docker-compose exec db psql -U postgres -d webreceptivo -c "VACUUM ANALYZE;"
```