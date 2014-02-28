#!/usr/bin/python
import os, sys 
import httplib2
from lxml import etree
from StringIO import StringIO
#import mx.DateTime
import re
import simplejson
import ipdb

# Table Three Scraper http://uscode.house.gov/table3/table3years.htm
# The scrapers grab the URLs for each year from 1789 to 2011, go one directory down to grab the directory, then go one directory below and grab the whole page.  THIS CODE TAKES A WHILE TO RUN.  It may be better to tweak just for the years you want.  Also, could use some refactoring, e.g. merge some of the functions.

# GLOBAL VARIABLES
years = range(1944, 2009)
years = { 1950 }
LIMIT_SUBSUBRELEASES = False
LIMIT = False


def mainscraper(content): #function to parse Table 3 website
	doc = etree.parse(StringIO(content), parser=etree.HTMLParser())
	releases = []
	subreleases = []
	for element in doc.xpath('//div[@class="alltable3years"]'):   #Could also use "alltable3statutesatlargevolumes"
		for d_element in element.xpath('span'):
			text = d_element.xpath('a')[0].text
			unitext = unicode(text).encode(sys.stdout.encoding, 'replace')
			for m_element in d_element.xpath('a'):
				
				addy = m_element.attrib['href']
				year = addy.replace( 'year', '' )
				year = year.replace( '.htm', '' )
				print year 
				if int( year ) in set( years ): 
					url = "http://uscode.house.gov/table3/" + addy
				        #print unitext, url
				        #releases += [(unitext, url)]
					subreleases += add_subrelease(url)
					#return subreleases
				else:
					pass
	return subreleases #releases, subreleases

def subscraper(content): #function to parse Table 3 website
	doc = etree.parse(StringIO(content), parser=etree.HTMLParser())
	subsubreleases = []	
	releases = []
	for element in doc.xpath('//div[@class="yearmaster"]'):   #Could also use "statutesatlargevolumemasterhead"
		for d_element in element.xpath('span'):
			text = d_element.xpath('a')[0].text
			unitext = unicode(text).encode(sys.stdout.encoding, 'replace')
			for m_element in d_element.xpath('a'):
				addy = m_element.attrib['href']
				url = "http://uscode.house.gov/table3/" + addy
				#print text, url
				#releases += [(text, url)]
				subsubreleases.append( add_subsubrelease(url) )
				if LIMIT_SUBSUBRELEASES and len( subsubreleases ) == LIMIT:
					return subsubreleases
	return	subsubreleases

def add_release(url): #function grab main page data
	http = httplib2.Http('/tmp/httpcache')
	response, content = http.request(url)
	if response.status != 200:
	    sys.stderr.write('Error, returned status: %s\n' % response.status)
	    sys.exit(1) #bomb out, non-zero return indicates error
	#print content
	return mainscraper(content)
	
def add_subrelease(url): #function to grab sub page data
	http = httplib2.Http('/tmp/httpcache')
	response, content = http.request(url)
	if response.status != 200:
	    sys.stderr.write('Error, returned status: %s\n' % response.status)
	    sys.exit(1) #bomb out, non-zero return indicates error
	#print content
	return subscraper(content)

def add_subsubrelease(url): #function to grab sub, sub page data
	http = httplib2.Http('/tmp/httpcache')
	response, content = http.request(url)
	if response.status != 200:
	    sys.stderr.write('Error, returned status: %s\n' % response.status)
	    sys.exit(1) #bomb out, non-zero return indicates error
	print url
	# print content
	return content
	

def _process_caption_span( expected_class, caption_span, caption_dict ):
    assert caption_span.get('class') == expected_class

    text_val = " ".join ( caption_span.itertext() )

    caption_dict[ caption_span.get('class') ] = text_val

def _process_table_content_row( table_content_row ):
	assert( len( table_content_row) == 5 )
	row_val_dict = {}
	_process_caption_span( 'actsection', table_content_row[0], row_val_dict )
	_process_caption_span( 'statutesatlargepage', table_content_row[1], row_val_dict )
	_process_caption_span( 'unitedstatescodetitle', table_content_row[2], row_val_dict )
	_process_caption_span( 'unitedstatescodesection', table_content_row[3], row_val_dict )
	_process_caption_span( 'unitedstatescodestatus', table_content_row[4], row_val_dict )

	return row_val_dict

def _parse_legislative_changes_page( page ):
	doc = etree.parse(StringIO(page), parser=etree.HTMLParser())
	tbl = doc.find('//table')
	
	caption_dict = {}
	
	caption = tbl[ 1 ]
	
	assert caption.tag == 'caption'
	
	assert len( caption ) == 6
	
	_process_caption_span( 'congress', caption[0], caption_dict )
	_process_caption_span( 'statutesatlargevolume', caption[1], caption_dict )
	_process_caption_span( 'textdate', caption[2], caption_dict )
	_process_caption_span( 'prioract', caption[3], caption_dict )
	_process_caption_span( 'act', caption[4], caption_dict )
	_process_caption_span( 'nextact', caption[5], caption_dict )
	
	table_header_1 = tbl[3]
	table_header_2 = tbl[4]
	
	#print caption_dict
	
	i = 6
	while i < len( tbl ) - 1:
		table_content_row = tbl[i]
		row_val_dict = _process_table_content_row( table_content_row )
		    #print row_val_dict
		i += 1

	
def main():
	dataset = []
	x = add_release("http://uscode.house.gov/table3/table3years.htm") #Could also use "/alltable3statutesatlargevolumes.html"
	if x != None:
		dataset += x

	# get the tables out
	for page in dataset:
		_parse_legislative_changes_page( page )
		#ipdb.set_trace()

		#print row_val_dict

if __name__ == '__main__':
	main()

dataset = []
	

#and save!  The data generated 
#simplejson.dump(dataset, open(sys.argv[1],'w'))
