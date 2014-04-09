"""
Contains flask db object
"""
from flask_sqlalchemy import SQLAlchemy
from lb.app import APP

DB = SQLAlchemy(APP)
