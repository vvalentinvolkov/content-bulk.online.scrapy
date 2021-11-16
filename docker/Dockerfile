FROM debian:buster-slim

WORKDIR /

COPY ./scrapyd.conf /etc/scrapyd/
COPY ./requirements.txt /requirements.txt
RUN set -xe \
    && apt-get update \
    && apt-get install -y autoconf \
                          build-essential \
                          libffi-dev \
                          libssl-dev \
                          libtool \
                          python3 \
                          python3-dev \
                          python3-pip

RUN pip3 install --upgrade pip3 \
    && pip3 install -r /requirements.txt \
    && rm /requirements.txt
RUN apt-get install -y scrapyd

RUN apt-get purge -y --auto-remove autoconf \
                                   build-essential \
                                   libffi-dev \
                                   libssl-dev \
                                   libtool \
                                   python-dev

EXPOSE 6800

CMD ["scrapyd"]