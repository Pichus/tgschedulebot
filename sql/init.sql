CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    user_telegram_id INTEGER NOT NULL,
    user_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chats (
    chat_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Users (user_id),
    chat_telegram_id INTEGER NOT NULL,
    chat_name TEXT NOT NULL,
    message_thread_id INTEGER,
    schedule_message_to_edit_id INTEGER
);

CREATE TABLE IF NOT EXISTS schedule_types (
    schedule_type_id SERIAL PRIMARY KEY,
    schedule_type VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO schedule_types (schedule_type) VALUES ( 'low'), ('high');

CREATE TABLE IF NOT EXISTS schedules (
    schedule_id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES chats (chat_id),
    schedule_type VARCHAR(100) NOT NULL REFERENCES schedule_types (schedule_type),
    schedule TEXT NOT NULL
)