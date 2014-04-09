"""
Data transfer objects:
- login, with OpenID, OpenID identity, email address, screenname
- user, with userid for user, system generated
- gameid for open, running or finished game
- range-based action
- open game, with list of users registered and details of situation
- general game, with status (open/running/finished), whose turn?, details of
  situation as per open game list
- hand history(!)
"""
from lb.db import tables
from argparse import ArgumentError

#pylint:disable=R0903,R0913,R0902

# Note: We do not log the user in until they have chosen a unique screenname
# But also note that we only know if their screenname is unique by trying.
class LoginRequest(object):
    """
    Details to record (or ensure) a user in the database.
    """
    def __init__(self, identity, email, screenname):
        """
        If the screenname is already taken, then error, ask user for new
        screenname, and try again.
        
        Response will be an error only when BOTH:
         - this user doesn't exist, AND
         - another user has this screenname
        """
        self.identity = identity
        self.email = email
        self.screenname = screenname

class ChangeScreennameRequest(object):
    """
    When the initial automatic login fails, the user gets a chance to choose a
    different screenname and try again. All is well, and this class is not
    needed.
    
    When the initial automatic login succeeds, the user may still want to change
    their screenname, and we give them that option. When they do so, this
    request object is sent to the backend to change their name.
    """
    def __init__(self, userid, screenname):
        self.userid = userid
        self.screenname = screenname

class UserDetails(object):
    """
    Response from a LoginRequest. Note that the screenname may change because
    the user has chosen a different one.
    
    If response has a different screenname to request, it means that the user
    has previously chosen to have a different screenname, possibly because their
    name was taken.
    
    If response has the same screenname, it means either that the user has
    logged in previously, or they were created with that screenname.
    """
    def __init__(self, userid, screenname):
        self.userid = userid
        self.screenname = screenname
    
    def __repr__(self):
        return "UserDetails(%r, id=%r)" % (self.screenname, self.userid)
        
    def __str__(self):
        return self.screenname
    
    @classmethod
    def from_user(cls, user):
        """
        Create object from tables.User
        """
        return cls(user.userid, user.screenname)
    
class DetailedUser(object):
    """
    OpenID identity, email address, screenname
    """
    def __init__(self, userid, identity, email, screenname):
        self.userid = userid
        self.identity = identity
        self.email = email
        self.screenname = screenname
