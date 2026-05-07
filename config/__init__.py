"""Default settings and file paths and a script for setting those up in .env"""

from .config import (YEAR_MIN, YEAR_MAX, LOWEST_RATING, HIGHEST_RATING,
                     ROUND_NDIGITS, API_ENV_KEY, API_URL, get_api_key,
                     DB_ENV_KEY, DEFAULT_DBPATH, get_db_path, ENV_FILE,
                     HTML_TEMPLATE, REPLACE_TITLE, REPLACE_GRID,
                     MOVIES_HTML_PATH, DEFAULT_TITLE, TABS_NUM,
                     JSON_STORAGE_PATH)


__all__ = ["YEAR_MIN", "YEAR_MAX", "LOWEST_RATING", "HIGHEST_RATING",
           "ROUND_NDIGITS", "API_ENV_KEY", "API_URL", "get_api_key",
           "DB_ENV_KEY", "DEFAULT_DBPATH", "get_db_path", "ENV_FILE",
           "HTML_TEMPLATE", "REPLACE_TITLE", "REPLACE_GRID",
           "MOVIES_HTML_PATH", "DEFAULT_TITLE", "TABS_NUM",
           "JSON_STORAGE_PATH"]
