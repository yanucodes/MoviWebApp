import sys
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.exceptions import BadRequest, NotFound
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


class AppBadRequest(BadRequest):
    """400 Bad Request carrying a back URL for the error page."""

    def __init__(self, message: str, back_url: str):
        super().__init__(description=message)
        self.back_url = back_url


class AppNotFound(NotFound):
    """404 Not Found carrying a back URL for the error page."""

    def __init__(self, message: str, back_url: str):
        super().__init__(description=message)
        self.back_url = back_url


@app.errorhandler(400)
@app.errorhandler(404)
def handle_app_error(error):
    """Render error_message.html for any 400 or 404 error.

    Reads ``description`` and ``back_url`` off the raised exception; falls
    back to a generic message and the list of users for plain errors.
    """
    back_url = getattr(error, 'back_url', url_for('list_users'))
    return render_template('error_message.html',
                           message=error.description,
                           back_url=back_url), error.code


def abort_user_not_found(user_id: int):
    """Raise a 404 for a missing user, linking back to the list of users.

    Args:
        user_id: ID of the user that was not found.
    """
    raise AppNotFound(f"User with ID {user_id} not found.",
                      url_for('list_users'))


def abort_movie_not_found(user_id: int, movie_id: int):
    """Raise a 404 for a missing movie, linking back to the user's list.

    Args:
        user_id: ID of the user (used to build the back link).
        movie_id: ID of the movie that was not found.
    """
    raise AppNotFound(f"Movie with ID {movie_id} not found.",
                      url_for('list_users_movies', user_id=user_id))


def abort_empty_field(field_name: str, back_url: str):
    """Raise a 400 for an empty form field, linking back to ``back_url``.

    Args:
        field_name: Label of the field.
        back_url: URL to go back to the form the user came from.
    """
    raise AppBadRequest(f"{field_name.capitalize()} cannot be empty.",
                        back_url)


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
    name = request.form.get('name', '').strip()
    if not name:
        abort_empty_field("Name", url_for('list_users'))
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
    if user is None:
        abort_user_not_found(user_id)
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
    if data_manager.get_user(user_id) is None:
        abort_user_not_found(user_id)
    new_name = request.form.get('name', '').strip()
    if not new_name:
        abort_empty_field("Name",
                          url_for('show_user_settings', user_id=user_id))
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
    if data_manager.get_user(user_id) is None:
        abort_user_not_found(user_id)
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
    if user is None:
        abort_user_not_found(user_id)
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
    if data_manager.get_user(user_id) is None:
        abort_user_not_found(user_id)
    title = request.form.get('title', '').strip()
    if not title:
        abort_empty_field("Title",
                          url_for('list_users_movies', user_id=user_id))
    try:
        rating = get_num_in_range(request.form.get('rating', ''),
                                  LOWEST_RATING, HIGHEST_RATING, 'Rating')
    except ValueError as error:
        raise AppBadRequest(str(error),
                            url_for('list_users_movies', user_id=user_id))

    movie_data = fetch_data(title)
    if movie_data.get("Response") != "True":
        return redirect(url_for('add_movie_form', user_id=user_id,
                                title=title))
    try:
        new_title = movie_data["Title"]
        director = movie_data["Director"]
        year = get_num_in_range(movie_data["Year"], YEAR_MIN, YEAR_MAX,
                                'Year')
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
        abort_user_not_found(user_id)
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
    if data_manager.get_user(user_id) is None:
        abort_user_not_found(user_id)
    title = request.form.get('title', '').strip()
    if not title:
        abort_empty_field("Title",
                          url_for('add_movie_form', user_id=user_id))
    director = request.form.get('director', '').strip() or None
    poster_url = request.form.get('poster_url', '').strip() or None
    try:
        year = get_num_in_range(request.form.get('year', ''),
                                YEAR_MIN, YEAR_MAX, 'Year')
        imdb_rating = get_num_in_range(request.form.get('imdb_rating', ''),
                                       LOWEST_RATING, HIGHEST_RATING,
                                       'IMDb rating')
        rating = get_num_in_range(request.form.get('rating', ''),
                                  LOWEST_RATING, HIGHEST_RATING, 'Rating')
    except ValueError as error:
        raise AppBadRequest(str(error),
                            url_for('add_movie_form', user_id=user_id))

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
        movie_id: ID of the movie.

    Returns:
        Redirect to the list of user's favorite movies.
    """
    if data_manager.get_user(user_id) is None:
        abort_user_not_found(user_id)
    if data_manager.get_movie(movie_id) is None:
        abort_movie_not_found(user_id, movie_id)
    try:
        rating = get_num_in_range(request.form.get('rating', ''),
                                  LOWEST_RATING, HIGHEST_RATING, 'Rating')
    except ValueError as error:
        raise AppBadRequest(str(error),
                            url_for('add_movie_form', user_id=user_id))
    data_manager.add_favorite(user_id, movie_id, rating)
    return redirect(url_for('list_users_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>', methods=['GET'])
def show_movie_details(user_id, movie_id):
    """
    Show details about the movie and user's rating for that movie if available.

    Args:
        user_id: ID of the user.
        movie_id: ID of the movie.

    Returns:
        Rendered movie.html template.
    """
    user = data_manager.get_user(user_id)
    if user is None:
        abort_user_not_found(user_id)
    movie = data_manager.get_movie(movie_id)
    if movie is None:
        abort_movie_not_found(user_id, movie_id)
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
        movie_id: ID of the movie.

    Returns:
        Rendered movie.html template (GET), redirect to the page with movie
        details (POST).
    """
    user = data_manager.get_user(user_id)
    if user is None:
        abort_user_not_found(user_id)
    movie = data_manager.get_movie(movie_id)
    if movie is None:
        abort_movie_not_found(user_id, movie_id)
    rating = data_manager.get_favorite_rating(user_id, movie_id)
    if request.method == 'POST':
        new_title = request.form.get('title', '').strip()
        if not new_title:
            abort_empty_field("Title",
                              url_for('update_movie', user_id=user_id,
                                      movie_id=movie_id))
        data_manager.update_movie_title(movie_id, new_title)
        try:
            new_rating = get_num_in_range(request.form.get('rating', ''),
                                          LOWEST_RATING, HIGHEST_RATING,
                                          'Rating')
        except ValueError as error:
            raise AppBadRequest(str(error),
                                url_for('update_movie', user_id=user_id,
                                        movie_id=movie_id))
        if new_rating is not None:
            data_manager.update_favorite_rating(user_id, movie_id,
                                                new_rating)
        return redirect(url_for('show_movie_details', user_id=user_id,
                                movie_id=movie_id))
    return render_template('movie.html', user=user, movie=movie,
                           rating=rating, update=True,
                           lowest_rating=LOWEST_RATING,
                           highest_rating=HIGHEST_RATING,
                           rating_step=RATING_STEP)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete',
           methods=['POST'])
def delete_movie_from_favorites(user_id, movie_id):
    """
    Delete the movie with the given ID from user's favorites.

    Args:
        user_id: ID of the user.
        movie_id: ID of the movie.

    Returns:
        Redirect to the list of user's favorite movies.
    """
    if data_manager.get_user(user_id) is None:
        abort_user_not_found(user_id)
    if data_manager.get_movie(movie_id) is None:
        abort_movie_not_found(user_id, movie_id)
    data_manager.delete_favorite(user_id, movie_id)
    return redirect(url_for('list_users_movies', user_id=user_id))


if __name__ == '__main__':
    app.run()
