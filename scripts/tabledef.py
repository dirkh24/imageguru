# -*- coding: utf-8 -*-

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Local
SQLALCHEMY_DATABASE_URI = 'sqlite:///accounts.db'

# Heroku
#SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

Base = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(SQLALCHEMY_DATABASE_URI)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    password = Column(String(512))
    email = Column(String(50))
    paid_plan = Column(Boolean, default=False)  # is true for paid plan
    images_processed = relationship("Images")

    def __repr__(self):
        return '<User %r>' % self.username


class Images(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    uploaded = Column(DateTime(timezone=True), default=func.now())
    user_id = Column(Integer, ForeignKey('user.id'))

engine = db_connect()  # Connect to database
Base.metadata.create_all(engine)  # Create models
