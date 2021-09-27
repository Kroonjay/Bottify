FROM python:3.8

WORKDIR /app

ENV SERVER_HOST 0.0.0.0
ENV SERVER_PORT 8001

COPY requirements.txt ./

EXPOSE 8001

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./main.py"]