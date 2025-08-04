# TermoApp - Gerador de Termos de Entrega

Um gerador automatizado de termos de entrega para as empresas PACTO e MOOVZ. Conecta-se à API do Google Sheets para buscar informações de patrimônios e insere automaticamente os dados no documento de termo de entrega. Isso agiliza e otimiza o processo de registro de equipamentos, eliminando a necessidade de acessar e inserir manualmente cada dado no arquivo.

## 🚀 Funcionalidades

- **Geração Automática**: Criação automática de documentos de entrega (.docx)
- **Conversão PDF**: Conversão automática para PDF usando LibreOffice
- **Integração Google Sheets**: Busca de dados de patrimônios via Google Sheets API
- **Validação em Tempo Real**: Validação de formulário com feedback visual
- **Logging Estruturado**: Logs em formato JSON para melhor observabilidade
- **Sistema de Cache**: Cache com suporte Redis e fallback em memória
- **Tratamento de Erros**: Sistema robusto de tratamento de exceções
- **Monitoramento**: Rastreamento de requisições e monitoramento de performance

## 📋 Pré-requisitos

- [Python](https://www.python.org/downloads/) versão **3.8 ou superior**
- [Poetry](https://python-poetry.org/docs/#installation) para gerenciamento de dependências
- [LibreOffice](https://www.libreoffice.org/download/download/) para conversão PDF
- Conta de serviço do Google Sheets API

## 🛠️ Instalação

1. **Clone o repositório:**
```bash
git clone https://github.com/your-username/termoapp-web.git
cd termoapp-web
```

2. **Instale as dependências:**
```bash
poetry install
```

3. **Configure as variáveis de ambiente:**
Crie um arquivo `.env` na raiz do projeto:
```env
# Obrigatórias
SHEET_ID=your_google_sheet_id_here
CREDENTIALS=credentials/service_account.json

# Opcionais
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
LOG_LEVEL=INFO
```

4. **Configure as credenciais do Google Sheets:**
- Coloque seu arquivo `service_account.json` na pasta `credentials/`
- Certifique-se de que o arquivo está referenciado corretamente na variável `CREDENTIALS`

## 🚀 Como Executar

### Desenvolvimento
```bash
poetry run python src/app.py
```

### Produção
```bash
poetry run flask run --host=0.0.0.0 --port=5000
```

### Docker
```bash
docker build -t termoapp .
docker run -p 5000:5000 termoapp
```

## 📖 Como Usar

1. Acesse a interface web em `http://localhost:5000`
2. Preencha o formulário com:
   - **Nome**: Nome completo do funcionário
   - **Função**: Cargo/função do funcionário
   - **Departamento**: Departamento selecionado
   - **Telefone**: Número de telefone (11 dígitos)
   - **Empresa**: PACTO ou MOOVZ
   - **Patrimônios**: Lista de equipamentos/patrimônios
   - **Observações**: Observações adicionais (opcional)

3. Clique em "Gerar Documento"
4. O sistema irá:
   - Validar os dados do formulário
   - Buscar informações dos patrimônios no Google Sheets
   - Gerar o documento .docx
   - Converter para PDF
   - Disponibilizar para download

## 🏗️ Estrutura do Projeto

```
termoapp-web/
├── src/
│   ├── app.py              # Aplicação Flask principal
│   ├── utils.py            # Utilitários para documentos e Google Sheets
│   ├── logger.py           # Sistema de logging estruturado
│   ├── exceptions.py       # Exceções customizadas
│   ├── cache.py            # Sistema de cache
│   ├── config.py           # Configurações da aplicação
│   ├── static/
│   │   ├── enhanced.js     # JavaScript com validação em tempo real
│   │   ├── styles.css      # Estilos CSS
│   │   └── logo2.png       # Logo da aplicação
│   └── templates/
│       └── index.html      # Template principal
├── modelos/                # Modelos de documentos (.docx)
├── credentials/            # Credenciais do Google Sheets
├── entrega_docx/          # Documentos .docx gerados
├── entrega_pdf/           # Documentos PDF gerados
├── requirements.txt       # Dependências Python
├── pyproject.toml        # Configuração Poetry
└── Dockerfile            # Configuração Docker
```

## 🔧 Configuração do Google Sheets

1. **Crie um projeto no Google Cloud Console**
2. **Ative a Google Sheets API**
3. **Crie uma conta de serviço**
4. **Baixe o arquivo JSON de credenciais**
5. **Compartilhe sua planilha com o email da conta de serviço**

### Como obter o Sheet ID:
- Abra sua planilha no Google Sheets
- O ID está na URL: `https://docs.google.com/spreadsheets/d/`**`SHEET_ID_AQUI`**`/edit`

## 🐛 Solução de Problemas

### Erro de credenciais:
- Verifique se o arquivo `service_account.json` está na pasta `credentials/`
- Confirme se a variável `CREDENTIALS` está configurada corretamente

### Erro de Sheet ID:
- Verifique se o `SHEET_ID` está correto na URL da planilha
- Confirme se a conta de serviço tem acesso à planilha

### Erro de LibreOffice:
- Instale o LibreOffice no sistema
- Configure o caminho correto na variável `LIBREOFFICE_PATH` (se necessário)

## 📝 Logs

Os logs são salvos em formato JSON estruturado e incluem:
- Requisições HTTP com IDs únicos
- Operações do Google Sheets
- Geração de documentos
- Erros e exceções
- Métricas de performance

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Criador

**Enrique Ribeiro**

## 📞 Suporte

Para suporte, entre em contato através de:
- Issues no GitHub
