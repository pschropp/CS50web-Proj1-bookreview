""" 
set environment variables in terminal before flask run or use bash script SetEnvInTerminal on Mac Desktop:
cd Users/Pascal/DEV/CS50-WebDev/Projects/project1
export FLASK_APP=application.py
export FLASK_DEBUG=1
export DATABASE_URL= see URI in DB and API Credentials.txt
flask run

or: do pip install python-dotenv in project folder and create .flaskenv file in project folder (which contains env-variables) for env variables to be set automatically

(flask run --host=0.0.0.0 with ip address of computer if serving to the network instead of only localhost 127.0.0.1)
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

import json

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

# Set API-Key for Goodreads, got from Goodreads after registration for API access
GR_API_Key = "uOl7cU35PPDAUm20ui6TCQ"

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
            flash("Your account has been created. Enjoy!")           
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
        app.logger.info('%s logged in successfully', session["username"]) #pylint: disable=no-member

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
    details = []
    details = db.execute("SELECT * FROM books WHERE isbn = :isbn", #pylint: disable=no-member
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
    #app.logger.info('searchresult for ratings: %s', own_reviewsisbn_ratings)
    if own_reviewsisbn_ratings[0][0] != 0:
        numberofownrev = int(own_reviewsisbn_ratings[0][0])
        own_avg_rating = float(own_reviewsisbn_ratings[0][1])
        
        #get reviews from database
        own_reviewsisbn = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", #pylint: disable=no-member
                                        {"isbn": isbn}).fetchall()
    else: # i.e. if there are no reviews for that book, set individ variables to accordant values that can be used by Jinja
        numberofownrev, own_avg_rating, own_reviewsisbn = 0, 0, []

    #get avg ratings and number of ratings from Goodreads-API and pass to bookdetails.html
    try:
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GR_API_Key, "isbns": isbn}).json()
        app.logger.info('answer from GoodReads-API: %s', res) #pylint: disable=no-member
        GR_ratings_count = res["books"][0]["work_ratings_count"]
        GR_ratings_avg = res["books"][0]["average_rating"]
        app.logger.info('avg from GoodReads-API: %s in %s ratings' % (GR_ratings_avg, GR_ratings_count)) #pylint: disable=no-member
    except:
        app.logger.error('problem with answer from GoodReads-API') #pylint: disable=no-member
        
    return render_template("bookdetails.html", bookdet=details, hidebutton=hidebutton, numberofownrev=numberofownrev, own_avg_rating=own_avg_rating, own_reviewsisbn=own_reviewsisbn, GR_ratings_avg=GR_ratings_avg, GR_ratings_count=GR_ratings_count) 

    

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


@app.route("/api/<string:isbn>", methods=["GET", "POST"]) # build route with variable for isbn; isbn is entered in Browser URL or via API-Req.
def api(isbn):
    """API to return bookdetails when isbn is passed"""

    if request.method == "POST":
        return errordisplay("Method Not Allowed: POST requests not allowed for this API-call", 405)

    if request.method == "GET":
        try:
            api_details = []
            api_details = db.execute("SELECT * FROM books WHERE isbn = :isbn", #pylint: disable=no-member
                                                {"isbn":isbn}).fetchone()
            #assign results of bookresult query to variables
            #app.logger.info('db results for isbn: %s', own_reviewsisbn_ratings)
            api_title = api_details[1]
            api_author = api_details[2]
            api_year = api_details[3]
            #assign results of ratings query to variables
            own_reviewsisbn_ratings = db.execute("SELECT COUNT(rev_rating), AVG(rev_rating) FROM reviews WHERE isbn = :isbn", #pylint: disable=no-member
                                            {"isbn": isbn}).fetchall()
                #check, if there are ratings in db. If yes, convert db.execute output (string, string) to int/float. If no ratings (result: (0, None) ) --> else...
            if own_reviewsisbn_ratings[0][0] != 0:
                api_ratings_count = int(own_reviewsisbn_ratings[0][0])
                api_ratings_avg = float(own_reviewsisbn_ratings[0][1])
            else: # i.e. if there are no reviews for that book, set individ variables to accordant values that can be used by Jinja
                api_ratings_avg = 0

            json_res = {
                "isbn" : isbn,
                "title": api_title,
                "author": api_author,
                "year": api_year,
                "review_count": api_ratings_count,
                "average_score": api_ratings_avg
            }
            #return json.dumps(json_res), works but better with jsonify, firefox does work better with that header
            return jsonify(json_res)

        except:
            #return json.dumps({"error_msg": "ISBN not in our database", "error_code": 404}), 404   , works but better with jsonify, firefox does work better with that header
            return jsonify({"error_msg": "ISBN not in our database", "error_code": 404}), 404



# Errorhandling
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return errordisplay(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
