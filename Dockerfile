FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY coc_server.py .
COPY .env .

CMD ["python", "coc_server.py"]

# docker build -t coc-server .
# docker run -d -p 8000:8000 coc-server