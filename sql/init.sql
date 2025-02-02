CREATE TABLE IF NOT EXISTS Users (
    UserID SERIAL PRIMARY KEY,
    UserTelegramID INTEGER NOT NULL,
    UserName TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Chats (
    ChatID SERIAL PRIMARY KEY,
    UserID INTEGER NOT NULL REFERENCES Users (UserID),
    ChatTelegramID INTEGER NOT NULL,
    ChatName TEXT NOT NULL,
    MessageThreadID INTEGER,
    ScheduleMessageToEditID INTEGER
);

CREATE TABLE IF NOT EXISTS ScheduleTypes (
    ScheduleTypeID SERIAL PRIMARY KEY,
    ScheduleType VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO ScheduleTypes (ScheduleType) VALUES ( 'low'), ('high');

CREATE TABLE IF NOT EXISTS Schedules (
    ScheduleID SERIAL PRIMARY KEY,
    ChatID INTEGER NOT NULL REFERENCES Chats (ChatID),
    ScheduleType VARCHAR(100) NOT NULL REFERENCES ScheduleTypes (ScheduleType),
    Schedule TEXT NOT NULL
)