#!/usr/bin/python
# encoding=utf8

import csv
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append(
    '/home/mustilica/ProgramFiles/google-cloud-sdk/platform/google_appengine')

from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.appengine.api import datastore

files = ['output-' + ` i ` for i in range(185)]

with open("all.csv", 'w') as csvfile:
    writer = csv.DictWriter(
        csvfile,
        fieldnames=['woeid', 'time', 'name', 'timestamp'],
        quoting=csv.QUOTE_NONNUMERIC,
        quotechar='"')
    writer.writeheader()

    for f in files:
        raw = open(f, 'r')
        try:
            reader = records.RecordsReader(raw)
            for record in reader:
                entity_proto = entity_pb.EntityProto(contents=record)
                entity = datastore.Entity.FromPb(entity_proto)
                writer.writerow(dict((k, v) for k, v in entity.iteritems()))
            print f, "completed."
        finally:
            raw.close()
