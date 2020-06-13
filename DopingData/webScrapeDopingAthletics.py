#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import libraries
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re
import pandas as pd

# generate empty data frame (to be filled)
dopingDF = pd.DataFrame()

# set URL to webscrape from
url = ['https://www.athleticsintegrity.org/disciplinary-process/global-list-of-ineligible-persons?isDopingViolation=#filters']

# indicates if there are more pages upcoming
flag = 1
       
while flag:
    
    # access the site
    response = requests.get(url[-1])
    
    # check 
    if response.status_code == 200:

        # parse the html to get nested BeautifulSoup data structure
        soup = BeautifulSoup(response.text, "html.parser")
        
        # find table with data
        findTable = soup.find('table', {'class':'table table-condensed table-striped'})
        findRows = findTable.find_all('tr') # get rows of table
        
        # get column names to fill data frame header later
        headers = []
        findColumns = findRows[0].findAll('th') # row 0 = header
        for iName in findColumns:
            headers.append(iName.text.replace('\n', ''))
        
        # get data of all rows in table (except header)
        for iRow in range(1, len(findRows)):
            values = []
            infoBit = findRows[iRow].findAll('td') 
            # get data of all columns 
            for iBit in infoBit:
                # remove whitespace from data
                cleanInfo = iBit.text.replace('\n', '').replace('\t', '')      
                values.append(cleanInfo)
            row_df = pd.DataFrame([values])
            dopingDF = pd.concat([dopingDF, row_df], ignore_index = True)
        
        # access page numbers to detect end of table
        findEnd = soup.findAll('span', {'class':'pagination__state'})
        cueEnd = findEnd[0].text.replace('Showing page ', '')
        # last numbers of text indicate max page count e.g. 22
        maxNum = re.findall('.*?([0-9]+)$', cueEnd)
        # change flag to stop while loop as soon as last page is reached
        if cueEnd == maxNum[0] + ' of ' + maxNum[0]: # page 22 of 22
            flag = 0
        
        # follow link of button to reach next page of table 
        findButton = soup.findAll('a', {'class':'pagination__button'})
        for iLink in range(0, len(findButton)):
            try:
                if findButton[iLink]['title'] == 'Next Page':
                    # link to next page 
                    link = findButton[iLink]['href']
            except: 
                continue
    
        url.append(link)


# header for data frame 
dopingDF.columns = headers

# export data frame as csv file
dopingDF.to_csv(str('dopingInAthletics.csv'), sep="\t", index = False)
