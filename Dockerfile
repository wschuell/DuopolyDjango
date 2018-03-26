FROM python:3
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

#ADD requirements-prod.txt /code/
#RUN apt-get update && apt-get install --yes --force-yes apt-utils build-essential python-dev liblzo2-dev liblzma-dev libsqlite3-dev python-tk tmux

RUN pip install numpy psycopg2 psycopg2-binary django django-click django-crispy-forms django-bulk-update

#RUN pip install -r requirements-prod.txt

ADD . /code/
RUN bash init_db.sh
