import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger():
    # Verifica se a pasta de log existe, se não, cria
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Logger setup
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Check if logger already has a handler
    if not logger.handlers:
        # Timed rotating file handler for daily log files
        file_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_directory, "app.log"),
            when="midnight",
            interval=1,
            backupCount=30,  # Keep logs for the last 30 days
        )
        file_handler.suffix = "%Y-%m-%d"
        file_formatter = logging.Formatter(
            "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] "
            "[%(levelname)s] %(name)s: %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
