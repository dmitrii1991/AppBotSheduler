FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN useradd appuser && chown -R appuser /app
USER appuser

COPY ./app/app /app/app
COPY ./app/logs /app/logs
COPY ./app/routers /app/routers
COPY ./app/main.py /app/main.py
COPY ./app/dependencies.py /app/dependencies.py
COPY ./app/settings.py /app/settings.py
COPY ./app/nginx/conf /app/nginx/conf
COPY ./requirements.txt /requirements.txt
COPY ./app/nginx/cert/pycry.key /etc/ssl/pycry.key
COPY ./app/nginx/cert/pycry.crt /etc/ssl/pycry.crt

RUN pip install -r  /requirements.txt
WORKDIR /app
RUN aerich init -t settings.TORTOISE_ORM
RUN aerich init-db
RUN aerich migrate
RUN aerich upgrade

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "6", "--proxy-headers"]
