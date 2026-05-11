"""Default settings and file paths"""

import os
from datetime import datetime
from dotenv import load_dotenv, set_key


RATING_STEP = 0.1
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
DEFAULT_DBNAME = "MoviWeb.db"
DEFAULT_DBPATH = os.path.join(PROJECT_ROOT, "data", DEFAULT_DBNAME)
API_URL = "http://www.omdbapi.com/"

API_ENV_KEY = "API_KEY"
DB_ENV_KEY = "DATABASE_PATH"

YEAR_MIN = 1878  # The year when the first movie was made.
YEAR_MAX = datetime.now().year
LOWEST_RATING = 0.0
HIGHEST_RATING = 10.0


def get_api_key() -> str | None:
    """
    Load .env file and get the API key.

    Returns:
        API key or ``None`` if it is not set.
    """
    load_dotenv()
    return os.getenv(API_ENV_KEY)


def get_db_path() -> str:
    """
    Load .env file and get the path to the database. Make parent directory
    if it does not exist. If user refuses to make the parent directory use
    the project root. If the path was not set in .env or the user did not
    make missing directories, set the correct path in .env.

    Returns:
        Path to the database.
    """
    load_dotenv()
    db_path = os.getenv(DB_ENV_KEY)
    add_path_to_dotenv = False
    if not db_path:
        db_path = DEFAULT_DBPATH
        print(f"Using default database path: {DEFAULT_DBPATH}")
        add_path_to_dotenv = True

    if not os.path.exists(os.path.dirname(db_path)):
        if (input(f"Create directories {os.path.dirname(db_path)}?"
                  " [y/n]").lower() == "y"):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        else:
            print("Database will be saved in the project root.")
            db_path = os.path.join(PROJECT_ROOT, DEFAULT_DBNAME)
            add_path_to_dotenv = True

    if add_path_to_dotenv:
        open(ENV_FILE, "a", encoding="utf-8").close()
        set_key(ENV_FILE, DB_ENV_KEY, db_path)

    return db_path
