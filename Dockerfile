FROM python:3.10-slim AS requirements

WORKDIR /opt/shiro/

COPY pyproject.toml poetry.lock /opt/shiro/
RUN pip install poetry && \
    poetry export --output requirements.txt --without-hashes

FROM python:3.10-slim AS runner

WORKDIR /opt/shiro/

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get clean && \
    useradd -m shiro
COPY --from=requirements /opt/shiro/requirements.txt /opt/shiro/
RUN pip install -r requirements.txt

COPY shiro /opt/shiro/

USER shiro

CMD ["python", "-OO", "main.py"]
