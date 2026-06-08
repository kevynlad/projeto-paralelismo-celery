FROM python:3.11-slim

WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da API
COPY . .

# Comando padrão: inicia a API
# O worker do Celery é iniciado como serviço separado no docker-compose/Railway
CMD uvicorn main:app --host 0.0.0.0 --port $PORT

