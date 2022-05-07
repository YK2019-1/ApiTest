FROM python:3.7

COPY pip.conf  /root/.pip/pip.conf

RUN mkdir -p /var/www/html/apitest

WORKDIR /var/www/html/apitest

ADD . /var/www/html/apitest

RUN pip install -r requirements.txt