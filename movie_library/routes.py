from flask import (Blueprint, render_template,
                   url_for, session, redirect,
                   request, current_app, flash)
import functools
from movie_library.forms import MovieForm, Extension, RegisterForm, LoginForm
from dataclasses import asdict
import uuid
from movie_library.movies import Movie, User
from passlib.hash import pbkdf2_sha256

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)


def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))
        return route(*args, **kwargs)
    return route_wrapper


@pages.route("/")
@login_required
def index():
    user_data = current_app.db.user.find_one({"email": session["email"]})
    user = User(**user_data)

    movie_data = current_app.db.movies.find({"_id": {"$in": user.movies}})
    mymovies = [Movie(**movie) for movie in movie_data]
    return render_template(
        "index.jinja",
        title="Movies Watchlist",
        movies_data=mymovies
    )


@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data)
        )

        current_app.db.user.insert_one(asdict(user))
        flash("User registered succesfully", "Success")

        return redirect(url_for(".login"))

    return render_template("register.jinja",
                           title="Movies Watchlist - Register",
                           form=form)


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
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))

        flash("Login credentials are not correct", category="danger")

    return render_template("login.jinja", title="Movie Watchlist - Login", form=form)


@pages.route("/logout")
def logout():
    session.clear()
    return redirect(url_for(".login"))


@pages.route("/add", methods=["GET", "POST"])
@login_required
def add_movie():
    form = MovieForm()

    if form.validate_on_submit():
        movie = Movie(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            director=form.director.data,
            year=form.year.data
        )
        current_app.db.movies.insert_one(asdict(movie))
        current_app.db.user.update_one({"_id": session["user_id"]}, {
                                       "$push": {"movies": movie._id}})

        return redirect(url_for(".index"))

    return render_template("new_movie.jinja", title="Movies Watchlist - Add Movie",
                           form=form)


@pages.route("/edit/movie/<string:_id>", methods=["GET", "POST"])
@login_required
def edit_movie(_id: str):
    movie_data = current_app.db.movies.find_one({"_id": _id})
    movie = Movie(**movie_data)
    form = Extension(obj=movie)

    if form.validate_on_submit():
        movie.tags = form.tags.data
        movie.video_link = form.video_link.data

        current_app.db.movies.update_one(
            {"_id": movie._id}, {"$set": asdict(movie)})
        return redirect(url_for(".movie", _id=_id))
    return render_template("movie_form.jinja", movie=movie, form=form)


@pages.route("/delete/movie/<string:_id>", methods=["GET", "POST"])
@login_required
def delete_movie(_id: str):
    current_app.db.user.update_one({"_id": session["user_id"]}, {
        "$pull": {"movies": _id}})
    return redirect(url_for(".index"))


@pages.get("/movie/<string:_id>")
def movie(_id: str):
    movie_data = current_app.db.movies.find_one({"_id": _id})
    movie = Movie(**movie_data)

    return render_template("movie_details.jinja", movie=movie)


@pages.get("/movie/<string:_id>/rate")
@login_required
def rate_movie(_id):
    rating = int(request.args.get("rating"))
    current_app.db.movies.update_one(
        {"_id": _id}, {"$set": {"rating": rating}})
    return redirect(url_for(".movie", _id=_id))


@pages.get("/movie/<string:_id>/watch")
@login_required
def watch_today(_id):
    movie_data = current_app.db.movies.find_one({"_id": _id})

    if movie_data:
        current_state = movie_data.get("last_watched", None)
        new_state = "Not Watched" if current_state == "Watched" else "Watched"

        current_app.db.movies.update_one(
            {"_id": _id},
            {"$set": {"last_watched": new_state}}
        )

        flash(f"Movie marked as {new_state}", "Success")

    return redirect(url_for(".movie", _id=_id))
