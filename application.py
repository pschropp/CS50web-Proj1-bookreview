""" 
set environment variables in terminal before flask run:
cd DEV/CS50-WebDev/Projects/project1
export FLASK_APP=application.py
export FLASK_DEBUG=1
export DATABASE_URL= see URI in DB and API Credentials.txt
flask run
"""

import os
import requests

from flask import Flask, session, flash, jsonify, redirect, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Set API-Key for Goodreads
GR_API_Key = "***REMOVED***"

@app.route("/")
#if needed, uncomment decorator login_required 
# @login_required
def index():
    #this should render the search, if user is logged in
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    """use generate_password_hash from werkzeug to create pwdhash from provided password"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # store form inputs in variables
        username = request.form.get("username")
        useremail = request.form.get("useremail")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure username was submitted
        elif not useremail:
            return apology("must provide mail address", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # Query database for username and check, if username exists already    
        rows = db.execute("SELECT * FROM users WHERE username = :username",         #pylint: disable=no-member
                    {"username": username}).rowcount
        if rows == 0: 
            #hash password
            pwdhash = generate_password_hash(password, "sha256")

            # make new entry in db for new user
            db.execute("INSERT INTO users (username, useremail, pwdhash) VALUES  (:username, :useremail, :pwdhash)",     #pylint: disable=no-member
                        {"username": username, "useremail": useremail, "pwdhash": pwdhash})
            db.commit()     #pylint: disable=no-member
            ### to be implemented: if successful, show congratulation msg, 
            ### maybe via separate route "newlogin" which returns to normal login just adding a differen title

        else:                  
            return apology("username already exists, please choose another username or login", 403)

        # Redirect user to login page
        return redirect("/login")
        
        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", #pylint: disable=no-member
                          {"username":request.form.get("username")}).fetchall()
        
        # Ensure username exists and password is correct; check_password_hash is imported from werkzeug
        if len(rows) != 1 or not check_password_hash(rows[0]["pwdhash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")






'''
# Errorhandling via error.html
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html", errormsg=e.name, errorcode=e.code),code

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
'''




#Error handling for cat pic using apology function in helpers.py and apology.html
# Errorhandling
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
