# -*- coding: utf-8 -*-

#### IMPORTS 1.0

import os
import re
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup


#### FUNCTIONS 1.2

import requests     # import requests to validate URL

def validateFilename(filename):
    filenameregex = '^[a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+_[0-9][0-9][0-9][0-9]_[0-9QY][0-9]$'
    dateregex = '[0-9][0-9][0-9][0-9]_[0-9QY][0-9]'
    validName = (re.search(filenameregex, filename) != None)
    found = re.search(dateregex, filename)
    if not found:
        return False
    date = found.group(0)
    now = datetime.now()
    year, month = date[:4], date[5:7]
    validYear = (2000 <= int(year) <= now.year)
    if 'Q' in date:
        validMonth = (month in ['Q0', 'Q1', 'Q2', 'Q3', 'Q4'])
    elif 'Y' in date:
        validMonth = (month in ['Y1'])
    else:
        try:
            validMonth = datetime.strptime(date, "%Y_%m") < now
        except:
            return False
    if all([validName, validYear, validMonth]):
        return True


def validateURL(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=20)
        count = 1
        while r.status_code == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = requests.get(url, allow_redirects=True, timeout=20)
        sourceFilename = r.headers.get('Content-Disposition')
        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        elif r.headers['Content-Type'] == 'text/csv':
            ext = '.csv'
        else:
            ext = os.path.splitext(url)[1]
        validURL = r.status_code == 200
        validFiletype = ext in ['.csv', '.xls', '.xlsx']
        return validURL, validFiletype
    except:
        print ("Error validating URL.")
        return False, False

def validate(filename, file_url):
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url)
    if not validFilename:
        print filename, "*Error: Invalid filename*"
        print file_url
        return False
    if not validURL:
        print filename, "*Error: Invalid URL*"
        print file_url
        return False
    if not validFiletype:
        print filename, "*Error: Invalid filetype*"
        print file_url
        return False
    return True


def convert_mth_strings ( mth_string ):
    month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
    for k, v in month_numbers.items():
        mth_string = mth_string.replace(k, v)
    return mth_string


#### VARIABLES 1.0

entity_id = "E5018_LLBC_gov"
url = 'http://www.lewisham.gov.uk/mayorandcouncil/aboutthecouncil/finances/council-spending-over-250/Pages/default.aspx'
errors = 0
data = []

#### READ HTML 1.0


html = urllib2.urlopen(url)
soup = BeautifulSoup(html, 'lxml')


#### SCRAPE DATA

menuBlock = soup.find('tr',{'class':'lbl-styleTableOddRow-inThisSectionBox'})
pageLinks = menuBlock.findAll('a', href=True)

for pageLink in pageLinks:
    href = pageLink['href']
    fullLink = "http://www.lewisham.gov.uk"+href
    html2 = requests.get(fullLink)
    soup2 = BeautifulSoup(html2.text, 'lxml')
    docBlock = soup2.find('div',{'class':'contentContainer documentsList'})
    fileLinks = docBlock.findAll('a', href=True)
    links = []
    for fileLink in fileLinks:
        fileUrl = fileLink['href']
        if '.csv' in fileUrl:
                if 'August 2015' in fileLink.text:
                     links.append(fileLink)
                else:
                    url = "http://www.lewisham.gov.uk"+fileUrl
                    title = fileLink.contents[0]
                    title = title.upper().strip()
                    csvYr = title.split(' ')[1]
                    csvMth = title.split(' ')[0][:3]
                    csvMth = convert_mth_strings(csvMth.upper())
                    data.append([csvYr, csvMth, url])

    for link in links[:1]:
        fileUrl = link['href']
        url = "http://www.lewisham.gov.uk"+fileUrl
        title = link.contents[0]
        title = title.upper().strip()
        csvYr = title.split(' ')[1]
        csvMth = title.split(' ')[0][:3]
        csvMth = convert_mth_strings(csvMth.upper())
        data.append([csvYr, csvMth, url])


#### STORE DATA 1.0

for row in data:
    csvYr, csvMth, url = row
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url.strip()

    valid = validate(filename, file_url)

    if valid == True:
        scraperwiki.sqlite.save(unique_keys=['l'], data={"l": file_url, "f": filename, "d": todays_date })
        print filename
    else:
        errors += 1

if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)


#### EOF

