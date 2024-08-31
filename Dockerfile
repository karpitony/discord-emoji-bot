FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
COPY commands ./commands
COPY main.py ./
COPY .env ./


RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]