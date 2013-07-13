# coding=utf-8
from globals import Globals
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from model import getTrends, getLastestTrends, mergeAndSortTrends
import json
import logging
import os
import traceback

class MainPage(webapp.RequestHandler):
    """ Renders the main template. """
    
    def get(self):
        
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


class RPCHandler(webapp.RequestHandler):
    """ Handles the RemoteProcedureCall requests. """
    
    def get(self):
        
        try:
            # Read paremeters
            history = self.request.get('history')  # history = ['ld', 'lw', 'lm'] last day, last week, last month
            woeid = self.request.get('woeid')
            timestamp = self.request.get('timestamp')
            endTimestamp = self.request.get('end_timestamp')
            limit = self.request.get('limit')
            
            # Init variables
            if endTimestamp is "":
                endTimestamp = "0"
            expireTime = Globals._10_MINUTES
            cacheMissed = False
            key = 'result-' + history + "-" + woeid + "-" + timestamp + "-" + endTimestamp + "-" + limit
            
            # Check cache
            trends = memcache.get(key)  # @UndefinedVariable
            
            if trends is None:
                # Cache miss
                logging.info("result cache missed")
                cacheMissed = True
                if history is "":
                    expireTime = Globals._1_DAY
                    trends = getTrends(int(woeid), int(timestamp), int(endTimestamp))
                else:
                    trends = getLastestTrends(history, int(woeid))
                
                # Merge and sort trends
                if limit is "":
                    trends = mergeAndSortTrends(trends)
                else:
                    trends = mergeAndSortTrends(trends)[:int(limit)]
                
            else:
                # Cache hit
                logging.info("cache hit")
            
            # If cache missed, write value to cache
            if cacheMissed and not memcache.set(key=key, value=trends, time=expireTime):  # @UndefinedVariable
                logging.error("Memcache set failed at trends-%s-%s-%s-%s-%s", history, woeid, timestamp, endTimestamp, limit)
            
            # Preapare json response
            results = []
            for t in trends:
                results.append({"name":t.name, "value":t.time})
            
            self.response.out.write(json.dumps({"trends":results}))
        
        except Exception, e:
            traceback.print_exc()
            self.response.out.write(json.dumps({"error":str(e)}))

application = webapp.WSGIApplication([('/rpc', RPCHandler),
                                      ('/.*', MainPage)], debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
