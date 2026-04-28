FROM debian:bookworm AS build

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libssl-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

COPY *.c *.h Makefile ./

RUN make

FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libssl3 zlib1g socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=build /src/backpack /app/backpack

RUN chmod +x /app/backpack \
    && mkdir -p /data/storage

EXPOSE 30034

ENTRYPOINT socat -s tcp-l:30034,reuseaddr,fork exec:/app/backpack\ /data/storage,stderr

