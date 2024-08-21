import os
import logging
from logging.handlers import TimedRotatingFileHandler
from app.configuracoes import limpar_arquivos_antigos


def setup_logger():
    # Verifica se a pasta de log existe, se não, cria
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Limpar arquivos antigos
    limpar_arquivos_antigos(
        log_directory, 60
    )  # 30 dias, você pode ajustar conforme necessário

    # Configuração do logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Verifica se o logger já possui um handler
    if not logger.handlers:
        # Timed rotating file handler para arquivos de log diários
        file_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_directory, "app.log"),
            when="midnight",
            interval=1,
            backupCount=30,  # Manter logs dos últimos 30 dias
        )
        file_handler.suffix = "%Y-%m-%d"
        file_formatter = logging.Formatter(
            "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] "
            "[%(levelname)s] %(name)s: %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
