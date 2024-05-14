FROM python:3.11

WORKDIR /app

COPY packages /packages
COPY requirements.txt .

RUN pip install --no-index --find-links=/packages -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
