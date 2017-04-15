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

import cloudstorage as gcs
import gzip
import logging


class CloudStorageUtils():

    # [START writeFile]
    def writeFile(self, data, filename):
        """Create a file.
        The retry_params specified in the open call will override the default
        retry params for this particular file handle.
        Args:
          filename: filename.
        """
        logging.info("Creating file %s" % filename)

        with gcs.open(
                filename,
                'w',
                content_type='text/plain',
                options={'content-encoding': 'gzip'},
                retry_params=gcs.RetryParams(backoff_factor=1.1)) as f:
            gz = gzip.GzipFile('', 'wb', 9, f)
            gz.write(data)
            gz.close()

    # [END writeFile]

    # TODO getFile
    # http://stackoverflow.com/questions/35708725/how-to-open-gzip-file-on-gae-cloud
    # https://github.com/GoogleCloudPlatform/appengine-gcs-client/blob/master/python/test/cloudstorage_test.py
