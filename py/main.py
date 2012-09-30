from globals import *

class MainHandler(webocrat_Request):

    @need_registered_user
    def get(self):
        template_vals = {}
        self.render_simple_template('HomePage.django.html', template_vals)



class HartaCainilorHandler(webocrat_Request):

#    @need_registered_user
    def get(self):
        template_vals = {
            'login_iframe': LOGIN_IFRAME,
            'BASE_URL': BASE_URL,
            'lat' : '44.44',
            'lng' : '26.1',
            'zoom' : 14
        }
        self.session['redirect_after_login'] = self.request.url
        self.render_template('HartaCainilor.django.html', template_vals)



from webapp2_extras import routes

app = webapp2.WSGIApplication([
        routes.DomainRoute('localhost',
            [webapp2.Route('/hartacainilor', handler=HartaCainilorHandler, name='hartacainilor-home0'),
        ]),
        routes.DomainRoute('hartacainilor.webocrat.com',
            [webapp2.Route('/', handler=HartaCainilorHandler, name='hartacainilor-home'),
        ]),
        routes.DomainRoute('www.webocrat.com',
            [webapp2.Route('/hartacainilor', handler=HartaCainilorHandler, name='hartacainilor-home'),
        ]),
        routes.DomainRoute('www.webocrat.com',
            [webapp2.Route('/', handler=MainHandler, name="webocrat-home"),
        ]),
        routes.DomainRoute(BASE_URL,
            [webapp2.Route('/', handler=MainHandler, name="webocrat-home2"),
        ]),
      ])
