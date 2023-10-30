FROM python:3.12-alpine

RUN apk --no-cache add gcc libc-dev

WORKDIR /app

COPY requirements.txt fan_control.py ./

RUN pip install --no-cache-dir --upgrade -r requirements.txt \
    && rm requirements.txt

CMD ["python3", "fan_control.py"]
