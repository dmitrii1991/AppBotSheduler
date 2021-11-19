import asyncio
import datetime

from tortoise import Tortoise
from aiogram import Bot, types
from aiogram.utils import exceptions

from app.models import *
from settings import TOKEN, POSTGRESQL_URL


async def send_message(user_id: int, log, bot, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender

    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def send_notes(logger):
    await Tortoise.init(db_url=POSTGRESQL_URL, modules={"models": ["app.models"]})
    now_date = datetime.datetime.now().date()
    events = await EventTortModel.filter(date_reminder=now_date).prefetch_related("user")
    logger.info(f"Find {len(events)} elements - events")
    if events:
        bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
        count = 0
        for event in events:
            try:
                if await send_message(
                        event.user.teleg_id, logger, bot,
                        f"EVENT: {event.type_event}!\nAT {event.date}\nNAME: {event.name}\n"
                        f"AFTER {event.days} days"):
                    count += 1
                    await event.next_step()
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30   messages per second)
            finally:
                logger.info(f"{count} messages successful sent.")
        await bot.session.close()
    await Tortoise.close_connections()
