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
from model import Trend, Error
from globals import Globals
from credentials import Crenditals
from trend_manager import TrendManager
from twitter import TwitterApi
from send_email import SendEmail
from google.appengine.api import taskqueue


class GetTrendsTask(webapp.RequestHandler):
    """ makes twitter api call, inserts trends to db """

    def get(self):
        logging.info("GetTrendsTask starting...")

        try:
            # create twitter client
            client = TwitterApi(
                consumer_key=Crenditals.CONSUMER_KEY,
                consumer_secret=Crenditals.CONSUMER_SECRET,
                access_token_key=Crenditals.CLIENT_TOKEN,
                access_token_secret=Crenditals.CLIENT_SECRET)

            q_futures = []
            for region in Globals.REGIONS:
                # request trends from twitter
                response = client.getTrendsByWoeid(woeid=region)
                # get current timestamp in seconds
                timestamp = int(time.time())
                # put trends to db
                entityList = []
                for trend in response:
                    entityList.append(
                        Trend(
                            name=trend['name'],
                            woeid=region,
                            timestamp=timestamp,
                            time=10,
                            volume=trend['tweet_volume']))
                q_futures.extend(ndb.put_multi_async(entityList))
                self.updateCacheValues(region, entityList)

            # wait all async put operations to finish.
            ndb.Future.wait_all(q_futures)
        except ValueError as v_e:
            logging.error(v_e)
            self.retry()
        except Exception, e:
            traceback.print_exc()
            Error(msg=str(e), timestamp=int(time.time())).put()
            SendEmail().send('Error on GetTrendsTask', str(e))
            self.retry()

        logging.info("GetTrendsTask finished.")

    def updateCacheValues(self, region, entityList):
        logging.info("updateCacheValues()")
        trendManager = TrendManager()
        trendManager.updateRawTrends(
            trendManager.convertTrendsToDict(entityList),
            "trends-ld-" + str(region))

    # Retry
    def retry(self):
        logging.info('Running task queue for getTrends')
        taskqueue.add(url='/tasks/getTrends')


application = webapp.WSGIApplication(
    [('/tasks/getTrends', GetTrendsTask)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
