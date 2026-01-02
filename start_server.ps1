# ========================================
# WebReceptivo - Iniciar Servidor Django
# ========================================
# Este script ativa o ambiente virtual e inicia o servidor Django
# acessível de outros dispositivos na rede local.

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WebReceptivo - Iniciando Servidor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "ERRO: manage.py não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script a partir do diretório raiz do projeto." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar se o ambiente virtual existe
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "ERRO: Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host "Crie o ambiente virtual primeiro com: python -m venv .venv" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Green
& .venv\Scripts\Activate.ps1

# Verificar se ativou corretamente
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha ao ativar ambiente virtual!" -ForegroundColor Red
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "Ambiente virtual ativado!" -ForegroundColor Green
Write-Host ""

# Obter IP local
$ipLocal = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch "Loopback" -and $_.IPAddress -notmatch "^169" } | Select-Object -First 1).IPAddress

if ($ipLocal) {
    Write-Host "Servidor acessível em:" -ForegroundColor Cyan
    Write-Host "  Local:  http://localhost:8000" -ForegroundColor White
    Write-Host "  Rede:   http://$ipLocal:8000" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "AVISO: Não foi possível detectar o IP da rede local." -ForegroundColor Yellow
    Write-Host "Servidor acessível em: http://localhost:8000" -ForegroundColor White
    Write-Host ""
}

Write-Host "Iniciando servidor Django..." -ForegroundColor Green
Write-Host "Pressione CTRL+BREAK ou CTRL+C para parar" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar servidor Django
python manage.py runserver 0.0.0.0:8000
