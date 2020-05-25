import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session, url_for
from functools import wraps

#creates error pages with cat pic. alternatively used: plain error msg on error.html
def errordisplay(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        """remove this comment for having escaping work
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        """
        return s
    return render_template("error.html", errorcode=code, errormsg=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function
