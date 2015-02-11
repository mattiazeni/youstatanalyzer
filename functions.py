#######################################################################
# File:        functions.py
# Description: YOUStatAnalyzer script.
# Author:      Mattia Zeni
# Created:     Wed Feb 11 16:08:015 CET 2015
# E-mail:      mattia.zeni@disi.unitn.it
# University of Trento - Department of Information Engineering and Computer Science
#
# (C) Copyright 2015, Mattia Zeni
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#######################################################################

import urllib2
import cookielib
from xml.dom.minidom import parse, parseString
import re
from bs4 import BeautifulSoup
from pymongo import MongoClient
import random
import linecache
import json

HOST = 'www.youtube.com'
GDATA_HOST = 'gdata.youtube.com'
TOKEN_KEYWORD = 'account_playback_token'
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) '
      'AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/31.0.1650.57 Safari/537.36')

config_file = "config.xml"

yt_video_url = lambda vid: 'http://%s/watch?v=%s' % (HOST, vid)
yt_video_api_url= lambda vid: ('https://%s/feeds/api/videos/%s?v=2' % (GDATA_HOST, vid))
yt_related_video_url= lambda vid: ('https://%s/feeds/api/videos/%s/related?v=2' % (GDATA_HOST, vid))
yt_insights_url = lambda vid: ('https://%s/insight_ajax?action_get_statistics_and_data=1&v=%s' % (HOST, vid))
yt_gplus_url = lambda vid: ('https://plus.google.com/ripples/details?url=https://%s/watch?v=%s' % (HOST, vid))

#***************************************************************************************#
# Function: extractAttributeFromConfigFile
# Parameters: attribute
# How it works: the purpose of this function is to extract from the xml configuration
#               file the value corresponding to the passed attribute
# Return: It returns the value of the corresponding configure parameter
#***************************************************************************************#
def extractAttributeFromConfigFile (tag, attribute):
	config_parser = parse(config_file)
	for configuration in config_parser.getElementsByTagName("config"):
		for tags in configuration.getElementsByTagName(tag):
			values = tags.getAttribute(attribute)
	return values

#***************************************************************************************#
# Function: extractAttributeFromConfigFile
# Parameters: attribute
# How it works: the purpose of this function is to extract from the xml configuration
#               file the value corresponding to the passed attribute
# Return: It returns the value of the corresponding configure parameter
#***************************************************************************************#
def extractVideoIDsFromConfigFile ():
	config_parser = parse(config_file)
	for configuration in config_parser.getElementsByTagName("config"):
		for singleVideoSearch in configuration.getElementsByTagName("singlevideosearch"):
			return singleVideoSearch.getElementsByTagName("video")

#***************************************************************************************#
# Function: getServerIp
# Parameters: none
# How it works: this 2P extract the MongoDB Server IP Address from the config file
# Return: It returns the IP address of the server running MongoDB
#***************************************************************************************#
def getServerIp ():
	return extractAttributeFromConfigFile('dbconfiguration', 'ip')
	
#***************************************************************************************#
# Function: getServerPort
# Parameters: none
# How it works: this function extract the MongoDB Server port from the config file
# Return: It returns the number of the port of the server (default is 27017)
#***************************************************************************************#
def getServerPort ():
	return int(extractAttributeFromConfigFile('dbconfiguration', 'port'))

#***************************************************************************************#
# Function: getServerDB
# Parameters: none
# How it works: this function extract the MongoDB Server database name
# Return: It returns the name of the database that must be used to store the documents
#***************************************************************************************#
def getServerDB ():
	return extractAttributeFromConfigFile('dbconfiguration', 'database')

#***************************************************************************************#
# Function: getServerCollection
# Parameters: none
# How it works: this function extract the MongoDB Server collection name
# Return: It returns the name of the collection that must be used to store the documents
#***************************************************************************************#
def getServerCollection ():
	return extractAttributeFromConfigFile('dbconfiguration', 'collection')

