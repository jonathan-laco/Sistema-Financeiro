# 💼 Sistema Financeiro Pessoal e MEI

Bem-vindo ao **Sistema Financeiro Pessoal e MEI**! Este projeto foi cuidadosamente desenvolvido para resolver um problema real: **a dificuldade de gerenciar finanças pessoais e empresariais de forma simples e eficiente**. Seja você um usuário comum ou um Microempreendedor Individual (MEI), este sistema foi pensado para **facilitar sua vida financeira** e trazer mais **organização e clareza** ao seu dia a dia. 🌟

---
## ✨ Acesse o sistema de testes

👉 [Clique aqui para acessar o sistema financeiro](https://sistema-financeiro-teste.onrender.com/)  
*Ambiente disponível apenas para fins de teste.*

⚠️ **Avisos importantes:**

- Pedimos por gentileza que **não altere a senha do usuário `admin`**.  
  Ela foi deixada aberta intencionalmente para que todos possam explorar as funções administrativas livremente.

  > ✨ **Tenha consciência**: assim como você acessou, outras pessoas também gostariam de testar, observar e aprender com o sistema.

- ⚙️ A função de **backup** **não está disponível nesta versão hospedada no Render**.  
  No entanto, o recurso **está implementado corretamente no código-fonte** e pode ser utilizado em outras implantações.

- ⏳ **A versão hospedada no Render pode apresentar lentidão**, devido ao uso da **versão gratuita** do serviço.  
  Este projeto **não é destinado para uso real** e foi feito **exclusivamente para testes**.

- 📑 **Importante**: Evite fornecer **documentos reais** (como CNPJ, documentos de notas fiscais e senhas) nas contas MEI neste projeto de testes.  
  O sistema não deve ser usado como um projeto real ou para armazenar dados sensíveis.

- 🔄 **Aviso sobre o banco de dados**: Caso o seu usuário não exista mais ao acessar, é porque o banco de dados foi **resetado periodicamente** para não manter informações de longo prazo no sistema de testes.

![image](https://github.com/user-attachments/assets/698c7baa-ef8f-4098-94dd-bd1aede4f084)

## 🎯 Por Que Usar Este Sistema?

Sabemos que lidar com finanças pode ser desafiador, mas com o **Sistema Financeiro Pessoal e MEI**, você terá uma ferramenta poderosa e intuitiva para:

- **Organizar suas finanças** em um só lugar.
- **Acompanhar receitas e despesas** com facilidade.
- **Planejar o futuro financeiro** com metas claras e alcançáveis.
- **Evitar surpresas desagradáveis**, como ultrapassar o limite de faturamento MEI.

Este sistema foi projetado com **carinho e atenção aos detalhes**, para que você possa focar no que realmente importa: **alcançar seus objetivos financeiros**. 💖

---

## ✨ Funcionalidades Que Fazem a Diferença

### 🔑 Administração

- Gerencie usuários: aprove, edite ou exclua contas.
- Configure o sistema: habilite ou desabilite cadastros MEI e permissões de registro.
- Monitore logs de acesso para maior segurança.
- Gere relatórios administrativos detalhados.
- Gerencie solicitações de acesso ao bot do Telegram, aprovando, rejeitando, renovando ou desativando tokens de usuários.
- **Realize backups do banco de dados diretamente no Discord(ADMIN)**, evitando perda de dados em problemas críticos. Para mais informações sobre como configurar webhooks no Discord, consulte a [documentação oficial de Webhooks do Discord](https://discord.com/developers/docs/resources/webhook).

### 🏦 Usuário Comum

- Controle suas contas bancárias: adicione, edite e exclua.
- Registre receitas e despesas de forma prática.
- Visualize relatórios financeiros mensais e anuais.
- Crie metas financeiras e acompanhe seu progresso.

### 📊 Usuário MEI

- Separe transações pessoais e empresariais.
- Faça upload de notas fiscais (PDF, JPG, JPEG ou PNG).
- Gere relatórios específicos para MEI com gráficos e tabelas.
- Receba alertas ao se aproximar do limite anual de faturamento de R$ 81.000,00.

### 🌟 Funcionalidades Gerais

- **Relatórios Personalizados**: Imprima ou exporte relatórios financeiros.
- **Modo Claro e Escuro**: Escolha o tema que mais combina com você.
- **Filtros Avançados**: Filtre transações por conta, categoria, tipo e presença de nota fiscal.
- **Gráficos Interativos**: Visualize dados financeiros com gráficos dinâmicos (requer internet para carregar via CDN).
- **Integração com Telegram**: Registre receitas e despesas direto pelo bot, usando os comandos `/entrar`, `/sair` e `/cancelar`, com autenticação por token aprovado pelo administrador.

---

## 🚀 Benefícios de Usar o Sistema

### Para Usuários Comuns:

- **Controle Total das Finanças**: Organize suas contas e transações de forma prática.
- **Planejamento Simplificado**: Crie metas financeiras e acompanhe seu progresso.
- **Relatórios Detalhados**: Entenda melhor seus gastos com gráficos e tabelas.

### Para Usuários MEI:

- **Gestão Empresarial Simplificada**: Controle receitas e despesas do CNPJ separadamente.
- **Organização de Notas Fiscais**: Mantenha tudo pronto para auditorias.
- **Relatórios Específicos**: Acompanhe o faturamento e evite ultrapassar limites legais.

### Para Todos:

- **Eficiência**: Pode ser executado em um computador caseiro, sem necessidade de servidores robustos.
- **Segurança**: Controle de acesso com login e senha, além de logs de auditoria.
- **Simplicidade**: Interface amigável e fácil de usar, mesmo para quem não tem experiência com sistemas financeiros.

---

## 🛠️ Como Usar

1. **Login Inicial**:
   - **Administrador**:
     - Usuário: `admin`
     - Senha: `admin123`
   - Após o login, configure o sistema e gerencie usuários.
2. **Usuários**:
   - Cadastre-se (se permitido) ou peça aprovação do administrador.
   - Comece a gerenciar suas contas, transações e metas.
3. **Relatórios**:
   - Acesse relatórios mensais ou anuais e imprima ou exporte para Excel.
4. **Telegram**:
   - Em Configurações > Telegram, solicite acesso ao bot.
   - Após a aprovação do administrador, copie o token gerado.
   - No Telegram, use `/entrar`, cole o token e registre transações pelo menu guiado.

---

## 🌐 Ambiente de Execução

⚠️ Este sistema foi projetado para **uso interno**, como em **máquinas locais** ou **redes intranet**. Ele **não é recomendado para exposição direta à internet**, mas precisa de conexão para carregar gráficos via **CDN**.

---

## 🔧 Pontos de Melhoria

Sabemos que todo sistema pode evoluir, e este não é diferente. Algumas áreas do código ainda podem ser **refatoradas** para melhorar a organização e a manutenção. Estamos comprometidos em tornar o sistema cada vez mais eficiente e robusto com o tempo. 💡

---

## 📜 Licença

Este projeto será licenciado sob a [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), permitindo que você o utilize e adapte conforme suas necessidades, com total transparência e liberdade.

---

## 📥 Como Baixar e Instalar

Siga os passos abaixo para configurar o **Sistema Financeiro Pessoal e MEI** no seu ambiente local:

1. **Clone o Repositório**:

   ```bash
   git clone https://github.com/jonathan-laco/finance-managerV1.git
   cd finance-managerV1
   ```

2. **Crie e Ative um Ambiente Virtual**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Instale as Dependências**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Banco de Dados**:
   - O projeto já vem configurado com o **SQLite** como banco de dados padrão.
   - O script `seed.py` será executado automaticamente na primeira inicialização para popular o banco com dados iniciais.

5. **Configuração do Telegram (opcional)**:
   - Crie um bot pelo [@BotFather](https://t.me/botfather).
   - Copie o token gerado e adicione no arquivo `.env`:

   ```env
   TELEGRAM_BOT_TOKEN=SEU_TOKEN_DO_BOTFATHER
   ```

   - Em desenvolvimento, ao iniciar o sistema com `python run.py`, o bot será iniciado automaticamente se essa variável estiver configurada.
   - Em produção com Waitress, Gunicorn ou outro servidor WSGI, rode o bot em um processo separado usando `bot_worker.py`.

---

## 🖥️ Executando o Sistema

### Modo Desenvolvimento

Para rodar o sistema em modo de desenvolvimento, utilize o comando:

```bash
python run.py
```

### Modo Produção

Para rodar o sistema em produção, utilize o **Waitress** (servidor WSGI para Python). Certifique-se de que o Waitress está instalado:

```bash
pip install waitress
```

Em seguida, execute o sistema com:

```bash
waitress-serve --port=8080 run:app
```

### No Linux

No Linux, você pode usar o **Gunicorn** como alternativa ao Waitress. Instale o Gunicorn:

```bash
pip install gunicorn
```

E execute o sistema com:

```bash
gunicorn -w 4 -b 0.0.0.0:8080 run:app
```

### Bot do Telegram em Produção

Quando o sistema web estiver rodando com Waitress, Gunicorn ou outro servidor WSGI, execute o bot do Telegram em um processo separado. Isso evita que o bot dependa do ciclo de vida dos workers do servidor web.

Em um terminal/processo, rode a aplicação web:

```bash
gunicorn -w 4 -b 0.0.0.0:8080 run:app
```

Em outro terminal/processo, rode o worker do Telegram:

```bash
python bot_worker.py
```

No Windows com ambiente virtual, o comando pode ser:

```bash
.\venv\Scripts\python.exe bot_worker.py
```

Mantenha apenas uma instância do `bot_worker.py` em execução. Rodar mais de uma instância pode causar conflito no polling do Telegram ou respostas duplicadas.

---

Desenvolvido com ❤️ para transformar a maneira como você gerencia suas finanças. Experimente e veja como é fácil alcançar seus objetivos financeiros com o **Sistema Financeiro Pessoal e MEI**! 🌟

**Desenvolvido por Jonathan Laco**

## 🎥 Demonstração do Projeto

Confira a demonstração do **Sistema Financeiro Pessoal e MEI** no YouTube:

[![Demonstração do Projeto](https://img.youtube.com/vi/Ja-9q4DmsPk/0.jpg)](https://youtu.be/Ja-9q4DmsPk)
