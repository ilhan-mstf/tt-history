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

import layer_cache
from globals import Globals


class RateLimitManager(object):
    def __init__(self):
        self.rateLimits = self.getRateLimits(key="rate-limits")

    @layer_cache.cache(
        layer=Globals.DUAL_LAYER_MEMCACHE_AND_IN_APP_MEMORY_CACHE,
        expiration=Globals._1_DAY)
    def getRateLimits(self, key=""):
        return {}

    @layer_cache.cache(
        layer=Globals.DUAL_LAYER_MEMCACHE_AND_IN_APP_MEMORY_CACHE,
        expiration=Globals._1_DAY,
        bust_cache=True)
    def setRateLimits(self, rateLimits, key=""):
        return rateLimits

    def getRateValue(self, key):
        if key not in self.rateLimits:
            return None
        return self.rateLimits[key]

    def setRateValue(self, rate, key):
        self.rateLimits[key] = rate
        self.setRateLimits(self.rateLimits, key="rate-limits")

    def checkRateLimit(self, ip):
        rate = self.getRateValue(ip)
        if rate is None:
            self.setRateValue(1, ip)
            return True
        else:
            if rate > Globals.MAX_REQUESTS:
                return False
            else:
                rate += 1
                self.setRateValue(rate, ip)
        return True
