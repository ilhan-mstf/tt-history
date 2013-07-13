# coding=utf-8
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from model import Trend, Error
from globals import Globals
import logging
import math
import time
import traceback
import twitter

def getAndPutTrends(woeid):
    try:
        # authenticate
        client = twitter.Api(consumer_key=Globals.CONSUMER_KEY,
                             consumer_secret=Globals.CONSUMER_SECRET,
                             access_token_key=Globals.CLIENT_TOKEN,
                             access_token_secret=Globals.CLIENT_SECRET,
                             cache=None)
        # make request
        response = client.GetTrendsWoeid(id=woeid)
        # get current timestamp in seconds
        timestamp = int(math.floor(time.time()))
        # put trends to db
        for trend in response:
            Trend(name=trend.name, woeid=woeid, timestamp=timestamp, time=10).put()
    except Exception, e:
        traceback.print_exc()
        Error(msg=str(e), timestamp=timestamp).put()

class Cron(webapp.RequestHandler):
    """makes twitter api call, inserts trends to db """

    def get(self):
        logging.info("Cron starting...")
        for region in Globals.REGIONS:
            getAndPutTrends(region)
        logging.info("Cron finished.")

application = webapp.WSGIApplication([('/cron', Cron)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
