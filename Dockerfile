FROM python:3.12-alpine

RUN apk --no-cache add gcc libc-dev && \
    pip install pipenv

WORKDIR /app

COPY Pipfile Pipfile.lock fan_control.py ./

RUN pipenv install --deploy --ignore-pipfile

CMD ["pipenv", "run", "python", "fan_control.py"]
