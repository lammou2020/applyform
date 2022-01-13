import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from intWeb.auth.models import db, User

bp = Blueprint("auth", __name__, url_prefix="/auth")

def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")
    g.user = User.query.get(user_id) if user_id is not None else None


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        CheckCode = request.form["CheckCode"]
        error = None

        if CheckCode =="3.14":
            pass
        else:
            error="CheckCode invalid."
            flash(error)
            return


        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif db.session.query(
            User.query.filter_by(user=username).exists()
        ).scalar():
            error = f"User {username} is already registered."

        if error is None:
            # the name is available, create the user and go to the login page
            db.session.add(User(user=username, password=password))
            db.session.commit()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("flaskr/auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        user_ = User.query.filter_by(user=username).first()

        if user_ is None:
            error = "Incorrect username."
        elif not user_.check_password(password):
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user_.id
            session['profile']= from_sql(user_)
            return redirect(url_for("index"))

        flash(error)

    return render_template("flaskr/auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    del session['profile']
    session.modified = True
    session.clear()
    return redirect(url_for("index"))
