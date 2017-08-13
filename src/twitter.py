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

import json
import oauth2 as oauth
import time
import traceback


class TwitterApi(object):
    def __init__(self, consumer_key, consumer_secret, access_token_key,
                 access_token_secret):
        self.base_url = 'https://api.twitter.com/1.1'
        self.client = self.createClient(consumer_key, consumer_secret,
                                        access_token_key, access_token_secret)

    def createClient(self, consumer_key, consumer_secret, access_token_key,
                     access_token_secret):
        consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        token = oauth.Token(key=access_token_key, secret=access_token_secret)
        return oauth.Client(consumer, token)

    def apiRequest(self,
                   url,
                   http_method="GET",
                   post_body="",
                   http_headers=None,
                   retry=True):
        try:
            resp, content = self.client.request(
                url, method=http_method, body=post_body, headers=http_headers)
            return content
        except Exception, e:
            if retry:
                traceback.print_exc()
                time.sleep(1)
                return self.apiRequest(url, http_method, post_body,
                                       http_headers, False)
            else:
                raise Exception(e)

    def getTrendsByWoeid(self, woeid):
        url = '%s/trends/place.json?id=%d' % (self.base_url, woeid)
        data = self.apiRequest(url)
        data = self.parseAndCheckTwitterResponse(data)
        return data[0]['trends']

        # Test for error case.
        #return self.parseAndCheckTwitterResponse("{'error':'<title>Twitter / Error</title>'}")

    def parseAndCheckTwitterResponse(self, data):
        """Try and parse the JSON returned from Twitter and return
        an empty dictionary if there is any error.

        This is a purely defensive check because during some Twitter
        network outages it will return an HTML failwhale page.

        retrieved from: https://github.com/bear/python-twitter
        """
        try:
            data = json.loads(data)
            self.checkForTwitterError(data)
        except ValueError as v_e:
            if "<title>Twitter / Over capacity</title>" in data:
                raise ValueError("Twitter Capacity Error")
            if "<title>Twitter / Error</title>" in data:
                raise ValueError("Twitter Technical Error")
            if "Exceeded connection limit for user" in data:
                raise ValueError("Twitter Exceeded connection limit for user")
            raise ValueError(v_e)

        return data

    def checkForTwitterError(self, data):
        """Raises a ValueError if twitter returns an error message.

        Args:
          data:
            A python dict created from the Twitter json response

        Raises:
          ValueError wrapping the twitter error message if one exists.

        retrieved from: https://github.com/bear/python-twitter
        """
        # Twitter errors are relatively unlikely, so it is faster
        # to check first, rather than try and catch the exception
        if 'error' in data:
            raise ValueError(data['error'])
        if 'errors' in data:
            raise ValueError(data['errors'])
