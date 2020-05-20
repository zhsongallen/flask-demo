from alpine:latest

RUN apk add --no-cache python3-dev \
    && pip3 install --upgrade pip    
      
WORKDIR /app

COPY requirements.txt /app

RUN apk add postgresql-dev gcc python3-dev musl-dev 

RUN pip3 --no-cache-dir install -r ./requirements.txt

COPY . /app      

EXPOSE 5000

ENTRYPOINT  ["python3"]

CMD ["app.py"]