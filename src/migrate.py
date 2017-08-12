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

from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from globals import Globals
from model import Trend, TrendWindow

import logging
import math
import time


class Migrate(webapp.RequestHandler):
    """  """

    def get(self):
        logging.info("Migration starting...")

        if self.request.get('v') == '3':
            self.toV3()

        logging.info("Migration finished.")

    def toV3(self):
        """ In this migration, only daily summary of trends are stored.
        Therefore, there is no need to store trends fetched in 10 minutes.
        To switch this version, this code moves last days trends to temp trend
        entity. """

        q_futures = []
        entityList = []
        for trend in self.getTrendsFromDatastore():
            entityList.append(
                TrendWindow(
                    name=trend.name,
                    woeid=trend.woeid,
                    timestamp=trend.timestamp,
                    time=trend.time,
                    volume=trend.volume))

        q_futures.extend(ndb.put_multi_async(entityList))
        ndb.Future.wait_all(q_futures)

    def getTrendsFromDatastore(self):
        q_futures = []
        endTimestamp = int(math.floor(time.time()))
        startTimestamp = endTimestamp - Globals._1_DAY
        for region in Globals.REGIONS:
            q_futures.extend(
                self.requestTrendsFromDatastore({
                    'name': '',
                    'history': 'ld',
                    'woeid': str(region),
                    'startTimestamp': startTimestamp,
                    'endTimestamp': endTimestamp,
                    'limit': ''
                }))

        trends = []
        for f in q_futures:
            trends.extend(f.get_result())

        return trends

    def requestTrendsFromDatastore(self, prms):
        """ Requests request to datastore and returns request objects. """

        prms['endTimestamp'] = int(prms['endTimestamp'])
        prms['startTimestamp'] = int(prms['startTimestamp'])

        if prms['endTimestamp'] == 0:
            prms['endTimestamp'] = prms['startTimestamp'] + Globals._10_MINUTES

        # split up timestamp space into {ts_intervals} equal parts and async
        # query each of them
        ts_intervals = 24
        ts_delta = (
            prms['endTimestamp'] - prms['startTimestamp']) / ts_intervals
        cur_start_time = prms['startTimestamp']
        q_futures = []

        for x in range(ts_intervals):
            cur_end_time = (cur_start_time + ts_delta)
            if x == (ts_intervals - 1):  # Last one has to cover full range
                cur_end_time = prms['endTimestamp']

            q_futures.append(
                Trend.query(Trend.timestamp >= cur_start_time,
                            Trend.timestamp < cur_end_time,
                            Trend.woeid == int(prms['woeid']))
                .order(-Trend.timestamp)
                .fetch_async(limit=None))
            cur_start_time = cur_end_time

        return q_futures


application = webapp.WSGIApplication([('/migrate', Migrate)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
