from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator, model_validator

class Cliente(BaseModel):
    
    model_config = ConfigDict(
        from_attributes=True,
    )
        
    IDCLIENTE: Optional[str] = None
    ID: str
    NOME: str
    PF_PJ: str
    CPF_CNPJ: str
    DOMICILIO: str
    CONTAGEM: int
    IE: str
    IM: str
    CIDADE: str
    CEP: str
    RUA: str
    NUMERO: str
    TELEFONE1: str
    COMP_SMS_TELEFONE1: str
    OBS_TELEFONE1: str
    TELEFONE2: str
    COMP_SMS_TELEFONE2: str
    OBS_TELEFONE2: str
    TELEFONE3: str
    COMP_SMS_TELEFONE3: str
    OBS_TELEFONE3: str
    TELEFONE4: str
    COMP_SMS_TELEFONE4: str
    OBS_TELEFONE4: str
    TELEFONE5: str
    COMP_SMS_TELEFONE5: str
    OBS_TELEFONE5: str
    EMAIL1: str
    OBS_EMAIL1: str
    EMAIL2: str
    OBS_EMAIL2: str
    EMAIL3: str
    OBS_EMAIL3: str
    EMAIL4: str
    OBS_EMAIL4: str
    EMAIL5: str
    OBS_EMAIL5: str
    EMAIL6: str
    OBS_EMAIL6: str
    VAREJO_ATACADO: str
    SEGMENTO_PRINCIPAL: str
    REGIAO_AGRO: str
    UF: str
    
    @model_validator(mode= 'before')
    def set_defaults(cls, values: Any) -> Any:
        for field in cls.__annotations__.keys():
            if getattr(values, field) is None:
                field_type = cls.__annotations__.get(field)
                if field_type == int:
                    setattr(values, field, 0)
                elif field_type == float:
                    setattr(values, field, 0.0)
                elif field_type == str:
                    setattr(values, field, '')
                elif field_type == datetime:
                    setattr(values, field, datetime.now())
        return values