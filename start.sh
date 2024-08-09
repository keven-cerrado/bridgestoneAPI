# Vá para o diretório do projeto
cd /code/app

# atualiza o repositório
git pull origin main

# Inicie a aplicação
uvicorn main:app --host 0.0.0.0 --port 8000