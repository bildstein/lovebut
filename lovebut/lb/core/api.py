"""
Core API for backend.
"""
from lb.db.creation import BASE, ENGINE, create_session
from lb.db import tables
from lb.core import dtos
from functools import wraps
import logging
from sqlalchemy.exc import IntegrityError
from lb.infrastructure.util import concatenate
from sqlalchemy.orm.exc import NoResultFound
import traceback
from lb.mail.notifications import send_message

#pylint:disable=R0903

def exception_mapper(fun):
    """
    Converts database exceptions to APIError
    """
    @wraps(fun)
    def inner(*args, **kwargs):
        """
        Catch exceptions and return API.ERR_UNKNOWN
        """
        # pylint:disable=W0703
        try:
            return fun(*args, **kwargs)
        except Exception as ex:
            logging.info("Unhandled exception in API function: %r", ex)
            logging.info("Exception traceback: %r", traceback.format_exc())
            return API.ERR_UNKNOWN
    return inner

def api(fun):
    """
    Equivalent to:
        @exception_mapper
        @create_session
        
    Used to ensure exception_mapper and create_session are applied in the
    correct order.
    """
    @wraps(fun)
    @exception_mapper
    @create_session
    def inner(*args, **kwargs):
        """
        No additional functionality
        """
        return fun(*args, **kwargs)
    return inner

class APIError(object):
    """
    These objects will be returned by @exception_mapper
    """
    def __init__(self, description):
        self.description = description
    
    def __str__(self):
        return self.description

class API(object):
    """
    Core API, which may be called by:
     - a website
     - an admin console or command line
     - a thick client
    """
    
    ERR_UNKNOWN = APIError("Internal error")
    ERR_NO_SUCH_USER = APIError("No such user")
    
    def __init__(self):
        self.session = None  # required for @create_session
    
    @exception_mapper
    def create_db(self):
        """
        Create and seed the database
        """
        #pylint:disable=R0201
        BASE.metadata.create_all(ENGINE)
    
    @api
    def login(self, request):
        """
        1. Create or validate OpenID-based account
        inputs: identity, email, screenname
        outputs: userid
        """
        matches = self.session.query(tables.User)  \
            .filter(tables.User.identity == request.identity)  \
            .filter(tables.User.email == request.email).all()
        if matches:
            # return user from database
            user = matches[0]
            user.unsubscribed = False
            return dtos.UserDetails.from_user(user)
        else:
            # create user in database
            user = tables.User()
            user.identity = request.identity
            user.email = request.email
            user.screenname = request.screenname
            user.unsubscribed = False
            self.session.add(user)
            self.session.flush()
            logging.debug("Created user %d with screenname '%s'",
                          user.userid, user.screenname)
            return dtos.UserDetails.from_user(user)
            
    @api
    def unsubscribe(self, identity):
        """
        Deletes the user.
        """
        matches = self.session.query(tables.User)  \
            .filter(tables.User.identity == identity).all()
        if not matches:
            return self.ERR_NO_SUCH_USER
        user = matches[0]
        self.session.delete(user)
        return True
            
    @api
    def change_screenname(self, request):
        """
        Change user's screenname
        """
        try:
            self.session.query(tables.User)  \
                .filter(tables.User.userid == request.userid)  \
                .one().screenname = request.screenname
        except NoResultFound:
            return self.ERR_NO_SUCH_USER
    
    @api
    def get_user(self, userid):
        """
        Get user's LoginDetails
        """
        matches = self.session.query(tables.User)  \
            .filter(tables.User.userid == userid).all()
        if not matches:
            return self.ERR_NO_SUCH_USER
        user = matches[0]
        return dtos.DetailedUser(userid=user.userid,
                                 identity=user.identity,
                                 email=user.email,
                                 screenname=user.screenname)
        
    @api
    def love(self, userid, message):
        """
        Send message to userid
        """
        matches = self.session.query(tables.User)  \
            .filter(tables.User.userid == userid).all()
        if not matches:
            return self.ERR_NO_SUCH_USER
        user = matches[0]
        send_message(recipient=user.email,
                     message=message,
                     identity=user.identity)
