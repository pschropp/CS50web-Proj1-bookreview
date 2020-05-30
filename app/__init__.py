import os
import requests
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, session, request
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config


app = Flask(__name__)

#importing configurations from config.py
app.config.from_object(Config)

#create and initiate Login-Manager for Flask-Login
login = LoginManager(app)
login.login_view = 'login'

# Check for environment variable db uri
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
# Set up database and db migration, according to imported configurations
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# routes.py and own model file with classes for ORM (has to be done after app = Flask(__name__) and after initiating db since that one is imported by models
from app import routes, models, errors


# add logging to file via rotating file handler
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/bookapp.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Bookapp startup')