FROM python:3.9.5-alpine
LABEL maintainer="ppotatoo"

RUN apk update && apk upgrade
RUN apk add --no-cache git make build-base linux-headers

WORKDIR /src
COPY . .
RUN pip install -r requirements.txt


