FROM python:3.11
LABEL authors="ruvl"

COPY ./panther_documents /srv/www/panther_documents
WORKDIR /srv/www/panther_documents

RUN pip3 install -r requirements.txt

RUN chmod +x entrypoint.sh
ENTRYPOINT ["sh", "entrypoint.sh"]