#***************************************************************************************#
# Function: create_opener
# Parameters: none
# How it works: this function creates a custom Opener with headers information that will
#               be later used to fetch the video's webpage content
# Return: It returns the custom urllib2 Opener
#***************************************************************************************#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def create_opener(cookie_jar=None):
  if not cookie_jar:
    cookie_jar = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
  opener.addheaders = [
    ('User-Agent', UA)
  ]
  return opener

#***************************************************************************************#
# Function: fetch_video_html
# Parameters: opener, video_id
# How it works: this function extracts html code of the video's page from which we  will
#               extract the token that will be later used to get the statistics.
#               It opens the videos webpage using open() funciton on the opener created 
#               by create_opener function.
# Return: It returns the html code of the webpage of the video
#***************************************************************************************#
def fetch_video_html(opener, video_id):
  stream = opener.open(yt_video_url(video_id))
  html = stream.read()
  stream.close()
  return html

#***************************************************************************************#
# Function: fetch_video_insights
# Parameters: opener, video_id, token
# How it works: this function extracts the statistics of the video using the custom
#               opener, the ID of the video to be analyzed and the session token
# Return: It returns the simil-json containing the statistics
#***************************************************************************************#
def fetch_video_insights(opener, video_id, token):
  url = yt_insights_url(video_id)
  data = 'session_token=%s' % token
  headers = {
    'Origin': 'http://%s' % HOST,
    'Referer': yt_video_url(video_id)
  }
  req = urllib2.Request(url, data, headers, HOST)
  stream = opener.open(req)
  return stream.read()

#***************************************************************************************#
# Function: get_insight_ajax_token
# Parameters: html
# How it works: this function gets the html content of the page containing the token and
#               uses a regex to extract it. At the date we wrote this document (Nov-2014)
#               the tag containing the token was 'account_playback_token'
# Return: It returns the session token as a string
#***************************************************************************************#
def get_insight_ajax_token(html):
	m = re.search('\"'+TOKEN_KEYWORD+'\":\"(.+?)\"', html)
	if m:
		return m.group(1)

#***************************************************************************************#
# Function: extractVideoStatistics
# Parameters: videoID, data
# How it works: this function gets the html content of the page containing the statistics
#               and returned by fetch_video_insights() with the videoID and using regex
#               generates the statistics and insert the video object in MongoDB
#***************************************************************************************#
def extractVideoStatistics (videoID, data):
    
	objectListData = [map(float, elem.split(',')) for elem in re.findall(r'["]+[\w]+[\\":]+[ ]+[\[]+([\d\.\d,\s]+|[\d,\s]+|[\d,\s\d]+|[-\d\.\d,\s]+|[-\d,\s]+|[-\d,\s\d]+)+[\]]', data)]
	objectListLabels = re.findall(r'["]+[views]+[\\":]+|["]+[shares]+[\\":]+|["]+[subscribers]+[\\":]+|["]+[day]+[\\":]+|["]+[cumulative]+[\\":]+|["]+[daily]+[\\":]+|["]+[watch\-time]+[\\":]+', data)
    
   	video = {}
	singleVideo = extractVideoData(videoID)

	gplusdata = extractGplusStatistics(videoID)
	
	if len(gplusdata) > 0:
		singleVideo["gplus"]=[]
		singleVideo["gplus"]=gplusdata
	
	ii=0
	for count2 in range(0,len(objectListLabels)):
		if ('views' in objectListLabels[count2]) or ('shares' in objectListLabels[count2]) or ('subscribers' in objectListLabels[count2]) or ('watch-time' in objectListLabels[count2]):
			level1 = filter(lambda x: x.isalpha(), objectListLabels[count2])
			singleVideo[level1] = {}
		elif ('daily' in objectListLabels[count2]) or ('cumulative' in objectListLabels[count2]):
			level2 = filter(lambda x: x.isalpha(), objectListLabels[count2])
			singleVideo[level1][level2] = {}
			singleVideo[level1][level2]["data"] = objectListData[ii]
			ii += 1
		elif ('day' in objectListLabels[count2]):
			level1 = filter(lambda x: x.isalpha(), objectListLabels[count2])
			singleVideo[level1] = {}
			singleVideo[level1]["data"] = objectListData[ii]
			ii += 1

	print(json.dumps(singleVideo))
	insertEntry(singleVideo)

	return

