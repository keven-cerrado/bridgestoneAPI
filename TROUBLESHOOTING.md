# Guia de Troubleshooting - API Bridgestone

Este guia fornece soluções para problemas comuns que podem ocorrer com a API Bridgestone.

## 📋 Índice

- [Problemas de Conexão](#problemas-de-conexão)
- [Erros de SSL/Certificados](#erros-de-sslcertificados)
- [Problemas de Banco de Dados](#problemas-de-banco-de-dados)
- [Erros da API ScannTech](#erros-da-api-scanntech)
- [Problemas de Docker](#problemas-de-docker)
- [Erros de Logs e Monitoramento](#erros-de-logs-e-monitoramento)
- [Performance](#performance)
- [Ferramentas de Debug](#ferramentas-de-debug)

## 🔌 Problemas de Conexão

### Erro: "Connection refused"

**Sintomas:**
```
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='localhost', port=8185): Max retries exceeded
```

**Possíveis Causas e Soluções:**

1. **Serviço não está rodando**
   ```bash
   # Verificar se o container está ativo
   docker ps | grep api_bridgestone
   
   # Se não estiver, iniciar
   docker-compose up -d
   ```

2. **Porta está sendo usada por outro processo**
   ```powershell
   # Windows - verificar porta 8185
   netstat -ano | findstr :8185
   
   # Se houver outro processo, parar ou mudar a porta no docker-compose.yaml
   ```

3. **Firewall bloqueando a conexão**
   ```bash
   # Verificar regras do firewall
   # Windows: Verificar Windows Firewall
   # Linux: sudo ufw status
   ```

### Erro: "SSL: CERTIFICATE_VERIFY_FAILED"

**Sintomas:**
```
requests.exceptions.SSLError: HTTPSConnectionPool(host='localhost', port=8185): SSL: CERTIFICATE_VERIFY_FAILED
```

**Soluções:**

1. **Para desenvolvimento - desabilitar verificação SSL**
   ```python
   import urllib3
   urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
   
   # Em requests
   response = requests.get(url, verify=False)
   ```

2. **Para produção - verificar certificados**
   ```bash
   # Verificar validade do certificado
   openssl x509 -in app/cert/cert.pem -text -noout
   
   # Verificar se a chave privada corresponde
   openssl rsa -in app/cert/key.pem -check
   ```

## 🔐 Erros de SSL/Certificados

### Erro: "SSL context error"

**Sintomas:**
```
ssl.SSLError: [SSL: NO_PRIVATE_KEY_FILE] no such file (app/cert/key.pem)
```

**Soluções:**

1. **Verificar se os arquivos existem**
   ```bash
   ls -la app/cert/
   # Deve mostrar cert.pem e key.pem
   ```

2. **Gerar certificados auto-assinados para desenvolvimento**
   ```bash
   # Criar diretório se não existir
   mkdir -p app/cert
   
   # Gerar certificado auto-assinado
   openssl req -x509 -newkey rsa:4096 -keyout app/cert/key.pem -out app/cert/cert.pem -days 365 -nodes -subj "/C=BR/ST=State/L=City/O=Organization/CN=localhost"
   ```

3. **Corrigir permissões**
   ```bash
   chmod 600 app/cert/key.pem
   chmod 644 app/cert/cert.pem
   ```

### Certificado Expirado

**Verificar expiração:**
```bash
openssl x509 -in app/cert/cert.pem -noout -enddate
```

**Renovar certificado:**
```bash
# Backup do certificado atual
cp app/cert/cert.pem app/cert/cert.pem.backup
cp app/cert/key.pem app/cert/key.pem.backup

# Gerar novo certificado
openssl req -x509 -newkey rsa:4096 -keyout app/cert/key.pem -out app/cert/cert.pem -days 365 -nodes -subj "/C=BR/ST=State/L=City/O=Organization/CN=localhost"

# Reiniciar o container
docker-compose restart
```

## 🗄️ Problemas de Banco de Dados

### Erro: "could not connect to server"

**Sintomas:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server: Connection refused
```

**Diagnóstico:**

1. **Testar conectividade básica**
   ```bash
   # Testar ping
   ping 91.108.126.196
   
   # Testar porta específica
   telnet 91.108.126.196 5452
   ```

2. **Verificar configurações no .env**
   ```bash
   cat .env | grep PG_
   # Verificar se host, porta, usuário e senha estão corretos
   ```

3. **Testar conexão direta**
   ```bash
   # Usar psql para testar
   psql -h 91.108.126.196 -p 5452 -U postgres -d datalake
   ```

**Soluções:**

1. **Verificar VPN/Rede**
   ```bash
   # Se usando VPN, verificar se está conectada
   # Verificar regras de firewall da rede
   ```

2. **Verificar se o servidor está ativo**
   ```bash
   # Contatar administrador do banco
   # Verificar logs do servidor PostgreSQL
   ```

### Erro: "password authentication failed"

**Sintomas:**
```
psycopg2.OperationalError: FATAL: password authentication failed for user "postgres"
```

**Soluções:**

1. **Verificar credenciais no .env**
   ```bash
   # Confirmar usuário e senha
   grep -E "(PG_USER|PG_PASSWORD)" .env
   ```

2. **Testar credenciais manualmente**
   ```bash
   psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_DATABASE
   ```

### Erro: "relation does not exist"

**Sintomas:**
```
psycopg2.errors.UndefinedTable: relation "tabela_faturamento" does not exist
```

**Diagnóstico:**

1. **Verificar schema configurado**
   ```sql
   -- Conectar ao banco e verificar schemas
   \dn
   
   -- Verificar tabelas no schema
   \dt schema_name.*
   ```

2. **Verificar search_path**
   ```sql
   SHOW search_path;
   ```

**Soluções:**

1. **Ajustar configuração de schema**
   ```python
   # Em database.py, verificar:
   engine = create_engine(
       SQLALCHEMY_DATABASE_URL,
       connect_args={"options": "-c search_path=dbo,public"}
   )
   ```

## 🌐 Erros da API ScannTech

### Erro: "401 Unauthorized"

**Sintomas:**
```
HTTPException: 401 Client Error: Unauthorized for url: http://parceiro.scanntech.com/api-minoristas/api
```

**Soluções:**

1. **Verificar credenciais**
   ```bash
   # Verificar no .env
   grep -E "(API_USUARIO|API_SENHA)" .env
   ```

2. **Testar credenciais manualmente**
   ```bash
   # Testar autenticação
   curl -X GET "http://parceiro.scanntech.com/api-minoristas/api/test" \
     -H "Authorization: Basic $(echo -n 'usuario:senha' | base64)"
   ```

3. **Verificar encoding Base64**
   ```python
   # Testar função de conversão
   from app.configuracoes import converte_base64
   print(converte_base64("seu_usuario", "sua_senha"))
   ```

### Erro: "422 Unprocessable Entity"

**Sintomas:**
```
HTTPException: 422 Client Error: Unprocessable Entity
```

**Diagnóstico:**

1. **Verificar formato dos dados enviados**
   ```python
   # Logs da API mostrarão o JSON enviado
   logger.debug(f"Dados enviados: {json.dumps(data, indent=2)}")
   ```

2. **Validar contra schema esperado**
   ```python
   # Verificar se todos os campos obrigatórios estão presentes
   # Verificar tipos de dados (string, float, int)
   # Verificar formatos de data
   ```

**Soluções:**

1. **Corrigir formato de data**
   ```python
   # ScannTech espera dd/mm/yyyy
   fecha = datetime.now().strftime("%d/%m/%Y")
   ```

2. **Verificar códigos de tipo de pagamento**
   ```python
   # Verificar mapeamento em configuracoes.py
   tipo_pagamento_map = {
       "DINHEIRO": 1,
       "CARTAO_CREDITO": 2,
       # ...
   }
   ```

### Erro: "500 Internal Server Error" da ScannTech

**Sintomas:**
```
HTTPException: 500 Server Error: Internal Server Error
```

**Ações:**

1. **Aguardar e tentar novamente**
   ```python
   # Implementar retry com backoff
   import time
   for attempt in range(3):
       try:
           response = enviar_dados()
           break
       except HTTPException as e:
           if e.status_code == 500 and attempt < 2:
               time.sleep(2 ** attempt)  # Backoff exponencial
               continue
           raise
   ```

2. **Verificar status da API ScannTech**
   ```bash
   # Testar endpoint básico
   curl -I "http://parceiro.scanntech.com/api-minoristas/api"
   ```

## 🐳 Problemas de Docker

### Container não inicia

**Diagnóstico:**
```bash
# Verificar logs do container
docker logs api_bridgestone

# Verificar status
docker ps -a | grep api_bridgestone
```

**Problemas comuns:**

1. **Erro de build**
   ```bash
   # Rebuild forçado
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Porta em uso**
   ```bash
   # Verificar que processo está usando a porta
   netstat -tulpn | grep :8185
   
   # Parar processo ou mudar porta no docker-compose.yaml
   ```

3. **Problemas de permissão**
   ```bash
   # Verificar permissões dos arquivos
   ls -la app/cert/
   
   # Ajustar se necessário
   chmod 644 app/cert/cert.pem
   chmod 600 app/cert/key.pem
   ```

### Container reiniciando constantemente

**Diagnóstico:**
```bash
# Verificar logs para ver o erro
docker logs api_bridgestone --tail 50

# Verificar eventos do Docker
docker events --filter container=api_bridgestone
```

**Soluções comuns:**

1. **Erro no arquivo .env**
   ```bash
   # Verificar sintaxe do .env
   cat .env | grep -v '^#' | grep '='
   ```

2. **Dependência não resolvida**
   ```bash
   # Entrar no container para debug
   docker run -it --rm bridgestoneapi_app bash
   
   # Testar importações
   python -c "import app.main"
   ```

## 📊 Erros de Logs e Monitoramento

### Logs não são gerados

**Verificar configuração:**
```python
# Em log_config.py
import logging
logger = logging.getLogger(__name__)
logger.info("Teste de log")
```

**Verificar permissões:**
```bash
# Verificar se diretório logs existe e tem permissão
ls -la logs/
mkdir -p logs
chmod 755 logs/
```

### Logs crescendo muito

**Soluções:**

1. **Verificar rotação automática**
   ```python
   # Em log_config.py, verificar configuração do TimedRotatingFileHandler
   handler = TimedRotatingFileHandler(
       filename='logs/app.log',
       when='midnight',
       interval=1,
       backupCount=30  # Manter 30 dias
   )
   ```

2. **Limpeza manual**
   ```bash
   # Remover logs antigos
   find logs/ -name "*.log.*" -mtime +30 -delete
   ```

## ⚡ Performance

### API lenta

**Diagnóstico:**

1. **Verificar logs de timing**
   ```python
   import time
   start = time.time()
   resultado = operacao_lenta()
   logger.info(f"Operação levou {time.time() - start:.2f}s")
   ```

2. **Verificar queries do banco**
   ```python
   # Habilitar log de SQL
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   ```

**Soluções:**

1. **Otimizar queries**
   ```python
   # Usar limit e offset para paginação
   query = db.query(Model).offset(skip).limit(limit)
   
   # Usar select específico em vez de SELECT *
   query = db.query(Model.campo1, Model.campo2)
   ```

2. **Implementar cache**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def get_configuracao():
       # Operação custosa
       pass
   ```

### Alto uso de memória

**Diagnóstico:**
```bash
# Verificar uso de memória do container
docker stats api_bridgestone

# Verificar dentro do container
docker exec api_bridgestone ps aux
```

**Soluções:**

1. **Limitar memória do container**
   ```yaml
   # Em docker-compose.yaml
   services:
     app:
       deploy:
         resources:
           limits:
             memory: 512M
   ```

2. **Otimizar processamento de dados**
   ```python
   # Processar em chunks em vez de carregar tudo na memória
   def processar_em_chunks(query, chunk_size=1000):
       offset = 0
       while True:
           chunk = query.offset(offset).limit(chunk_size).all()
           if not chunk:
               break
           for item in chunk:
               yield item
           offset += chunk_size
   ```

## 🛠️ Ferramentas de Debug

### 1. Script de Diagnóstico Completo

```bash
#!/bin/bash
# diagnostic.sh

echo "=== Diagnóstico da API Bridgestone ==="
echo "Data: $(date)"
echo

# Verificar Docker
echo "--- Docker ---"
docker --version
docker-compose --version
docker ps | grep bridgestone

# Verificar conectividade
echo -e "\n--- Conectividade ---"
ping -c 1 91.108.126.196 && echo "✓ Banco acessível" || echo "✗ Banco inacessível"
curl -k -s -o /dev/null -w "%{http_code}" https://localhost:8185/faturamento?limit=1 && echo "✓ API respondendo" || echo "✗ API não responde"

# Verificar certificados
echo -e "\n--- Certificados ---"
if [ -f "app/cert/cert.pem" ]; then
    echo "✓ Certificado existe"
    openssl x509 -in app/cert/cert.pem -noout -enddate
else
    echo "✗ Certificado não encontrado"
fi

# Verificar logs
echo -e "\n--- Logs Recentes ---"
if [ -f "logs/app.log" ]; then
    echo "Últimas 5 linhas dos logs:"
    tail -5 logs/app.log
else
    echo "✗ Log não encontrado"
fi

echo -e "\n=== Fim do Diagnóstico ==="
```

### 2. Debug no Python

```python
# debug.py
import sys
import os
sys.path.append('/code')

from app.database import SessionLocal
from app.configuracoes import headers, url_base
import requests

def test_database():
    """Testa conexão com banco de dados"""
    try:
        db = SessionLocal()
        result = db.execute("SELECT 1").fetchone()
        db.close()
        print("✓ Banco de dados: Conectado")
        return True
    except Exception as e:
        print(f"✗ Banco de dados: {e}")
        return False

def test_scanntech_api():
    """Testa conexão com API ScannTech"""
    try:
        response = requests.get(f"{url_base}/test", headers=headers, timeout=10)
        print(f"✓ API ScannTech: Status {response.status_code}")
        return True
    except Exception as e:
        print(f"✗ API ScannTech: {e}")
        return False

def test_certificates():
    """Testa certificados SSL"""
    cert_path = "/code/app/cert/cert.pem"
    key_path = "/code/app/cert/key.pem"
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        print("✓ Certificados: Encontrados")
        return True
    else:
        print("✗ Certificados: Não encontrados")
        return False

if __name__ == "__main__":
    print("=== Debug da API Bridgestone ===")
    test_database()
    test_scanntech_api()
    test_certificates()
```

### 3. Monitoramento em Tempo Real

```bash
# monitor.sh
#!/bin/bash

watch -n 5 '
echo "=== Status da API Bridgestone ==="
echo "Container: $(docker ps --filter name=api_bridgestone --format "table {{.Status}}")"
echo "CPU/Mem: $(docker stats api_bridgestone --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}")"
echo "Logs recentes:"
docker logs api_bridgestone --tail 3 2>/dev/null || echo "Container não encontrado"
echo "Última atualização: $(date)"
'
```

---

**Importante**: Sempre verifique os logs antes de aplicar qualquer solução. A maioria dos problemas deixa rastros nos logs que podem indicar a causa raiz do problema.
