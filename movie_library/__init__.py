import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient

# import secrets

from movie_library.routes import pages

# key = secrets.token_urlsafe()
# print(key)

load_dotenv()  # Load environment variables from a .env file


# Function to create and configure the Flask application
def create_app():
    app = Flask(__name__)  # Create a Flask application instance

    # Set the MongoDB URI and Secret Key for the Flask application
    app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "NhEOTIILXYVgmrOpaqZPNBr5dnho-Zj-iRmcZmiqdA"
    )

    # Connect to the MongoDB database using the MongoClient
    app.db = MongoClient(app.config["MONGODB_URI"]).watchlist

    # Register the 'pages' blueprint with the Flask application
    app.register_blueprint(pages)
    return app
