from globals import *


class _Hubs(webocrat_Request):

    @need_registered_user
    def post(self):
        template_vals={
            'hubs_title' : 'All Hubs',
            'hubs' : Hub.all()
        }
        self.render_simple_template('Hubs.django.html', template_vals)


def main():
    application = webapp.WSGIApplication([('/hubs', _Hubs)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
