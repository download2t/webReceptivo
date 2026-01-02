"""
Script para inicializar pacotes de tradução do Argos Translate
Execute uma vez para baixar os modelos de idiomas necessários
"""
import argostranslate.package
import argostranslate.translate

def setup_translation_packages():
    """Baixa e instala pacotes de tradução PT->EN, PT->ES, EN->FR (para PT->EN->FR)"""
    
    print("🔄 Atualizando índice de pacotes...")
    argostranslate.package.update_package_index()
    
    available_packages = argostranslate.package.get_available_packages()
    installed_packages = argostranslate.package.get_installed_packages()
    
    # Pacotes necessários (incluindo EN->FR para tradução em cadeia)
    needed_packages = [
        ('pt', 'en', 'PT → EN'),
        ('pt', 'es', 'PT → ES'),
        ('en', 'fr', 'EN → FR (para PT→FR)')
    ]
    
    for from_code, to_code, description in needed_packages:
        # Verificar se já está instalado
        already_installed = any(
            pkg.from_code == from_code and pkg.to_code == to_code 
            for pkg in installed_packages
        )
        
        if already_installed:
            print(f"✅ Pacote {description} já instalado")
            continue
        
        # Procurar e instalar pacote
        package_to_install = next(
            (pkg for pkg in available_packages 
             if pkg.from_code == from_code and pkg.to_code == to_code),
            None
        )
        
        if package_to_install:
            print(f"📥 Baixando pacote {description}...")
            download_path = package_to_install.download()
            print(f"💾 Instalando pacote {description}...")
            argostranslate.package.install_from_path(download_path)
            print(f"✅ Pacote {description} instalado com sucesso!")
        else:
            print(f"❌ Pacote {description} não encontrado")
    
    print("\n🎉 Configuração de tradução concluída!")
    print("\nPacotes instalados:")
    installed = argostranslate.package.get_installed_packages()
    for pkg in installed:
        if pkg.from_code in ['pt', 'en']:
            print(f"  - {pkg.from_name} → {pkg.to_name}")

if __name__ == "__main__":
    setup_translation_packages()
