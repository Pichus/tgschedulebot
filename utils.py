import json
from datetime import datetime

from aiogram.types import MessageEntity


def message_entities_to_json_string(message_entities: list[MessageEntity]) -> str:
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
