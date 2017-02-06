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
import logging
import time
import traceback
import os

from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import app_identity
from globals import Globals
from model import Error
from model import TrendSummary
from trend_manager import TrendManager
from data_model_converter import DataModelConverter
from csv_utils import CsvUtils
from cloud_storage_utils import CloudStorageUtils
from timezone_aware_date import TimezoneAwareDate
from send_email import SendEmail


class SummaryTask(webapp.RequestHandler):
    """ saves daily summary of trends as a file to the google cloud storage and datastore. """

    def get(self):
        logging.info("SummaryTask starting...")

        # init class and variables
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name
        trendManager = TrendManager()
        dataModelConverter = DataModelConverter()
        csvUtils = CsvUtils()
        cloudStorageUtils = CloudStorageUtils()

        q_futures = []
        for region in self.getRegions():
            try:
                date = TimezoneAwareDate(region)
                trendsJson = self.getTrends(region, trendManager)
                self.saveToCloudStorage(dataModelConverter, csvUtils,
                                        cloudStorageUtils, trendsJson, region,
                                        bucket, date)
                self.saveToDatastore(q_futures, trendsJson, region, date)

                # TODO delete previous data

            except Exception, e:
                traceback.print_exc()
                Error(msg=str(e), timestamp=int(time.time())).put()
                SendEmail().send('Error on GetTrendsTask', str(e))

        # wait all async put operations to finish.
        ndb.Future.wait_all(q_futures)

        logging.info("SummaryTask finished.")

    def getRegions(self):
        regions = []
        woeid = self.request.get('woeid')
        if woeid is not "":
            regions.append(int(woeid))
        else:
            regions = Globals.REGIONS
        return regions

    def getTrends(self, region, trendManager):
        return trendManager.getResultTrends({
            'name': '',
            'history': 'ld',
            'woeid': str(region),
            'startTimestamp': '',
            'endTimestamp': '',
            'limit': ''
        })

    def saveToCloudStorage(self, dataModelConverter, csvUtils,
                           cloudStorageUtils, trendsJson, woeid, bucket, date):
        processedJson = dataModelConverter.preProcessForCsvFile(trendsJson)
        csvData = csvUtils.jsonToCsv(processedJson)
        filename = "woeid-%d/%s.csv.gz" % (woeid, date.getDate())
        fullPath = "%s/daily_summary/%s" % (bucket, filename)
        cloudStorageUtils.writeFile(csvData, fullPath)

    def saveToDatastore(self, q_futures, trends, woeid, date):
        entityList = []
        for trend in trends:
            entityList.append(
                TrendSummary(
                    name=trend['name'],
                    woeid=woeid,
                    date=date.getDate(),
                    duration=trend['duration'],
                    volume=trend['volume']))
        q_futures.extend(ndb.put_multi_async(entityList))


application = webapp.WSGIApplication(
    [('/tasks/summary', SummaryTask)], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == "__main__":
    main()
