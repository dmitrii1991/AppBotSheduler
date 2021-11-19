FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./app/app /app/app
COPY ./app/logs /app/logs
COPY ./app/main_sheduler /app/main_sheduler
COPY ./app/main_sheduler.py /app/main_sheduler.py
COPY ./app/settings.py /app/settings.py
COPY ./requirements.txt /requirements.txt

RUN pip install -r  /requirements.txt
WORKDIR /app

CMD ["python", "main_sheduler.py"]