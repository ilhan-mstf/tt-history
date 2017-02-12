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

import time
import traceback
import json

from google.appengine.api import urlfetch
from credentials import Crenditals
from model import Error


class TimezoneAwareDate(object):
    def __init__(self, woeid):
        self.timezone = self.getTimezoneInfo(woeid)
        self.rpc = self.requestDateInfo()
        self.date = ''

    def getTimezoneInfo(self, woeid):
        return {23424969: 'Europe/Istanbul'}.get(woeid, 'UTC')

    def requestDateInfo(self):
        rpc = urlfetch.create_rpc()
        urlfetch.make_fetch_call(
            rpc,
            'http://api.timezonedb.com/v2/get-time-zone?key=%s&format=json&by=zone&zone=%s'
            % (Crenditals.TIMEZONEDB_API_KEY, self.timezone))
        return rpc

    def readDateInfo(self):
        try:
            result = self.rpc.get_result()
            if result.status_code == 200:
                data = result.content
                jsonData = json.loads(data)
                return jsonData['formatted'].split()[0]
            else:
                SendEmail().send('Error on TimezoneAwareDate',
                                 'Timezonedb api request error.')
        except Exception, e:
            traceback.print_exc()
            Error(msg=str(e), timestamp=int(time.time())).put()
            SendEmail().send('Error on TimezoneAwareDate', str(e))

        return time.strftime('%Y-%m-%d')

    def getDate(self):
        if self.date is '':
            self.date = self.readDateInfo()
        return self.date
