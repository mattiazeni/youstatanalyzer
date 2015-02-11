#######################################################################
# File:        youtube_script.xml
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
from xml.dom.minidom import parse, parseString
import functions

try:
	#Open config file and read it
	config_parser = parse("config.xml")
	for configuration in config_parser.getElementsByTagName("config"):
		for keywordSearchStatus in configuration.getElementsByTagName("keywordsearch"):
			keywordSearch = keywordSearchStatus.getAttribute("status")
			print "Keyword search: ", keywordSearch
		for standardSearchStatus in configuration.getElementsByTagName("standardsearch"):
			standardSearch = standardSearchStatus.getAttribute("status")
			print "Standard search: ", standardSearch
		for singleVideoSearchStatus in configuration.getElementsByTagName("singlevideosearch"):
			singleVideoSearch = singleVideoSearchStatus.getAttribute("status")
			print "SingleVideo search: ", singleVideoSearch
		for randomSearchStatus in configuration.getElementsByTagName("randomsearch"):
			randomSearch = randomSearchStatus.getAttribute("status")
			print "Random search: ", randomSearch

	#If keyword search is enabled
	#MAX 50 results
	if keywordSearch == 'true':
		#Read config file in order to extract each keyword with its parameters: videos_number, videos_number, duration, hd, safeSearh, timeParameter, category, keyword	
		config_parser = parse("config.xml")
		for configuration in config_parser.getElementsByTagName("config"):
			for singleKeyword in configuration.getElementsByTagName("keywordsearch"):
				for single_keyword in singleKeyword.getElementsByTagName("keyword"):
					videos_number = ""
					duration = ""
					hd = ""
					safeSearch = ""
					timeParameter = ""
					keyword_scan = ""
					category_scan = ""
					category = ""
					keyword = ""
					videos_number = single_keyword.getAttribute("results")
					orderBy = single_keyword.getAttribute("orderby")
					duration = single_keyword.getAttribute("duration")
					hd = single_keyword.getAttribute("hd")
					safeSearch = single_keyword.getAttribute("safeSearch")
					timeParameter = single_keyword.getAttribute("time")	

					for search_term_and in single_keyword.getElementsByTagName("search_term_and"):
						keyword_scan = search_term_and.getAttribute("value")

						if len(keyword) != 0 and len(keyword_scan) != 0: 
							keyword = keyword + "+" + keyword_scan
						else:
							keyword = keyword + keyword_scan
					for search_term_or in single_keyword.getElementsByTagName("search_term_or"):
						keyword_scan = search_term_or.getAttribute("value")

						if len(keyword) != 0 and len(keyword_scan) != 0:
							keyword = keyword + "%7C" + keyword_scan
						else:
							keyword = keyword + keyword_scan
					for search_term_not in single_keyword.getElementsByTagName("search_term_not"):
						keyword_scan = search_term_not.getAttribute("value")
						if len(keyword) != 0 and len(keyword_scan) != 0:
							keyword = keyword + "+-" + keyword_scan
					for search_term_exactly in single_keyword.getElementsByTagName("search_term_exactly"):
						keyword_scan = search_term_exactly.getAttribute("value")
						if len(keyword_scan) != 0:
							keyword = '"' + keyword_scan + '"'

					for category_term_and in single_keyword.getElementsByTagName("category_term_and"):
						category_scan = category_term_and.getAttribute("value")

						if len(category) != 0 and len(category_scan) != 0:
							category = category + "+" + category_scan
						else:
							category = category + category_scan
					for category_term_or in single_keyword.getElementsByTagName("category_term_or"):
						category_scan = category_term_or.getAttribute("value")

						if len(category) != 0 and len(category_scan) != 0:
							category = category + "%7C" + category_scan
						else:
							category = category + category_scan
					for category_term_not in single_keyword.getElementsByTagName("category_term_not"):
						category_scan = category_term_not.getAttribute("value")
						if len(category) != 0 and len(category_scan) != 0:
							category = category + "+-" + category_scan
					i=0
					max_index=(int(videos_number)/50)+1
					for ii in range(0,max_index):
						index = 1+(ii*50)
						#Define the url for the request to youtube servers	
						url = "https://gdata.youtube.com/feeds/api/videos?q="

						if len(keyword) != 0:
							url = url + keyword
							print "Search keyword(s): " + keyword
						if len(orderBy) != 0:
							url = url + "&orderby=" + orderBy
							print "Order by: " + orderBy
						if len(duration) != 0:
							url = url + "&duration=" + duration
							print "Video duration: " + duration
						if len(category) != 0:
							url = url + "&category=" + category
							print "Search categories: " + category
						if len(hd) != 0:
							url = url + "&hd=" + hd
							print "Only HD videos: " + hd
						if len(safeSearch) != 0:
							url = url + "&safeSearch=" + safeSearch
							print "Safesearch level: " + safeSearch
						if len(timeParameter) != 0:
							url = url + "&time=" + timeParameter
							print "Time: " + timeParameter
						if int(videos_number)/50 > 1:
							url = url + "&start-index=" + str(index)
							print "Start-index: " + str(index)
						if ii == max_index-1:
							print "Number of results: " + str(int(videos_number)%50)
							url = url + "&max-results="+str(int(videos_number)%50)
						else:
							if videos_number < 50:
								print "Number of results: " + videos_number
								url = url + "&max-results="+videos_number
							else:
								print "Number of results: " + "50"
								url = url + "&max-results=50"
					
						url = url + "&v=2"

						print "URL: " + url

						s = urllib2.urlopen(url)				
			
						#Read the xml file in order to extract videos IDs
						parser_video = parseString(s.read())
						for videos in parser_video.getElementsByTagName("entry"):
							for single_video in videos.getElementsByTagName("id"):
								for xo in single_video.childNodes:
									try:
										i+=1
										print i
										print "Video id: " + xo.data.split('video:')[1]
										
										#For each video, capture the statistics xml file
										functions.launchScraper(xo.data.split('video:')[1])
									except:
										pass

	#If single video search by ID is enabled
	if singleVideoSearch == 'true':
		#Read config file in order to extract each videoID to analyze
		config_parser = parse("config.xml")
		for configuration in config_parser.getElementsByTagName("config"):
			for singleVideoSearch in configuration.getElementsByTagName("singlevideosearch"):
				for singleVideo in singleVideoSearch.getElementsByTagName("video"):
					videoID = singleVideo.getAttribute("id")
					functions.launchScraper(videoID)

	#MAX 50 results
	#If standard search is enabled
	if standardSearch == 'true':
		#Read config file in order to extract the standard search parameters, feedID, timeParameter, region, category
		config_parser = parse("config.xml")
		for configuration in config_parser.getElementsByTagName("config"):
			for standardSearch in configuration.getElementsByTagName("standardsearch"):
				for singleFeed in standardSearch.getElementsByTagName("feed"):
					feedID = ""
					timeParameter = ""
					region = ""
					category = ""
					videos_number= ""
					feedID = singleFeed.getAttribute("id")
					timeParameter = singleFeed.getAttribute("time")
					region = singleFeed.getAttribute("region")
					category = singleFeed.getAttribute("category")
					videos_number = singleFeed.getAttribute("results")
				
					i=0
					max_index=(int(videos_number)/50)+1
					for ii in range(0,max_index):
						index = 1+(ii*50)
						#Define the url for the request to youtube servers
						url = "http://gdata.youtube.com/feeds/api/standardfeeds"

						if len(region) != 0:
							url = url + "/" + region
							print "Region: " + region
						if len(feedID) != 0:
							url = url + "/" + feedID
							print "Feed ID: " + feedID
						if len(category) != 0:
							url = url + "_" + category + "?"
							print "Search category: " + category
						if len(timeParameter) != 0:
							url = url + "time=" + timeParameter
							print "Time: " + timeParameter
						if int(videos_number)/50 > 1:
							url = url + "&start-index=" + str(index)
							print "Start-index: " + str(index)
						if ii == max_index-1:
							print "Number of results: " + str(int(videos_number)%50)
							url = url + "&max-results="+str(int(videos_number)%50)
						else:
							if videos_number < 50:
								print "Number of results: " + videos_number
								url = url + "&max-results="+videos_number
							else:
								print "Number of results: " + "50"
								url = url + "&max-results=50"
						
						url = url + "&v=2"

						print "URL: " + url

						s = urllib2.urlopen(url)				

						#Read the xml file in order to extract videos IDs
						parser_video = parseString(s.read())
						for videos in parser_video.getElementsByTagName("entry"):
							for single_video in videos.getElementsByTagName("id"):
								for xo in single_video.childNodes:
									i+=1
									print i
									print "Video id: " + xo.data.split('video:')[1]
									functions.launchScraper(xo.data.split('video:')[1])
	
	if randomSearch == 'true':    
		for randomSearchVideo in configuration.getElementsByTagName("randomsearch"):
			for wordList in randomSearchVideo.getElementsByTagName("wordlist"):
				wordListFilename = wordList.getAttribute("filename")
				numberOfKeywords = wordList.getAttribute("numberOfKeywords")
				resultsPerKeyword = wordList.getAttribute("resultsPerKeyword")
				orderBy = wordList.getAttribute("orderBy")
				duration = wordList.getAttribute("duration")
				category = wordList.getAttribute("category")
				safeSearch = wordList.getAttribute("safeSearch")
				hd = wordList.getAttribute("hd")
				timeParameter = wordList.getAttribute("timeParameter")
	
				lineNumber=functions.getLineNumber(wordListFilename)
			
				for i in range(0,int(numberOfKeywords)):
					keyword=functions.getRandomLine(wordListFilename, lineNumber)
					print keyword
					i=0
					max_index=(int(resultsPerKeyword)/50)+1
					for ii in range(0,max_index):
						index = 1+(ii*50)
						#Define the url for the request to youtube servers	
						url = "https://gdata.youtube.com/feeds/api/videos?q="

						if len(keyword) != 0:
							url = url + keyword
							print "Search keyword(s): " + keyword
						if len(orderBy) != 0:
							url = url + "&orderby=" + orderBy
							print "Order by: " + orderBy
						if len(duration) != 0:
							url = url + "&duration=" + duration
							print "Video duration: " + duration
						if len(category) != 0:
							url = url + "&category=" + category
							print "Search categories: " + category
						if len(hd) != 0:
							url = url + "&hd=" + hd
							print "Only HD videos: " + hd
						if len(safeSearch) != 0:
							url = url + "&safeSearch=" + safeSearch
							print "Safesearch level: " + safeSearch
						if len(timeParameter) != 0:
							url = url + "&time=" + timeParameter
							print "Time: " + timeParameter
						if int(resultsPerKeyword)/50 > 1:
							url = url + "&start-index=" + str(index)
							print "Start-index: " + str(index)
						if ii == max_index-1:
							print "Number of results: " + str(int(resultsPerKeyword)%50)
							url = url + "&max-results="+str(int(resultsPerKeyword)%50)
						else:
							if resultsPerKeyword < 50:
								print "Number of results: " + resultsPerKeyword
								url = url + "&max-results="+resultsPerKeyword
							else:
								print "Number of results: " + "50"
								url = url + "&max-results=50"
					
						url = url + "&v=2"

						print "URL: " + url

						s = urllib2.urlopen(url)				
			
						#Read the xml stream in order to extract videos IDs
						parser_video = parseString(s.read())
						for videos in parser_video.getElementsByTagName("entry"):
							for single_video in videos.getElementsByTagName("id"):
								for xo in single_video.childNodes:
									i+=1
									print i
									print "Video id: " + xo.data.split('video:')[1]
									functions.launchScraper(xo.data.split('video:')[1])

except KeyboardInterrupt:
	pass
