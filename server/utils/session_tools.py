from flask import request
from functools import wraps
import uuid

def requires_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_token = request.cookies.get('session_token')
        if not session_token:
            return "Invalid session", 401
        try:
            uuid.UUID(session_token)  # Try to parse the token as a UUID
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
    query = "SELECT email FROM sessions WHERE session_token = %s"
    #need to execute this query with correct sql system

def establish_session(email, session_token):
    #delete all sessions where email exists and then make new session
    query = "INSERT INTO sessions (email, session_token) VALUES (%s, %s)"