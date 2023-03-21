FROM python:3.11-slim AS build
ARG POETRY_VERSION=1.4.1
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /opt
RUN pip install "poetry==${POETRY_VERSION}"
COPY poetry.lock pyproject.toml ./
RUN poetry export -o requirements.txt

FROM python:3.11-slim
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
EXPOSE 80
WORKDIR /app
COPY --from=build /opt/requirements.txt ./
RUN pip install -r requirements.txt
COPY cities500.txt ./cities500.txt
COPY geopopcountd ./geopopcountd
ENTRYPOINT ["gunicorn" , "--bind", "0.0.0.0:80", "geopopcountd:app"]
