#!/usr/bin/python
# encoding=utf8

import mysql.connector
import sys
import pytz
import time
import gzip
import csv

from datetime import datetime, timedelta
from pytz import timezone

reload(sys)
sys.setdefaultencoding('utf8')

file_fmt = '%Y-%m-%d'

def fetchData(cur, woeid, timestamp, end_timestamp):
    # Use all the SQL you like
    params = {'woeid': woeid, 'start': timestamp, 'end': end_timestamp}
    cur.execute("""
        SELECT name, SUM(duration) FROM trends
        WHERE woeid = %(woeid)s
        AND timestamp >= %(start)s
        AND timestamp < %(end)s
        GROUP BY name
        ORDER BY SUM(duration) DESC""", params)

    return cur.fetchall()


def createCsvFile(data, woeid, loc_dt):
    filename = '/home/mustilica/tthistory_backup/csvBucket/woeid-%d/%s.csv.gz' % (
        woeid, loc_dt.strftime(file_fmt))

    # Print all the first cell of all the rows
    trends = [{
        'name': row[0],
        'duration': row[1],
        'volume': -1
    } for row in data]

    #write(sorted(trends, key=lambda x: x['duration'], reverse=True), filename)
    write(trends, filename)

def write(data, filename):
    fieldnames = ['name', 'duration', 'volume']
    with gzip.open(filename, 'w') as f:
        csvWriter = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_NONNUMERIC,
            quotechar='"')
        csvWriter.writeheader()
        for obj in data:
            csvWriter.writerow(dict((k, v) for k, v in obj.iteritems()))

# Connect to db
db = mysql.connector.connect(
    user='root', password='5tonnane', host='127.0.0.1', database='tthistory')

try:
    # It will let you execute all the queries you need.
    cur = db.cursor()

    for woeid in [23424969]: #[1, 23424969]
        # Init date and time values
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        timezoneData = timezone('Europe/Istanbul' if woeid == 23424969 else 'UTC')
        loc_dt = timezoneData.localize(datetime(2013, 7, 12, 0, 0, 0))
        timestamp = int(time.mktime(loc_dt.timetuple()))

        while timestamp < 1478974943:
            print(loc_dt.strftime(fmt))
            end_loc_dt = timezoneData.normalize(loc_dt + timedelta(days=1))
            end_timestamp = int(time.mktime(end_loc_dt.timetuple()))

            data = fetchData(cur, woeid, timestamp, end_timestamp)
            createCsvFile(data, woeid, loc_dt)

            loc_dt = end_loc_dt
            timestamp = end_timestamp

finally:
    db.close()
