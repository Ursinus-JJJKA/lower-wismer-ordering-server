ARG PYTHON_VERSION=latest

FROM python:${PYTHON_VERSION}

WORKDIR /code

RUN mkdir /code/app

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/run/secrets/server_x509_key", "--ssl-certfile", "/run/secrets/server_x509_cert"]
