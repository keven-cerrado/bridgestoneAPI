# API Bridgestone - Documentação

Uma API FastAPI para integração de dados de faturamento com a plataforma ScannTech da Bridgestone.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Instalação e Execução](#instalação-e-execução)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Endpoints da API](#endpoints-da-api)
- [Configurações](#configurações)
- [Logs](#logs)
- [Desenvolvimento](#desenvolvimento)
- [Troubleshooting](#troubleshooting)
- [Documentação Adicional](#documentação-adicional)

## 🎯 Visão Geral

A API Bridgestone é responsável por:
- Extrair dados de faturamento do banco de dados interno
- Transformar os dados para o formato exigido pela API ScannTech
- Enviar faturamentos, fechamentos e gerenciar cancelamentos/devoluções
- Fornecer endpoints para consulta e reenvio de dados
- Monitorar e registrar todas as operações através de logs

## 🛠️ Tecnologias Utilizadas

- **Python 3.10**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **PostgreSQL** - Banco de dados principal
- **Docker & Docker Compose** - Containerização
- **Uvicorn** - Servidor ASGI
- **Pandas** - Manipulação de dados
- **Telegram Bot** - Notificações
- **SSL/HTTPS** - Segurança

## 📋 Pré-requisitos

- Docker e Docker Compose instalados
- Acesso ao banco de dados PostgreSQL
- Certificados SSL válidos
- Credenciais de acesso à API ScannTech
- Token do bot Telegram (opcional)

## ⚙️ Configuração do Ambiente

### 1. Arquivo .env

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Configurações do Banco de Dados
PG_HOST='seu_host_postgresql'
PG_PORT='5432'
PG_USER='seu_usuario'
PG_PASSWORD='sua_senha'
PG_DATABASE='nome_do_banco'
PG_SCHEMA='schema_do_banco'

SQLALCHEMY_DATABASE_URL="postgresql+psycopg2://usuario:senha@host:porta/banco"

# Credenciais da API ScannTech
API_USUARIO='seu_usuario_scanntech'
API_SENHA='sua_senha_scanntech'

# Token do Bot Telegram (opcional)
BOT_TOKEN_TELEGRAM='seu_token_telegram'
```

### 2. Certificados SSL

Coloque os certificados SSL nos seguintes caminhos:
- `app/cert/cert.pem` - Certificado público
- `app/cert/key.pem` - Chave privada

## 🚀 Instalação e Execução

### Usando Docker (Recomendado)

```bash
# Clone o repositório
git clone git@github.com:keven-cerrado/bridgestoneAPI.git
cd bridgestoneAPI

# Construa e execute com Docker Compose
docker-compose up -d --build
```

### Execução Local

```bash
# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
uvicorn app.main:app --host 0.0.0.0 --port 8185 --ssl-keyfile app/cert/key.pem --ssl-certfile app/cert/cert.pem
```

A API estará disponível em: `https://localhost:8185`

## 📁 Estrutura do Projeto

```
bridgestoneAPI/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicação principal FastAPI
│   ├── configuracoes.py        # Configurações globais
│   ├── database.py             # Configuração do banco de dados
│   ├── dependencies.py         # Dependências da aplicação
│   ├── log_config.py           # Configuração de logs
│   ├── cert/                   # Certificados SSL
│   │   ├── cert.pem
│   │   └── key.pem
│   └── routers/                # Roteadores da API
│       ├── clientes/           # Endpoints de clientes
│       ├── envios/             # Endpoints de envios
│       │   └── envios.py
│       ├── faturamento/        # Endpoints de faturamento
│       │   ├── crud.py         # Operações de banco
│       │   ├── faturamento.py  # Endpoints principais
│       │   ├── models.py       # Modelos SQLAlchemy
│       │   ├── schemas.py      # Schemas Pydantic
│       │   ├── scriptSend.py   # Scripts de envio
│       │   └── utils.py        # Funções utilitárias
│       └── login/              # Autenticação (desabilitada)
├── data/                       # Dados exportados
├── logs/                       # Logs da aplicação
├── docker-compose.yaml         # Configuração Docker
├── dockerfile                  # Imagem Docker
├── requirements.txt            # Dependências Python
├── run.sh                      # Script de inicialização
└── README.md                   # Esta documentação
```

## 🔗 Endpoints da API

### Faturamento

#### `GET /faturamento`
Obtém lista de faturamentos com paginação.

**Parâmetros:**
- `skip` (int, opcional): Registros a pular (padrão: 0)
- `limit` (int, opcional): Limite de registros (padrão: 100)

#### `GET /faturamento/`
Obtém faturamentos por período e filial.

**Parâmetros:**
- `start` (str): Data inicial (formato: YYYY-MM-DD)
- `end` (str): Data final (formato: YYYY-MM-DD)
- `centro` (str, opcional): Código da filial

#### `GET /fechamento`
Obtém dados de fechamento diário.

**Parâmetros:**
- `start` (str, opcional): Data inicial (formato: dd/mm/yyyy)
- `end` (str, opcional): Data final (formato: dd/mm/yyyy)
- `centro` (str, opcional): Código da filial

#### `GET /solicitacoes`
Lista solicitações de reenvio pendentes.

**Parâmetros:**
- `centro` (str, opcional): Código da filial

### Envios

#### `GET /enviar/faturamento`
Envia faturamento do dia atual para todas as filiais.

#### `GET /enviar/faturamento/`
Envia faturamento para período e filial específicos.

**Parâmetros:**
- `start` (str, opcional): Data inicial (formato: dd/mm/yyyy)
- `end` (str, opcional): Data final (formato: dd/mm/yyyy)
- `centro` (str, opcional): Código da filial

#### `GET /enviar/fechamento`
Envia fechamento do dia atual.

#### `GET /enviar/fechamento/`
Envia fechamento para período específico.

**Parâmetros:**
- `start` (str, opcional): Data inicial (formato: dd/mm/yyyy)
- `end` (str, opcional): Data final (formato: dd/mm/yyyy)
- `centro` (str, opcional): Código da filial

#### `GET /verificar/reenvio`
Verifica e executa reenvios automáticos.

**Parâmetros:**
- `centro` (str, opcional): Código da filial

#### `POST /executar/reenvio`
Executa reenvio manual.

**Parâmetros:**
- `data` (str): Data para reenvio (formato: dd/mm/yyyy)
- `tipo` (str): Tipo de reenvio ('movimientos' ou 'cierresDiarios')
- `centro` (str): Código da filial

#### `GET /verificar/cancelamentos`
Verifica e processa cancelamentos.

**Parâmetros:**
- `centro` (str, opcional): Código da filial

#### `GET /verificar/devolucoes`
Verifica e processa devoluções.

**Parâmetros:**
- `centro` (str, opcional): Código da filial

## ⚙️ Configurações

### Arquivo configuracoes.py

Principais configurações que podem ser ajustadas:

```python
# Flag para agrupar itens não-Bridgestone como "Outros"
agrupar_outros_flag = True

# Tempo para manter arquivos de log (dias)
tempo_manter_arquivo = 60

# URLs da API ScannTech
url_base = "http://parceiro.scanntech.com/api-minoristas/api"  # Produção
# url_base = "https://test-parceiro.scanntech.com/api-minoristas/api"  # Teste

# IDs da empresa
idEmpresa = 88975  # Produção
# idEmpresa = 74984  # Teste

# Horários de execução automática
hora_envio_faturamento = "21:00"
hora_verificacao_reenvio = "21:05"
hora_verificacao_cancelamentos = "21:10"
hora_verificacao_devolucoes = "21:15"

# Lista de filiais
filiais = ["0101", "0102", "0103", "0104", "0105", "0106", "0107", "0201"]
```

### Configurações de Banco de Dados

O banco é configurado através das variáveis de ambiente no arquivo `.env`. A aplicação usa SQLAlchemy com PostgreSQL.

## 📊 Logs

Os logs são configurados para rotacionar diariamente e são salvos em:
- `logs/app.log` - Log atual
- `logs/app.log.YYYY-MM-DD` - Logs de dias anteriores

Níveis de log disponíveis:
- **DEBUG**: Informações detalhadas para desenvolvimento
- **INFO**: Informações gerais de funcionamento
- **WARNING**: Avisos sobre situações que merecem atenção
- **ERROR**: Erros que impedem operações específicas

## 🔧 Desenvolvimento

### Adicionando Novos Endpoints

1. Crie ou edite arquivos em `app/routers/`
2. Defina schemas em `schemas.py`
3. Implemente a lógica em `crud.py` (para banco de dados)
4. Adicione utilitários em `utils.py` se necessário
5. Registre o router em `main.py`

### Estrutura de um Router

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas
from ...database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/exemplo", response_model=schemas.Exemplo)
async def endpoint_exemplo(db: Session = Depends(get_db)):
    # Sua lógica aqui
    pass
```

### Testes

Para testar os endpoints, você pode usar:
- **Postman** ou **Insomnia**
- **curl** via linha de comando
- **httpie**
- Interface automática do FastAPI em `https://localhost:8185/docs`

### Exemplo de Teste com curl

```bash
# Teste básico de faturamento
curl -k -X GET "https://localhost:8185/faturamento?skip=0&limit=10"

# Teste de envio de faturamento para data específica
curl -k -X GET "https://localhost:8185/enviar/faturamento/?start=01/01/2024&end=01/01/2024&centro=0101"
```

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão com Banco de Dados
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Solução:**
- Verifique as configurações no arquivo `.env`
- Confirme se o banco está acessível
- Teste a conectividade de rede

#### 2. Erro de Certificado SSL
```
ssl.SSLError: [SSL] certificate verify failed
```
**Solução:**
- Verifique se os certificados estão no diretório correto
- Confirme se os certificados não expiraram
- Teste com certificados auto-assinados para desenvolvimento

#### 3. Erro na API ScannTech
```
HTTPException: 401 Unauthorized
```
**Solução:**
- Verifique as credenciais no arquivo `.env`
- Confirme se as credenciais não expiraram
- Teste a conectividade com a API externa

#### 4. Container Docker não inicia
```
docker: Error response from daemon
```
**Solução:**
- Verifique se as portas não estão em uso
- Confirme se o Docker tem permissões adequadas
- Revise os logs do container: `docker logs api_bridgestone`

### Logs de Debug

Para habilitar logs mais detalhados, edite `log_config.py`:

```python
# Mude o nível de log para DEBUG
logging.getLogger().setLevel(logging.DEBUG)
```

### Testando Conectividade

```bash
# Teste de conexão com a API
curl -k -X GET "https://localhost:8185/faturamento" -v

# Verificar logs em tempo real
docker logs -f api_bridgestone

# Verificar status do container
docker ps | grep api_bridgestone
```

## 📈 Monitoramento

### Verificação de Saúde

A API não possui endpoint de health check dedicado, mas você pode usar:

```bash
curl -k -X GET "https://localhost:8185/faturamento?limit=1"
```

### Métricas Importantes

- **Taxa de sucesso dos envios**: Monitore os logs para verificar se os envios estão sendo bem-sucedidos
- **Tempo de resposta**: Monitore a performance dos endpoints
- **Erros de conexão**: Acompanhe problemas de conectividade com banco e API externa
- **Utilização de memória**: Monitore o uso de recursos do container

## 📚 Documentação Adicional

Este projeto possui documentação abrangente dividida em arquivos específicos:

### 📖 Documentos Principais
- **[README.md](README.md)** - Documentação principal (este arquivo)
- **[TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)** - Arquitetura técnica e fluxos de dados
- **[CRUD_DOCUMENTATION.md](CRUD_DOCUMENTATION.md)** - **Documentação detalhada do módulo CRUD** ⭐
- **[EXAMPLES.md](EXAMPLES.md)** - Exemplos práticos de uso da API
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Guia de solução de problemas
- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de mudanças e versionamento

### 🎯 Documentação por Área

#### Para Desenvolvedores Iniciantes
1. Comece com o [README.md](README.md) para visão geral
2. Configure o ambiente seguindo os passos aqui
3. Teste com os exemplos do [EXAMPLES.md](EXAMPLES.md)

#### Para Análise Técnica
1. **[CRUD_DOCUMENTATION.md](CRUD_DOCUMENTATION.md)** - **ESSENCIAL** para entender cálculos e filtros
2. [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md) - Arquitetura completa
3. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Solução de problemas

#### Para Manutenção
1. [CHANGELOG.md](CHANGELOG.md) - Histórico de mudanças
2. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problemas comuns
3. [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md) - Checklist de manutenção

### ⚡ Documento Destacado: CRUD_DOCUMENTATION.md

O arquivo **[CRUD_DOCUMENTATION.md](CRUD_DOCUMENTATION.md)** é **fundamental** para entender:
- 🧮 **Cálculos financeiros** (ICMS ST, taxas de importação)
- 🔍 **Filtros de dados** (quais vendas são incluídas/excluídas)
- 📊 **Regras de negócio** (produtos Bridgestone vs "Outros")
- 🔄 **Transformação de dados** (formato interno → ScannTech)
- 💰 **Mapeamentos** (formas de pagamento, códigos de produto)

**Este documento é essencial para qualquer desenvolvedor que precise modificar a lógica de cálculos ou filtros!**

---

**Última atualização:** Agosto 2025
**Versão da API:** 1.0.0
