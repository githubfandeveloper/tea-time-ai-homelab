FROM docker.io/python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY webhook_server.py .
COPY investigator.py .
EXPOSE 8080
CMD ["python", "webhook_server.py"]