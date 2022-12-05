FROM python:latest

COPY requirements.txt .

RUN apt-get update \
 && apt-get install -y docker.io \
 && pip install -r requirements.txt

COPY . ./

CMD ["flask", "--app", "dlogs", "run", "--host", "0.0.0.0"]
