FROM python:3.13-slim

WORKDIR /app

# Dependencias del sistema mínimas (ajusta si tu bot necesita más)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiamos primero requirements para aprovechar cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código (el repo clonado)
COPY . .

CMD ["python3", "bot.py"]
