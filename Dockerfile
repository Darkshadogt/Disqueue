FROM python:3.12-slim

WORKDIR /app

COPY bot/requirements.txt bot/requirements.txt
RUN pip install --no-cache-dir -r bot/requirements.txt

COPY . .

WORKDIR /app/bot
CMD ["python", "-u", "main.py"]