#***************************************************************************************#
# Function: insertEntry
# Parameters: video
# How it works: this function inserts the dictionary into MongoDB
#***************************************************************************************#
def insertEntry(video):
	try:
		client = MongoClient(getServerIp(), getServerPort())
		db = client[getServerDB()][getServerCollection()]
		db.insert(video)
	except pymongo.errors.DuplicateKeyError:
		print 'Insert Error: Duplicate'
		pass

#***************************************************************************************#
# Function: extractVideoData
# Parameters: videoID
# How it works: this function extracts video's meta-data information using youtube APIs
# Return: it returns a dict conteining these information
#***************************************************************************************#
def extractVideoData(videoID):
	singleVideo = {}
	singleVideo["_id"] = videoID
	singleVideo["accessControl"] = {}
	singleVideo["relatedVideos"] = []

	s = urllib2.urlopen(yt_video_api_url(videoID))				

	videoParser = parseString(s.read())

	for published in videoParser.getElementsByTagName("published"):
		for published_sub in published.childNodes:
			singleVideo["publishedDate"] = published_sub.data
	for title in videoParser.getElementsByTagName("title"):
		for title_sub in title.childNodes:
			singleVideo["title"] = title_sub.data
	for author in videoParser.getElementsByTagName("author"):
		for authorName in author.getElementsByTagName("name"):
			for authorName_sub in authorName.childNodes:
				singleVideo["author"] = authorName_sub.data
	for mediaGroup in videoParser.getElementsByTagName("media:group"):
		for mediaInfo in mediaGroup.getElementsByTagName("media:content"):
			singleVideo["type"] = mediaInfo.getAttribute("type")
			singleVideo["duration"] = mediaInfo.getAttribute("duration")
		for mediaCategory in mediaGroup.getElementsByTagName("media:category"):
			for category_sub in mediaCategory.childNodes:
				singleVideo["category"] = category_sub.data
		for mediaDescription in mediaGroup.getElementsByTagName("media:description"):
			for description_sub in mediaDescription.childNodes:
				singleVideo["description"] = description_sub.data
	for gdComments in videoParser.getElementsByTagName("gd:comments"):
		for gdFeedlink in gdComments.getElementsByTagName("gd:feedLink"):
			singleVideo["commentsNumber"] = gdFeedlink.getAttribute("countHint")
	for accessControl in videoParser.getElementsByTagName("yt:accessControl"):
		singleVideo["accessControl"][accessControl.getAttribute("action")] = {}
		singleVideo["accessControl"][accessControl.getAttribute("action")]["permission"] = accessControl.getAttribute("permission")

	sRelated = urllib2.urlopen(yt_related_video_url(videoID))				
	relatedVideoParser = parseString(sRelated.read())
	for relatedMediaGroup in relatedVideoParser.getElementsByTagName("media:group"):
		for relatedVideoID in relatedMediaGroup.getElementsByTagName("yt:videoid"):
			for relatedVideoID_sub in relatedVideoID.childNodes:
				singleVideo["relatedVideos"].append(relatedVideoID_sub.data)
	return singleVideo

