"""
Defines the Flask container, 'APP'
"""
from flask import Flask
from werkzeug import SharedDataMiddleware  #IGNORE:E0611 @UnresolvedImport
import os
from flask_googleauth import GoogleAuth
from flask_mail import Mail
from flask.helpers import url_for

APP = Flask(__name__)
APP.config.from_object('lb.config')
APP.config.from_object('lb.local_settings')
APP.wsgi_app = SharedDataMiddleware(APP.wsgi_app,
    {'/':os.path.join(os.path.dirname(__file__), 'static')})

MAIL = Mail(APP)

# Flask-GoogleAuth, used by main.py
AUTH = GoogleAuth(APP)
