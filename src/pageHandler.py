# coding=utf-8

"""
The MIT License

Copyright (c) 2013 Mustafa İlhan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

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
