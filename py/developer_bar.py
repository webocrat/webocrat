from globals import *

class DeveloperBar(webocrat_Request):

    @need_registered_user
    def post(self):
        template_vals = {
            'trusted_egos' : Ego.all().filter('trust = ', True),
            'blacklist_egos' : Ego.all().filter('trust = ', False),
            'subscribed_egos' : Ego.all().filter('trust = ', None),
            'all_egos' : Ego.all()
        }
        self.render_simple_template('debug/DeveloperBar.django.html', template_vals)


app = webapp2.WSGIApplication(
    [
        ('/developer_bar', DeveloperBar)
    ],
    debug=True)
