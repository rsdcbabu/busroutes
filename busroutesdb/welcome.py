import webapp2
import cgi

from google.appengine.api import users,urlfetch


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('Welcome to busroutes App. <br /> Courtesy: busroutes.in')
 

application = webapp2.WSGIApplication([
    ('/',MainPage)
], debug=True)

