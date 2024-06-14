import base64
import os


usuario = os.getenv("API_USUARIO")
senha = os.getenv("API_SENHA")

# Flag que indica se os itens que não são Bridgestone devem ser agrupados e o valor deve ser enviado como "Outros"
agrupar_outros_flag = True

url_base = "https://test-parceiro.scanntech.com/api-minoristas/api"
idEmpresa = 74984
idLocal = 0
idCaja = 0
hora_envio_faturamento = "21:00"
hora_verificacao_reenvio = "21:10"
hora_verificacao_cancelamentos = "21:20"
hora_verificacao_devolucoes = "21:30"


def converte_base64(usuario, senha):
    credentials = f"{usuario}:{senha}".encode("ascii")
    encoded_credentials = base64.b64encode(credentials).decode("ascii")
    return f"Basic {encoded_credentials}"


headers = {
    "Authorization": converte_base64(usuario, senha),
    "Content-Type": "application/json",
}
