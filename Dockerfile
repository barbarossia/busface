FROM python:3.7.4-slim as base

# Create app directory
WORKDIR /app

RUN apt-get -o Acquire::Check-Valid-Until=false update \
    && apt-get install \
    --no-install-recommends --yes \
    build-essential libpq-dev cron git \
    python3-dev --yes

FROM base as build

COPY . /app

COPY requirements.txt .

RUN mkdir /install

RUN pip download --destination-directory /install -r /app/requirements.txt

FROM python:3.7.4-slim  as release

RUN apt-get update && apt-get -y install cron git libglib2.0-0 libsm6 libxext6 libxrender-dev
RUN apt-get update && apt-get -y install build-essential cmake pkg-config
RUN apt-get update && apt-get -y install libgtk-3-dev libboost-python-dev

WORKDIR /app

COPY --from=build /install /install

COPY requirements.txt .

RUN pip install --no-index --find-links=/install -r requirements.txt

COPY busface /app/busface

RUN mkdir /app/docker

COPY docker/entry.sh /app/docker/

RUN touch /var/log/busface.log

RUN rm -rf /install &&  rm -rf /root/.cache/pip

RUN chmod 755 /app/docker/*.sh

EXPOSE 8000

LABEL maintainer="barbarossia <barbarossia@gmail.com>"

CMD ["/app/docker/entry.sh"]