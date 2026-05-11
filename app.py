import sys
from flask import Flask, request, redirect, url_for, render_template
from api import fetch_data
from data_manager import DataManager
from models import db, Movie, User
from config import (get_db_path, LOWEST_RATING, HIGHEST_RATING, RATING_STEP,
                    YEAR_MIN, YEAR_MAX)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{get_db_path()}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
data_manager = DataManager()


def get_num_in_range(raw: str, num_min: float | int, num_max: float | int,
                     name: str = 'number') -> float | int | None:
    """Parse a number from form input and check it is in range.

    Args:
        raw: Raw value from the request (may be empty).
        num_min: Lower range limit.
        num_max: Upper range limit.
        name: Label for the number used in error messages.

    Returns:
        A number in range from ``num_min`` to ``num_max`` (type matches
        the type of ``num_min``), or ``None`` if ``raw`` is blank.

    Raises:
        ValueError: If ``raw`` is not a valid number or is out of range.
    """
    raw = (raw or '').strip()
    if not raw:
        return None
    num_type = type(num_min)
    num = num_type(raw)
    if not num_min <= num <= num_max:
        raise ValueError(f"{name} should be in range from {num_min} to"
                         f" {num_max}.")
    return num


@app.route('/')
def main_page():
    """
    Main page.

    Returns:
        Redirect to the list of users.
    """
    return redirect(url_for('list_users'))


@app.route('/users')
def list_users():
    """
    Show the list of all users.

    Returns:
        Rendered index.html template with the list of users.
    """
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    """
    Add a new user to the database.

    Returns:
        Redirect to the list of users.
    """
    name = request.form['name']
    data_manager.add_user(name)
    return redirect(url_for('list_users'))


@app.route('/users/<int:user_id>', methods=['GET'])
def show_user_settings(user_id):
    """
    Show user's profile and settings.

    Args:
        user_id: ID of the user.

    Returns:
        Rendered template with user's data.
    """
    user = data_manager.get_user(user_id)
    return render_template('user.html', user=user)


