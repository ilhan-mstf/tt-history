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

import json
import os
import traceback
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from trend_manager import TrendManager
from rate_limit_manager import RateLimitManager


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
            # Check request ip
            if "localhost" not in self.request.url and not RateLimitManager().checkRateLimit(self.request.remote_addr):
                logging.warning("Remote user has exceed limits; rejecting. %s" %
                                self.request.remote_addr)
                self.error(503)
                return

            # Read and set paremeters
            prms = {
                'name': self.request.get('name'),
                'history': self.request.get('history'),  # history = ['ld'] last day
                'woeid': self.request.get('woeid'),
                'startTimestamp': self.request.get('timestamp'),
                'endTimestamp': self.request.get('end_timestamp', '0'),
                'limit': self.request.get('limit')
            }

            # Get trends
            if prms['name'] is not "":
                trends = TrendManager().getResultsTrendByName(prms)
            else:
                trends = TrendManager().getResultTrends(prms)

            # Set response in json format
            self.response.out.write(json.dumps({"trends": trends}))

        except Exception, e:
            traceback.print_exc()
            self.response.out.write(json.dumps({"error": str(e)}))


application = webapp.WSGIApplication(
    [('/rpc', RPCHandler), ('/.*', MainPage)], debug=False)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
