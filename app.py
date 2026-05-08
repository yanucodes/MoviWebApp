from flask import Flask
from data_manager import DataManager
from models import db, Movie, User
from config import get_db_path

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{get_db_path()}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
data_manager = DataManager()


@app.route('/')
def hello_world():
    return 'Welcome to MoviWeb App!'


if __name__ == '__main__':
    app.run()
