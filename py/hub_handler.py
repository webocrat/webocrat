__author__ = 'vlad.lego@webocrat.com (Vlad Lego)'

from globals import *

import re
import cgi
import urllib
import random
import string
import webapp2

from datetime import *
from google.appengine.api import mail
from google.appengine.api import urlfetch

from google.appengine.api import channel

class HubNew(webocrat_Request):
    @need_registered_user
    def get(self):
        user = self.user
        newHub = {
            'lat': user.ego.location.lat,
            'lng': user.ego.location.lon
        }
        self.render_template("Hub.New.django.html", newHub)


class HubView(webocrat_Request):
    @need_registered_user
    def get(self, id):
        user = self.user
        theHub = Hub().get_by_id(int(id))

        hubVars = {
            'hub' : theHub,
            'lat' : theHub.location.lat,
            'lng' : theHub.location.lon
        }
        self.render_template("Hub.View.django.html",hubVars)

class HubsBrowse(webocrat_Request):
    @need_registered_user
    def get(self):
        user = self.user
        hubVars = {
            'lat' : user.ego.location.lat,
            'lng' : user.ego.location.lon
        }
        self.render_template("Hub.Browse.django.html", hubVars)

app = webapp2.WSGIApplication([
        ('/hubs', HubsBrowse),
        ('/hub/new', HubNew),
        ('/(.*).hub', HubView)
    ])
