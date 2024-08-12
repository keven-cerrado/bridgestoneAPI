# SETAR SERVIDOR DNS DO GOOGLE
echo "nameserver 8.8.8.8" >> /etc/resolv.conf

if test -f "install_check"; then
    echo "install_check exists."
else
    touch install_check

    # COMANDOS DE INSTALAÇÃO
    apt-get update -y
    apt-get install -y git

    # Ajustar timezone
    rm -rf /etc/localtime
    ln -s /usr/share/zoneinfo/America/Bahia /etc/localtime

    # Gerar chave para o git (se ainda não estiver gerada)
    if [ ! -f "/root/.ssh/id_ed25519" ]; then
        ssh-keygen -t ed25519 -N '' -C "keven.barbosa@cerradopneus.com.br" -f /root/.ssh/id_ed25519
        cat /root/.ssh/id_ed25519.pub

        # Adicionando GitHub nos hosts confiáveis
        ssh-keyscan github.com >> ~/.ssh/known_hosts
        echo "AUTORIZE A CHAVE NO GIT E REINICIE O CONTAINER"
        read -p "AGUARDANDO REINICIAR O CONTAINER"
    fi
fi

# Vá para o diretório do projeto
cd /code

# Realize o login no GitHub (você precisa ter suas credenciais ou chave SSH configuradas)
if [ -z "$(git config --global user.name)" ]; then
    git config --global user.name "keven-cerrado"
    git config --global user.email "keven.barbosa@cerradopneus.com.br"
fi

# Atualiza o repositório
git init
git remote add origin git@github.com:keven-cerrado/bridgestoneAPI.git
git reset --hard HEAD
git clean -f -d
git pull origin main
git checkout main

# Instale as dependências
pip install --no-cache-dir -r /code/requirements.txt

# Inicie a aplicação
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4