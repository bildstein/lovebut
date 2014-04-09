"""
Declares database tables
"""
from sqlalchemy import Column, Integer, String, Boolean, Sequence, ForeignKey
from sqlalchemy.orm import relationship, backref
from lb.db.creation import BASE
from sqlalchemy.types import Float
from sqlalchemy.orm.session import object_session

#pylint:disable=W0232,R0903

class User(BASE):
    """
    A user of the application.
    
    Has many-to-many relationships with OpenGame, RunningGame.
    """
    __tablename__ = 'user'
    userid = Column(Integer, Sequence('user_seq'), primary_key=True)
    identity = Column(String(120), nullable=False)
    screenname = Column(String(20), nullable=False)
    email = Column(String(256), nullable=False, unique=True)
    unsubscribed = Column(Boolean, nullable=False)
    
    def __repr__(self):
        return ("User(userid='%r', screenname='%r', email='%r', " +  \
            "identity='%r', unsubscribed='%r')") %  \
            (self.userid, self.screenname, self.email, self.identity,
             self.unsubscribed)