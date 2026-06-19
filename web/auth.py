from flask import session
from app.database_sqlite import verify_user


def login_user(username, password):

    user = verify_user(username, password)

    if user:

        if "error" in user:
            return "pending"

        session["user"] = user["username"]
        session["role"] = user["role"]
        session["organization_id"] = user["organization_id"]

        return True

    return False


def is_logged_in():
    return "user" in session


def logout_user():
    session.pop("user", None)
    session.pop("role", None)
    session.pop("organization_id", None)
def is_admin():
    return session.get("role") == "admin"