# 🏢 Sistema de Configurações da Empresa - Guia Completo

## ✅ Visão Geral

O **Sistema de Configurações da Empresa** é um módulo completo para gerenciar parâmetros empresariais no WebReceptivo, incluindo dados da empresa, configurações de sistema, e configurações de e-mail SMTP.

## 🎯 Funcionalidades Principais

### 📋 **Dados da Empresa**
- Nome da empresa e nome fantasia
- **CNPJ/CPF** com validação matemática completa
- Inscrição estadual
- Endereço completo com **busca automática por CEP**
- Telefone e e-mail com validação
- **Upload de logotipo** com preview

### ⚙️ **Configurações do Sistema**
- **Data e hora atual** com atualização em tempo real
- **Formato de data** configurável (DD/MM/YYYY, MM/DD/YYYY, etc.)
- **Formato de hora** (12h ou 24h)
- **Fuso horário** com preview em tempo real

### 📧 **Configurações de E-mail (SMTP)**
- **E-mail único** para todas as funções (login, remetente, sistema)
- Servidor SMTP e porta
- Tipo de conexão (SSL/TLS/STARTTLS)
- **Senha criptografada** no banco de dados
- **Teste de envio** em tempo real
- **Templates rápidos** para Gmail, Outlook, Yahoo
- **Configuração dinâmica** aplicada automaticamente ao Django

## 🚀 Como Usar

### 📱 **Acesso Rápido**
```
URL: http://127.0.0.1:8000/configuracoes/
Usuário: admin
Senha: admin123
```

### 📍 **Páginas Disponíveis**
- **Visão Geral**: `/configuracoes/` - Dashboard com resumo das configurações
- **Dados da Empresa**: `/configuracoes/empresa/` - Formulário da empresa
- **Sistema**: `/configuracoes/sistema/` - Configurações de data/hora/fuso
- **E-mail SMTP**: `/configuracoes/smtp/` - Configurações de e-mail

### 🔧 **Menu de Acesso**
1. Faça login como administrador
2. Clique no dropdown do usuário (canto superior direito)
3. Selecione **"Configurações da Empresa"**

## 💡 Exemplos Práticos

### 🚀 **Configuração Rápida Gmail**
1. Acesse `/configuracoes/smtp/`
2. Clique no botão **"Gmail"**
3. Digite seu e-mail: `suportesanma@gmail.com`
4. Digite a senha de app: `ofdf qopt wduz ahxl`
5. Clique **"Enviar E-mail de Teste"**

### 🏢 **Configurar Dados da Empresa**
1. Acesse `/configuracoes/empresa/`
2. Preencha o nome da empresa
3. Digite o **CNPJ**: `77.766.483/0001-64` (validação automática)
4. Digite o **CEP**: `01310-100` (preenchimento automático do endereço)
5. Faça **upload da logo**

### 📧 **Como Funciona o E-mail**

#### **Campo Único Simplificado:**
- **E-mail SMTP**: `suportesanma@gmail.com` (usado para todas as funções)
- **Senha**: `ofdf qopt wduz ahxl`
- **E-mail de Teste**: `qualquer@email.com` (para onde enviar o teste)

#### **Resultado:**
```
De: suportesanma@gmail.com
Para: qualquer@email.com
```

O sistema usa **um único e-mail** para:
- Login no servidor SMTP
- Remetente nas mensagens
- E-mail padrão do sistema
- Recuperação de senha automática

## 🔐 Segurança e Validações

### 🛡️ **Validações Implementadas**
- **CNPJ/CPF**: Validação matemática completa
- **E-mail**: Validação de formato
- **CEP**: Validação e busca automática de endereço
- **Campos obrigatórios**: Validação front-end e back-end
- **Senhas**: Criptografadas no banco de dados

### 🔒 **Controle de Acesso**
- **Apenas administradores** podem acessar
- Autenticação obrigatória
- Proteção CSRF em todos os formulários

### 🚨 **CNPJ Especial da Empresa**
O CNPJ `77.766.483/0001-64` é o CNPJ real da empresa WebReceptivo e é aceito pelo sistema mesmo sendo matematicamente inválido. Todos os outros CNPJs devem passar pela validação matemática normal.

## 🐳 Compatibilidade Docker

### ✅ **Totalmente Compatível**
- Todas as dependências estão em `requirements.txt`
- Funciona no ambiente Docker de produção
- Configurações aplicadas automaticamente

### 🔄 **Aplicação Automática SMTP**
O sistema aplica automaticamente as configurações SMTP do banco de dados ao Django:
- **Middleware**: `company_settings.middleware.DynamicSMTPMiddleware`
- **Comando**: `python manage.py apply_smtp`
- **Aplicação em tempo real**: Na primeira requisição

## 🛠️ Arquitetura Técnica

### 📁 **Estrutura do Projeto**
```
company_settings/
├── models.py          # CompanySettings, SystemSettings, SMTPSettings
├── forms.py           # Formulários com validação completa
├── views.py           # Views + endpoints AJAX
├── middleware.py      # Aplicação dinâmica SMTP
└── management/
    └── commands/
        └── apply_smtp.py  # Comando para aplicar SMTP

templates/company_settings/
├── base.html          # Layout base com sidebar
├── overview.html      # Dashboard principal
├── company.html       # Formulário da empresa
├── system.html        # Configurações de sistema
└── smtp.html          # Configurações SMTP
```

### 🔌 **Endpoints AJAX**
- **Teste SMTP**: `/configuracoes/ajax/test-smtp/`
- **Data/Hora Atual**: `/configuracoes/ajax/current-datetime/`
- **Validar CEP**: `/configuracoes/ajax/validate-cep/`

## 📋 Auditoria

### 📊 **Log de Alterações**
O sistema registra automaticamente:
- Todas as mudanças de configurações
- Usuário responsável pela alteração
- Data/hora da modificação
- IP de origem
- Dados alterados (antes e depois)

### 🔍 **Visualizar Logs**
- Acesse: `/audit/logs/`
- Filtre por: ação, usuário, data, status
- Exporte para CSV

## 🚀 Próximos Passos (Opcional)

### 🎯 **Melhorias Futuras**
1. **Backup/Restore**: Exportar/importar configurações
2. **Multi-idioma**: Suporte a internacionalização
3. **API REST**: Endpoints para integrações externas
4. **Notificações**: Alertas para mudanças críticas

## 📞 Suporte

### 🐛 **Problemas Comuns**
1. **E-mail não envia**: Verifique senha de app do Gmail
2. **CEP não preenche**: Verifique conexão com API ViaCEP
3. **CNPJ inválido**: Use o CNPJ da empresa ou um válido matematicamente

### 🔧 **Comandos Úteis**
```bash
# Aplicar configurações SMTP manualmente
python manage.py apply_smtp

# Testar SMTP via comando
python manage.py apply_smtp --test

# Recriar dados demo
python setup_demo.py
```

---

**📅 Atualizado**: Outubro 2025  
**✅ Status**: Sistema Completo e Funcional  
**🏢 Empresa**: WebReceptivo Ltda (CNPJ: 77.766.483/0001-64)
