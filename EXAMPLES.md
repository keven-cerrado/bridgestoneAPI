# Exemplos de Uso - API Bridgestone

Este documento contém exemplos práticos de como usar a API Bridgestone, incluindo requests, responses e casos de uso comuns.

## 📋 Índice

- [Configuração Inicial](#configuração-inicial)
- [Endpoints de Consulta](#endpoints-de-consulta)
- [Endpoints de Envio](#endpoints-de-envio)
- [Gerenciamento de Reenvios](#gerenciamento-de-reenvios)
- [Monitoramento](#monitoramento)
- [Scripts de Automação](#scripts-de-automação)

## ⚙️ Configuração Inicial

### Teste de Conectividade

```bash
# Teste básico da API
curl -k -X GET "https://localhost:8185/faturamento?limit=1" \
  -H "Accept: application/json"
```

### Variáveis de Ambiente (PowerShell)

```powershell
# Configurar variáveis para os exemplos
$API_BASE = "https://localhost:8185"
$HEADERS = @{
    "Accept" = "application/json"
    "Content-Type" = "application/json"
}
```

## 🔍 Endpoints de Consulta

### 1. Consultar Faturamento com Paginação

#### Request
```bash
curl -k -X GET "$API_BASE/faturamento?skip=0&limit=5" \
  -H "Accept: application/json"
```

#### Response
```json
[
  {
    "fecha": "07/08/2025",
    "numero": "000001234",
    "idCliente": "12345678901",
    "total": 1250.75,
    "cancelacion": false,
    "cotizacion": 1.0,
    "codigoMoneda": "986",
    "recargoTotal": 0.0,
    "descuentoTotal": 25.50,
    "codigoCanalVenta": 1,
    "documentoCliente": null,
    "descripcionCanalVenta": "Loja Física",
    "detalles": [
      {
        "codigoArticulo": "PNEU123",
        "descripcionArticulo": "Pneu Bridgestone 205/55R16",
        "cantidad": 4.0,
        "importeUnitario": 312.50,
        "importe": 1250.0,
        "descuento": 25.50,
        "recargo": 0.0,
        "codigoBarras": "7891234567890"
      }
    ],
    "pagos": [
      {
        "importe": 1225.25,
        "cotizacion": 1.0,
        "codigoMoneda": "986",
        "codigoTipoPago": 1,
        "documentoCliente": null
      }
    ]
  }
]
```

### 2. Consultar Faturamento por Período

#### Request
```bash
curl -k -X GET "$API_BASE/faturamento/?start=2025-08-01&end=2025-08-07&centro=0101" \
  -H "Accept: application/json"
```

#### PowerShell
```powershell
$params = @{
    start = "2025-08-01"
    end = "2025-08-07"
    centro = "0101"
}
$query = ($params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
Invoke-RestMethod -Uri "$API_BASE/faturamento/?$query" -Headers $HEADERS -SkipCertificateCheck
```

### 3. Consultar Fechamento Diário

#### Request
```bash
curl -k -X GET "$API_BASE/fechamento?start=07/08/2025&end=07/08/2025&centro=0101" \
  -H "Accept: application/json"
```

#### Response
```json
{
  "fechaVentas": "2025-08-07",
  "montoVentaLiquida": 15750.25,
  "montoCancelaciones": 125.50,
  "cantidadMovimientos": 45,
  "cantidadCancelaciones": 2
}
```

### 4. Listar Solicitações de Reenvio

#### Request
```bash
curl -k -X GET "$API_BASE/solicitacoes?centro=0101" \
  -H "Accept: application/json"
```

#### Response
```json
[
  {
    "fecha": "2025-08-06",
    "codigoCaja": 1,
    "tipo": "movimientos"
  },
  {
    "fecha": "2025-08-05",
    "codigoCaja": 1,
    "tipo": "cierresDiarios"
  }
]
```

## 📤 Endpoints de Envio

### 1. Enviar Faturamento do Dia Atual

#### Request
```bash
curl -k -X GET "$API_BASE/enviar/faturamento" \
  -H "Accept: application/json"
```

#### Response
```json
{
  "status": "success",
  "message": "Faturamento enviado com sucesso",
  "detalhes": {
    "filiais_processadas": ["0101", "0102", "0103"],
    "total_envios": 3,
    "sucessos": 3,
    "erros": 0,
    "timestamp": "2025-08-07T21:00:00"
  }
}
```

### 2. Enviar Faturamento para Período Específico

#### Request
```bash
curl -k -X GET "$API_BASE/enviar/faturamento/?start=01/08/2025&end=01/08/2025&centro=0101" \
  -H "Accept: application/json"
```

#### PowerShell
```powershell
$params = @{
    start = "01/08/2025"
    end = "01/08/2025"
    centro = "0101"
}
$query = ($params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
Invoke-RestMethod -Uri "$API_BASE/enviar/faturamento/?$query" -Headers $HEADERS -SkipCertificateCheck
```

### 3. Enviar Fechamento

#### Request
```bash
curl -k -X GET "$API_BASE/enviar/fechamento/?start=07/08/2025&end=07/08/2025&centro=0101" \
  -H "Accept: application/json"
```

## 🔄 Gerenciamento de Reenvios

### 1. Verificar e Executar Reenvios Automáticos

#### Request
```bash
curl -k -X GET "$API_BASE/verificar/reenvio?centro=0101" \
  -H "Accept: application/json"
```

#### Response Detalhada
```json
{
  "status": "success",
  "message": "Verificação de reenvio concluída com sucesso",
  "data": {
    "resumo": {
      "filiais_verificadas": ["0101"],
      "total_solicitacoes_encontradas": 2,
      "total_reenvios_executados": 2,
      "sucessos": 2,
      "erros": 0
    },
    "detalhes_por_filial": {
      "0101": {
        "tipos_verificados": {
          "movimientos": {
            "solicitacoes_encontradas": 1,
            "sucessos": 1,
            "erros": 0
          },
          "cierresDiarios": {
            "solicitacoes_encontradas": 1,
            "sucessos": 1,
            "erros": 0
          }
        },
        "total_solicitacoes": 2,
        "reenvios_executados": 2,
        "sucessos": 2,
        "erros": 0
      }
    },
    "reenvios_executados": [
      {
        "filial": "0101",
        "data": "2025-08-06",
        "tipo": "movimientos",
        "status": "sucesso",
        "timestamp": "2025-08-07T21:05:15"
      },
      {
        "filial": "0101",
        "data": "2025-08-05",
        "tipo": "cierresDiarios",
        "status": "sucesso",
        "timestamp": "2025-08-07T21:05:18"
      }
    ],
    "timestamp": 1691439918.123
  }
}
```

### 2. Executar Reenvio Manual

#### Request
```bash
curl -k -X POST "$API_BASE/executar/reenvio" \
  -H "Content-Type: application/json" \
  -d '{
    "data": "06/08/2025",
    "tipo": "movimientos",
    "centro": "0101"
  }'
```

#### PowerShell
```powershell
$body = @{
    data = "06/08/2025"
    tipo = "movimientos"
    centro = "0101"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$API_BASE/executar/reenvio" -Method POST -Headers $HEADERS -Body $body -SkipCertificateCheck
```

## 🔍 Monitoramento

### 1. Verificar Cancelamentos

#### Request
```bash
curl -k -X GET "$API_BASE/verificar/cancelamentos?centro=0101" \
  -H "Accept: application/json"
```

### 2. Verificar Devoluções

#### Request
```bash
curl -k -X GET "$API_BASE/verificar/devolucoes?centro=0101" \
  -H "Accept: application/json"
```

## 🤖 Scripts de Automação

### 1. Script PowerShell - Envio Diário Automático

```powershell
# envio_diario.ps1
param(
    [string]$ApiBase = "https://localhost:8185",
    [string]$Centro = $null,
    [string]$Data = (Get-Date -Format "dd/MM/yyyy")
)

$headers = @{
    "Accept" = "application/json"
}

function Invoke-ApiCall {
    param($Endpoint, $Description)
    
    try {
        Write-Host "Executando: $Description" -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri "$ApiBase$Endpoint" -Headers $headers -SkipCertificateCheck
        Write-Host "✓ Sucesso: $Description" -ForegroundColor Green
        return $response
    }
    catch {
        Write-Host "✗ Erro: $Description - $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Executar sequência de envios
Write-Host "=== Iniciando Envio Diário ===" -ForegroundColor Cyan
Write-Host "Data: $Data" -ForegroundColor Cyan
if ($Centro) { Write-Host "Centro: $Centro" -ForegroundColor Cyan }

$centroParam = if ($Centro) { "&centro=$Centro" } else { "" }

# 1. Enviar faturamento
$faturamento = Invoke-ApiCall "/enviar/faturamento/?start=$Data&end=$Data$centroParam" "Envio de Faturamento"

# 2. Enviar fechamento
$fechamento = Invoke-ApiCall "/enviar/fechamento/?start=$Data&end=$Data$centroParam" "Envio de Fechamento"

# 3. Verificar reenvios
$reenvios = Invoke-ApiCall "/verificar/reenvio?$($centroParam.TrimStart('&'))" "Verificação de Reenvios"

# 4. Verificar cancelamentos
$cancelamentos = Invoke-ApiCall "/verificar/cancelamentos?$($centroParam.TrimStart('&'))" "Verificação de Cancelamentos"

# 5. Verificar devoluções
$devolucoes = Invoke-ApiCall "/verificar/devolucoes?$($centroParam.TrimStart('&'))" "Verificação de Devoluções"

Write-Host "=== Envio Diário Concluído ===" -ForegroundColor Cyan
```

### 2. Script Bash - Monitoramento de Saúde

```bash
#!/bin/bash
# health_check.sh

API_BASE="https://localhost:8185"
LOG_FILE="/tmp/api_health_$(date +%Y%m%d).log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

check_endpoint() {
    local endpoint="$1"
    local description="$2"
    
    log_message "Testando: $description"
    
    if curl -k -s -f "$API_BASE$endpoint" >/dev/null 2>&1; then
        log_message "✓ OK: $description"
        return 0
    else
        log_message "✗ ERRO: $description"
        return 1
    fi
}

# Verificações de saúde
log_message "=== Iniciando Health Check ==="

check_endpoint "/faturamento?limit=1" "Endpoint de Faturamento"
check_endpoint "/solicitacoes" "Endpoint de Solicitações"

log_message "=== Health Check Concluído ==="
```

### 3. Script Python - Consulta e Relatório

```python
# relatorio_diario.py
import requests
import json
from datetime import datetime, timedelta
import urllib3

# Desabilitar warnings SSL para desenvolvimento
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BridgestoneAPIClient:
    def __init__(self, base_url="https://localhost:8185"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False  # Para desenvolvimento
        
    def get_faturamento(self, start_date, end_date, centro=None):
        """Consulta faturamento por período"""
        params = {
            'start': start_date,
            'end': end_date
        }
        if centro:
            params['centro'] = centro
            
        response = self.session.get(
            f"{self.base_url}/faturamento/",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_fechamento(self, date, centro=None):
        """Consulta fechamento do dia"""
        params = {
            'start': date,
            'end': date
        }
        if centro:
            params['centro'] = centro
            
        response = self.session.get(
            f"{self.base_url}/fechamento",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_solicitacoes(self, centro=None):
        """Lista solicitações pendentes"""
        params = {}
        if centro:
            params['centro'] = centro
            
        response = self.session.get(
            f"{self.base_url}/solicitacoes",
            params=params
        )
        response.raise_for_status()
        return response.json()

def gerar_relatorio_diario():
    """Gera relatório diário consolidado"""
    client = BridgestoneAPIClient()
    hoje = datetime.now().strftime("%d/%m/%Y")
    ontem = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    
    print(f"=== Relatório Diário - {hoje} ===\n")
    
    # Fechamento de ontem
    try:
        fechamento = client.get_fechamento(ontem)
        print("📊 Fechamento do dia anterior:")
        print(f"   • Data: {fechamento['fechaVentas']}")
        print(f"   • Vendas Líquidas: R$ {fechamento['montoVentaLiquida']:,.2f}")
        print(f"   • Movimentos: {fechamento['cantidadMovimientos']}")
        print(f"   • Cancelamentos: {fechamento['cantidadCancelaciones']}")
        print()
    except Exception as e:
        print(f"❌ Erro ao consultar fechamento: {e}\n")
    
    # Solicitações pendentes
    try:
        solicitacoes = client.get_solicitacoes()
        print("📋 Solicitações de Reenvio Pendentes:")
        if solicitacoes:
            for sol in solicitacoes:
                print(f"   • {sol['fecha']} - {sol['tipo']} (Caixa: {sol['codigoCaja']})")
        else:
            print("   • Nenhuma solicitação pendente")
        print()
    except Exception as e:
        print(f"❌ Erro ao consultar solicitações: {e}\n")

if __name__ == "__main__":
    gerar_relatorio_diario()
```

## 📋 Casos de Uso Comuns

### 1. Reenvio Manual por Falha de Sistema

```bash
# Cenário: Sistema ficou fora por algumas horas
# Necessário reenviar dados do período

# 1. Verificar solicitações pendentes
curl -k -X GET "$API_BASE/solicitacoes"

# 2. Reenviar faturamento manualmente
curl -k -X GET "$API_BASE/enviar/faturamento/?start=06/08/2025&end=06/08/2025"

# 3. Reenviar fechamento
curl -k -X GET "$API_BASE/enviar/fechamento/?start=06/08/2025&end=06/08/2025"

# 4. Verificar se ainda há pendências
curl -k -X GET "$API_BASE/verificar/reenvio"
```

### 2. Consulta de Dados para Auditoria

```bash
# Consultar faturamento de um cliente específico em um período
curl -k -X GET "$API_BASE/faturamento/?start=2025-08-01&end=2025-08-07" | \
  jq '.[] | select(.idCliente == "12345678901")'

# Consultar totais por filial
for centro in 0101 0102 0103; do
  echo "=== Centro $centro ==="
  curl -k -X GET "$API_BASE/fechamento?start=07/08/2025&end=07/08/2025&centro=$centro"
  echo
done
```

### 3. Monitoramento de Performance

```bash
# Teste de tempo de resposta
time curl -k -X GET "$API_BASE/faturamento?limit=100"

# Teste de carga com múltiplas requisições
for i in {1..10}; do
  curl -k -X GET "$API_BASE/solicitacoes" &
done
wait
```

---

**Nota**: Todos os exemplos assumem um ambiente de desenvolvimento com certificados auto-assinados (flag `-k` no curl). Em produção, remova esta flag e use certificados válidos.
