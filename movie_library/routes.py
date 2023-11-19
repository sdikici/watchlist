from flask import (
    Blueprint,
    render_template,
    url_for,
    session,
    redirect,
    request,
    current_app,
    flash,
)
import functools
from movie_library.forms import MovieForm, Extension, RegisterForm, LoginForm
from dataclasses import asdict
from movie_library.database import MovieDB
import uuid
from movie_library.movies import Movie, User
from passlib.hash import pbkdf2_sha256
import os

# Creating a Flask Blueprint for organized route and view management
pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)


# Decorator function to ensure authentication for routes requiring logged-in users
def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))
        return route(*args, **kwargs)

    return route_wrapper


# Home page route displaying the user's watchlist for authenticated users
@pages.route("/")
@login_required
def index():
    # Retrieving user and movie data from the database
    user_data = current_app.db.user.find_one({"email": session["email"]})
    user = User(**user_data)

    movie_data = current_app.db.movies.find({"_id": {"$in": user.movies}})
    mymovies = [Movie(**movie) for movie in movie_data]
    return render_template(
        "index.jinja", title="Movies Watchlist", movies_data=mymovies
    )


# User registration route allowing users to register with a unique email and securely hashed password
@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))
    form = RegisterForm()

    if form.validate_on_submit():
        # Creating a new user and inserting into the database
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data),
        )

        current_app.db.user.insert_one(asdict(user))
        flash("User registered succesfully", "Success")

        return redirect(url_for(".login"))

    return render_template(
        "register.jinja", title="Movies Watchlist - Register", form=form
    )


# User login route enabling users to log in securely
@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = LoginForm()

    if form.validate_on_submit():
        user_data = current_app.db.user.find_one({"email": form.email.data})
        if not user_data:
            flash("Login credentials are not correct", category="danger")
            return redirect(url_for(".login"))
        user = User(**user_data)

        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            # Setting user session upon successful login
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))

        flash("Login credentials are not correct", category="danger")

    return render_template("login.jinja", title="Movie Watchlist - Login", form=form)


# User logout route logging out the currently authenticated user
@pages.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(".login"))


# Add movie route allowing authenticated users to add new movies to their watchlist
@pages.route("/add", methods=["GET", "POST"])
@login_required
def add_movie():
    form = MovieForm()

    if form.validate_on_submit():
        # Creating a new movie and updating the user's watchlist in the database
        movie = Movie(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            director=form.director.data,
            year=form.year.data,
        )
        current_app.db.movies.insert_one(asdict(movie))
        current_app.db.user.update_one(
            {"_id": session["user_id"]}, {"$push": {"movies": movie._id}}
        )

        return redirect(url_for(".index"))

    return render_template(
        "new_movie.jinja", title="Movies Watchlist - Add Movie", form=form
    )


# Edit movie route allowing users to edit details of a specific movie
@pages.route("/edit/movie/<string:_id>", methods=["GET", "POST"])
@login_required
def edit_movie(_id: str):
    movie_data = current_app.db.movies.find_one({"_id": _id})
    movie = Movie(**movie_data)
    form = Extension(obj=movie)

    if form.validate_on_submit():
        # Updating movie details in the database upon form validation
        print(f"Form validated. Values: {form.data}")

        movie.title = form.title.data
        movie.director = form.director.data
        movie.year = form.year.data
        movie.tag1 = form.tag1.data
        movie.tag2 = form.tag2.data
        movie.video_link = form.video_link.data

        current_app.db.movies.update_one({"_id": movie._id}, {"$set": asdict(movie)})
        return redirect(url_for(".movie", _id=_id))
    return render_template("movie_form.jinja", movie=movie, form=form)


# Delete movie route enabling users to delete a specific movie
@pages.route("/delete/movie/<string:_id>", methods=["GET", "POST"])
@login_required
def delete_movie(_id: str):
    current_app.db.user.update_one(
        {"_id": session["user_id"]}, {"$pull": {"movies": _id}}
    )
    return redirect(url_for(".index"))


# View movie details route displaying detailed information about a specific movie
@pages.get("/movie/<string:_id>")
def movie(_id: str):
    movie_data = current_app.db.movies.find_one({"_id": _id})
    movie = Movie(**movie_data)

    return render_template("movie_details.jinja", movie=movie)


# Rate movie route allowing users to rate a specific movie
@pages.get("/movie/<string:_id>/rate")
@login_required
def rate_movie(_id):
    rating = int(request.args.get("rating"))
    current_app.db.movies.update_one({"_id": _id}, {"$set": {"rating": rating}})
    return redirect(url_for(".movie", _id=_id))


# Mark movie as watched route allowing users to mark a movie as watched or not watched
@pages.get("/movie/<string:_id>/watch")
@login_required
def watch_today(_id):
    movie_data = current_app.db.movies.find_one({"_id": _id})

    if movie_data:
        current_state = movie_data.get("last_watched", None)
        new_state = "Not Watched" if current_state == "Watched" else "Watched"

        current_app.db.movies.update_one(
            {"_id": _id}, {"$set": {"last_watched": new_state}}
        )

        flash(f"Movie marked as {new_state}", "Success")

    return redirect(url_for(".movie", _id=_id))


# Search movies route providing a search interface for users to find movies in the database
@pages.route("/search", methods=["GET", "POST"])
@login_required
def search_movies():
    if request.method == "GET":
        return render_template(
            "search.jinja", title="Movies Watchlist - Database Search"
        )

    if request.method == "POST":
        search_query = request.form.get("search_query", "")

        # Use the MovieDB class to search for movies
        API_KEY = os.environ.get("API_KEY")
        movie_db = MovieDB(API_KEY)
        search_results = movie_db.search_and_return_movie_details(search_query)

        return render_template(
            "search.jinja",
            title="Movies Watchlist - Search Results",
            search_query=search_query,
            search_results=search_results,
        )

    return render_template("search.jinja", title="Movies Watchlist - Database Search")


# Select and add movies route allowing users to select and add movies from search results to their watchlist
@pages.route("/select_add_movie", methods=["POST"])
@login_required
def select_movie():
    selected_movie_ids = request.form.getlist("selected_movie")

    # Add the selected movies to the user's watchlist
    user_id = session["user_id"]

    for movie_id in selected_movie_ids:
        # Fetch details of the selected movie using the MovieDB class
        API_KEY = os.environ.get("API_KEY")
        movie_db = MovieDB(API_KEY)
        movie_details_list = movie_db.search_and_return_movie_details_by_id(movie_id)

        # Iterate over the list of movie details
        for movie_details in movie_details_list:
            # Create a new movie and add it to the database
            new_movie = Movie(
                _id=uuid.uuid4().hex,
                title=movie_details.get("name", ""),
                director=movie_details.get("director", ""),
                year=movie_details.get("year", ""),
                tag1=movie_details.get("tag1", ""),
                tag2=movie_details.get("tag2", ""),
                video_link=movie_details.get("YouTube_Link", ""),
            )

            current_app.db.movies.insert_one(asdict(new_movie))
            current_app.db.user.update_one(
                {"_id": user_id}, {"$push": {"movies": new_movie._id}}
            )

    flash("Selected movies added to your watchlist", "success")
    return redirect(url_for(".index"))
