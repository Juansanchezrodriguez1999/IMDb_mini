import os
import gzip
import shutil
import sys
import time
import requests
from pathlib import Path
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from tqdm import tqdm
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger()


IMDB_URLS = {
    "name.basics": "https://datasets.imdbws.com/name.basics.tsv.gz",
    "title.basics": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "title.principals": "https://datasets.imdbws.com/title.principals.tsv.gz",
    "title.ratings": "https://datasets.imdbws.com/title.ratings.tsv.gz",
}

DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "imdb_data"))
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

DB = dict(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST", "db"),
    port=os.getenv("POSTGRES_PORT", "5432"),
)


def download_and_extract(name, url):
    gz_path = DOWNLOAD_DIR / f"{name}.tsv.gz"
    tsv_path = DOWNLOAD_DIR / f"{name}.tsv"

    if tsv_path.exists():
        logger.info(f"{tsv_path} already exists, skipping download.")
        return tsv_path

    logger.info(f"Downloading {name} ...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))

        with open(gz_path, "wb") as f:
            for chunk in tqdm(r.iter_content(chunk_size=8192), total=(total // 8192) + 1):
                if chunk:
                    f.write(chunk)

    logger.info("Decompressing ...")
    with gzip.open(gz_path, "rb") as f_in, open(tsv_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    return tsv_path


def copy_file_to_table(conn, tsv_path, table, columns):
    with conn.cursor() as cur:
        with open(tsv_path, "r", encoding="utf-8") as f:
            sql_text = sql.SQL(
                """
                COPY imdb.{table} ({cols})
                FROM STDIN WITH (
                    FORMAT csv,
                    DELIMITER E'\\t',
                    NULL '\\N',
                    HEADER TRUE,
                    QUOTE E'\\b'
                );
            """
            ).format(
                table=sql.Identifier(table),
                cols=sql.SQL(",").join(map(sql.Identifier, columns)),
            )
            cur.copy_expert(sql_text, f)

    conn.commit()
    logger.info(f"Loaded {table} from {tsv_path}")


PREPARE_SQL = """
SET search_path TO imdb;

CREATE EXTENSION IF NOT EXISTS pg_trgm;


DELETE FROM imdb.title_principals p
WHERE NOT EXISTS (
    SELECT 1 FROM imdb.title_basics b WHERE b.tconst = p.tconst
);

DELETE FROM imdb.title_principals p
WHERE p.nconst IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM imdb.name_basics n WHERE n.nconst = p.nconst
);

DELETE FROM imdb.title_ratings r
WHERE NOT EXISTS (
    SELECT 1 FROM imdb.title_basics b WHERE b.tconst = r.tconst
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_principals_title'
    ) THEN
        ALTER TABLE imdb.title_principals
            ADD CONSTRAINT fk_principals_title
            FOREIGN KEY (tconst) REFERENCES imdb.title_basics(tconst)
            ON DELETE CASCADE;
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_principals_name'
    ) THEN
        ALTER TABLE imdb.title_principals
            ADD CONSTRAINT fk_principals_name
            FOREIGN KEY (nconst) REFERENCES imdb.name_basics(nconst)
            ON DELETE SET NULL;
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'fk_ratings_title'
    ) THEN
        ALTER TABLE imdb.title_ratings
            ADD CONSTRAINT fk_ratings_title
            FOREIGN KEY (tconst) REFERENCES imdb.title_basics(tconst)
            ON DELETE CASCADE;
    END IF;
END$$;

CREATE INDEX IF NOT EXISTS idx_name_basics_primary_name
    ON imdb.name_basics USING gin (primary_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_title_basics_primary_title
    ON imdb.title_basics USING gin (primary_title gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_title_basics_title_type
    ON imdb.title_basics(title_type);

CREATE INDEX IF NOT EXISTS idx_principals_tconst
    ON imdb.title_principals(tconst);

CREATE INDEX IF NOT EXISTS idx_principals_nconst
    ON imdb.title_principals(nconst);

CREATE INDEX IF NOT EXISTS idx_ratings_num_votes
    ON imdb.title_ratings(num_votes DESC);

CREATE INDEX IF NOT EXISTS idx_ratings_avg
    ON imdb.title_ratings(average_rating DESC);


CREATE OR REPLACE VIEW imdb.person_info AS
SELECT
    n.nconst,
    n.primary_name,
    n.birth_year,
    n.death_year,
    n.primary_profession,
    n.known_for_titles
FROM imdb.name_basics n;

CREATE OR REPLACE VIEW imdb.title_info AS
SELECT
    b.tconst,
    b.primary_title,
    b.original_title,
    b.title_type,
    b.start_year,
    b.end_year,
    b.runtime_minutes,
    b.genres,
    r.average_rating,
    r.num_votes
FROM imdb.title_basics b
LEFT JOIN imdb.title_ratings r ON r.tconst = b.tconst;

CREATE OR REPLACE VIEW imdb.title_cast AS
SELECT
    p.tconst,
    t.primary_title,
    p.ordering,
    p.category,
    p.job,
    p.characters,
    n.primary_name AS person_name
FROM imdb.title_principals p
LEFT JOIN imdb.name_basics n ON n.nconst = p.nconst
LEFT JOIN imdb.title_basics t ON t.tconst = p.tconst;
"""

def prepare_schema(conn):
    with conn.cursor() as cur:
        cur.execute(PREPARE_SQL)
    conn.commit()


def main():
    start = time.time()
    logger.info("Start ETL IMDb process")

    paths = {name: download_and_extract(name, url) for name, url in IMDB_URLS.items()}

    conn = psycopg2.connect(**DB)

    try:
        copy_file_to_table(conn, paths["name.basics"], "name_basics", [
            "nconst", "primary_name", "birth_year", "death_year",
            "primary_profession", "known_for_titles"
        ])

        copy_file_to_table(conn, paths["title.basics"], "title_basics", [
            "tconst", "title_type", "primary_title", "original_title",
            "is_adult", "start_year", "end_year", "runtime_minutes", "genres"
        ])

        copy_file_to_table(conn, paths["title.principals"], "title_principals", [
            "tconst", "ordering", "nconst", "category", "job", "characters"
        ])

        copy_file_to_table(conn, paths["title.ratings"], "title_ratings", [
            "tconst", "average_rating", "num_votes"
        ])

        logger.info("Files loaded successfully into the database.")

        logger.info("Preparing tables and indexes...")
        prepare_schema(conn)

    finally:
        conn.close()

    elapsed = time.time() - start
    logger.info(f"Finish ETL IMDb {elapsed:.1f} seconds")


if __name__ == "__main__":
    main()
