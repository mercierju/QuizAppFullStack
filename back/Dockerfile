FROM python:3.9-slim-buster

RUN apt-get update && \
apt-get install -y libpq-dev gcc

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Lancer l'application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]