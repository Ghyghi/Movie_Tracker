from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *

#Define Choice Dictionaries
rates = [
    ('', 'Select rating'),
    ("Can't wait to start'", "Can't wait to start"),
    ("It doesn't get better than this", "It doesn't get better than this"),
    ('Loved', 'Loved'),
    ('Liked', 'Liked'),
    ('Neutral', 'Neutral'),
    ('Hated', 'Hated'),
    ('If I could destroy it I could', 'If I could destroy it I could')
]
kind = [
    # ('', 'Select genres'),
    ('Action', 'Action'),
    ('Adventure', 'Adventure'),
    ('Comedy', 'Comedy'),
    ('Drama', 'Drama'),
    ('Horror', 'Horror'),
    ('Thriller', 'Thriller'),
    ('Mystery', 'Mystery'),
    ('Romance', 'Romance'),
    ('Science Fiction', 'Science Fiction'),
    ('Fantasy', 'Fantasy'),
    ('Animated', 'Animated'),
    ('Documentary', 'Documentary'),
    ('Musical', 'Musical'),
    ('Crime', 'Crime'),
    ('Historical', 'Historical')
]
where = [
    ('', 'Select progress'),
    ('To be Watched', 'To be Watched'),
    ('Watching', 'Watching'),
    ('Completed', 'Completed'),
    ('Dropped', 'Dropped'),
    ('Haitus', 'Haitus')
]
repeats = [
    ('', 'Select repeat'),
    ('Yes', 'Yes'),
    ('Maybe', 'Maybe'),
    ('No', 'No')
]

# Define the form classes
class RegisterForm(FlaskForm):
    names=StringField("Names", validators=[DataRequired()])
    username=StringField("Username", validators=[DataRequired()])
    password=PasswordField("Password", validators=[InputRequired()])
    submit=SubmitField("Register")

class LoginForm(FlaskForm):
    username=StringField("Username", validators=[InputRequired()])
    password=PasswordField("Password", validators=[InputRequired()])
    submit=SubmitField("Login")

class AddMovieForm(FlaskForm):
    name = StringField("What is the movie called?", validators=[InputRequired()])
    rate = SelectField("What do you rate it?", choices=rates, validators=[InputRequired()])
    added = DateField("When was it added?", validators=[InputRequired()])
    genre = SelectMultipleField("What kind is it?", choices=kind, validators=[InputRequired()])
    progress = SelectField("What is your current progress?", choices=where, validators=[InputRequired()])
    repeat = SelectField("Would you repeat it?", choices=repeats)
    start = DateField("When did you start it?", validators=[Optional()])
    finish = DateField("When did you finish it?", validators=[Optional()])
    notes = TextAreaField("What would you say about it?", validators=[Optional()])
    submit = SubmitField("Add")