from flask import request
from functools import wraps
import uuid
from config.database import db


def requires_user_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_token = request.cookies.get('session_token')
        if not session_token:
            return "Invalid session", 401
        try:
            uuid.UUID(session_token)
        except:
            return 'Invalid token', 401
        validated_user = user_from_session(session_token)
        if validated_user:
            return func(validated_user, *args, **kwargs)
        else:
            return "Invalid session", 401
    return wrapper

def user_from_session(session_token):
    if not session_token:
        return None
    query = "SELECT email FROM sessions WHERE session_token = %s;"
    values = db.engine.execute(query, (session_token)).fetchone()
    return values.email

def establish_session(email, session_token):
    try:
        query_delete = "DELETE FROM sessions where email = %s;"
        db.engine.execute(query_delete, (email))
        query = "INSERT INTO sessions (email, session_token) VALUES (%s, %s);"
        data = (email, session_token)
        db.engine.execute(query, data)
    except:
        raise ValueError('session could not be estalished')

def get_privledge(email):
    try:
        query = "SELECT user_privledge FROM users where email = %s;"
        return db.engine.execute(query, (email)).fetchone().user_privledge

    except:
        raise ValueError('session could not be estalished')