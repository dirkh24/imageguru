# -*- coding: utf-8 -*-

from scripts import tabledef
from flask import session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from contextlib import contextmanager
import bcrypt
import datetime

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    s = get_session()
    s.expire_on_commit = False
    try:
        yield s
        s.commit()
    except:
        s.rollback()
        raise
    finally:
        s.close()

def get_session():
    return sessionmaker(bind=tabledef.engine)()

def get_user():
    username = session['username']
    with session_scope() as s:
        user = s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()
        return user

def add_user(username, password, email):
    with session_scope() as s:
        u = tabledef.User(username=username, password=password.decode('utf8'), email=email)
        s.add(u)
        s.commit()

def change_user(**kwargs):
    username = session['username']
    with session_scope() as s:
        user = s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()
        for arg, val in kwargs.items():
            if val != "":
                setattr(user, arg, val)
        s.commit()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

def credentials_valid(username, password):
    with session_scope() as s:
        user = s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()
        if user:
            return bcrypt.checkpw(password.encode('utf8'), user.password.encode('utf8'))
        else:
            return False

def username_taken(username):
    with session_scope() as s:
        return s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()

# set the plan, when user has paid
def set_plan(username):
    print("set_plan")
    with session_scope() as s:
        s.query(tabledef.User).filter(tabledef.User.username == username).update({tabledef.User.paid_plan: True}, synchronize_session=False)
        s.commit()

# get the plan of the current user
def get_plan(username):
    print("get_plan")
    with session_scope() as s:
        result = s.execute(select([tabledef.User.username, tabledef.User.paid_plan]).where(tabledef.User.username == username))
        return result.first()

def set_last_image(username):
    print("set_last_image")
    with session_scope() as s:
        s.query(tabledef.User).filter(tabledef.User.username == username).update({tabledef.User.last_image: datetime.datetime.utcnow()}, synchronize_session=False)
        s.commit()

def get_last_image(username):
    print("get_last_image")
    with session_scope() as s:
        result = s.execute(select([tabledef.User.username, tabledef.User.last_image]).where(tabledef.User.username == username))
        return result.first()
