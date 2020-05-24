import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    username = db.Column(db.String, primary_key=True)
    useremail = db.Column(db.String, nullable=True)
    pwdhash = db.Column(db.String, nullable=False)
    #reviews = db.relationship("Review", backref="username", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Book(db.Model):
    __tablename__ = "books"
    isbn = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)
    reviews = db.relationship("Review", backref="book", lazy=True)

    def compose_review(self, username, rev_rating, rev_text):
        r = Review(isbn=self.isbn, username=username, rev_rating=rev_rating, rev_text=rev_text)
        db.session.add(r)
        db.session.commit()


class Review(db.Model):
    __tablename_ = "reviews"
    rev_id = db.Column(db.String, primary_key=True)
    isbn = db.Column(db.String, db.ForeignKey("books.isbn"), nullable=False)
    username = db.Column(db.String, db.ForeignKey("users.username"), nullable=False)
    rev_rating = db.Column(db.Integer, nullable=False)
    rev_text = db.Column(db.String, nullable=False)

