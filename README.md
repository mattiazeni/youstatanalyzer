YOUStatAnalyzer
===============

YOUStatAnalyzer is a tool written in Python able to capture the popularity metrics of YouTube's videos. Since in June 2013 YouTube removed the API that allowed to retrieve the statistics available below each video, we needed to find a new way of obtain those kind of data. The result is this piece of software that allows to automatically and in a fast way to download YouTube's videos statistics with the final purpose of creating a dataset for analysis. In order to extract these data from YouTube, the tool obtains a session token that is later used for making the request to YouTube's servers. Once the data have been downloaded thay are parsed in order to save them in a known format inside a MongoDB Server.

## Dependencies and Libraries

The Libraries we are using within YOUStatAnalyzer are listed below:

- urllib2
- cookielib
- parse and parseString from xml.dom.minidom
- re
- BeautifulSoup from bs4
- MongoClient from pymongo
- random
- linecache

In order to get YOUStatAnalyzer to work you need to have those libraries installed in your system.

## Usage

The software is very easy to use, just need to configure it and run.

To run it use the command: ```python youtube_script.py config.xml``` where config.xml is of course the configuration file. The tool will automatically read it and react accordingly.

## The Database

As database system we used MongoDB through the pymongo library. If you are not confortable with it you can just replace the only functions that interacts with the database: ```insertEntry()``` in functions.py:

```
def insertEntry(video):
	try:
		client = MongoClient(getServerIp(), getServerPort())
		db = client[getServerDB()][getServerCollection()]
		db.insert(video)
	except pymongo.errors.DuplicateKeyError:
		print 'Insert Error: Duplicate'
		pass
```

This function takes as argument the dictionary containing all the information about the video that needs to be inserted into the database. In particular, this function creates an Instance of MongoClient with the IP and Port of the Server. Then Creates an instance of the database with Database Name and Collection Name and in the end inserts the dictionary. We surrounded it with ```try...catch``` to avoid duplicates: if a duplicated _id occurs, the script throws a ```DuplicateKeyError``` exception.

Tha database contains 1006469 videos for 31488523593bytes.

### The Data Structure

