from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__= "user"
    names = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, default='abc@gmail.com')

    movie = db.relationship('Movie', back_populates='user', uselist=False, cascade="all, delete-orphan")

    def get_id(self):
        return self.username
    
class Movie(db.Model):
    __tablename__="movie"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), db.ForeignKey('user.username', ondelete='CASCADE', onupdate='CASCADE', name='movie_owner_username'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    plot = db.Column(db.String(255))
    release = db.Column(db.DateTime)
    rate = db.Column(db.String(255))
    added = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    progress = db.Column(db.String(255), nullable=False)
    repeat = db.Column(db.String(255))
    finish = db.Column(db.DateTime)
    start = db.Column(db.DateTime)
    notes = db.Column(db.String(255))

    user = db.relationship('User', back_populates='movie')

    def get_id(self):
        return self.id
    
class Glossary(db.Model):
    _tablename_ = "glossary"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    term = db.Column(db.String(255), nullable=False)
    definition = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"Glossary('{self.term}')"