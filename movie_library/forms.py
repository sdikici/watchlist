from flask_wtf import FlaskForm
from wtforms import (IntegerField, StringField, SubmitField,
                     TextAreaField, URLField, PasswordField,)
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo


class MovieForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])

    director = StringField("Director")

    year = IntegerField("Year", validators=[InputRequired(), NumberRange(
        min=1878, max=2099, message="Please enter a year in format 1877 < YYYY > 2100.")])

    submit = SubmitField("Add Movie")


class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []


class Extension(MovieForm):
    tags = StringListField("Tags")
    video_link = URLField("Video Link")

    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(),
                             Length(min=4,
                                    message="Your password must be between min 4 characters long")
    ])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo(
                "password",
                message="This password does not match"
            )
        ]
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")
