FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --gid 10001 platformhealth \
    && useradd \
        --uid 10001 \
        --gid platformhealth \
        --create-home \
        --shell /usr/sbin/nologin \
        platformhealth

COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    --upgrade pip \
    && pip install \
        --no-cache-dir \
        -r requirements.txt

COPY app ./app

RUN chown -R platformhealth:platformhealth /app

USER platformhealth

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
