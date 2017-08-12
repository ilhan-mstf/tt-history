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


# Old version's trend storage table. It is very huge. To reduce the costs,
# project switches to window and summary based approaches.
class Trend(ndb.Model):
    name = ndb.StringProperty(indexed=False)
    woeid = ndb.IntegerProperty(indexed=True)
    timestamp = ndb.IntegerProperty(indexed=True)
    time = ndb.IntegerProperty(indexed=False)
    volume = ndb.IntegerProperty(indexed=False)


# To migrate v3 version of tthistory old (10 minutes resolution) trends
# will be deleted. Therefore, temporarily trends will be saved to this entity.
# Trends will be stored in this table for a specified window (e.g last 24 hours).
class TrendWindow(ndb.Model):
    name = ndb.StringProperty(indexed=False)
    woeid = ndb.IntegerProperty(indexed=True)
    timestamp = ndb.IntegerProperty(indexed=True)
    time = ndb.IntegerProperty(indexed=False)
    volume = ndb.IntegerProperty(indexed=False)


# Daily summary of trends.
class TrendSummary(ndb.Model):
    name = ndb.StringProperty(indexed=True)
    woeid = ndb.IntegerProperty(indexed=False)
    date = ndb.StringProperty(indexed=False)
    duration = ndb.IntegerProperty(indexed=False)
    volume = ndb.IntegerProperty(indexed=False)


class Error(ndb.Model):
    msg = ndb.StringProperty(indexed=False)
    timestamp = ndb.IntegerProperty(indexed=False)
