from flask import Flask, request, redirect, url_for, render_template
from data_manager import DataManager
from models import db, Movie, User
from config import get_db_path

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
    return render_template('movies.html', user=user, movies=movies)


if __name__ == '__main__':
    app.run()
