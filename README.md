YOUStatAnalyzer
===============

YOUStatAnalyzer is a tool written in Python able to capture the popularity metrics of YouTube's videos. Since in June 2013 YouTube removed the API that allowed to retrieve the statistics available below each video, we needed to find a new way of obtain those kind of data. Il risultato di questo studio e' YOUStatAnalyzer, un software che permette in maniera molto rapida di ottenere tutte le statistiche dei video YouTube con lo scopo finale di generare un dataset su cui effettuare analisi. Per scaricare queste statistiche il tool ottiene un token di sessione che poi verra' utilizzato per effettuare la richiesta dei dati, che verranno poi interpretati e salvati in un database in un formato noto.

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

## The Database

As database system we used MongoDB through pymongo. If you are not confortable with it you can just replace the few functions that use the database such as insertEntry()

### The Data Structure

