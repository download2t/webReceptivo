import os
from pathlib import Path

# --- CONFIGURAÇÃO FORÇADA DE CAMINHO ---
# Pega o diretório atual onde o script está
BASE_DIR = Path(__file__).resolve().parent
ARGOS_DIR = os.path.join(BASE_DIR, 'argos_data')

print(f"📂 Definindo diretório de pacotes para: {ARGOS_DIR}")

# Define a variável de ambiente ANTES de importar o argos
os.environ['ARGOS_PACKAGES_DIR'] = ARGOS_DIR
os.environ['XDG_DATA_HOME'] = ARGOS_DIR

import argostranslate.package
import argostranslate.translate

def install():
    print("🔄 Atualizando índice de pacotes...")
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    
    # Lista de pares para instalar
    pairs = [
        ('pt', 'en'),
        ('en', 'pt'), # Necessário para alguns fluxos
        ('en', 'fr'), # Pivô para francês
        ('en', 'es'),
        ('pt', 'es')  # Se disponível direto
    ]
    
    for from_code, to_code in pairs:
        print(f"🔍 Verificando {from_code} -> {to_code}...")
        pkg = next(filter(
            lambda x: x.from_code == from_code and x.to_code == to_code,
            available_packages
        ), None)
        
        if pkg:
            if pkg in argostranslate.package.get_installed_packages():
                print(f"✅ {from_code}->{to_code} já instalado em {ARGOS_DIR}")
            else:
                print(f"📥 Baixando {from_code}->{to_code}...")
                path = pkg.download()
                argostranslate.package.install_from_path(path)
                print("✅ Instalado com sucesso.")
        else:
            print(f"⚠️ Pacote {from_code}->{to_code} não encontrado no índice oficial.")

if __name__ == "__main__":
    install()