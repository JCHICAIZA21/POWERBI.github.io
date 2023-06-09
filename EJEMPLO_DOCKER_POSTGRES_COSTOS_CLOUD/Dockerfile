    FROM python:3.9-slim-buster

    RUN apt-get update \
        && apt-get install -y postgresql-server-dev-all\
        && apt-get install -y gcc postgresql-client \
        && rm -rf /var/lib/apt/lists/*

    WORKDIR /code

    ENV FLASK_APP app\app.py
    ENV FLASK_RUN_HOST 0.0.0.0
  
    COPY requirements.txt .

    RUN pip install --no-cache-dir -r requirements.txt

    COPY . .

    ENTRYPOINT ["python", "app/app.py"]
    #CMD ["flask", "run", "--host", "0.0.0.0"]
