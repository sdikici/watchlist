import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient

# import secrets

from movie_library.routes import pages

# key = secrets.token_urlsafe()
# print(key)

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "NhEOTIILXYVgmrOpaqZPNBr5dnho-Zj-iRmcZmiqdA"
    )
    app.db = MongoClient(app.config["MONGODB_URI"]).watchlist
    app.register_blueprint(pages)
    return app
