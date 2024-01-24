FROM python:3
LABEL authors="dune"

WORKDIR /usr/src/app
COPY . /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt

ENV docker=TRUE
CMD sh -c "python3 main.py > nohup.out"
