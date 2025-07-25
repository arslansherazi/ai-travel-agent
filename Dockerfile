FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY .env.example .env

EXPOSE 7860

CMD ["python", "-m", "main"]
