import json
from datetime import datetime

import pytz
from aiogram.types import MessageEntity
from asyncpg.pgproto.pgproto import timedelta
from pytz import timezone

from scheduler import CronDate


def get_most_recent_monday() -> datetime:
    today = datetime.now(tz=timezone("UTC"))
    days_since_monday = today.weekday()
    most_recent_monday = today - timedelta(days=days_since_monday)
    return datetime.combine(most_recent_monday, datetime.min.time())


def convert_cron_date_to_utc(from_timezone: str, cron_date: CronDate) -> CronDate:
    reference_monday = get_most_recent_monday()
    local_date = reference_monday + timedelta(
        days=cron_date.day_of_week, hours=cron_date.hour, minutes=cron_date.minute
    )
    timezone_object = timezone(from_timezone)
    local_time = timezone_object.localize(local_date)
    utc_time = local_time.astimezone(pytz.UTC)
    return CronDate(
        day_of_week=utc_time.weekday(), hour=utc_time.hour, minute=utc_time.minute
    )


def message_entities_to_json_string(message_entities: list[MessageEntity]) -> str:
    if not message_entities:
        return ""

    message_entities_dictionaries = []
    for message_entity in message_entities:
        message_entities_dictionaries.append(
            {
                "type": message_entity.type,
                "offset": message_entity.offset,
                "length": message_entity.length,
                "url": message_entity.url,
                "language": message_entity.language,
                "custom_emoji_id": message_entity.custom_emoji_id,
            }
        )
    json_string = json.dumps(message_entities_dictionaries)
    return json_string


def json_string_to_message_entities(json_string: str) -> list[MessageEntity]:
    if not json_string:
        return []

    message_entities = []
    message_entities_dictionaries = json.loads(json_string)

    for message_entity_dictionary in message_entities_dictionaries:
        message_entities.append(
            MessageEntity(
                type=message_entity_dictionary["type"],
                offset=int(message_entity_dictionary["offset"]),
                length=int(message_entity_dictionary["length"]),
                url=message_entity_dictionary["url"],
                language=message_entity_dictionary["language"],
                custom_emoji_id=message_entity_dictionary["custom_emoji_id"],
            )
        )

    return message_entities


def get_current_week_type() -> str:
    if datetime.now().isocalendar().week % 2 == 0:
        return "верхній"
    else:
        return "нижній"
