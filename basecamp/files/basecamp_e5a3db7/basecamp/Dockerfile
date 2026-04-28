FROM golang:1.25-bookworm AS server-build
WORKDIR /src/server
COPY server/go.mod server/go.sum ./
RUN go mod download
COPY server/ ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/server ./cmd/server/

FROM golang:1.25-bookworm AS revocation-build
WORKDIR /src/revocation
COPY revocation/go.mod revocation/go.sum ./
RUN go mod download
COPY revocation/ ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/revocation ./cmd/server/

FROM debian:bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends supervisor ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /var/lib/basecamp /var/lib/revocation /usr/local/share/basecamp/migrations /srv/web

COPY --from=server-build     /out/server     /usr/local/bin/server
COPY --from=revocation-build /out/revocation /usr/local/bin/revocation
COPY server/migrations/      /usr/local/share/basecamp/migrations/
COPY web/                    /srv/web/
COPY supervisord.conf        /etc/supervisor/conf.d/basecamp.conf

EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
