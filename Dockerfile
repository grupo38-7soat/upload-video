# Use uma imagem base do Python 3.12
FROM python:3.12-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie o arquivo de requisitos e instale as dependências
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação
COPY . .

# Expoe a porta que a aplicação irá rodar
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["python", "src/app.py"]