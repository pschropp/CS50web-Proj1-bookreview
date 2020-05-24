import os

class Config(object):
    #app secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or '65421231564897654351'

    #database configurations
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True

    # Configure session to use filesystem
    SESSION_FILE_DIR = "mkdtemp()"
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"

    # Set API-Key for Goodreads, got from Goodreads after registration for API access
    GR_API_Key = "***REMOVED***"


"""
heroku: cs50web-pro1-orm
set environment variables in terminal before flask run or use bash script SetEnvInTerminal on Mac Desktop:
cd Users/Pascal/DEV/CS50-WebDev/Projects/proj1_ORM
export FLASK_APP=application.py
export FLASK_DEBUG=1
export DATABASE_URL= see URI in DB and API Credentials.txt
flask run

or: do pip install python-dotenv in project folder and create .flaskenv file in project folder (which contains env-variables) for env variables to be set automatically
"""