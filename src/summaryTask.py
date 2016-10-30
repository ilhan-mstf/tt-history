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

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from model import Error
from globals import Globals
from google.appengine.api import urlfetch
from google.appengine.api import app_identity
import cloudstorage as gcs
import os
import logging
import math
import time
import traceback

class SummaryTask(webapp.RequestHandler):
    """ saves daily summary of trends as a file to the google cloud storage """

    def get(self):
        logging.info("SummaryTask starting...")

        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name

        for region in Globals.REGIONS:
            try:
                #url = "http://localhost:8080/rpc?woeid=%d&history=ld" % region
                url = "http://tt-history.appspot.com/rpc?woeid=%d&history=ld" % region
                result = urlfetch.fetch(url)
                if result.status_code == 200:
                    filename = "woeid-%d/%s.json" % (region, time.strftime("%Y-%m-%d"))
                    fullPath = "%s/daily_summary/%s" % (bucket, filename)
                    self.writeToCloudStorage(result.content, fullPath)
                else:
                    logging.error("SummaryTask failed for region: %d" % region)
            except Exception, e:
                traceback.print_exc()
                Error(msg=str(e), timestamp=int(math.floor(time.time()))).put()

        logging.info("SummaryTask finished.")

    #[START write]
    def writeToCloudStorage(self, data, filename):
        """Create a file.
        The retry_params specified in the open call will override the default
        retry params for this particular file handle.
        Args:
          filename: filename.
        """
        logging.info("Creating file %s" % filename)

        gcs_file = gcs.open(filename,
                            'w',
                            content_type='text/plain',
                            retry_params=gcs.RetryParams(backoff_factor=1.1))
        gcs_file.write(data)
        gcs_file.close()
    #[END write]

application = webapp.WSGIApplication([('/tasks/summary', SummaryTask)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
