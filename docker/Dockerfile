FROM python:3.10.0-bullseye

WORKDIR /

COPY ./scrapyd.conf /etc/scrapyd/
COPY ./requirements.txt /requirements.txt
COPY ./sources.list /etc/apt/sources.list

RUN apt-get -y upgrade
RUN apt-get -y update
RUN apt-get install -y libxml2-dev libxslt-dev python-dev\
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /requirements.txt \
    && rm /requirements.txt \
    && pip install --no-cache-dir scrapyd

EXPOSE 6800

CMD ["scrapyd"]