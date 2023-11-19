from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    SubmitField,
    URLField,
    PasswordField,
)
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo


class MovieForm(FlaskForm):
    # Form for adding movies to the watchlist
    title = StringField("Title", validators=[InputRequired()])

    director = StringField("Director")
    tag1 = StringField("Tag1")
    tag2 = StringField("Tag2")

    year = IntegerField(
        "Year",
        validators=[
            InputRequired(),
            NumberRange(
                min=1878,
                max=2099,
                message="Please enter a year in format 1877 < YYYY > 2100.",
            ),
        ],
    )

    submit = SubmitField("Add Movie")


class StringListField(StringField):
    def _value(self):
        if self.data:
            return "".join(filter(None, self.data))
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []


class Extension(MovieForm):
    # Form for extending the movie details
    video_link = URLField("Video Link")
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    # Form for user registration
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(min=4, message="Your password can be min 4 characters long"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo("password", message="This password does not match"),
        ],
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    # Form for user login
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")
