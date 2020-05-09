""" 
set environment variables in terminal before flask run or use bash script SetEnvInTerminal on Mac Desktop:
cd DEV/CS50-WebDev/Projects/project1
export FLASK_APP=application.py
export FLASK_DEBUG=1
export DATABASE_URL= see URI in DB and API Credentials.txt
flask run
"""

import os
import requests

from flask import Flask, session, flash, jsonify, redirect, render_template, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import errordisplay, login_required

# Importing the statistics module 
import statistics 

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
@login_required     #decorator to only show page, if logged in. if not, redirect to login page. defined in helpers.py
def index():
    #this renders the searchforms, if user is logged in
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
            return errordisplay("must provide username", 403)

        # Ensure username was submitted
        elif not useremail:
            return errordisplay("must provide mail address", 403)

        # Ensure password was submitted
        elif not password:
            return errordisplay("must provide password", 403)

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
        else:                  
            return errordisplay("username already exists, please choose another username or login", 403)

        # Log in user directly after registration and redirect to home page
        session["username"] = username
        return redirect("/")
        # alternatively instead of logging in directly: Redirect user to login page: return redirect("/login")

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
            return errordisplay("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return errordisplay("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", #pylint: disable=no-member
                          {"username":request.form.get("username")}).fetchall()
        
        # Ensure username exists and password is correct; check_password_hash is imported from werkzeug
        if len(rows) != 1 or not check_password_hash(rows[0]["pwdhash"], request.form.get("password")):
            return errordisplay("invalid username and/or password", 403)

        # Remember which user has logged in
        session["username"] = rows[0]["username"]

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


@app.route("/searchresults", methods=["GET", "POST"])
@login_required     #decorator to only show page, if logged in. if not, redirect to login page. defined in helpers.py
def searchresults():
    """generate and render search results for book search"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        #session["results"] = [] #delete search results list of user
        searchresults = []
        #store inputs in variables and create regular expression for the LIKE statement
        #using iLIKE for case insensitivity in SQL-query. this ist postgreSQL specific. Otherwise title.lowercase().replace... and user LOWER(column) in query.
        isbn = request.form.get("isbn")
        like_isbn = "%" + isbn.replace("*", "") + "%"
        title = request.form.get("title")
        like_title = "%" + title.replace("*", "") + "%"
        author = request.form.get("author")
        like_author = "%" + author.replace("*", "") + "%"
        # start query based on actually filled input fields, hierarchy: if first found, rest will be skipped and so on
        if isbn:
            searchresults = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", #pylint: disable=no-member
                                                    {"isbn":like_isbn}).fetchall()
            return render_template("searchresults.html", booklist=searchresults)  
        elif title:
            searchresults = db.execute("SELECT * FROM books WHERE title iLIKE :title", #pylint: disable=no-member
                                                    {"title":like_title}).fetchall()
            return render_template("searchresults.html", booklist=searchresults)
        elif author:
            searchresults = db.execute("SELECT * FROM books WHERE author iLIKE :author", #pylint: disable=no-member
                                                    {"author":like_author}).fetchall()
            return render_template("searchresults.html", booklist=searchresults)
            
            # no inputs specified
        else:
            return errordisplay("must provide at least one search criterion", 403)


        # User reached route via GET (mainly via search link in navbar)
    else:
        return redirect("/")



@app.route("/bookdetails/<string:isbn>") # build route with variable for isbn, isbn passed from bookdetails-link
@login_required     #decorator to only show page, if logged in. if not, redirect to login page. defined in helpers.py
def bookdetails(isbn):
    """generate and render search results for book search"""
    session["details"] = []
    session["details"] = db.execute("SELECT * FROM books WHERE isbn = :isbn", #pylint: disable=no-member
                                        {"isbn":isbn}).fetchone()

        #hide compose review button on bookdetails.html, if user has already posted a review
    if db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND username = :username", #pylint: disable=no-member
                        {"isbn": isbn, "username": session["username"]}).rowcount > 0:
        flash("You have already written a review for this book")
        hidebutton = True
    else:
        hidebutton = False

    own_reviewsisbn_ratings = db.execute("SELECT COUNT(rev_rating), AVG(rev_rating) FROM reviews WHERE isbn = :isbn", #pylint: disable=no-member
                                    {"isbn": isbn}).fetchall()
        #check, if there are ratings in db. If yes, convert db.execute output (string, string) to int/float. If no ratings (result: (0, None) ) --> else...
    if own_reviewsisbn_ratings[0][0] != 0:
        numberofownrev = int(own_reviewsisbn_ratings[0][0])
        own_avg_rating = float(own_reviewsisbn_ratings[0][1])
        
        #get reviews from database
        own_reviewsisbn = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", #pylint: disable=no-member
                                        {"isbn": isbn}).fetchall()
    else: # i.e. if there are no reviews for that book, set individ variables to accordant values that can be used by Jinja
        numberofownrev, own_avg_rating, own_reviewsisbn = 0, 0, []

    """show reviews (own + from API)"""
            
    return render_template("bookdetails.html", bookdet=session["details"], hidebutton=hidebutton, numberofownrev=numberofownrev, own_avg_rating=own_avg_rating, own_reviewsisbn=own_reviewsisbn) 

    


@app.route("/composereview/<string:isbn>", methods=["GET", "POST"]) # build route with variable for isbn, isbn passed from bookdetails-link
@login_required     #decorator to only show page, if logged in. if not, redirect to login page. defined in helpers.py
def composereview(isbn):
    """generate and render search results for book search"""

    if request.method == "GET":

        if db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND username = :username", #pylint: disable=no-member
                        {"isbn": isbn, "username": session["username"]}).rowcount == 0:
            #allow review, prepare label for input field and have composereview page rendered for input
            book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone() #pylint: disable=no-member
            return render_template("composereview.html", isbn=isbn, title=book.title, author=book.author, year=book.year)

        else: #i.e. if user has already written a review for that isbn
            return errordisplay("You have already written a review for this book", 403) 
    
    elif request.method == "POST":
        # take review from reviewtextfield on composereview.html and radiobutton rating and save in db table reviews
        rev_rating = request.form.get("ratingRadioOptions")
        rev_text = request.form.get("reviewtextfield")
        if rev_rating == None:
            return errordisplay("Please rate the book (1 - 5)", 403)
        if len(rev_text) == 0 or len(rev_text) > 9999:
            return errordisplay("Please enter a review text (1-9999 characters)", 403)
 
        db.execute("INSERT INTO reviews (isbn, username, rev_rating, rev_text) VALUES (:isbn, :username, :rev_rating, :rev_text)", #pylint: disable=no-member
                        {"isbn": isbn, "username": session["username"], "rev_rating": rev_rating, "rev_text": rev_text})
        db.commit() #pylint: disable=no-member
        # flash sucess message on next page (will be back to bookdetails) 
        flash("Your review has been submitted. Thank you!")
        return redirect(url_for("bookdetails", isbn=isbn))
        



# Errorhandling
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return errordisplay(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