#***************************************************************************************#
# Function: launchScraper
# Parameters: videoID
# How it works: function called by the main Program of the script that for each video
#               passed as parameter, collects all the needed information 
# Details: This function is called for each videoID found, it generates the custom urllib2
#          Opener with create_opener(), then gets the html content of the video's webpage
#          with fetch_video_html(opener, videoID) in order to extract the session token
#          with get_insight_ajax_token(video_page), then if the token has been succesfully
#          found, it proceeds downloading the statistics in a simil-json format with 
#          fetch_video_insights(opener, videoID, token). Then if the statistic's simil-json
#          is valid (contains "data" keyword), it proceeds with the parsing and inserting
#          phases.
# Return: it returns 1 if the video is provided with statistics, 0 otherwise
#***************************************************************************************#
def launchScraper (videoID):
	try:
		print 'Video id: '+str(videoID)
		opener = create_opener()
		video_page = fetch_video_html(opener, videoID)
		token = get_insight_ajax_token(video_page)

		if not token:
			print "No session token"
			raise ValueError("Couldn't find session_token in %s" % video_page)
		data = fetch_video_insights(opener, videoID, token)

		if '"data":' in data:
			extractVideoStatistics(videoID,data)
			return 1
		else:
			print "No statistics available for this video"
			return 0
	except:
		return 0

#***************************************************************************************#
# Function: getLineNumber
# Parameters: filename
# How it works: this function returns the number of lines contained in the file from 
#               which we get the random word to be used as keyword
# Return: it returns the number of the lines in the file
#***************************************************************************************#
def getLineNumber(filename):
	fh = open(filename, "r")
	lineNum = len(fh.readlines())
	fh.close()
	return lineNum

#***************************************************************************************#
# Function: getRandomLine
# Parameters: filename, lineNum
# How it works: this function gets the name of the file containing the words to be used 
#               as keywords and the number of lines of that file and extracts a random 
#               keyword using random.randrange().
# Return: returns a keyword
#***************************************************************************************#
def getRandomLine(filename, lineNum):
	randomNumber = random.randrange(0,lineNum+1)
	return linecache.getline(filename,randomNumber).split(" ")[0].replace("_"," ").split(" ")[0]

#***************************************************************************************#
# Function: extractGplusStatistics
# Parameters: videoID
# How it works: knowing the ID of the video to be analyzed, this function extracts the 
#               Gplus activities related to that video from Ripples. It uses a regex in 
#               order to extract each activity from the simil-json returned by Ripple.
# Return: returns a list containing all the activities
#***************************************************************************************#
def extractGplusStatistics (videoID):
	content = urllib2.urlopen(yt_gplus_url(videoID))
	parsedHtmlContent = BeautifulSoup(content.read())
	scripts=parsedHtmlContent.findAll('script')

	gplusdata={}
	gplusentry=[]

	for script in scripts:
		if 'OZ_ripplesData' in str(script):
			for single in re.findall(r'\["(?P<name>[^"]*)","(?P<number1>[^"]*)","(?P<data>[^"]*)",(?P<number2>\d*),"(?P<website>[^"]*)","(?P<language>[^"]*)"\]', str(script.contents)):
				if 'youtube' in single[4]:

					gplusdata['authorName']=single[0]
					gplusdata['authorID']=single[1]
					gplusdata['activityID']=single[2]
					gplusdata['activityTimestamp']=single[3]
					gplusdata['activityType']='share'
					gplusdata['activityLanguage']=single[5]
					
				else:
					gplusdata['authorName']=single[0]
					gplusdata['authorID']=single[1]
					gplusdata['activityID']=single[2]
					gplusdata['activityTimestamp']=single[3]
					gplusdata['activityReshared']=single[4]
					gplusdata['activityType']='reshare'
					gplusdata['activityLanguage']=single[5]
					
				gplusentry.append(gplusdata)

			for single in re.findall(r'\["(?P<name>[^"]*)","(?P<number1>[^"]*)","(?P<data>[^"]*)",(?P<number2>\d*),,"(?P<language>[^"]*)"\]', str(script.contents)):

				gplusdata['authorName']=single[0]
				gplusdata['authorID']=single[1]
				gplusdata['activityID']=single[2]
				gplusdata['activityTimestamp']=single[3]
				gplusdata['activityType']='share'
				gplusdata['activityLanguage']=single[4]
				
				gplusentry.append(gplusdata)
	return gplusentry
