import webapp2
import cgi
import json
import re

from google.appengine.api import users,urlfetch


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        points = cgi.escape(self.request.get('txtweb-message'))
        start = end = None
        if points:
            if points.__contains__(","):
                stages = points.split(",")
                if len(stages) >= 2:
                    start,end = stages[0].lower(),stages[1].lower()
        if not points or not start or not end:
            self.response.out.write('<html><head><meta name="txtweb-appkey" content="app-key" /></head><body>Get bus route for any two places. <br /> To use, SMS @busroutes location1,location2 to 92665 92665 <br />Eg: @busroutes thiruvanmiyur,central</body></html>')
            return
        all_stages = self.get_stages()
        if all_stages:
            start_stage_info = self.get_stage_id(all_stages, start)
            end_stage_info = self.get_stage_id(all_stages, end)
            msg = ''
            if not start_stage_info['found']:
                if start_stage_info['suggestions']:
                    msg = 'Please select correct starting point: %s'% (','.join(start_stage_info['suggestions']))
                else:
                    msg = 'Please select different starting point.'
            if msg:
                msg = '%s <br />' % msg
            if not end_stage_info['found']:
                if end_stage_info['suggestions']:
                    msg = '%sPlease select correct ending point: %s'% (msg, ','.join(end_stage_info['suggestions']))
                else:
                    msg = '%sPlease select different ending point.'%msg
            if msg:
                self.response.out.write('<html><head><meta name="txtweb-appkey" content="app-key" /></head><body>%s<br />Thanks to busroutes.in</body></html>'%(msg))
            else:
                start_id = start_stage_info['stage_id']
                end_id = end_stage_info['stage_id']
                bus_route = self.get_bus_route(start_id, end_id)
                self.response.out.write('<html><head><meta name="txtweb-appkey" content="app-key" /></head><body>Bus Route for %s to %s: <br />%s<br />Thanks to busroutes.in</body></html>'%(start_stage_info['stage_req'], end_stage_info['stage_req'], bus_route))

    def get_stages(self):
        stages_api = 'http://busroutes.in/chennai/api/autocomplete/stages'
        s = urlfetch.fetch(url=stages_api,method=urlfetch.GET,deadline=60)
        stages = s.content
        if stages:
            content_dict = json.loads(stages)
            content_dict = k = [{x[0].lower():x[1]} for x in content_dict.items()]
            stages = {}
            for each in content_dict:
                stages[each.items()[0][0]] = each.items()[0][1]
        else:
            stages = {}
        return stages

    def get_bus_route(self, start_id, end_id):
        bus_route = ''
        route_api = 'http://busroutes.in/chennai/path/%s/%s'% (start_id, end_id)
        s = urlfetch.fetch(url=route_api,method=urlfetch.GET,deadline=60)
        bus_re = re.compile('.*?<div class="leftCol">(.*?)</div>', re.DOTALL)
        bus_route = bus_re.findall(s.content)
        if bus_route:
            bus_route = bus_route[0]
            bus_route = bus_route.replace('</span>',',')
            bus_route = re.sub('<.*?>','',bus_route)
            bus_route = bus_route.replace('From','<br>From')
            bus_route = bus_route.replace('Take','<br>Take')
            bus_route = '<br>'.join(bus_route.split('<br>')[1:])
        else:
            bus_route = ''
        return bus_route

    def get_stage_id(self, all_stages, stage_req):
        stage_resp = {}
        stage_resp['stage_req'] = stage_req
        stage_resp['found'] = False
        stage_resp['stage_id'] = None
        stage_resp['suggestions'] = []

        if stage_req in all_stages.keys():
            stage_resp['found'] = True
            stage_resp['stage_id'] = all_stages[stage_req]
        else:
            suggestions = [x for x in all_stages.keys() if x.startswith(stage_req)]
            stage_resp['suggestions'] = suggestions
        if len(stage_resp['suggestions']) == 1:
            stage_resp['found'] = True
            stage_resp['stage_id'] = all_stages[stage_resp['suggestions'][0]]
            stage_resp['stage_req'] = stage_resp['suggestions'][0]
        
        return stage_resp


application = webapp2.WSGIApplication([
    ('/getpath', MainPage)
], debug=True)

