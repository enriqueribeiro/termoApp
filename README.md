# TermoApp - Gerador de Termos de Entrega

Um gerador automatizado de termos de entrega com templates diversos. Conecta-se à API do Google Sheets para buscar informações de patrimônios e insere automaticamente os dados no documento de termo de entrega. Isso agiliza e otimiza o processo de registro de equipamentos, eliminando a necessidade de acessar e inserir manualmente cada dado no arquivo.

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

## 📝 Logs

Os logs são salvos em formato JSON estruturado e incluem:
- Requisições HTTP com IDs únicos
- Operações do Google Sheets
- Geração de documentos
- Erros e exceções
- Métricas de performance

## 👨‍💻 Criador

**Enrique Ribeiro**
