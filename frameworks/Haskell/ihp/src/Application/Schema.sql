CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE World (
    id SERIAL PRIMARY KEY NOT NULL,
    randomnumber INT DEFAULT 0 NOT NULL
);
CREATE TABLE Fortune (
    id SERIAL PRIMARY KEY NOT NULL,
    message TEXT NOT NULL
);
