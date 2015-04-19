# -*- coding: utf-8 -*-

import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup

# Set up variables
entity_id = "E5042_HLBC_gov"
url = "http://www.hounslow.gov.uk/index/council_and_democracy/budgets_spending/payments_to_suppliers.htm"

# Set up functions
def convert_mth_strings ( mth_string ):
	month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
	#loop through the months in our dictionary
	for k, v in month_numbers.items():
		#then replace the word with the number
		mth_string = mth_string.replace(k, v)
	return mth_string

# pull down the content from the webpage
html = urllib2.urlopen(url)
soup = BeautifulSoup(html)

# find all entries with the required class
menuBlock = soup.find('ul',{'id':'leftnav'}) # Use the left hand nav for the page links
pageLinks = menuBlock.findAll('a', href=True)

for pageLink in pageLinks:
	href = pageLink['href']
	if '/payments_to_supplier' in href:
		print href
	  	html2 = urllib2.urlopen(href)
	  	soup2 = BeautifulSoup(html2)
	  	
	  	fileBlocks = soup2.findAll('a', href=True)
	  	
		for fileBlock in fileBlocks:
		  	fileUrl = fileBlock['href']
		  	if '.csv' in fileUrl:
			  	fileUrl = "http://www.hounslow.gov.uk/"+fileUrl
			  	title = fileBlock.contents[0]
				# create the right strings for the new filename
				title = title.upper().strip()
				csvYr = title.split(' ')[1]
				csvMth = title.split(' ')[0][:3]
				csvMth = convert_mth_strings(csvMth);
			
				filename = entity_id + "_" + csvYr + "_" + csvMth
				todays_date = str(datetime.now())
				scraperwiki.sqlite.save(unique_keys=['l'], data={"l": fileUrl, "f": filename, "d": todays_date })
				print filename
