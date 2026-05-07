"""Script to set up .env file"""

import os
from dotenv import load_dotenv, set_key
from config import (API_ENV_KEY, API_URL, DB_ENV_KEY, DEFAULT_DBPATH,
                    ENV_FILE)


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


if __name__ == "__main__":
    setup_env()
