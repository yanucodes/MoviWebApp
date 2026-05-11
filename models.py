"""Database models for the movie app."""

from statistics import mean

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """A registered user of the app.

    Attributes:
        user_id: Primary key.
        name: User's name shown in the UI.
        favorites: ``Favorite`` rows owned by this user. Deleting the
            user cascades to delete their favorites.
    """

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    favorites = db.relationship("Favorite", back_populates="user",
                                cascade="all, delete-orphan")


class Movie(db.Model):
    """A movie that one or more users added as their favorite.

    Attributes:
        movie_id: Primary key.
        title: Movie title.
        director: Director's name.
        year: Release year.
        imdb_rating: Official IMDb rating, 0.0–10.0 (one decimal place).
        poster_url: URL to the poster image.
        favorites: ``Favorite`` rows pointing at this movie. Deleting
            the movie cascades to delete those rows.
    """

    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    director = db.Column(db.String(100))
    year = db.Column(db.Integer)
    imdb_rating = db.Column(db.Numeric(3, 1))
    poster_url = db.Column(db.String(1000))
    favorites = db.relationship("Favorite", back_populates="movie",
                                cascade="all, delete-orphan")

    @property
    def average_rating(self):
        """Average rating among MoviWebApp users for this movie.

        Favorites without a specified rating are skipped. Returns ``None``
        if no user has rated the movie yet.
        """
        ratings = [f.rating for f in self.favorites if f.rating is not None]
        return mean(ratings) if ratings else None

    @property
    def number_of_ratings(self):
        """Number of MoviWebApp users that have rated this movie.

        Favorites without a specified rating are skipped.
        """
        return sum(1 for f in self.favorites if f.rating is not None)


class Favorite(db.Model):
    """Link between a ``User`` and a ``Movie`` they have favorited.

    Association object joining users and movies. The composite primary
    key ``(user_id, movie_id)`` prevents a user from favoriting the
    same movie twice.

    Attributes:
        user_id: Foreign key to ``User``; part of the composite PK.
        movie_id: Foreign key to ``Movie``; part of the composite PK.
        rating: User's personal 1–10 rating, or ``None`` if not rated.
        user: The ``User`` who created this favorite.
        movie: The ``Movie`` being favorited.
    """

    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"),
                        primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.movie_id"),
                         primary_key=True)
    rating = db.Column(db.Integer)
    user = db.relationship("User", back_populates="favorites")
    movie = db.relationship("Movie", back_populates="favorites")
