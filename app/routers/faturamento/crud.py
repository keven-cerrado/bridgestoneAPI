from copy import deepcopy
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from . import models, schemas
from collections import defaultdict
from datetime import datetime, date

def get_faturamento(db: Session, skip: int = 0, limit: int = 100):
    try:
        faturamentos = db.query(models.ItemFaturamento).filter(models.ItemFaturamento.DOC_FAT.isnot(None)).order_by(models.ItemFaturamento.DATA_CRIADA.desc()).offset(skip).limit(limit).all()
        return aggregate_by_numero_nota(faturamentos)
    except Exception as e:
        print(e)
        return None

# Filtro por range de datas
def get_faturamento_per_date(db: Session, data_inicial: str, data_final: str):
    data_inicial = datetime.strptime(data_inicial, '%d/%m/%Y').date()
    data_final = datetime.strptime(data_final, '%d/%m/%Y').date()
    
    try:
        faturamentos = db.query(models.ItemFaturamento).filter(models.ItemFaturamento.DATA_CRIADA.between(data_inicial, data_final)).all()
        return aggregate_by_numero_nota(faturamentos)
    except Exception as e:
        print(e)
        return None

def aggregate_by_numero_nota(faturamentos):
    grouped = defaultdict(list)
    
    # Listas de família e grupos permitidos
    familia_permitida = 'PNEU NOVO'
    grupos_permitidos = [
        'PNEU 020 HP', 'PNEU 030 UHP', 'PNEU 040 STD', 'PNEU 060 LTR',
        'PNEU 070 VAN', 'PNEU 100 TBR M', 'PNEU 120 TBR L', 'PNEU 130 AGS S',
        'PNEU 150 AGS L', 'PNEU 160 AGR L', 'PNEU 170 OTR', 'PNEU 180 OTR'
    ]
    
    # Agrupar itens por numero_nota
    for faturamento in faturamentos:
        faturamento: models.ItemFaturamento
        grouped[faturamento.NUMERO_NOTA].append(faturamento)
    
    # Construir resposta agregada
    aggregated = []
    for numero_nota, items in grouped.items():
        items: List[schemas.ItemFaturamento]
        total_faturamento = items[0].TOTALNF
        cliente_id = items[0].CLIENTE_ID
        cliente_nome = items[0].CLIENTE_NOME
        data_criacao = items[0].DATA_CRIADA

        itens_modificados: List[schemas.ItemFaturamento] = [] 
        item_agregado: schemas.ItemFaturamento = None
        for item in items:
            if (item.GRUPO not in grupos_permitidos):
                if item_agregado is None:
                    item_agregado = deepcopy(item)
                    item_agregado.DESC_MATERIAL = "Outros"
                    item_agregado.CODIGO_MATERIAL = "Outros"
                    item_agregado.COD_FAB = "Outros"
                    item_agregado.CFOP = "Outros"
                    item_agregado.NATUREZA_OPERACAO = "Outros"
                    item_agregado.GRUPO = "Outros"
                    item_agregado.FAMILIA = "Outros"
                    item_agregado.VALOR_BASE_COMISSAO = 0
                    item_agregado.PORCENTAGEM_COMISSAO_VENDEDOR = 0
                    item_agregado.PORCENTAGEM_COMISSAO_COLETADOR = 0
                    item_agregado.QUANTIDADE = 1
                else:
                    item_agregado.TOTAL = (item_agregado.TOTAL or 0) + (item.TOTAL or 0)
                    item_agregado.TOTAL_BRUTO = (item_agregado.TOTAL_BRUTO or 0) + (item.TOTAL_BRUTO or 0)
                    item_agregado.TOTALNF = (item_agregado.TOTALNF or 0) + (item.TOTALNF or 0)
                    item_agregado.CUSTO_SAP_TOTAL = (item_agregado.CUSTO_SAP_TOTAL or 0) + (item.CUSTO_SAP_TOTAL or 0)
                    item_agregado.CUSTO_SAP_ITEM = (item_agregado.CUSTO_SAP_ITEM or 0) + (item.CUSTO_SAP_ITEM or 0)
                    item_agregado.LUCRO_SAP_ITEM = (item_agregado.LUCRO_SAP_ITEM or 0) + (item.LUCRO_SAP_ITEM or 0)
                    item_agregado.MARGEM_SAP = (item_agregado.MARGEM_SAP or 0) + (item.MARGEM_SAP or 0)
                    item_agregado.ICMS_ST = (item_agregado.ICMS_ST or 0) + (item.ICMS_ST or 0)
                    item_agregado.DESCONTO_ABSOLUTO = (item_agregado.DESCONTO_ABSOLUTO or 0) + (item.DESCONTO_ABSOLUTO or 0)
                    item_agregado.DESCONTO_ABSOLUTO_PERCENT = (item_agregado.DESCONTO_ABSOLUTO_PERCENT or 0) + (item.DESCONTO_ABSOLUTO_PERCENT or 0)
                    item_agregado.DESCONTO_REAL = (item_agregado.DESCONTO_REAL or 0) + (item.DESCONTO_REAL or 0)
                    item_agregado.DESCONTO_REAL_PERCENT = (item_agregado.DESCONTO_REAL_PERCENT or 0) + (item.DESCONTO_REAL_PERCENT or 0)
                    item_agregado.TOTAL_SEMDESCONTO_SEMJUROS = (item_agregado.TOTAL_SEMDESCONTO_SEMJUROS or 0) + (item.TOTAL_SEMDESCONTO_SEMJUROS or 0)
                    item_agregado.TOTAL_COM_DESCONTO = (item_agregado.TOTAL_COM_DESCONTO or 0) + (item.TOTAL_COM_DESCONTO or 0)
                    item_agregado.TOTAL_COM_DESCONTO_ITEM = (item_agregado.TOTAL_COM_DESCONTO_ITEM or 0) + (item.TOTAL_COM_DESCONTO_ITEM or 0)
                    item_agregado.TOTAL_DEVIDO = (item_agregado.TOTAL_DEVIDO or 0) + (item.TOTAL_DEVIDO or 0)
            else:
                itens_modificados.append(item)
        
        if item_agregado is not None:
            item_agregado.VLR_UNITARIO = (item_agregado.TOTAL or 0)
            item_agregado.TOTAL_COM_DESCONTO_ITEM = (item_agregado.TOTAL or 0)
            item_agregado.CUSTO_SAP_ITEM = (item_agregado.CUSTO_SAP_TOTAL or 0)
            itens_modificados.append(item_agregado)
        
        documento = schemas.Faturamento(
            numero_nota=str(numero_nota) if str(numero_nota) else "",
            data_criacao=data_criacao,
            cliente_id=cliente_id,
            cliente_nome=cliente_nome,
            total_faturamento=total_faturamento,
            itens=itens_modificados
        )
        
        aggregated.append(documento)
    
    return aggregated

