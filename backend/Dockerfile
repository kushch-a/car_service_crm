FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
# Встановлюємо залежності окремим кроком, щоб кешувати цей шар
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
