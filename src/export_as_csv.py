# Run from GAE remote API:
# 	{GAE Path}\remote_api_shell.py -s {YourAPPName}.appspot.com
# 	import export_as_csv

import csv
from google.appengine.ext import db
from google.appengine.ext.db import GqlQuery


def exportToCsv(query, csvFileName, delimiter):
    with open(csvFileName, 'wb') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=delimiter,
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writeHeader(csvWriter)

        rowsPerQuery = 1000
        totalRowsSaved = 0
        cursor = None
        areMoreRows = True

        while areMoreRows:
            if cursor is not None:
                query.with_cursor(cursor)
            items = query.fetch(rowsPerQuery)
            cursor = query.cursor()

            currentRows = 0
            for item in items:
                saveItem(csvWriter, item)
                currentRows += 1

            totalRowsSaved += currentRows
            areMoreRows = currentRows >= rowsPerQuery
            print 'Saved ' + str(totalRowsSaved) + ' rows'

        print 'Finished saving all rows.'


def writeHeader(csvWriter):
        # Output csv header
    csvWriter.writerow(['hashtag', 'region', 'timestamp',
                        'duration (in minutes)'])


def saveItem(csvWriter, item):
    # Save items in preferred format
    csvWriter.writerow([item.name, item.woeid, item.timestamp, item.time])


class Trend(db.Model):
    name = db.StringProperty()
    woeid = db.IntegerProperty()
    timestamp = db.IntegerProperty()
    time = db.IntegerProperty()


# Query for items
query = GqlQuery("SELECT * FROM Trend WHERE name = '#JeSuisCharlie'")
exportToCsv(query, '/home/mustilica/remote.csv', ',')
