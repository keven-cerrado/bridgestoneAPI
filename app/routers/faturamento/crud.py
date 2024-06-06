from copy import deepcopy
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from . import models, schemas
from ..clientes import schemas as clientes_schemas
from ..clientes import models as clientes_models
from collections import defaultdict
from datetime import datetime, date


def get_faturamento(db: Session, skip: int = 0, limit: int = 100):
    try:
        faturamentos = (
            db.query(models.ItemFaturamento)
            .filter(
                models.ItemFaturamento.DOC_FAT.isnot(None)
                & models.ItemFaturamento.NUMERO_NOTA.isnot(None)
            )
            .order_by(models.ItemFaturamento.DATA_CRIADA.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return aggregate_by_numero_nota(db, faturamentos)
    except Exception as e:
        print(e)
        return None


# Filtro por range de datas
def get_faturamento_per_date(db: Session, data_inicial: str, data_final: str):
    data_inicial = datetime.strptime(data_inicial, "%d/%m/%Y").date()
    data_final = datetime.strptime(data_final, "%d/%m/%Y").date()

    try:
        faturamentos = (
            db.query(models.ItemFaturamento)
            .filter(
                models.ItemFaturamento.DATA_CRIADA.between(data_inicial, data_final)
            )
            .all()
        )
        return aggregate_by_numero_nota(db, faturamentos)
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


def aggregate_by_numero_nota(db: Session, faturamentos):
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

    # Construir resposta agregada
    aggregated = []
    for numero_nota, items in grouped.items():
        items: List[schemas.ItemFaturamentoInDB]
        total_faturamento = items[0].TOTALNF
        cliente = (
            db.query(clientes_models.Cliente)
            .filter(clientes_models.Cliente.ID == items[0].CLIENTE_ID)
            .first()
        )
        clienteSchema = clientes_schemas.Cliente.model_validate(cliente)
        clienteSchema.IDCLIENTE = set_idCliente(clienteSchema.IDCLIENTE, clienteSchema)
        data_criacao = items[0].DATA_CRIADA
        desconto_total = sum(abs(item.DESCONTO_ABSOLUTO) or 0 for item in items)
        cancelada = items[0].CANCELADA
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
                    importeUnitario=item.VLR_UNITARIO,
                    importe=item.TOTAL,
                    descuento=abs(item.DESCONTO_ABSOLUTO),
                    recargo=0.0,
                )
                if item.GRUPO not in grupos_permitidos:
                    if item_agregado is None:
                        item_agregado = deepcopy(itemDetalhes)
                        item_agregado.descripcionArticulo = "Outros"
                        item_agregado.cantidad = 1
                    else:
                        item_agregado.importeUnitario += itemDetalhes.importeUnitario
                        item_agregado.importe += itemDetalhes.importe
                        item_agregado.descuento += itemDetalhes.descuento
                else:
                    itens_modificados.append(itemDetalhes)
            except Exception as e:
                print(e)

        if item_agregado is not None:
            itens_modificados.append(item_agregado)

        # documento = schemas.Faturamento(
        #     numero_nota=str(numero_nota) if str(numero_nota) else "",
        #     data_criacao=data_criacao,
        #     idCliente=clienteSchema.IDCLIENTE if clienteSchema.IDCLIENTE else "",
        #     total_faturamento=total_faturamento,
        #     itens=itens_modificados,
        # )

        condicoes_pagamento = {
            "K": 10,
            "B": 13,
            "D": 13,
            "E": 9,
            "G": 11,
            "L": 9,
            "A": 0,
            "R": 13,
            "V": 0,
            "H": 12 if "TICKET" in cond_descricao else 13,
            "F": 13,
            "N": 11,
            "U": 9,
            "C": 11,
            "O": 13,
        }

        responseScannTech = schemas.ModelScannTech(
            fecha=data_criacao,
            total=total_faturamento,
            numero=numero_nota,
            descuentoTotal=abs(desconto_total),
            recargoTotal=0,
            cancelacion=False if cancelada == "" else True,
            idCliente=clienteSchema.IDCLIENTE if clienteSchema.IDCLIENTE else "",
            documentoCliente=None,
            codigoCanalVenta=1,
            descripcionCanalVenta="VENDA NA LOJA",
            detalles=itens_modificados,
            pagos=[
                schemas.Pagos(
                    importe=total_faturamento,
                    codigoTipoPago=condicoes_pagamento.get(forma_pagamento, 0),
                    documentoCliente=None,
                )
            ],
        )

        aggregated.append(responseScannTech)

    return aggregated
