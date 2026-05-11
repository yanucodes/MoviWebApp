"""Data access layer for the movie app."""

from models import db, User, Movie, Favorite


class DataManager:
    """CRUD operations for users, movies, and favorites."""

    def add_user(self, name: str) -> User:
        """Insert a new user with the given display name.

        Args:
            name: User's name.

        Returns:
            The newly created ``User``.
        """
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_users(self):
        """Return all users in the database."""
        return User.query.all()

    def get_user(self, user_id: int):
        """Return user by given ID."""
        return db.session.get(User, user_id)

    def update_users_name(self, user_id: int, new_name: str):
        """Change the name of an existing user.

        Args:
            user_id: ID of the user.
            new_name: New name of the user.
        """
        user = db.session.get(User, user_id)
        user.name = new_name
        db.session.commit()

    def delete_user(self, user_id: int):
        """Delete a user from the database.

        Cascades to delete every ``Favorite`` row pointing at this user.

        Args:
            user_id: ID of the user to delete.
        """
        user = db.session.get(User, user_id)
        db.session.delete(user)
        db.session.commit()

    def add_movie(self, title: str, director: str, year: int,
                  imdb_rating: float, poster_url: str) -> Movie:
        """Insert a new movie into the catalog.

        Args:
            title: Movie title.
            director: Director's name.
            year: Release year.
            imdb_rating: Official IMDb rating, 0.0–10.0 (one decimal place).
            poster_url: URL to the poster image.

        Returns:
            The newly created ``Movie``.
        """
        new_movie = Movie(title=title, director=director, year=year,
                          imdb_rating=imdb_rating, poster_url=poster_url)
        db.session.add(new_movie)
        db.session.commit()
        return new_movie

    def get_movies(self):
        """Return all movies in the catalog."""
        return Movie.query.all()

    def get_movie(self, movie_id: int):
        """Return movie by given ID."""
        return db.session.get(Movie, movie_id)

    def find_movie_title(self, title: str) -> int | None:
        """Return the ID of a movie with the given title, or None.

        Args:
            title: Title of the movie to look up.

        Returns:
            ID of the matching movie, or None if no such movie exists.
        """
        movie = Movie.query.filter_by(title=title).first()
        return movie.movie_id if movie else None

    def update_movie_title(self, movie_id: int, new_title: str):
        """Change the title of an existing movie.

        Args:
            movie_id: ID of the movie.
            new_title: New title of the movie.
        """
        movie = db.session.get(Movie, movie_id)
        movie.title = new_title
        db.session.commit()

    def delete_movie(self, movie_id: int):
        """Delete a movie from the catalog.

        Cascades to delete every ``Favorite`` row pointing at this
        movie, so it disappears from every user's list as well.

        Args:
            movie_id: ID of the movie to delete.
        """
        movie = db.session.get(Movie, movie_id)
        db.session.delete(movie)
        db.session.commit()

    def add_favorite(self, user_id: int, movie_id: int,
                     rating: int = None) -> Favorite:
        """Link a user to a movie they have added as their favorite.

        Args:
            user_id: ID of the user.
            movie_id: ID of the movie.
            rating: User's personal rating for the movie.

        Returns:
            The newly created ``Favorite`` link row.
        """
        favorite = Favorite(user_id=user_id, movie_id=movie_id, rating=rating)
        db.session.add(favorite)
        db.session.commit()
        return favorite

    def is_users_favorite(self, user_id: int, movie_id: int) -> bool:
        """Return whether the user has the given movie as their favorite.

        Args:
            user_id: ID of the user.
            movie_id: ID of the movie.
        """
        return db.session.get(Favorite, (user_id, movie_id)) is not None

    def get_users_favorite_movies(self, user_id: int) -> list:
        """Return the list of ``Movie`` objects a user has added as their
        favorite.

        Args:
            user_id: ID of the user.
        """
        favorites = Favorite.query.filter_by(user_id=user_id).all()
        return [favorite.movie for favorite in favorites]

    def get_users_nonfavorites(self, user_id: int) -> list:
        """Return the list of ``Movie`` objects the user has not yet added
        as their favorite.

        Args:
            user_id: ID of the user.
        """
        favorite_ids = [favorite.movie_id for favorite in
                        Favorite.query.filter_by(user_id=user_id).all()]
        return Movie.query.filter(
            Movie.movie_id.notin_(favorite_ids)).all()

    def get_favorite_rating(self, user_id: int, movie_id: int):
        """Return user's personal rating for a movie, or None if the
        user has not added the movie as their favorite.

        Args:
            user_id: ID of the user.
            movie_id: ID of the movie.
        """
        favorite = db.session.get(Favorite, (user_id, movie_id))
        return favorite.rating if favorite else None

    def update_favorite_rating(self, user_id: int, movie_id: int,
                               new_rating: int):
        """Change a user's personal rating for a favorite movie.

        Does nothing if the user has not added the movie as their favorite.

        Args:
            user_id: ID of the user.
            movie_id: ID of the movie.
            new_rating: New personal rating for the movie.
        """
        favorite = db.session.get(Favorite, (user_id, movie_id))
        if favorite is None:
            return
        favorite.rating = new_rating
        db.session.commit()

    def delete_favorite(self, user_id: int, movie_id: int):
        """Remove a movie from user's favorites.

        Does nothing if the user has not added the movie as their favorite.

        Args:
            user_id: ID of the user.
            movie_id: ID of the movie to delete from user's favorites.
        """
        favorite = db.session.get(Favorite, (user_id, movie_id))
        if favorite is None:
            return
        db.session.delete(favorite)
        db.session.commit()
