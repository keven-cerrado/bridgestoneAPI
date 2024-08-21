from copy import deepcopy
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from . import models, schemas
from ..clientes import schemas as clientes_schemas
from ..clientes import models as clientes_models
from collections import defaultdict
from datetime import datetime, date
import os
import pandas as pd
from app.configuracoes import (
    agrupar_outros_flag,
    limpar_arquivos_antigos,
)


def get_faturamento(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    agrupar_outros: bool = True,
    filial: str = None,
):
    try:
        faturamentos = (
            db.query(models.ItemFaturamento)
            .filter(
                models.ItemFaturamento.NUMERO_NOTA.isnot(None)
                & models.ItemFaturamento.RESULTADO_FATURAMENTO.isnot(None)
                & models.ItemFaturamento.COMISSAO_TIPO.like("VENDA")
                # & models.ItemFaturamento.TIPO_ORDEM.not_like("ZVSR")
                & (
                    models.ItemFaturamento.CFOP.not_like("5117AA")
                    | models.ItemFaturamento.CFOP.not_like("6117AA")
                )
                # & models.ItemFaturamento.CENTRO.not_like("02%")
                & models.ItemFaturamento.CENTRO.not_like("03%")
                # & models.ItemFaturamento.CENTRO.not_like("0105")
                & (models.ItemFaturamento.CENTRO.like(filial) if filial else True)
            )
            .order_by(models.ItemFaturamento.DATA_CRIADA.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        resposta = aggregate_by_numero_nota(db, faturamentos, agrupar_outros=agrupar_outros)
        generate_csv(resposta)
        return resposta
    except Exception as e:
        print(e)
        return None


# Filtro por range de datas
def get_faturamento_per_date(
    db: Session,
    data_inicial: str,
    data_final: str,
    agrupar_outros: bool = True,
    filtrar_canceladas: bool = True,
    filial: str = None,
) -> List[schemas.ModelScannTech]:
    data_inicial = datetime.strptime(data_inicial, "%d/%m/%Y").date()
    data_final = datetime.strptime(data_final, "%d/%m/%Y").date()

    try:
        faturamentos = (
            db.query(models.ItemFaturamento)
            .filter(
                models.ItemFaturamento.NUMERO_NOTA.isnot(None)
                & models.ItemFaturamento.RESULTADO_FATURAMENTO.isnot(None)
                & models.ItemFaturamento.COMISSAO_TIPO.like("VENDA")
                # & models.ItemFaturamento.TIPO_ORDEM.not_like("ZVSR")
                & (
                    models.ItemFaturamento.CFOP.not_like("5117AA")
                    | models.ItemFaturamento.CFOP.not_like("6117AA")
                )
                # & models.ItemFaturamento.CENTRO.not_like("02%")
                & models.ItemFaturamento.CENTRO.not_like("03%")
                # & models.ItemFaturamento.CENTRO.not_like("0105")
                & (models.ItemFaturamento.CENTRO.like(filial) if filial else True)
                & (
                    models.ItemFaturamento.CANCELADA.is_(None)
                    if filtrar_canceladas
                    else True
                )
                & models.ItemFaturamento.DATA_CRIADA.between(data_inicial, data_final)
            )
            .order_by(models.ItemFaturamento.DATA_CRIADA.desc())
            .all()
        )
        resposta = aggregate_by_numero_nota(db, faturamentos, agrupar_outros=agrupar_outros)
        generate_csv_and_xlsx(resposta, data_inicial)
        return resposta
    except Exception as e:
        print(e)
        return None


def get_fechamento_per_date(
    db: Session,
    data_inicial: str,
    data_final: str,
    agrupar_outros: bool = True,
    filial: str = None,
):
    current_date = datetime.now().strftime("%d/%m/%Y")

    try:
        # Get the faturamentos for the specified date range
        faturamentos: List[schemas.ModelScannTech] = get_faturamento_per_date(
            db,
            (data_inicial if data_inicial else current_date),
            (data_final if data_final else current_date),
            agrupar_outros=agrupar_outros_flag,
            filial=filial,
        )

        if not faturamentos:
            return schemas.Fechamento(
                fechaVentas=datetime.now().date(),
                montoVentaLiquida=0.0,
                montoCancelaciones=0.0,
                cantidadMovimientos=0,
                cantidadCancelaciones=0,
            )

        fechamento_data = faturamentos[0].fecha.split("T")[0]
        total_vendas = sum([f.total for f in faturamentos])
        qtd_vendas = len(faturamentos)
        qtd_cancelamentos = len([f for f in faturamentos if f.cancelacion])

        fechamento: schemas.Fechamento = schemas.Fechamento(
            fechaVentas=fechamento_data,
            montoVentaLiquida=round(total_vendas, 2),
            montoCancelaciones=0.0,
            cantidadMovimientos=qtd_vendas,
            cantidadCancelaciones=qtd_cancelamentos,
        )

        return fechamento
    except Exception as e:
        print(e)
        return None


def set_idCliente(v, values: clientes_schemas.Cliente):
    ddd = values.TELEFONE1[:2] if values.TELEFONE1 else "00"  # DDD do telefone
    last_4_phone = (
        values.TELEFONE1[-4:] if values.TELEFONE1 else "0000"
    )  # Últimos 4 dígitos do telefone
    first_5_cpf_cnpj = (
        values.CPF_CNPJ[:5] if values.CPF_CNPJ else "00000"
    )  # Primeiros 5 dígitos do CPF/CNPJ
    last_2_cpf_cnpj = (
        values.CPF_CNPJ[-2:] if values.CPF_CNPJ else "00"
    )  # Últimos 2 dígitos do CPF/CNPJ
    return ddd + last_4_phone + first_5_cpf_cnpj + last_2_cpf_cnpj

def generate_csv_and_xlsx(faturamentos: List[schemas.ModelScannTech], data: date = None):
    data_list = []
    for faturamento in faturamentos:
        data_list.append({
            'data': faturamento.fecha,
            'total': faturamento.total,
            'numero_nf': faturamento.numero,
            'desconto_total': faturamento.descuentoTotal,
            'acrescimos_total': faturamento.recargoTotal,
            'cancelada': faturamento.cancelacion,
            'idCliente': faturamento.idCliente,
            'documentoCliente': faturamento.documentoCliente,
            'canal_venda': faturamento.codigoCanalVenta,
            'descricao_canal_venda': faturamento.descripcionCanalVenta,
            'forma_pagamento': faturamento.pagos[0].codigoTipoPago,
            'valor_pagamento': faturamento.pagos[0].importe,
            'codigoBarras': faturamento.detalles[0].codigoBarras,
            'codigoSAP': faturamento.detalles[0].codigoArticulo,
            'descricao_produto': faturamento.detalles[0].descripcionArticulo,
            'quantidade': faturamento.detalles[0].cantidad,
            'valorUnitario': faturamento.detalles[0].importeUnitario,
            'desconto': faturamento.detalles[0].descuento,
            'acrescimo_item': faturamento.detalles[0].recargo
        })

    df = pd.DataFrame(data_list)
    
    # Create the 'data' directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Limpar arquivos antigos
    limpar_arquivos_antigos('data', 60)  # 60 dias, você pode ajustar conforme necessário
    
    # Generate the filename based on the current date
    current_date = data or datetime.now().strftime("%Y-%m-%d")
    
    # Create a folder for each day
    folder_path = f"data/{current_date}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Generate the filename for the CSV file
    csv_filename = f"{folder_path}/faturamentos_{current_date}.csv"
    
    # Generate the filename for the Excel file
    xlsx_filename = f"{folder_path}/faturamentos_{current_date}.xlsx"
    
    # Write the CSV file
    df.to_csv(csv_filename, index=False)
    
    # Write the Excel file
    df.to_excel(xlsx_filename, index=False)


def aggregate_by_numero_nota(db: Session, faturamentos, agrupar_outros: bool = True):
    grouped = defaultdict(list)

    # Listas de família e grupos permitidos
    familia_permitida = "PNEU NOVO"
    grupos_permitidos = [
        "PNEU 020 HP",
        "PNEU 030 UHP",
        "PNEU 040 STD",
        "PNEU 060 LTR",
        "PNEU 070 VAN",
        "PNEU 100 TBR M",
        "PNEU 120 TBR L",
        "PNEU 130 AGS S",
        "PNEU 150 AGS L",
        "PNEU 160 AGR L",
        "PNEU 170 OTR",
        "PNEU 180 OTR",
    ]

    # Agrupar itens por numero_nota
    for faturamento in faturamentos:
        faturamento: models.ItemFaturamento
        grouped[faturamento.NUMERO_NOTA].append(faturamento)
        total_faturamento = faturamento.TOTAL_BRUTO

    # Construir resposta agregada
    aggregated = []
    for numero_nota, items in grouped.items():
        items: List[schemas.ItemFaturamentoInDB]
        total_faturamento = 0
        for item in items:
            total_faturamento += item.TOTAL_BRUTO
        cliente = (
            db.query(clientes_models.Cliente)
            .filter(clientes_models.Cliente.ID == items[0].CLIENTE_ID)
            .first()
        )
        clienteSchema = clientes_schemas.Cliente.model_validate(cliente)
        clienteSchema.IDCLIENTE = set_idCliente(clienteSchema.IDCLIENTE, clienteSchema)
        hora_formatada = f"{items[0].HORA_CRIADA[:2]}:{items[0].HORA_CRIADA[2:4]}:{items[0].HORA_CRIADA[4:]}"
        data_criacao = (
            f"{items[0].DATA_CRIADA.strftime('%Y-%m-%d')}T{hora_formatada}.000-0300"
        )
        desconto_total = round(
            sum(abs(item.DESCONTO_ABSOLUTO) or 0 for item in items), 2
        )
        cancelada = True if items[0].CANCELADA else False
        forma_pagamento = items[0].FORMA_PAGAMENTO
        cond_descricao = items[0].COND_DESCRICAO

        itens_modificados: List[schemas.Detalles] = []
        item_agregado: schemas.Detalles = None
        for item in items:
            try:
                itemDetalhes: schemas.Detalles = schemas.Detalles(
                    codigoArticulo=item.CODIGO_MATERIAL,
                    codigoBarras=item.CODIGO_MATERIAL,
                    descripcionArticulo=item.DESC_MATERIAL,
                    cantidad=item.QUANTIDADE,
                    importeUnitario=item.VLR_UNITARIO
                    + (
                        (
                            (item.ICMS_ST / item.QUANTIDADE)
                            if (item.QUANTIDADE and item.ICMS_ST)
                            else 0
                        )
                        + (
                            (
                                (
                                    (item.ICMS_ST / item.QUANTIDADE)
                                    if (item.QUANTIDADE and item.ICMS_ST)
                                    else 0
                                )
                                * 1.3
                                / 100
                            )
                            if item.GRUPO_MERC == "4153"
                            else 0
                        )
                    ),
                    importe=(
                        item.TOTAL_BRUTO
                        + (item.ICMS_ST or 0)
                        + (
                            ((item.TOTAL_BRUTO + (item.ICMS_ST or 0)) * 1.3 / 100)
                            if item.GRUPO_MERC == "4153"
                            else 0
                        )
                    ),
                    descuento=round(abs(item.DESCONTO_ABSOLUTO), 2),
                    recargo=0.0,
                )
                # if item.GRUPO_MERC == "4153":
                #     itemDetalhes.importe += itemDetalhes.importe * 1.3 / 100
                if item.GRUPO not in grupos_permitidos:
                    if agrupar_outros:
                        if item_agregado is None:
                            item_agregado = deepcopy(itemDetalhes)
                            item_agregado.descripcionArticulo = "Outros"
                            item_agregado.codigoArticulo = "0"
                            item_agregado.codigoBarras = None
                            item_agregado.cantidad = 1
                        else:
                            item_agregado.importeUnitario += (
                                itemDetalhes.importeUnitario
                            )
                            item_agregado.importe += itemDetalhes.importe
                            item_agregado.descuento += itemDetalhes.descuento
                    else:
                        itens_modificados.append(itemDetalhes)
                else:
                    itens_modificados.append(itemDetalhes)
            except Exception as e:
                print(e)

        if item_agregado is not None:
            item_agregado.importeUnitario = (
                round(item_agregado.importe, 2) + item_agregado.descuento
            )
            item_agregado.descuento = round(item_agregado.descuento, 2)
            item_agregado.importe = round(item_agregado.importe, 2)
            itens_modificados.append(item_agregado)

        condicoes_pagamento = {
            "K": 10,
            "B": 9,
            "D": 9,
            "E": 13 if "CIELO DEBITO" in cond_descricao else 9,
            "G": 11,
            "L": 9,
            "A": 0,
            "R": 9,
            "V": 0,
            "H": 12 if "TICKET" in cond_descricao else 9,
            "F": 9,
            "N": 11,
            "U": 9,
            "C": 11,
            "O": 9,
        }

        responseScannTech = schemas.ModelScannTech(
            fecha=data_criacao,
            total=round(total_faturamento, 2),
            numero=numero_nota,
            descuentoTotal=abs(desconto_total),
            recargoTotal=0,
            cancelacion=cancelada,
            idCliente=clienteSchema.IDCLIENTE,
            documentoCliente=None,
            codigoCanalVenta=1,
            descripcionCanalVenta="VENDA NA LOJA",
            detalles=itens_modificados,
            pagos=[
                schemas.Pagos(
                    importe=round(total_faturamento, 2),
                    codigoTipoPago=condicoes_pagamento.get(forma_pagamento, 0),
                    documentoCliente=None,
                )
            ],
        )

        aggregated.append(responseScannTech)

    return aggregated
