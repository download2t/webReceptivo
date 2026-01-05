# 🌐 Configuração Cloudflare + Django

## 📋 Pré-requisitos

- ✅ Domínio: `mydevsystem.site` (já registrado)
- ✅ VPS IP: `31.97.254.220`
- ⏳ Conta Cloudflare: (você precisa criar se não tiver)

---

## 🚀 PASSO 1: Adicionar Domínio no Cloudflare

### 1.1 Criar Conta Cloudflare (se não tiver)
```
https://dash.cloudflare.com/
```

### 1.2 Adicionar Seu Domínio
1. Clique em **"+ Adicionar site"**
2. Digite: `mydevsystem.site`
3. Clique em **"Continuar"**
4. Selecione plano **"Gratuito"** (Free Plan)
5. Clique em **"Continuar"**

### 1.3 Copiar Nameservers do Cloudflare
Você verá 2 nameservers assim:
```
ns1.cloudflare.com
ns2.cloudflare.com
(ou similar)
```

**COPIE ESSES NOMES!**

---

## 🔧 PASSO 2: Mudar Nameservers no Registrador

Onde você registrou `mydevsystem.site`? (Hostinger, GoDaddy, NameCheap, etc?)

### Instruções Genéricas:
1. Acesse o painel do seu registrador de domínio
2. Procure por **"DNS"**, **"Nameservers"** ou **"Gerenciar DNS"**
3. **REMOVA** os nameservers atuais
4. **ADICIONE** os 2 nameservers do Cloudflare que você copiou
5. Clique em **"Salvar"**

⏱️ **Espere 24-48 horas** para propagação de DNS (pode ser mais rápido)

---

## 📝 PASSO 3: Configurar DNS no Cloudflare

### 3.1 Criar Record A (apontar para sua VPS)

No Cloudflare, vá para **DNS** e clique em **"+ Adicionar registro"**:

```
Tipo:     A
Nome:     mydevsystem.site  (ou deixe em branco/@ para raiz)
IPv4:     31.97.254.220
TTL:      Auto
Proxy:    ☑️ Proxied (Cloudflare) - recomendado
```

Clique em **"Salvar"**

### 3.2 Criar Record CNAME para www (opcional mas recomendado)

```
Tipo:     CNAME
Nome:     www
Conteúdo: mydevsystem.site
TTL:      Auto
Proxy:    ☑️ Proxied
```

Clique em **"Salvar"**

---

## 🔐 PASSO 4: Configurar SSL/HTTPS no Cloudflare (IMPORTANTE!)

1. No Cloudflare, vá para **SSL/TLS**
2. Escolha **"Full"** ou **"Full (strict)"**
   - Full: Conexão criptografada até sua VPS
   - Full strict: Requer certificado válido na VPS

⚠️ **Recomendação:** Use "Full" por enquanto

---

## 💻 PASSO 5: Configurar Django (WebReceptivo)

Você precisa atualizar o arquivo `.env` na VPS:

### Editar arquivo .env

```bash
ssh root@31.97.254.220
nano /var/www/webreceptivo/.env
```

**Procure e altere:**

```ini
# ANTES:
ALLOWED_HOSTS=localhost,127.0.0.1,seu-ip-vps

# DEPOIS:
ALLOWED_HOSTS=mydevsystem.site,www.mydevsystem.site,31.97.254.220
```

Salve: `Ctrl+X` → `Y` → `Enter`

### Reiniciar Django

```bash
sudo systemctl restart webreceptivo
```

---

## ✅ PASSO 6: Testar

### 6.1 Verificar DNS (seu PC)

```bash
# Windows PowerShell:
nslookup mydevsystem.site

# Deve retornar:
# Address: 31.97.254.220 (ou similar)
```

### 6.2 Testar HTTPS

Abra seu navegador:
```
https://mydevsystem.site
https://www.mydevsystem.site
https://mydevsystem.site/admin
```

Deve funcionar sem erros!

### 6.3 Ver Certificado SSL

Clique no cadeado 🔒 no navegador → **"Certificado"**

Deve mostrar certificado Cloudflare.

---

## 🛠️ TROUBLESHOOTING

### Problema: "Não consegue acessar o site"

**Solução 1:** Aguarde propagação de DNS (24-48h)

**Solução 2:** Verifique records no Cloudflare
```bash
nslookup mydevsystem.site
dig mydevsystem.site
```

**Solução 3:** Verifique ALLOWED_HOSTS no `.env`
```bash
ssh root@31.97.254.220
cat /var/www/webreceptivo/.env | grep ALLOWED_HOSTS
```

### Problema: "Certificado inválido"

**Solução:** Certifique-se de que no Cloudflare:
- SSL está em modo **"Full"** (não "Off")
- Record A está em **"Proxied"** (nuvem laranja)

### Problema: "Connection refused"

**Solução:** Verifique se Nginx está rodando:
```bash
ssh root@31.97.254.220
sudo systemctl status nginx
```

Se não estiver:
```bash
sudo systemctl restart nginx
```

---

## 📊 Status Final Esperado

```
✅ Domínio apontando para VPS (record A no Cloudflare)
✅ SSL/HTTPS funcionando (Cloudflare Full)
✅ WWW funcionando (CNAME)
✅ Django aceitando o domínio (ALLOWED_HOSTS)
✅ Site acessível: https://mydevsystem.site
✅ Admin: https://mydevsystem.site/admin
```

---

## 🔄 Próximas Etapas

1. ✅ Adicionar domínio no Cloudflare
2. ✅ Mudar nameservers no registrador
3. ✅ Configurar records A e CNAME
4. ✅ Aguardar propagação DNS (24-48h)
5. ✅ Editar .env na VPS
6. ✅ Reiniciar Django
7. ✅ Testar HTTPS e SSL

---

## 📞 Dúvidas Frequentes

**P: Qual é a diferença entre "Proxied" e "DNS only"?**
A: 
- Proxied (recomendado): Cloudflare fica entre você e seu servidor (mais seguro, mais rápido)
- DNS only: Apenas DNS, sem proteção extra

**P: Preciso de certificado SSL na VPS?**
A: No modo "Full" do Cloudflare, sim. Você já tem (Certbot Let's Encrypt).

**P: Quanto custa?**
A: Cloudflare Free plan é grátis! Domínio você já pagou.

**P: Quanto tempo para DNS propagar?**
A: De 5 minutos a 48 horas. Geralmente 15 minutos.

---

**Última atualização:** 2026-01-05  
**Status:** Pronto para configuração
