FROM python:3.12-alpine AS build

ENV PIPENV_VENV_IN_PROJECT=1

RUN apk --no-cache add gcc libc-dev && \
    pip install pipenv

WORKDIR /build

COPY Pipfile Pipfile.lock ./

RUN pipenv sync

FROM build

WORKDIR /app

COPY --from=build /build/.venv/ ./.venv/
COPY fan_control.py ./

CMD ["/app/.venv/bin/python", "fan_control.py"]
