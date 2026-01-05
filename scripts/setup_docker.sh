#!/bin/bash
# Script para setup completo do Docker com banco de dados fresco

set -e

echo "🚀 Iniciando setup do Docker para WebReceptivo..."

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Remove containers e volumes antigos
echo -e "${BLUE}1️⃣  Removendo containers e volumes antigos...${NC}"
docker-compose down -v 2>/dev/null || true
echo -e "${GREEN}✓ Limpo${NC}"

# 2. Build da imagem Docker
echo -e "${BLUE}2️⃣  Construindo imagem Docker...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✓ Imagem criada${NC}"

# 3. Inicia o banco de dados
echo -e "${BLUE}3️⃣  Iniciando banco de dados...${NC}"
docker-compose up -d db
echo -e "${GREEN}✓ Banco iniciado${NC}"

# Aguarda banco ficar pronto
echo -e "${BLUE}⏳ Aguardando banco de dados ficar pronto...${NC}"
sleep 10

# 4. Executa migrações
echo -e "${BLUE}4️⃣  Executando migrações...${NC}"
docker-compose exec -T web python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrações executadas${NC}"

# 5. Coleta arquivos estáticos
echo -e "${BLUE}5️⃣  Coletando arquivos estáticos...${NC}"
docker-compose exec -T web python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Estáticos coletados${NC}"

# 6. Cria super usuário padrão (opcional)
echo -e "${BLUE}6️⃣  Criando super usuário padrão...${NC}"
docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✓ Super usuário admin/admin123 criado')
else:
    print('✓ Super usuário admin já existe')
"
echo -e "${GREEN}✓ Super usuário pronto${NC}"

# 7. Inicia o servidor web
echo -e "${BLUE}7️⃣  Iniciando servidor web...${NC}"
docker-compose up -d web
echo -e "${GREEN}✓ Servidor iniciado${NC}"

# 8. Status final
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Setup concluído com sucesso!${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Informações úteis:${NC}"
echo "  🌐 Acesse: http://localhost:8000"
echo "  👤 Admin: http://localhost:8000/admin"
echo "  📝 Credentials: admin / admin123"
echo "  🗄️  Banco: PostgreSQL na porta 5432"
echo ""
echo -e "${BLUE}Comandos úteis:${NC}"
echo "  Logs: docker-compose logs -f web"
echo "  Shell: docker-compose exec web python manage.py shell"
echo "  Parar: docker-compose down"
echo "  Remover tudo: docker-compose down -v"
echo ""
