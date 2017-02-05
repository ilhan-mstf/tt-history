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

from collections import defaultdict
from globals import Globals
from model import Trend

import logging
import math
import time
import layer_cache
import cachepy


class TrendManager(object):

    def getResultTrends(self, prms):
        logging.info("getResultTrends()")

        expiration = Globals._10_MINUTES
        layer = Globals.DUAL_LAYER_MEMCACHE_AND_IN_APP_MEMORY_CACHE
        key = "result-" + prms['history'] + "-" + prms['woeid'] + "-" + prms[
            'startTimestamp'] + "-" + prms['endTimestamp'] + "-" + prms['limit']

        if prms['history'] is "":
            # specific day
            expiration = Globals._1_WEEK
            layer = Globals.SINGLE_LAYER_MEMCACHE_ONLY

        trends = self.calculateResultTrends(
            prms, key=key, layer=layer, expiration=expiration)

        if prms['limit'] is not "":
            trends = trends[:int(prms['limit'])]

        logging.info(cachepy.stats())
        return trends

    @layer_cache.cache(
        layer=Globals.DUAL_LAYER_MEMCACHE_AND_IN_APP_MEMORY_CACHE,
        expiration=Globals._1_DAY,
        bust_cache=True)
    def setResultTrends(self, trends, key=""):
        logging.info("setResultTrends()")
        return trends

    def updateResultTrends(self, trends, key):
        logging.info("updateResultTrends()")
        self.setResultTrends(self.groupSumAndSortTrends(trends), key=key)

    @layer_cache.cache()
    def calculateResultTrends(
            self,
            prms,
            key="",
            layer=Globals.DUAL_LAYER_MEMCACHE_AND_IN_APP_MEMORY_CACHE,
            expiration=Globals._10_MINUTES):
        logging.info("calculateResultTrends()")
        trends = []
        if prms['history'] is "":
            trends = self.getTrendsFromDatastore(prms)
        else:
            trends = self.getLastestTrends(prms)

        # Merge and sort trends
        return self.groupSumAndSortTrends(trends)

    @layer_cache.cache(
        layer=Globals.DUAL_LAYER_MEMCACHE_AND_IN_APP_MEMORY_CACHE,
        expiration=Globals._1_DAY)
    def getRawTrends(self, key=""):
        logging.info("getRawTrends()")
        return []

    @layer_cache.cache(
        layer=Globals.DUAL_LAYER_MEMCACHE_AND_IN_APP_MEMORY_CACHE,
        expiration=Globals._1_DAY,
        bust_cache=True)
    def setRawTrends(self, trends, key=""):
        logging.info("setRawTrends()")
        return trends

    def mergeSortAndSetRawTrends(self, newTrends, cachedTrends, key):
        # Merge and sort trends
        trends = sorted(
            newTrends + cachedTrends,
            key=lambda x: x['timestamp'],
            reverse=True)
        logging.info(
            "mergeSortAndSetRawTrends() key %s, cachedTrends: %s, newTrends: %s, allTrends: %s",
            key, len(cachedTrends), len(newTrends), len(trends))
        return self.setRawTrends(trends, key=key)

    def updateRawTrends(self, newTrends, key):
        logging.info("updateRawTrends()")

        # Get cached trends
        cachedTrends = self.getRawTrends(key=key)

        if len(cachedTrends) > 0:

            # Remove lastest trends
            #cachedTrends = cachedTrends[:-len(newTrends)]

            logging.info("before checking boundaries of cachedTrends: %s",
                         len(cachedTrends))

            startTimestamp = int(math.floor(time.time())) - Globals._1_DAY
            if len(cachedTrends) > 0 and cachedTrends[0][
                    'timestamp'] >= startTimestamp:
                for index, trend in enumerate(cachedTrends):
                    if trend['timestamp'] < startTimestamp:
                        cachedTrends = cachedTrends[:index]
                        break

            logging.info("after boundaries of cachedTrends checked: %s",
                         len(cachedTrends))

            self.mergeSortAndSetRawTrends(newTrends, cachedTrends, key)
            # For updateResultTrends key must be updated.
            #self.updateResultTrends(self.mergeSortAndSetRawTrends(newTrends, cachedTrends, key), key)
        else:
            logging.info("cached trends empty")

    def requestTrendsFromDatastore(self, prms):
        """ Requests request to datastore and returns request objects. """

        prms['endTimestamp'] = int(prms['endTimestamp'])
        prms['startTimestamp'] = int(prms['startTimestamp'])

        if prms['endTimestamp'] == 0:
            prms['endTimestamp'] = prms['startTimestamp'] + Globals._10_MINUTES

        # split up timestamp space into {ts_intervals} equal parts and async query each of them
        ts_intervals = 24
        ts_delta = (
            prms['endTimestamp'] - prms['startTimestamp']) / ts_intervals
        cur_start_time = prms['startTimestamp']
        q_futures = []

        for x in range(ts_intervals):
            cur_end_time = (cur_start_time + ts_delta)
            if x == (ts_intervals - 1):  # Last one has to cover full range
                cur_end_time = prms['endTimestamp']

            q_futures.append(Trend.query(Trend.timestamp >= cur_start_time,
                                         Trend.timestamp < cur_end_time,
                                         Trend.woeid == int(prms['woeid'])) \
                                  .order(-Trend.timestamp) \
                                  .fetch_async(limit=None))
            cur_start_time = cur_end_time

        return q_futures

    def collectTrendsFromDatastore(self, q_futures):
        """ Collects datastore query results. """

        # Loop through and collect results
        trends = []
        for f in q_futures:
            trends.extend(f.get_result())
        logging.info("trends collected from datastore.")

        # Serialization of entity takes too much time, therefore convert it to the dictionary
        return self.convertTrendsToDict(trends)

    def convertTrendsToDict(self, trends):
        """ Converts trend entity to dictionary. """

        return [{
            'name': trend.name,
            'timestamp': trend.timestamp,
            'duration': trend.time,
            'volume': trend.volume
        } for trend in trends]

    def getTrendsFromDatastore(self, prms):
        """ get trends on specific timestamp or between timestamps """
        logging.info("getTrendsFromDatastore()")

        return self.collectTrendsFromDatastore(
            self.requestTrendsFromDatastore(prms))

    def getLastestTrends(self, prms):
        """ get lastest trends """
        logging.info("getLastestTrends()")

        # Set start and end timestamp
        endTimestamp = int(math.floor(time.time()))
        startTimestamp = endTimestamp - Globals._1_DAY

        # Get cached trends
        key = 'trends-' + prms['history'] + "-" + str(prms['woeid'])
        cachedTrends = self.getRawTrends(key=key)

        # Check boundaries
        if len(cachedTrends) > 0 and cachedTrends[0][
                'timestamp'] >= startTimestamp:
            for index, trend in enumerate(cachedTrends):
                if trend['timestamp'] < startTimestamp:
                    cachedTrends = cachedTrends[:index]
                    break

            logging.info("end changed from: %s, to: %s", endTimestamp,
                         (cachedTrends[-1]['timestamp'] - 1))
            endTimestamp = cachedTrends[-1]['timestamp'] - 1

        # Update fields
        prms['endTimestamp'] = endTimestamp
        prms['startTimestamp'] = startTimestamp
        logging.info("start: %s, end: %s", startTimestamp, endTimestamp)

        # Not every time datastore call is required. check that start and end timestamps.
        newTrends = []
        if endTimestamp - startTimestamp > Globals._10_MINUTES:
            # Get new trends from datastore
            newTrends = self.getTrendsFromDatastore(prms)

        return self.mergeSortAndSetRawTrends(newTrends, cachedTrends, key)

    def groupSumAndSortTrends(self, trends):
        logging.info("groupSumAndSortTrends()")

        durationSum = defaultdict(int)
        for trend in trends:
            durationSum[trend['name']] += trend['duration']

        maxVolume = defaultdict(int)
        for trend in trends:
            if maxVolume[trend['name']] is None or maxVolume[trend[
                    'name']] < trend['volume']:
                maxVolume[trend['name']] = trend['volume']

        trends = [{
            'name': key,
            'duration': value,
            'volume': maxVolume[key]
        } for key, value in durationSum.items()]
        return sorted(trends, key=lambda x: x['duration'], reverse=True)

    def getResultsTrendByName(self, prms):
        trends = []
        offset = 0

        while True:
            fetchedTrends = Trend.query(Trend.name == prms['name']).fetch(
                limit=100, offset=offset)
            trends.extend(fetchedTrends)
            if len(fetchedTrends) != 100:
                break
            offset += 100

        return self.convertTrendsToDict(trends)
