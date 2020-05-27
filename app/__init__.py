import os
import requests

from flask import Flask, session, request
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
#from sqlalchemy import create_engine
#from sqlalchemy.orm import scoped_session, sessionmaker
from config import Config

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

# Configure session to use filesystem, according to imported configurations
Session(app)

# routes.py and own model file with classes for ORM (has to be done after app = Flask(__name__) and after initiating db since that one is imported by models
from app import routes, models 
