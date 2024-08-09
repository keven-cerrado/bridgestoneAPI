FROM python:3.10

# Set the working directory
WORKDIR /code

# Copy the current directory contents into the container at /code
COPY ./requirements.txt /code/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy the current directory contents into the container at /code
COPY ./app /code/app

# Run code.py when the container launches
# CMD ["fastapi", "run", "code/main.py", "--port", "80"]

# Copie o script de inicialização
COPY start.sh /code/start.sh

# Comando para iniciar a aplicação usando o script de inicialização
CMD ["bash", "/code/start.sh"]
