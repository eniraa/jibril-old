FROM python:3.10-slim AS requirements

WORKDIR /opt/shiro/

COPY pyproject.toml poetry.lock /opt/shiro/
RUN pip install poetry && \
    poetry export --output requirements.txt --without-hashes

FROM python:3.10-slim AS runner

WORKDIR /opt/shiro/

COPY --from=requirements /opt/shiro/requirements.txt /opt/shiro/
COPY shiro /opt/shiro/
RUN useradd -m shiro && \
    apt-get update && apt-get install -y --no-install-recommends build-essential && \
    pip install -r requirements.txt && \
    apt-get clean

USER shiro

CMD ["python", "-OO", "main.py"]
