FROM python:3.13-alpine AS build

RUN apk --no-cache add gcc libc-dev && \
    pip install uv

WORKDIR /build

COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev --frozen

FROM build

WORKDIR /app

COPY --from=build /build/.venv/ ./.venv/
COPY main.py ./

CMD ["/app/.venv/bin/python", "main.py"]
