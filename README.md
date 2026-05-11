# MoviWebApp

A Flask web app that lets multiple users keep their own list of favorite movies. Movie data is fetched from the OMDb API and stored in a shared SQLite database; each user has their own favorites and personal ratings.

## Getting Started

### Prerequisites

- Python 3.10+
- An API key from [https://www.omdbapi.com/]

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yanucodes/Movies-Web-App.git
cd Movies-Web-App

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables and the database
python setup.py
```

When you run the setup script, you will be prompted to enter your API_KEY
and the path to the database. These values will be saved in .env. If you
change those values later, re-run the script to set up new values.

## Usage

```bash
flask run
```

Then open the URL shown in the terminal (by default http://127.0.0.1:5000).

From the web interface you can:

- Add and remove users, and rename them.
- For each user, browse their list of favorite movies.
- Add a movie by title (data is fetched from OMDb), pick an existing movie
  from the catalog, or enter movie details manually.
- View movie details, including the user's personal rating, the IMDb
  rating, and the average rating among all users of the app.
- Update a movie's title and the user's personal rating.
- Remove a movie from the user's favorites.

Enjoy!
