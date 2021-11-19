import asyncio
import time

from loguru import logger
import schedule

from app_sheduler.logic import send_notes
from settings import config

logger.configure(**config)


def notes():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_notes(logger))


schedule.every().day.at("12:00").do(notes)


while True:
    schedule.run_pending()
    time.sleep(1)
