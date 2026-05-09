from flask import Flask, request, redirect, url_for
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
    return 'Welcome to MoviWeb App!'


@app.route('/users', methods=['POST'])
def add_user():
    name = request.form['name']
    data_manager.add_user(name)
    return redirect(url_for('list_users'))

if __name__ == '__main__':
    app.run()
