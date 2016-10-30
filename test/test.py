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

"""
Test to meausure the performance of merging and sorting trends 
with two different code.
"""

from collections import defaultdict
import time

def mergeAndSortTrends(trends):
    mergedList = []
    for t in trends:
        found = False
        for m in mergedList:
            if t.name == m.name:
                m.time += t.time
                found = True
                break
        if not found:
            mergedList.append(t)
    
    mergedList = sorted(mergedList, key=lambda trend: trend.time, reverse=True)
    results = []
    for t in mergedList:
        results.append({"name":t.name, "value":t.time}) 
    return results

def groupSumAndSortTrends(trends):
    totals = defaultdict(int)
    for trend in trends:
        totals[trend.name] += trend.time
    trends = [{'name':key,'value':value} for key,value in totals.items()]
    return sorted(trends, key=lambda x: x['value'], reverse=True)

class Trend:
    def __init__(self, name, time):
        self.name = name
        self.time = time
        
# Test starts
trends = []
for i in range(1000000):
    trends.append(Trend(str(i%100), i))

start_time = time.time()
# Method 1
trends = groupSumAndSortTrends(trends)
# Method 2
#trends = mergeAndSortTrends(trends)
print("--- %s seconds ---" % (time.time() - start_time))

print trends

