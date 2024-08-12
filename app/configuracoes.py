import base64
import os


usuario = os.getenv("API_USUARIO")
senha = os.getenv("API_SENHA")

# Flag que indica se os itens que não são Bridgestone devem ser agrupados e o valor deve ser enviado como "Outros"
agrupar_outros_flag = True

# url_base = "https://test-parceiro.scanntech.com/api-minoristas/api"
url_base = "http://parceiro.scanntech.com/api-minoristas/api"
# idEmpresa = 74984 # Teste
idEmpresa = 88975  # Produção
idLocal = 1
idCaja = 1
hora_envio_faturamento = "14:11"
hora_verificacao_reenvio = "21:05"
hora_verificacao_cancelamentos = "21:10"
hora_verificacao_devolucoes = "21:15"
filiais = ["0101", "0102", "0103", "0104", "0105", "0106", "0107"]


def converte_base64(usuario, senha):
    credentials = f"{usuario}:{senha}".encode("ascii")
    encoded_credentials = base64.b64encode(credentials).decode("ascii")
    return f"Basic {encoded_credentials}"


headers = {
    "Authorization": converte_base64(usuario, senha),
    "Content-Type": "application/json",
    "backend-version": "1.0.0",
    "pdv-version": "1.0.0",
}
