QUERY_SEARCH_PERSON = """
SELECT nconst, primary_name, birth_year, death_year, primary_profession, known_for_titles
FROM imdb.name_basics
WHERE primary_name ILIKE '%' || $1 || '%'
ORDER BY primary_name
LIMIT 20;
"""

QUERY_SEARCH_TITLE = """
SELECT tconst, primary_title, original_title, title_type, start_year, end_year,
       runtime_minutes, genres
FROM imdb.title_basics
WHERE primary_title ILIKE '%' || $1 || '%'
ORDER BY start_year NULLS LAST
LIMIT 20;
"""

QUERY_PERSON_DETAILS = """
SELECT nconst, primary_name, birth_year, death_year, primary_profession, known_for_titles
FROM imdb.name_basics
WHERE nconst = $1;
"""

QUERY_KNOWN_FOR = """
SELECT b.tconst, b.primary_title
FROM imdb.title_basics b
WHERE b.tconst = ANY($1::text[]);
"""

QUERY_TITLE_DETAILS = """
SELECT b.tconst, b.primary_title, b.original_title, b.title_type,
       b.start_year, b.end_year, b.runtime_minutes, b.genres,
       r.average_rating, r.num_votes
FROM imdb.title_basics b
LEFT JOIN imdb.title_ratings r ON r.tconst = b.tconst
WHERE b.tconst = $1;
"""

QUERY_TITLE_CAST = """
SELECT p.category, p.job, p.characters, n.primary_name
FROM imdb.title_principals p
LEFT JOIN imdb.name_basics n ON p.nconst = n.nconst
WHERE p.tconst = $1
ORDER BY p.ordering ASC;
"""
