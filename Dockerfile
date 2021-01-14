FROM python:3.9
ENV FLASK_APP=geopopcountd
ENV FLASK_RUN_PORT=80
EXPOSE 80
WORKDIR /app
COPY cities500.txt ./cities500.txt
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY geopopcountd ./geopopcountd
ENTRYPOINT ["flask" , "run", "-h", "0.0.0.0"]
