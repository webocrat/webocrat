from globals import *

DEFAULT_LATITUDE = 45.943161
DEFAULT_LONGITUDE = 24.96676

class _New_Hub(webocrat_Request):

    def get(self):
        self.show_form(False)

    def post(self):
        self.show_form(True)

    @need_registered_user
    def show_form(self, post = False):
        errors = dict()
        if post:
            #posting form
            # verify the data

            #-- NAME CHECK --
            post_name = self.request.get('hub-name')
            if post_name == 'Name':
                errors['name'] = "Please enter a valid name"

            if len(errors)==0:
                # DATA_OK:
                newEgo = Ego()
                newEgo.display_name = self.request.get('hub-name')
#                newEgo.location =
                newEgo.put()

                newHub = Hub(ego = newEgo)
                newHub.display_name = newEgo.display_name
                newHub.put()

                self.redirect("/hub."+str(newHub.key().id()))

        template_vals={
            'lat': self.request.get('lat', DEFAULT_LATITUDE),
            'lng': self.request.get('lng', DEFAULT_LONGITUDE),
            'errors': errors
        }
        self.render_simple_template('NewHubForm.django.html', template_vals)


def main():
    application = webapp.WSGIApplication([('/new.hub', _New_Hub)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
