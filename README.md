# Harvard CS50 Web Development Project1: Book Review Web App
There are two versions in this repo, each on a different branch:

1. branch master: original version for CS50 project
2. branch Proj1_ORM: refactored using ORM instead of direct approach. Also adds features and uses more libraries etc.


## Table of Contents

1. [Motivation](#motivation)
2. [Setup](#setup)
3. [Repository Structure](#structure)
4. [Usage](#usage)
5. [License and Acknowledgements](#license)


### Motivation <a name="motivation"></a>
This repo contains the Harvard CS50web Project1 on the master branch and an extended (+ORM) version of it. The app is created using Flask for the BookReview page in combination with a PostgreSQL database and the Goodreads REST API. The app has then been deployed on Heroku.

Users can register for the book review website and then log in using their username and password. 
Once they log in, they can search for books, leave reviews for individual books, and see the reviews made by other people. 
A third-party API by Goodreads, another book review website, is used to pull in ratings from a broader audience. 
Finally, users are able to query for book details and book reviews programmatically via the website’s API.

### Setup <a name="setup"></a>
1. Clone this repo or download it as a zip file and unzip it.
2. In a terminal window, navigate into the project folder.
3. Run `pip3 install -r requirements.txt` in your terminal window to make sure that all of the necessary Python packages (Flask and SQLAlchemy, for instance) are
installed.
4. Set the environment variable FLASK_APP to be application.py. On a Mac or on Linux, the command to do this is `export FLASK_APP=application.py`. On Windows,
the command is instead `set FLASK_APP=application.py`. You may optionally want to set the environment variable `FLASK_DEBUG` to 1 , which will activate Flask’s
debugger and will automatically reload your web application whenever you save a change to a file.
5. Set the environment variable `DATABASE_URL` to be the URI of your database, which you should be able to see from the credentials page on Heroku.
6. Run flask run to start up your Flask application.

