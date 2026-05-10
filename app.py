import sys
from flask import Flask, request, redirect, url_for, render_template
from api import fetch_data
from data_manager import DataManager
from models import db, Movie, User
from config import (get_db_path, LOWEST_RATING, HIGHEST_RATING, RATING_STEP)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{get_db_path()}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
data_manager = DataManager()


@app.route('/')
def list_users():
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    name = request.form['name']
    data_manager.add_user(name)
    return redirect(url_for('list_users'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def list_users_movies(user_id):
    user = data_manager.get_user(user_id)
    movies = data_manager.get_users_favorite_movies(user_id)
    return render_template('movies.html', user=user, movies=movies,
                           lowest_rating=LOWEST_RATING,
                           highest_rating=HIGHEST_RATING,
                           rating_step=RATING_STEP)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie_to_favorites(user_id):
    title = request.form.get('title', '').strip()
    if not title:
        return "Bad request", 400
    rating_raw = request.form.get('rating', '').strip()
    rating = None
    if rating_raw:
        try:
            rating = float(rating_raw)
        except ValueError:
            return "Bad rating", 400
        if not LOWEST_RATING <= rating <= HIGHEST_RATING:
            return "Rating out of range", 400
        rating = round(rating / RATING_STEP) * RATING_STEP
    movie_data = fetch_data(title)
    if movie_data["Response"] == "True":
        try:
            new_title = movie_data["Title"]
            director = movie_data["Director"]
            year = int(movie_data["Year"])
            imdb_rating = float(movie_data["imdbRating"])
            poster_url = movie_data["Poster"]
        except ValueError:
            print(f"Failed to interpret data for the movie {title}.",
                  file=sys.stderr)
        else:
            new_movie = data_manager.add_movie(new_title, director, year,
                                               imdb_rating, poster_url)
            data_manager.add_favorite(user_id, new_movie.movie_id, rating)
    return redirect(url_for('list_users_movies', user_id=user_id))


if __name__ == '__main__':
    app.run()