@app.route('/users/<int:user_id>/update', methods=['POST'])
def update_user(user_id):
    """
    Update user's name in the database.

    Args:
        user_id: ID of the user.

    Returns:
        Redirect to the page with user's settings.
    """
    new_name = request.form['name']
    data_manager.update_users_name(user_id, new_name)
    return redirect(url_for('show_user_settings', user_id=user_id))


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """
    Delete user from the database.

    Args:
        user_id: ID of the user.

    Returns:
        Redirect to the list of users.
    """
    data_manager.delete_user(user_id)
    return redirect(url_for('list_users'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def list_users_movies(user_id):
    """
    Show the grid with user's favorite movies.

    Args:
        user_id: ID of the user.

    Returns:
        Rendered template with the list of user's favorite movies.
    """
    user = data_manager.get_user(user_id)
    movies = data_manager.get_users_favorite_movies(user_id)
    return render_template('movies.html', user=user, movies=movies,
                           lowest_rating=LOWEST_RATING,
                           highest_rating=HIGHEST_RATING,
                           rating_step=RATING_STEP)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie_by_title(user_id):
    """
    Add movie by its title. Fetch missing information from OMDB API.

    Args:
        user_id: ID of the user.

    Returns:
        Redirect to the list of user's favorite movies.
    """
    title = request.form.get('title', '').strip()
    if not title:
        return "Bad request", 400
    try:
        rating = get_num_in_range(request.form.get('rating', ''),
                                  LOWEST_RATING, HIGHEST_RATING, 'rating')
    except ValueError:
        return "Bad rating", 400

    movie_data = fetch_data(title)
    if movie_data.get("Response") != "True":
        return redirect(url_for('add_movie_form', user_id=user_id,
                                title=title))
    try:
        new_title = movie_data["Title"]
        director = movie_data["Director"]
        year = get_num_in_range(movie_data["Year"], YEAR_MIN, YEAR_MAX,
                                'year')
        imdb_rating = get_num_in_range(movie_data["imdbRating"],
                                       LOWEST_RATING, HIGHEST_RATING,
                                       'IMDb rating')
        poster_url = movie_data["Poster"]
    except (KeyError, ValueError):
        print(f"Failed to interpret data for the movie {title}.",
              file=sys.stderr)
        return redirect(url_for('add_movie_form', user_id=user_id,
                                title=title))

    new_movie = data_manager.add_movie(new_title, director, year,
                                       imdb_rating, poster_url)
    data_manager.add_favorite(user_id, new_movie.movie_id, rating)
    return redirect(url_for('list_users_movies', user_id=user_id))


@app.route('/users/<int:user_id>/add_movie', methods=['GET'])
def add_movie_form(user_id):
    """
    Show a form to add a new movie manually or by selecting an existing
    movie in the database.

    Args:
        user_id: ID of the user.

    Returns:
        Rendered template with the form to add a new movie and a grid of
        movies in the database.
    """
    user = data_manager.get_user(user_id)
    if user is None:
        return "User not found", 404
    catalog = data_manager.get_movies()
    return render_template('add_movie.html', user=user, movies=catalog,
                           prefilled_title=request.args.get('title', ''),
                           lowest_rating=LOWEST_RATING,
                           highest_rating=HIGHEST_RATING,
                           rating_step=RATING_STEP,
                           year_min=YEAR_MIN, year_max=YEAR_MAX)


@app.route('/users/<int:user_id>/add_movie', methods=['POST'])
def add_movie_manually(user_id):
    """
    Add a new movie to the database and to users favorite.

    Args:
        user_id: ID of the user.

    Returns:
        Redirect to the list of user's favorite movies.
    """
    title = request.form.get('title', '').strip()
    if not title:
        return "Bad request", 400
    director = request.form.get('director', '').strip() or None
    poster_url = request.form.get('poster_url', '').strip() or None
    try:
        year = get_num_in_range(request.form.get('year', ''),
                                YEAR_MIN, YEAR_MAX, 'year')
        imdb_rating = get_num_in_range(request.form.get('imdb_rating', ''),
                                       LOWEST_RATING, HIGHEST_RATING,
                                       'IMDb rating')
        rating = get_num_in_range(request.form.get('rating', ''),
                                  LOWEST_RATING, HIGHEST_RATING, 'rating')
    except ValueError:
        return "Bad input", 400

    new_movie = data_manager.add_movie(title, director, year, imdb_rating,
                                       poster_url)
    data_manager.add_favorite(user_id, new_movie.movie_id, rating)
    return redirect(url_for('list_users_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>', methods=['POST'])
def add_existing_movie(user_id, movie_id):
    """
    Add a movie from the database to user's favorite movies.

    Args:
        user_id: ID of the user.
        movie_id: ID of the book.

    Returns:
        Redirect to the list of user's favorite movies.
    """
    try:
        rating = get_num_in_range(request.form.get('rating', ''),
                                  LOWEST_RATING, HIGHEST_RATING, 'rating')
    except ValueError:
        return "Bad rating", 400
    data_manager.add_favorite(user_id, movie_id, rating)
    return redirect(url_for('list_users_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>', methods=['GET'])
def show_movie_details(user_id, movie_id):
    """
    Show details about the movie and user's rating for that movie if available.

    Args:
        user_id: ID of the user.
        movie_id: ID of the book.

    Returns:
        Rendered movie.html template.
    """
    user = data_manager.get_user(user_id)
    movie = data_manager.get_movie(movie_id)
    rating = data_manager.get_favorite_rating(user_id, movie_id)
    return render_template('movie.html', user=user, movie=movie,
                           rating=rating, update=False)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update',
           methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Show the form to update a movie pre-filled with existing data and handle
    submission.

    On GET: render the form pre-filled with the movie's current data.
    On POST: save the updated movie and redirect to the homepage.

    Args:
        user_id: ID of the user.
        movie_id: ID of the book.

    Returns:
        Rendered movie.html template (GET), redirect to the page with movie
        details (POST).
    """
    if request.method == 'POST':
        new_title = request.form['title']
        data_manager.update_movie_title(movie_id, new_title)
        return redirect(url_for('show_movie_details', user_id=user_id,
                                movie_id=movie_id))
    user = data_manager.get_user(user_id)
    movie = data_manager.get_movie(movie_id)
    rating = data_manager.get_favorite_rating(user_id, movie_id)
    return render_template('movie.html', user=user, movie=movie,
                           rating=rating, update=True)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete',
           methods=['POST'])
def delete_movie_from_favorites(user_id, movie_id):
    """
    Delete the movie with the given ID from user's favorites.

    Args:
        user_id: ID of the user.
        movie_id: ID of the book.

    Returns:
        Redirect to the list of user's favorite movies.
    """
    data_manager.delete_favorite(user_id, movie_id)
    return redirect(url_for('list_users_movies', user_id=user_id))


if __name__ == '__main__':
    app.run()
