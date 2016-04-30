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

class Globals:
    _1_DAY = 86400  # 24 * 60 * 60 seconds
    _1_WEEK = 604800  # 7 * 24 * 60 * 60 seconds
    _1_MONTH = 2592000  # 30 * 24 * 60 * 60 seconds
    _10_MINUTES = 600  # seconds

    DEFAULT_LIMIT = 5

    MAX_REQUESTS = 5

    REGIONS = [23424969, 1]  # regions = [('tr', '23424969'), ('usa', '23424977'), ('world', '1')]

    DUAL_LAYER_MEMCACHE_AND_IN_APP_MEMORY_CACHE = 0 # Cache in both memcache and cachepy by default
    SINGLE_LAYER_MEMCACHE_ONLY = 1
    SINGLE_LAYER_IN_APP_MEMORY_CACHE_ONLY = 2
