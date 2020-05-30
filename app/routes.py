from app import app

import os
import requests

from flask import Flask, session, flash, jsonify, redirect, render_template, request, url_for
from flask_session import Session

from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.urls import url_parse
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

import json

from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm
#from app.helpers import errordisplay

@app.route("/")
@app.route("/index") 
@login_required     #decorator to only show page, if logged in. if not, redirect to login page. defined by flask-login, set-up in __init__.py
def index():
    #this renders the searchforms, if user is logged in
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register user"""
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, useremail=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are registered!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log user in"""

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    """Log user out"""

    logout_user()
    # Redirect user to login form
    return redirect(url_for('index'))


@app.route("/searchresults", methods=["GET", "POST"])
@login_required     #decorator to only show page, if logged in. if not, redirect to login page.
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
            return render_template('error.html', errormsg="you must provide at least one search criterion", errorcode=403), 403

     # User reached route via GET (mainly via search link in navbar)
    else:
        return redirect(url_for("index"))



@app.route("/bookdetails/<string:isbn>") # build route with variable for isbn, isbn passed from bookdetails-link
@login_required     #decorator to only show page, if logged in. if not, redirect to login page.
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
@login_required     #decorator to only show page, if logged in. if not, redirect to login page.
def composereview(isbn):
    """generate and render search results for book search"""

    if request.method == "GET":

        if db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND username = :username", #pylint: disable=no-member
                        {"isbn": isbn, "username": session["username"]}).rowcount == 0:
            #allow review, prepare label for input field and have composereview page rendered for input
            book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone() #pylint: disable=no-member
            return render_template("composereview.html", isbn=isbn, title=book.title, author=book.author, year=book.year)

        else: #i.e. if user has already written a review for that isbn
            return render_template('error.html', errormsg="You have already written a review for this book", errorcode=403), 403
            
    
    elif request.method == "POST":
        # take review from reviewtextfield on composereview.html and radiobutton rating and save in db table reviews
        rev_rating = request.form.get("ratingRadioOptions")
        rev_text = request.form.get("reviewtextfield")
        if rev_rating == None:
            return render_template('error.html', errormsg="Please rate the book (1 - 5)", errorcode=403), 403
        if len(rev_text) == 0 or len(rev_text) > 9999:
            return render_template('error.html', errormsg="Please enter a review text (1-9999 characters)", errorcode=403), 403
 
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
        return render_template('error.html', errormsg="Method Not Allowed: POST requests not allowed for this API-call", errorcode=405), 405

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

