tt-history
==========

A project that keeps history of trending topics of Twitter.


Every 10 minutes trending topics are fetched from twitter.com and stored on the database and later represented in a visual way.


This data visualization project done as a side project.

 
Credits:
- runs on Google App Engine <https://developers.google.com/appengine/>
- Python-Twitter <https://code.google.com/p/python-twitter/> (for Twitter api)
- jQuery <http://jquery.com/>
- D3.js <http://d3js.org> (for visualization)
- <https://github.com/tobiasahlin/SpinKit> (for loading animation, underline animation)
- tipsy <https://github.com/jaz303/tipsy> (for tooltips)


TODOs:
- Add different visualizations.
- Copy datastore to BigQuery and analyze data
- Add search.
- Look at push-to-deploy. (https://cloud.google.com/tools/repo/push-to-deploy)