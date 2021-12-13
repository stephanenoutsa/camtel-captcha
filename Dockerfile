FROM python:3.7.11

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt --default-timeout=9000

COPY . .

CMD ["python3", "app.py", "--host=0.0.0.0"]
