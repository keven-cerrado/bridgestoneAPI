FROM python:3.10

# Defina o diretório de trabalho
WORKDIR /code

# Copie o arquivo de requisitos e o script de execução
COPY ./requirements.txt /code/requirements.txt

COPY ./run.sh /code/run.sh

# Instale dependências do sistema e do Python
RUN apt-get update -y && \
    apt-get install -y git openssh-client && \
    pip install --no-cache-dir -r /code/requirements.txt && \
    chmod +x /code/run.sh

# Copie o código da aplicação
COPY ./app /code/

# Comando para iniciar o script de execução
CMD ["bash", "/code/run.sh"]
