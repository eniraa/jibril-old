FROM python:3.10-slim AS requirements

WORKDIR /opt/jibril/

COPY pyproject.toml poetry.lock /opt/jibril/
RUN pip install poetry && \
    poetry export --output requirements.txt --without-hashes

FROM python:3.10-slim AS runner

WORKDIR /opt/jibril/

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get clean && \
    useradd -m jibril
COPY --from=requirements /opt/jibril/requirements.txt /opt/jibril/
RUN pip install -r requirements.txt

COPY jibril /opt/jibril/

USER jibril

CMD ["python", "-OO", "main.py"]
