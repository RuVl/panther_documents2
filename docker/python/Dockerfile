FROM python:3.11
LABEL authors="ruvl"

COPY ./panther_documents /srv/www/panther_documents
WORKDIR /srv/www/panther_documents

RUN pip install -r requirements.txt
