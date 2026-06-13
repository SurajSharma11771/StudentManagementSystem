from flask import session, redirect

# simple demo credentials (later DB me shift kar sakte ho)
USERNAME = "admin"
PASSWORD = "1234"


def login_user(username, password):
    if username == USERNAME and password == PASSWORD:
        session["user"] = username
        return True
    return False


def is_logged_in():
    return "user" in session


def logout_user():
    session.pop("user", None)