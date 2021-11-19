FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./app/app /app/app
COPY ./app/logs /app/logs
COPY ./app/app_bot /app/app_bot
COPY ./app/main_bot.py /app/main_bot.py
COPY ./app/settings.py /app/settings.py
COPY ./requirements.txt /requirements.txt

RUN pip install -r  /requirements.txt
WORKDIR /app

CMD ["python", "main_bot.py"]
