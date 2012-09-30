#!/usr/bin/env python

from google.appengine.ext.webapp import util
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from gaesessions import get_current_session
#TODO: replace gaesessions with webapp2 sessions
from webapp2_extras import sessions

from datetime import *
import json

from google.appengine.api import memcache

from datamodels import *
import os, logging
import webapp2


DOMAIN_NAME = 'www.webocrat.com'
DEVELOPMENT_IP = 'localhost'
RPX_NOW_ID = 'webocrat.rpxnow.com'


#   The following piece of code is used to detect the python server type (development or deployment)
#   It sets :
#        BASE_URL
#        LOGIN_IFRAME


ON_LOCALHOST = ('Development' == os.environ['SERVER_SOFTWARE'][:11])
if ON_LOCALHOST:
    CAINI_URL = 'localhost:8080/hartacainilor'
    BASE_URL = DEVELOPMENT_IP
    if os.environ['SERVER_PORT'] is not '80':
        BASE_URL = '%s:%s' % (BASE_URL, os.environ['SERVER_PORT'])
else:
    BASE_URL = DOMAIN_NAME
    CAINI_URL = 'hartacainilor.webocrat.com'


#BASE_URL = 'hartacainilor.webocrat.com'
#BASE_URL = 'localhost:8080'

LOGIN_IFRAME = '<iframe src="http://' + RPX_NOW_ID + '/openid/embed?token_url=http%3A%2F%2F' + BASE_URL + '%2Frpx" scrolling="no" frameBorder="no" allowtransparency="true" class="login-iframe"></iframe>'



#    create decorator: @need_registered_user

def need_registered_user(wrapped_function):
    def new_function(self, *args):
        if not self.force_registered_user(): return
        # force current open session/document
        wrapped_function(self, *args)

    new_function.__name__ = wrapped_function.__name__
    return new_function



class webocrat_Request(webapp2.RequestHandler):

    def initialize(self,request,response):
        webapp2.RequestHandler.initialize(self, request, response)
        self.session = get_current_session()
        self.set_current_user()

    def set_current_user(self):
        # set .user_loggedin
        # set .user_registered              if session['user_key'] is present, the user is considered to be registered
        # set .user
        # set .unique_identifier - no use at the moment

        self.user_loggedin = 'unique_identifier' in self.session
        self.user_registered = False
        self.user = None

        try:
            user_key = self.session.get('user_key',False)
            self.user = WebocratUser.get(db.Key(user_key))
            if self.user:
                self.user_registered = True
                self.ego = self.user.current_ego
        except Exception:
            logging.error("can't get user from the Datastore. user_key=%s" % self.session.get('user_key'))


        #self.unique_identifier = self.session.get('unique_identifier', None)
        logging.info('set current user : registered=%d  logged_in=%d' % (int(self.user_registered), int(self.user_loggedin)))


    def force_loggedin_user(self):
        if self.user_loggedin:  #            logging.info('force_loggedin_user: logged in - OK')
            return True
        else:                   #            logging.info('force loggedin user: not logged in - redirect to /welcome + yahoo')
            self.redirect("/welcome")
            return False


    def force_registered_user(self, persist_url=False):
        """
            forces logged in user - via google, facebook, yahoo or openid

        """
        if not self.force_loggedin_user():
            return False

        if not self.user_registered:
            #logging.info('force registered user : user not registered - redirect to /hello')
            if persist_url:        self.session['redirect_after_login'] = self.request.url
            self.redirect("/hello")
            return False
        else:
            return True



    def redirect_with_message(self, msg, dst='/'):
        self.session['message'] = msg
        self.redirect(dst)

    def render_template(self, file, template_vals):
        template_vals['user'] = self.user
        if self.user:
            template_vals['user_trust_level'] = self.user.ego.trust_level
        self.render_simple_template(file, template_vals)

    def render_simple_template(self, file, template_vals):
        path = os.path.join(os.path.dirname(__file__), '../templates/', file)
        self.response.out.write(template.render(path, template_vals))

# ------------------
# ------------------
# ------------------

def save_user_data(self):
    # the data is saved in the session by the Hug Form
    # at this point the data is trusted as valid (checked before)
    # name, height(cm), lat,lng, year, month, day,

#    logging.info('save user data')

    s = self.session

    myUser = self.user
    if not myUser:
        #new user
        new_ego = Ego()
        new_ego.name = s['fullName']
        new_ego.put()

        myUser = WebocratUser(ego=new_ego)
        myUser.current_ego = new_ego

    myUser.uniqueID = s['unique_identifier']
    myUser.provider = s['provider']
    myUser.emailIsVerified = s['email_is_verified']
    myUser.email = s['email']

    user_ego = myUser.ego
    # temporary workaround - set lat lon to 0,0
    s['lat'] = 0
    s['lng'] = 0
    user_ego.location = "%f, %f" % (s['lat'], s['lng'])
    user_ego.update_location()
#2.7    user_ego.location = "{lat}, {lon}".format(lat=float(s['lat']), lon=float(s['lng']))
    user_ego.name = s['fullName']
    user_ego.put()

    try:
        userkey = myUser.put()
        s['user_key'] = str(userkey)
        self.user_registered=True
    except Exception:
        myUser = False

    return myUser





