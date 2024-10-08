import base64
import os
import time
from dotenv import load_dotenv
from decouple import config

# load_dotenv()


usuario = config("API_USUARIO")
senha = config("API_SENHA")

# Flag que indica se os itens que não são Bridgestone devem ser agrupados e o valor deve ser enviado como "Outros"
agrupar_outros_flag = True

# tempo para manter arquivo de log e data
tempo_manter_arquivo = 60  # dias

# url_base = "https://test-parceiro.scanntech.com/api-minoristas/api"
url_base = "http://parceiro.scanntech.com/api-minoristas/api"
# idEmpresa = 74984 # Teste
idEmpresa = 88975  # Produção
idLocal = 1
idCaja = 1
hora_envio_faturamento = "21:00"
hora_verificacao_reenvio = "21:05"
hora_verificacao_cancelamentos = "21:10"
hora_verificacao_devolucoes = "21:15"
filiais = ["0101", "0102", "0103", "0104", "0105", "0106", "0107", "0201"]


def converte_base64(usuario, senha):
    """
    Converte as credenciais de usuário e senha em uma string codificada em base64.

    Args:
        usuario (str): O nome de usuário.
        senha (str): A senha do usuário.

    Returns:
        str: A string codificada em base64 no formato "Basic {encoded_credentials}".
    """
    credentials = f"{usuario}:{senha}".encode("ascii")
    encoded_credentials = base64.b64encode(credentials).decode("ascii")
    return f"Basic {encoded_credentials}"


headers = {
    "Authorization": converte_base64(usuario, senha),
    "Content-Type": "application/json",
    "backend-version": "1.0.0",
    "pdv-version": "1.0.0",
}


def limpar_arquivos_antigos(diretorio, dias):
    """
    Remove arquivos antigos de um diretório.

    Args:
        diretorio (str): O caminho para o diretório onde os arquivos serão verificados e removidos.
        dias (int): O número de dias a partir dos quais os arquivos serão considerados antigos.

    Returns:
        None

    Raises:
        None
    """
    agora = time.time()
    periodo = dias * 86400  # Convertendo dias para segundos

    if os.path.exists(diretorio):
        for arquivo in os.listdir(diretorio):
            caminho_arquivo = os.path.join(diretorio, arquivo)
            if os.path.isfile(caminho_arquivo):
                idade_arquivo = agora - os.path.getmtime(caminho_arquivo)
                if idade_arquivo > periodo:
                    os.remove(caminho_arquivo)
                    print(f"Arquivo removido: {caminho_arquivo}")
