from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__= "user"
    names = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(255), nullable=False)

    movie = db.relationship('Movie', back_populates='user', uselist=False, cascade="all, delete-orphan")

    def get_id(self):
        return self.username
    
class Movie(db.Model):
    __tablename__="movie"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), db.ForeignKey('user.username', ondelete='CASCADE', onupdate='CASCADE', name='movie_owner_username'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
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