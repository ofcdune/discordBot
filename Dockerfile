FROM python11
LABEL authors="dune"

WORKDIR /app
COPY . /app

RUN sh -c "pip install -r requirements.txt"

ENV docker=TRUE
CMD sh -c "python3 main.py > nohup.out"
