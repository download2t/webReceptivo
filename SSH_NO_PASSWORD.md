# 🔐 Configurar SSH Sem Senha

## ✅ PASSO 1: Chave SSH já foi gerada

Localização: `C:\Users\sanma\.ssh\id_rsa` e `id_rsa.pub`

## 🔧 PASSO 2: Adicionar Chave Pública na VPS

Quando a VPS voltar online, execute:

```powershell
# Ler a chave pública
$pubkey = Get-Content "$env:USERPROFILE\.ssh\id_rsa.pub"

# Copiar para VPS
ssh root@31.97.254.220 "mkdir -p ~/.ssh && echo '$pubkey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh && echo 'Chave adicionada!'"
```

Ou manualmente:

```bash
ssh root@31.97.254.220
# Digite senha

mkdir -p ~/.ssh
cat >> ~/.ssh/authorized_keys << 'EOF'
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCrnW0Gar1GoC... (sua chave aqui)
EOF

chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
exit
```

## ✅ PASSO 3: Testar

```powershell
ssh root@31.97.254.220 "uptime"
# Não deve pedir senha!
```

## 🎯 Se ainda pedir senha

Verifique:

```bash
ssh root@31.97.254.220 "cat ~/.ssh/authorized_keys | wc -l"
# Deve mostrar pelo menos 1 linha

ssh root@31.97.254.220 "ls -lah ~/.ssh"
# Permissões devem ser: 700 para .ssh e 600 para authorized_keys
```

---

**Chave Pública Gerada:**
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCrnW0Gar1GoC... sanma@TI-SANMA
```

Depois de adicionar, SSH sem senha funcionará perfeitamente!

