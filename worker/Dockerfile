
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY get_messages_local_key.py .

CMD ["python", "get_messages_local_key.py"]
