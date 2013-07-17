import webapp2
import cgi

from google.appengine.api import users,urlfetch


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('<html><head><meta name="txtweb-appkey" content="app-key" /></head><body>Welcome to busroutes App. <br /> Courtesy: busroutes.in</body></html>')
 

application = webapp2.WSGIApplication([
    ('/',MainPage)
], debug=True)

