FROM python:3
LABEL authors="dune"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD sh -c "python3 main.py > nohup.out"
