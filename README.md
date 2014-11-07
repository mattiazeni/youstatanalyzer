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

As database system we used MongoDB through the pymongo library. If you are not confortable with it you can just replace the only functions that interacts with the database: ```insertEntry()``` in functions.py

### The Data Structure

