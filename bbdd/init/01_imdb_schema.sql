CREATE SCHEMA IF NOT EXISTS imdb;
SET search_path TO imdb;

-- 1. name_basics
CREATE TABLE IF NOT EXISTS imdb.name_basics (
    nconst             VARCHAR(16) PRIMARY KEY,
    primary_name       TEXT,
    birth_year         INTEGER,
    death_year         INTEGER,
    primary_profession TEXT,
    known_for_titles   TEXT,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. title_basics
CREATE TABLE IF NOT EXISTS imdb.title_basics (
    tconst           VARCHAR(16) PRIMARY KEY,
    title_type       VARCHAR(32),
    primary_title    TEXT NOT NULL,
    original_title   TEXT,
    is_adult         BOOLEAN,
    start_year       INTEGER,
    end_year         INTEGER,
    runtime_minutes  INTEGER,
    genres           TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. title_principals
CREATE TABLE IF NOT EXISTS imdb.title_principals (
    id          SERIAL PRIMARY KEY,
    tconst      VARCHAR(16) NOT NULL,
    ordering    INTEGER NOT NULL,
    nconst      VARCHAR(16),
    category    TEXT,
    job         TEXT,
    characters  TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tconst, ordering)
);

-- 4. title_ratings
CREATE TABLE IF NOT EXISTS imdb.title_ratings (
    tconst          VARCHAR(16) PRIMARY KEY,
    average_rating  NUMERIC(3,1),
    num_votes       INTEGER,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
