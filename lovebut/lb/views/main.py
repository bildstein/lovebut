"""
The main pages for the site
"""
from flask import render_template, redirect, url_for
from lb.app import APP
from lb.core.api import API, APIError
from lb.app import AUTH
from lb.core.dtos import LoginRequest
from lb.forms.love import LoveForm
import logging
from flask.helpers import flash
from flask.globals import request, session, g
from lb.core import dtos
from flask_googleauth import logout
from lb.mail import notifications

def is_authenticated():
    """
    Is the user authenticated with OpenID?
    """
    return g.user and 'identity' in g.user

@APP.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    """
    Record that the user does not want to receive any more emails, at least
    until they log in again and in so doing clear that flag.
    
    Note that authentication is not required.
    """
    api = API()
    identity = request.args.get('identity', None)
    if identity is None:
        msg = "Invalid request, sorry."
    else:
        response = api.unsubscribe(identity)
        if response is api.ERR_NO_SUCH_USER:
            msg = "No record of you on love, but, sorry."
        elif isinstance(response, APIError):
            msg = "An unknown error occurred."
        else:
            session.clear()  # not just logout... total destruction
            return redirect(url_for('goodbye'))
    flash(msg)
    return render_template('base.html')

@APP.route('/goodbye', methods=['GET'])
def goodbye():
    flash("I don't know who you are any more... goodbye...")
    return render_template('base.html')

@logout.connect_via(APP)
def on_logout(_source, **_kwargs):
    """
    I prefer to be explicit about what we remove on logout. 
    """
    session.pop('userid', None)
    session.pop('screenname', None)

@APP.route('/log-in', methods=['GET'])
@AUTH.required
def log_in():
    """
    Does what /login does, but in a way that I can get a URL for with url_for!
    """
    # TODO: REVISIT: get a relative URL for /login, instead of this.
    return redirect(url_for('home_page'))

@APP.route('/error', methods=['GET'])
def error_page():
    """
    Unauthenticated page for showing errors to user.
    """
    return render_template('base.html', title='Sorry')

@APP.route('/', methods=['GET'])
def home_page():
    """
    Generates the unauthenticated landing page. AKA the main or home page.
    """
    if not is_authenticated():
        return render_template('landing.html')
    screenname = g.user['name'].split()[0]
    api = API()
    req = LoginRequest(identity=g.user['identity'],  # @UndefinedVariable
                       email=g.user['email'],  # @UndefinedVariable
                       screenname=screenname)
    result = api.login(req)  # commit user to database and determine userid
    if isinstance(result, APIError):
        flash("Error registering user details.")
        logging.debug("login error: %s", result)
        return redirect(url_for('error_page'))
    else:
        session['screenname'] = result.screenname
        session['userid'] = result.userid
    api = API()
    userid = session['userid']
    screenname = session['screenname']
    identity = g.user['identity']
    personal_url = url_for("love", user=userid, _external=True)
    unsubscribe_url = notifications.make_unsubscribe_url(identity)
    return render_template('home.html', screenname=screenname,
        personal_url=personal_url, unsubscribe_url=unsubscribe_url)

@APP.route('/love', methods=['GET', 'POST'])
@AUTH.required
def love():
    """
    Main message-sending page.
    Note that you don't have to log in or have an account for this, you just
    have to be authenticated by Google.
    """
    userid = request.args.get('user', None)
    if userid is None:
        flash("That URL doesn't specify a valid user. I'm so sorry...")
        return render_template('base.html')
    api = API()
    response = api.get_user(userid)
    if isinstance(response, APIError):
        flash("That URL doesn't specify a valid user. I'm so sorry...")
        return render_template('base.html')
    target = response.screenname
    form = LoveForm()
    if not form.validate_on_submit():
        form = LoveForm()
        return render_template('love.html', form=form, userid=userid,
                               target=target)
    but = form.but.data
    message = "I love %s, but I wish %s" % (target, but)
    api.love(userid, message)
    return render_template('loved.html', message=message)
