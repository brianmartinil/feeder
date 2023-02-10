FROM python:3.8-slim-buster
VOLUME /config
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --disable-pip-version-check -r requirements.txt
COPY ./app/ .
CMD ["python3","feeder.py","/config/feeds.yml"]
