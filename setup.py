"""Script to set up the .env file and create the database."""

import os
from dotenv import load_dotenv, set_key
from flask import Flask

from config import (API_ENV_KEY, API_URL, DB_ENV_KEY, DEFAULT_DBPATH,
                    ENV_FILE, get_db_path)
from models import db


ENV_KEYS = [API_ENV_KEY, DB_ENV_KEY]
KEY_PROMPTS = {
    API_ENV_KEY: f"Enter your omdb API key (use {API_URL} to get one): ",
    DB_ENV_KEY: "Enter path to your database (enter nothing to use "
                f"default path: {DEFAULT_DBPATH}): "
}


def setup_env():
    """
    Assign values to keys in .env files.
    """
    default_key_values = {DB_ENV_KEY: DEFAULT_DBPATH}
    if not os.path.exists(ENV_FILE):
        open(ENV_FILE, "w", encoding="utf-8").close()
    load_dotenv()
    for key in ENV_KEYS:
        current_key = os.getenv(key)
        if current_key:
            if input(f"Do you want to set up new {key}? [y/n]").lower() != "y":
                continue
        new_value = input(KEY_PROMPTS[key])
        if new_value:
            set_key(ENV_FILE, key, new_value)
        else:
            if current_key:
                print(f"Skipping. Will keep the current {key}.")
            elif default_key_values.get(key, False):
                set_key(ENV_FILE, key, default_key_values[key])
                print(f"{key} was set to default value "
                      f"{default_key_values[key]}.")
            else:
                print(f"Warning: You did not provide {key}. Some "
                      "functionality might not work.")

    print("Finished setup.")


def setup_db():
    """Create the database tables defined in ``models``.

    Idempotent: tables that already exist are left untouched.
    """
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{get_db_path()}"
    db.init_app(app)
    with app.app_context():
        db.create_all()
    print("Database is ready.")


if __name__ == "__main__":
    setup_env()
    setup_db()
