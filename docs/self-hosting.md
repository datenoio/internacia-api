# Self-hosting

internacia-api is a read-only service over one immutable `internacia.duckdb` file. It keeps no
state between requests and writes nothing, so instances can be scaled out freely, and the data
changes only when you deploy a new database (a new image tag or a new mounted file).

## Process model and resources

- The server opens one read-only DuckDB connection at startup; each request runs on its own
  cursor. Route handlers are synchronous and run in the server's thread pool (40 threads by
  default), so one process serves concurrent requests.
- With `PRELOAD_CATALOGS=true` (the default), the full country and block lists, block types and
  the currency, language, time zone and region catalogs are loaded into memory at startup and
  served from there. With internacia-db 3.0.0 this takes under a second and about 80 MB;
  `GET /blocks` drops from about 110 ms to under 20 ms per 1,000 blocks and `GET /countries`
  from about 12 ms to 2 ms. Set `PRELOAD_CATALOGS=false` on small instances; filtered queries,
  single records and search always go to the database.
- Plan on roughly 300 MB of memory per process with preloading on. For more throughput, run
  more containers rather than `uvicorn --workers N`: every worker loads its own catalogs.
- `/health` runs a query and returns 503 if the database cannot be read. Use it for readiness
  and liveness probes; the Docker image already declares it as its `HEALTHCHECK`.

## Production settings

| Variable | Recommendation |
|---|---|
| `INTERNACIA_DB_VERSION` | Set it (the image does) so a wrong file stops startup instead of being served |
| `CORS_ORIGINS` | List the browser origins that call the API, or keep `["*"]` for a public read-only service |
| `CACHE_MAX_AGE` | How long clients and caches may reuse a response. Data changes only on deploy, so hours are fine; after deploying new data, clients may see the old data for up to this long |
| `PRELOAD_CATALOGS` | `true` unless memory is tight |
| `FORWARDED_ALLOW_IPS` | Addresses of your reverse proxy (see below) |

The image runs as a non-root user and works with a read-only root filesystem; `compose.yaml`
sets `read_only: true` with a `/tmp` tmpfs.

## Behind a reverse proxy

List responses contain an absolute `next` URL and moved IDs answer `301` with an absolute
`Location`, both built from the request. Behind a proxy the API must see the public scheme and
host:

- The image starts uvicorn with `--proxy-headers`, which applies `X-Forwarded-Proto` and
  `X-Forwarded-For` from trusted addresses only. uvicorn trusts `127.0.0.1` by default; set
  `FORWARDED_ALLOW_IPS` to the proxy's address (or `*` when the container is reachable only
  through the proxy).
- uvicorn does not read `X-Forwarded-Host`: the proxy must pass the original `Host` header.
- To serve the API under a path prefix, strip the prefix in the proxy and start uvicorn with
  `--root-path /prefix` so links and `/docs` include it.

Responses are uncompressed JSON (a full page of 1,000 blocks is about 9 MB), so let the proxy
compress them.

### nginx

```nginx
limit_req_zone $binary_remote_addr zone=internacia:10m rate=10r/s;
proxy_cache_path /var/cache/nginx/internacia levels=1:2 keys_zone=internacia_cache:10m
                 max_size=1g inactive=1h use_temp_path=off;

upstream internacia_api {
    server 127.0.0.1:8000;
    keepalive 16;
}

server {
    listen 443 ssl;
    server_name data.example.org;

    gzip on;
    gzip_types application/json;
    gzip_min_length 1024;

    location / {
        limit_req zone=internacia burst=40 nodelay;
        limit_req_status 429;

        proxy_cache internacia_cache;          # honours the API's Cache-Control and ETag
        proxy_cache_lock on;
        add_header X-Cache-Status $upstream_cache_status;

        proxy_pass http://internacia_api;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location = /health {
        proxy_pass http://internacia_api;
        proxy_set_header Host $host;
    }
}
```

`proxy_cache` stores responses for `CACHE_MAX_AGE` and answers `If-None-Match` itself. When
you deploy new data, the API's ETags change; purge or wait out the proxy cache as well.

### Caddy

```caddyfile
data.example.org {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8000
}
```

Caddy sends `X-Forwarded-Proto` and keeps the `Host` header. Rate limiting needs the
[`caddy-ratelimit`](https://github.com/mholt/caddy-ratelimit) plugin, for example:

```caddyfile
data.example.org {
    encode zstd gzip
    rate_limit {
        zone per_client {
            key {remote_host}
            events 600
            window 1m
        }
    }
    reverse_proxy 127.0.0.1:8000
}
```

### Traefik

```yaml
http:
  middlewares:
    internacia-ratelimit:
      rateLimit:
        average: 10
        burst: 40
    internacia-compress:
      compress: {}
  routers:
    internacia:
      rule: Host(`data.example.org`)
      service: internacia
      middlewares: [internacia-ratelimit, internacia-compress]
  services:
    internacia:
      loadBalancer:
        servers:
          - url: http://internacia-api:8000
```

## Rate limiting

The API has no built-in rate limiting or authentication: apply both at the proxy. The limits
above (10 requests per second per client, bursts of 40) are a starting point for a public
instance. Things to weigh:

- Large pages cost the most. `GET /blocks?limit=1000` returns about 9 MB; clients that need
  only a few fields should use `fields=` (for example `fields=id,name`). Consider a stricter
  zone for `limit` values above the default of 100 if bandwidth matters.
- `/search` is the most expensive query per request (about 20 ms); a separate, lower limit
  for it protects the rest of the API.
- Conditional requests (`If-None-Match`) that match are answered with `304` without touching
  the database, and cached responses never reach the API. With a proxy cache, the limit mostly
  protects bandwidth.
- Exclude `/health` from limits so probes are not throttled.

## Updating the data

Each internacia-db release is a new image tag (`<api>-db-<db>`, `db-<db>`). Roll it out like any
stateless deployment; responses from the new instances carry the new `X-Internacia-Version` and
new ETags. To serve a database the image does not bake in, mount it read-only over
`/data/internacia.duckdb` and set `INTERNACIA_DB_VERSION` to its version (see the README).
