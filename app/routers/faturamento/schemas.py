from datetime import date, datetime
from typing import Any, List
from pydantic import BaseModel, ConfigDict, model_validator


class ItemFaturamentoInDB(BaseModel):
    # sync_updated_at: datetime
    # sync_created_at: datetime
    ID: str
    CFOP: str
    NATUREZA_OPERACAO: str
    CANCELADA: str
    RESULTADO_FATURAMENTO: str
    DOCTYP: str
    DOC_FAT: str
    NF_SERVICO: str
    DOCNUM: int
    NUMERO_NOTA: str
    OV: int
    OV_MAE: int
    DATA_CRIADA_OV: datetime
    DATA_CRIADA: date
    SERIE: str
    CENTRO: str
    CLIENTE_ID: str
    CLIENTE_NOME: str
    CLASSIFICACAO: str = ""
    SEGMENTO: str = ""
    FAMILIA: str = ""
    GRUPO: str = ""
    CODIGO_MATERIAL: str
    COD_FAB: str = ""
    DESC_MATERIAL: str
    CONDICAO_PAG: str
    COND_DESCRICAO: str
    FORMA_PAGAMENTO: str
    PAG_FORMA_DESC: str
    MEIO_PAGTO: str
    MEIO_PAGTO_DESC: str
    VLR_UNITARIO: float
    QUANTIDADE: float
    TOTAL: float
    TOTAL_SEMDESCONTO_SEMJUROS: float
    TOTAL_COM_DESCONTO: float
    TOTAL_COM_DESCONTO_ITEM: float
    TOTAL_DEVIDO: float
    DESCONTO_REAL: float
    DESCONTO_REAL_PERCENT: float
    CUSTO_SAP_TOTAL: float
    CUSTO_SAP_ITEM: float
    LUCRO_SAP_ITEM: float
    MARGEM_SAP: float
    ICMS_ST: float
    DESCONTO_ABSOLUTO: float
    DESCONTO_ABSOLUTO_PERCENT: str
    TOTAL_BRUTO: float
    TOTALNF: float
    UNIDADE: str
    ESTADO: str
    CIDADE: str
    VENDEDOR_TIPO: str
    VENDEDOR_ID: int
    VENDEDOR: str
    MECANICOZ4: str
    MECANICOZ5: str
    MECANICOZ6: str
    MECANICOZ7: str
    MECANICOZ8: str
    PLACA: str
    KM: str
    CREDAT: str
    OV_TIPO: str
    BP_TIPO: str
    CRIADO_POR: str
    PRECO_VAREJO: float
    PRECO_ATACADO: float
    JUROS_CONDICAO: float
    TIPO_ORDEM: str
    COMISSAO_TIPO: str
    COMISSAO_PORCENTAGEM: float
    ITEM: str
    COLETADOR: str
    MOTIVO_ORDEM: str
    CENTRO_REG: str
    COLETADOR_NOME: str
    COLETADOR_NOME_COMPLETO: str
    GRUPO_MERC: str
    GRUPO_MERC_DESC: str
    SEGMENTO_PRINCIPAL_BP: str
    REGIAO_AGRO_BP: str
    # TIMESTAMP_ATUALIZACAO: str
    VENDEDOR_OV_MAE_ID: int
    VENDEDOR_OV_MAE_NOME: str
    TIPO_COMISSAO: str
    AJUSTES_COMISSAO: str
    PORCENTAGEM_COMISSAO_VENDEDOR: float
    PORCENTAGEM_COMISSAO_COLETADOR: float
    VALOR_BASE_COMISSAO: float

    @model_validator(mode="before")
    def set_defaults(cls, values: Any) -> Any:
        for field in cls.__annotations__.keys():
            if getattr(values, field) is None:
                field_type = cls.__annotations__.get(field)
                if field_type == int:
                    setattr(values, field, 0)
                elif field_type == float:
                    setattr(values, field, 0.0)
                elif field_type == str:
                    setattr(values, field, "")
                elif field_type == datetime:
                    setattr(values, field, datetime.now())
        return values

    model_config = ConfigDict(
        from_attributes=True,
    )


class Faturamento(BaseModel):
    numero_nota: str
    data_criacao: date
    idCliente: str
    total_faturamento: float
    itens: List[ItemFaturamentoInDB]


class Pagos(BaseModel):
    importe: float
    cotizacion: float = 1.0
    codigoMoneda: str = "986"
    codigoTipoPago: int
    documentoCliente: None


class Detalles(BaseModel):
    importe: float
    recargo: float
    cantidad: float
    descuento: float
    codigoBarras: str
    codigoArticulo: str
    importeUnitario: float
    descripcionArticulo: str


class ModelScannTech(BaseModel):
    fecha: str
    pagos: List[Pagos]
    total: float
    numero: str = ""
    detalles: List[Detalles]
    idCliente: str
    cotizacion: float = 1.0
    cancelacion: bool
    codigoMoneda: str = "986"
    recargoTotal: float
    descuentoTotal: float
    codigoCanalVenta: int
    documentoCliente: None
    descripcionCanalVenta: str


class Fechamento(BaseModel):
    fechaVentas: date
    montoVentaLiquida: float
    montoCancelaciones: float = 0.0
    cantidadMovimientos: int
    cantidadCancelaciones: int = 0
    
    
class Solicitacoes(BaseModel):
    fecha: date
    codigoCaja: int
    tipo: str
