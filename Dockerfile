FROM python:3.9:debian-buster-slim
LABEL maintainer="ppotatoo"

RUN apt update && apt upgrade
RUN apt add --no-cache git make build-base linux-headers

WORKDIR /src
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "bot"]

