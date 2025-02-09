# Use uma imagem base do Python 3.12
FROM python:3.12-slim

WORKDIR /app

ADD Pipfile Pipfile.lock ./

RUN pipenv install --system

ADD . .

# Comando para rodar a aplicação
CMD ["python", "src/app.py"]