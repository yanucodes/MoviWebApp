"""
Connect to omdb API to fetch data about a movie.
"""

import requests
from config import API_URL, get_api_key


API_KEY = get_api_key()


def fetch_data(title: str) -> dict:
    """
    Fetch information about the movie with the title [title].

    Args:
        title: Search string passed to API.

    Returns:
        Dictionary with the information about the movie. On failure,
        returns a dict shaped like an OMDb error response:
        ``{"Response": "False", "Error": <message>}``.
    """
    try:
        result = requests.get(API_URL,
                              params={"apikey": API_KEY, "t": title},
                              timeout=30)
        result.raise_for_status()
        return result.json()
    except requests.RequestException as error:
        return {"Response": "False", "Error": f"Network error: {error}"}
    except ValueError:
        return {"Response": "False", "Error": "Invalid response from OMDb."}
