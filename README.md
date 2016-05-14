Trending Topic History (tt-history)
===================================

This project has stored the trending topics on Twitter since July 2013. Specifically stored trending topics and hashtags are the ones that appeared in the regions: Turkey and World Wide. Every 10 minutes trending topics are fetched via Twitter API and stored on the database. Website of this project visually shows trending topics in terms of how much time they appeared on the list of Twitter.

Motivations:
------------
Twitter shows us only current trending topics with their volume information like 11.7K tweets in last hour. However, one year ago at 12:00 PM what are the trending topics? How many time people continue to talk about that topic? What is the -average, min, max- life time of a trending topic? What is the relationship between the volume and duration of a topic? How do they change in terms of region? These questions are some them that motivates me to build this project. Further, It draws the attention of other researchers around the world and they request me the collected data by this project. It already used in one research project, others in progress.

Limitations:
------------
Although collecting trending topics of every region is a trivial job, it is not preferred because of these two problems:
1. Twitter API has a request rate limit. Therefore, it does not allow to make too many requests in a specified time frame. Fetching every region's trending topics result in rate limit exceed.
2. It increases the datastore write costs and bills on Google App Engine. This project has not any income(Now I started to accept donation via website to keep running the website). Therefore, keeping bills low is more preferrable.

Because of this two limitation, only Turkey and World Wide is selected to collect trending topics. One of them is Turkey because it is my hometown. Another one is World Wide in order to offer common trending topics to the visitors of the website.

Credits:
--------
- Google App Engine <https://developers.google.com/appengine/> (for hosting and datastore)
- Python-Twitter <https://code.google.com/p/python-twitter/> (for Twitter API)
- jQuery <http://jquery.com/> (for building web ui)
- D3.js <http://d3js.org> (for visualization)
- <https://github.com/tobiasahlin/SpinKit> (for loading animation and underlining animation)
- tipsy <https://github.com/jaz303/tipsy> (for tooltips)
