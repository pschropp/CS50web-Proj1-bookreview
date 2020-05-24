import os
import requests

from flask import Flask, session, request
from flask_session import Session
#from sqlalchemy import create_engine
#from sqlalchemy.orm import scoped_session, sessionmaker
from config import Config
from app.models import * #own model file with classes for ORM

app = Flask(__name__)

#importing configurations from config.py
app.config.from_object(Config)

#create and initiate Login-Manager for Flask-Login
#login = LoginManager(app)

# Set up database, according to imported configurations
db.init_app(app)
# Check for environment variable db url
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem, according to imported configurations
Session(app)


from app import routes