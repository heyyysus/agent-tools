FROM python:3-alpine

WORKDIR /app

RUN apk add --no-cache libstdc++

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . ./

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080"]
