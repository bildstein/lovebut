"""
For sending email to users, like telling them it's their turn to act in a game.
"""
from flask_mail import Message
from flask.templating import render_template
from flask import copy_current_request_context, url_for
from lb.app import MAIL
from threading import Thread
from functools import wraps

class NotificationSettings(object):
    """
    A simple holder for a setting to suppress email. Provides for a singleton.
    """
    def __init__(self):
        self.suppress_email = False

def make_unsubscribe_url(identity):
    """
    Make a proper Flask-smart URL for unsubscribing.
    """
    return url_for('unsubscribe', _external=True, identity=identity)
        
NOTIFICATION_SETTINGS = NotificationSettings()

def send_email_async(msg):
    """
    Send email on a different thread.
    
    Per http://stackoverflow.com/questions/11047307/
        run-flask-mail-asynchronously/18407455
    """
    @copy_current_request_context
    def with_context():
        """
        Wrapper to send message with copied context
        """
        MAIL.send(msg)
    
    thr = Thread(target=with_context)
    thr.start()

def send_message(recipient, message, identity):
    """
    Send message to userid.

    The identity is used to create the unsubscribe link. We can safely use
    that to identify the user in plain text, because they get to see it
    anyway during authentication.
    
    Uses Flask-Mail; sends asynchronously.
    """
    msg = Message("A message for you!")
    msg.add_recipient(recipient)
    msg.html = render_template('email.html',
                               message=message,
                               unsubscribe=make_unsubscribe_url(identity))
    send_email_async(msg)
