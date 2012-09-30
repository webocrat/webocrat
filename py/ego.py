TO MOVE IN SERVICES

from globals import *

class _Ego(webocrat_Request):

    @need_registered_user
    def get(self):
        template_vals={}
        self.render_simple_template('HomePage.django.html', template_vals)


class _EgoTransaction(webocrat_Request):

    @need_registered_user
    def post(self):
        targetEgo = Ego.get_by_id(int(self.request.get('target_ego_id', False)))
        request_trust = self.request.get('trust')
        if request_trust is '-1': trust = False
        if request_trust is '1': trust = True
        if request_trust is '0': trust = None
        template_vals={}
        self.render_simple_template('HomePage.django.html', template_vals)        

def main():
    application = webapp.WSGIApplication([('/', _Ego),
                                         ('/x.ego', _EgoTransaction)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
