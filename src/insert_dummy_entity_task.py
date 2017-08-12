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

import logging
import time
import traceback

from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from model import TrendWindow
from globals import Globals


class InsertDummyEntityTask(webapp.RequestHandler):
    """ insert dummy entities """

    def get(self):
        if "localhost" not in self.request.url:
            return

        logging.info("InsertDummyEntityTask starting...")

        dummyVals = [{
            'name': 'mustilica',
            'time': 300,
            'tweet_volume': 45225
        }, {
            'name': 'freebird',
            'time': 30,
            'tweet_volume': 225
        }, {
            'name': 'flyingbird',
            'time': 240,
            'tweet_volume': 5225
        }, {
            'name': 'bahattin abi',
            'time': 80,
            'tweet_volume': 85
        }, {
            'name': '#ThisIsSparta',
            'time': 320,
            'tweet_volume': 231198
        }]

        q_futures = []
        for region in Globals.REGIONS:
            try:
                # get current timestamp in seconds
                timestamp = int(time.time())
                # put trends to db
                entityList = []
                for trend in dummyVals:
                    entityList.append(
                        TrendWindow(
                            name=trend['name'],
                            woeid=region,
                            timestamp=timestamp,
                            time=trend['time'],
                            volume=trend['tweet_volume']))
                q_futures.extend(ndb.put_multi_async(entityList))

                # wait all async put operations to finish.
                ndb.Future.wait_all(q_futures)
            except Exception, e:
                traceback.print_exc()

    logging.info("InsertDummyEntityTask finished.")


application = webapp.WSGIApplication(
    [('/tasks/insertDummyEntity', InsertDummyEntityTask)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
