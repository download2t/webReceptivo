import os
import shutil
from pathlib import Path

# --- CONFIGURAÇÃO FORÇADA DE CAMINHO ---
BASE_DIR = Path(__file__).resolve().parent
ARGOS_DIR = os.path.join(BASE_DIR, 'argos_data')

print(f"📂 Definindo diretório de pacotes para: {ARGOS_DIR}")

# Define variáveis de ambiente ANTES de importar o argos
os.environ['ARGOS_PACKAGES_DIR'] = ARGOS_DIR
os.environ['XDG_DATA_HOME'] = ARGOS_DIR

import argostranslate.package
import argostranslate.translate

def safe_check_installed(pkg):
    """Tenta verificar se está instalado sem quebrar o script"""
    try:
        installed_pkgs = argostranslate.package.get_installed_packages()
        return pkg in installed_pkgs
    except Exception:
        # Se der erro ao ler (como FileNotFoundError), assume que não está instalado
        return False

def install():
    # 1. LIMPEZA PREVENTIVA (Opcional, mas recomendada se estiver corrompido)
    # Se a pasta existe mas está dando erro, vamos limpar caches internos dela
    # Não apagamos a pasta toda para não perder permissões, mas limpamos o conteúdo se necessário.
    
    print("🔄 Atualizando índice de pacotes...")
    argostranslate.package.update_package_index()
    
    available_packages = argostranslate.package.get_available_packages()
    
    # Lista de pares
    pairs = [
        ('pt', 'en'),
        ('en', 'pt'),
        ('en', 'fr'),
        ('en', 'es'),
        ('pt', 'es')
    ]
    
    for from_code, to_code in pairs:
        print(f"🔍 Processando {from_code} -> {to_code}...")
        
        # Encontrar o pacote disponível para download
        pkg_to_install = next(filter(
            lambda x: x.from_code == from_code and x.to_code == to_code,
            available_packages
        ), None)
        
        if pkg_to_install:
            # Verifica se já está instalado de forma segura
            if safe_check_installed(pkg_to_install):
                print(f"✅ {from_code}->{to_code} já instalado.")
            else:
                print(f"📥 Baixando {from_code}->{to_code}...")
                try:
                    download_path = pkg_to_install.download()
                    argostranslate.package.install_from_path(download_path)
                    print(f"✅ Sucesso: {from_code}->{to_code}")
                except Exception as e:
                    print(f"❌ Erro ao instalar {from_code}->{to_code}: {e}")
        else:
            print(f"⚠️ Pacote {from_code}->{to_code} não encontrado no índice.")

if __name__ == "__main__":
    # Garante que a pasta existe
    if not os.path.exists(ARGOS_DIR):
        os.makedirs(ARGOS_DIR)
        os.chmod(ARGOS_DIR, 0o777)
    
    install()