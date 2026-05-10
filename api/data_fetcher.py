"""
Connect to omdb API to fetch data about a movie.
"""

import requests
from config import API_URL, get_api_key


API_KEY = get_api_key()
AUTHORIZATION_FAILED_MESSAGE = """
Authorization failed. Either API key was not set up or is invalid.
  Please run:
      python setup.py
  to set up your API key.
"""


def fetch_data(title: str) -> dict:
    """
    Fetch information about the movie with the title [title].

    Args:
        title: Search string passed to API.

    Returns:
        Dictionary with the information about the movie.
    """
    result = requests.get(f"{API_URL}?apikey={API_KEY}&t={title}",
                          timeout=30)
    if result.status_code == 200:
        return result.json()
    if result.status_code == 401:
        print(AUTHORIZATION_FAILED_MESSAGE)
        return {"Response": "False", "Error": ""}
    return {"Response": "False", "Error": "Server error. Status code "
            f"{result.status_code}."}
