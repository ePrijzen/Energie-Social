#**************************************
# Build By:
# https://itheo.tech 2022
# MIT License
# Dockerfile to run the python script
#**************************************

# FROM python:3.10.4-slim-buster as base
FROM python:3.11.0-slim-buster as base

LABEL org.opencontainers.image.authors="info@itheo.tech"
ENV TZ=Europe/Amsterdam

RUN apt-get update && apt-get install -y tzdata

RUN pip install poetry

WORKDIR /src

COPY poetry.lock .
COPY pyproject.toml .
COPY ./src .

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

FROM base as dev
ENV PY_ENV=dev
CMD [ "python", "app.py" ]

FROM base as acc
ENV PY_ENV=acc
CMD [ "python", "app.py" ]

FROM base as PROD
ENV PY_ENV=prod
CMD [ "python", "app.py" ]