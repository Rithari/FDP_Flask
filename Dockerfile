FROM python:3.12.1-bookworm

RUN apt install gcc

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 4000
CMD ["flask", "run", "--host=0.0.0.0"]