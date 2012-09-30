
from globals import *

import os, re, urllib
import cgi
import hashlib

from google.appengine.api import mail
from google.appengine.api import urlfetch


class Dashboard(webocrat_Request):

    @need_registered_user
    def get(self):
        #logging.info('Dashboard: ' + self.session.get('fullName', 'noname'))
        
        template_values = {
            's': self.session,
        }
        
        self.render_template('Dashboard.django.html', template_values)





class Welcome(webocrat_Request):

# url : /welcome
# info : default landing page
# info : force_loggedin_user() redirects here if no user is logged in with facebook, google, yahoo or twitter account
# logic : if not loggedin = show the Welcome page 
# logic : if loggedin & registered = redirect to /
# logic : if loggedin & not registered = redirect to /hello

# content: Join hug yellow paper
# content: you can use your facebook , google, yahoo or twitter account to log in

    def get(self):
        s = self.session
        if not self.user_loggedin:
            logging.info('Welcome : user is not logged in') # with Facebook, Google, Yahoo or Twitter account
            template_values = {
                'invitation': self.session.get('invitation', False),
                'login_iframe': LOGIN_IFRAME,
                'BASE_URL': BASE_URL
            }
            self.render_simple_template('Welcome.django.html', template_values)
        else:
            logging.info('Welcome : user IS logged in with ' + s['provider']) #Facebook, Google, Yahoo or Twitter account
            if not self.user_registered:
                #logging.info('Welcome : user is NOT registered - redirecting to /hello')
                self.redirect("/hello")
            else:
                #logging.info('Welcome : user IS registered - redirecting to /')
                self.redirect("/")

    
#----------------------------------------------------------
#----------------------------------------------------------
#----------------------------------------------------------
class RPXTokenHandler(webocrat_Request):
    #"""Receive the POST from RPX with our user's login information."""
    def post(self):
        token = self.request.get('token')
        url = 'https://rpxnow.com/api/v2/auth_info'
        args = {
            'format': 'json',
            'apiKey': '97540d0df8db1a34260801d0c5a11c00ce1b6128',
            #TODO(vlad.lego): remove before open-sourcing
            'token': token
        }
        r = urlfetch.fetch(url=url,
                           payload=urllib.urlencode(args),
                           method=urlfetch.POST,
                           headers={'Content-Type': 'application/x-www-form-urlencoded'})
        rsp = json.loads(r.content)

        #session = get_current_session()
        if rsp['stat'] == 'ok':
            # extract some useful fields
            profile = rsp['profile']
            user = self.log_user_in(profile)
            after = self.session.pop('redirect_after_login', "/")
            self.redirect(after)
        else:
            self.response.out.write('Something went wrong, please try logging in again later.')
            return


    def log_user_in(self, profile):
        #sets session user data - called by RPX
        #if user exists         > get from database
        #if user doesn't exist  > session['newUser']=True

        #logging.info('RPX: log_user_in')

        s = self.session
        unique_identifier = profile.get('identifier')
        s['unique_identifier'] = unique_identifier

        theUserQuery = WebocratUser.gql("WHERE uniqueID = :1 LIMIT 1", unique_identifier)
        theUser = theUserQuery.get()

        if theUser is None:
            logging.info('RPX: log_user_in : NOT registered')
            s['user_key'] = None
            s['provider'] = profile.get('providerName')
            s['fullName'] = profile.get('displayName', '')
            thename = profile.get('name', '')
            s['firstName'] = thename.get('givenName', '')
            thebirthdate = profile.get('birthday', '1910-1-1').split('-') #YYYY-MM-DD
            try:
                byear = int(thebirthdate[0])
            except ValueError:
                byear = 1910
            if byear == 0: byear = 1910
            s['birthyear'] = byear
            s['birthmonth'] = thebirthdate[1]
            s['birthday'] = thebirthdate[2]

            s['profile_pic_url'] = profile.get('photo', False)
            s['email'] = profile.get('email', False)
            verified_email = profile.get('verifiedEmail', False)
            if verified_email:
                s['email'] = verified_email
                s['email_is_verified'] = True
        else:
            logging.info('RPX: log_user_in : user already registered')
            s['user_key'] = str(theUser.key())
            s['provider'] = theUser.provider
            s['email'] = theUser.email
            s['email_is_verified'] = theUser.email_is_verified
            s['fullName'] = theUser.ego.name
            s['lat'] = theUser.ego.location.lat
            s['lng'] = theUser.ego.location.lon

            # generate token - a new one for each log in - just like a session
            #TODO(vlad.lego): make sure the session is unique
            # added unique id at the beginning

            theUser.token = hashlib.md5(s['unique_identifier']).hexdigest()
            theUser.token += hashlib.md5(os.urandom(16)).hexdigest()
            theUser.put()

        return theUser


#----------------------------------------------------------
#----------- HELLO PAGE www.hug-fu.com/hello --------------
#----------------------------------------------------------

class Hello(webocrat_Request):

# url : /hello
# info : force_registered_user() redirects here if user is not registered


    def get(self):
        self.showpage()
        
    def post(self):
        self.showpage(True)

    def showpage(self,post=False):
        if not self.force_loggedin_user(): return

        s = self.session

        errors = dict()
        if post:
            #posting form
            # verify the data

            #-- NAME CHECK --
            postName = self.request.get('name')
            if postName == 'Name':
                errors['name'] = "Please enter your name"
            else:
                if s.get('fullName', 'Name') == postName:
                    #name is the same as on social network - treated as "safe"
                    pass
                else:
                    #name is different than the name used on network
                    pass

            #-- EMAIL CHECK --
            if s.get('email', None) != self.request.get('email'):
                s['email_is_verified'] = False

#            #-- LAT LNG CHECK --
#            s['lat'] = float(self.request.get('lat'))
#            s['lng'] = float(self.request.get('lng'))

            if not len(errors):
                # DATA_OK:
                # save the data in the session
                s['email'] = self.request.get('email')
                s['fullName'] = self.request.get('name')
                save_user_data(self)

        #getting form / displaying form
        template_values = {
            'user_registered': self.user_registered,
            'name': s.get('fullName', 'Name'),
            'email': s.get('email', 'Your email'),
#            'lat': s.get('lat', DEFAULT_LATITUDE),
#            'lng': s.get('lng', DEFAULT_LONGITUDE),
            'errors': errors
        }

        edit = self.request.get('edit',None) == 'profile'

        if self.user_registered and (edit==False):
            self.redirect("/")
        else:
            self.render_template('Join.django.html', template_values)





class Logout(webocrat_Request):

    @need_registered_user
    def get(self):
        #delete token
        self.user.token = None
        self.user.put()
        #end session
        self.session.terminate()
        self.redirect("/")


app = webapp2.WSGIApplication([
#                                ('/', Dashboard),
                                ('/welcome', Welcome),
                                ('/rpx', RPXTokenHandler),
                                ('/hello', Hello),
                                ('/logout', Logout),
                            ], debug=True)

#
#
#def main():
#    application = webapp.WSGIApplication([      ('/', Dashboard),
#                                                ('/welcome', Welcome),
#                                                ('/rpx', RPXTokenHandler),
#                                                ('/hello', Hello),
#                                                ('/logout', Logout),
#                                                ('/(.*)', Dashboard)
#                                         ], debug=True)
#    util.run_wsgi_app(application)
#
#
#if __name__ == '__main__':
#    main()
