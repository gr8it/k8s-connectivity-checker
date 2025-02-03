FROM python:3.9-slim

WORKDIR /app

LABEL org.opencontainers.image.source=https://github.com/gr8it/k8s-connectivity-checker

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8080

CMD ["python", "app.py"]
