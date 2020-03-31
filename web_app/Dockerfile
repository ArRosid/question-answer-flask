FROM python:3.8.1-slim-buster

ENV INSTALL_PATH /usr/src/app/
WORKDIR $INSTALL_PATH

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt $INSTALL_PATH/requirements.txt
RUN pip install -r requirements.txt

COPY . $INSTALL_PATH