import os
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    useremail = db.Column(db.String(120), index=True, unique=True, nullable=True)
    pwdhash = db.Column(db.String(128), nullable=False)
    reviews = db.relationship("Review", backref="composer", lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Book(db.Model):
    __tablename__ = "books"
    isbn = db.Column(db.String(13), primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.String(4), nullable=False)
    reviews = db.relationship("Review", backref="book", lazy=True)

    def __repr__(self):
        return '<Book {}>'.format(self.isbn)

    def compose_review(self, username, rev_rating, rev_text):
        r = Review(isbn=self.isbn, username=username, rev_rating=rev_rating, rev_text=rev_text)
        db.session.add(r)
        db.session.commit()


class Review(db.Model):
    __tablename_ = "reviews"
    rev_id = db.Column(db.String(10), primary_key=True)
    isbn = db.Column(db.String(13), db.ForeignKey("books.isbn"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rev_rating = db.Column(db.Integer, nullable=False)
    rev_text = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Review {}>'.format(self.rev_text)