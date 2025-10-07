FROM python:3.13-slim

WORKDIR /app

COPY ./../../requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential pkg-config default-libmysqlclient-dev python3.13-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./../../django_project/ ./

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
