FROM python:3.11
ARG POETRY_VERSION=1.4.1
ENV FLASK_APP=geopopcountd
ENV FLASK_RUN_PORT=80
EXPOSE 80
WORKDIR /app
COPY cities500.txt ./cities500.txt
RUN pip install "poetry==${POETRY_VERSION}"
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi
COPY geopopcountd ./geopopcountd
ENTRYPOINT ["flask" , "run", "-h", "0.0.0.0"]
