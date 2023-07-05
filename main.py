from bs4 import BeautifulSoup
import urllib.request,sys,time
import requests
import pandas as pd
import re
import math
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime

# Initialise global variables

links = list()
titles = list()
dates = list()

monthDict = {	1:'Janauary',
            2:'February',
            3:'March',
            4:'April',
            5:'May',
            6:'June',
            7:'July',
            8:'August',
            9:'September',
            10:'October',
            11:'November',
            12:'December'		}

todayDate = str(datetime.now().date())
month = monthDict[datetime.now().month]
year = str(datetime.now().year)

def us_fed():
    url = 'https://www.federalreserve.gov/recentpostings.htm'
    try:
        page = requests.get(url)
    except:
        print("Something is wrong with US FED link.")
    soup = BeautifulSoup(page.text, "html.parser")
    titlesAndLinks = soup.find_all('div', class_='col-xs-9 col-md-10 eventlist__event')
    datesBlock = soup.find_all('div', class_='col-xs-3 col-md-2 eventlist__time')

    titles.append('US FED')
    links.append('US FED')
    dates.append('US FED')

    base_url = 'https://www.federalreserve.gov'

    links_list = list()
    titles_list = list()
    dates_list = list()

    for a in titlesAndLinks:
        new_link = base_url + a.find('a',href=True)['href']
        links_list.append(new_link) # Link
        titles_list.append(a.text.strip()) # Desc


    pattern = r'(\d{1,2}/\d{1,2}/2023)' 
        
    for b in datesBlock:
        d = b.find('time').text.strip()
        match = re.search(pattern, d)
        matched_date = match.group(1)
        month, day, year = map(int, matched_date.split('/'))                # Using regex to filter out date. Since date on website uses numerical date instead of string.
        if month == 7 and year == 2023:
                dates_list.append(matched_date)
                dates.append(matched_date)

    for a in links_list[0:len(dates_list)]:
        links.append(a)
    for b in titles_list[0:len(dates_list)]:
        titles.append(b)
    

    # d = {'Title': titles_list,'Link':links_list,'Date':dates_list}
    # df = pd.DataFrame(data=d)
    # df.to_csv(r'C:\Users\65936\\OneDrive\Desktop\MAS\\USFED_new.csv')

def boj():
    url = 'https://www.boj.or.jp/en/whatsnew/index.htm'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    aa = soup.find_all('li', class_='news_list-li')
    combined_list=list()
    titles.append('BOJ')
    links.append('BOJ')
    dates.append('BOJ')

    for a in aa:
        text = a.find('time',class_='time').text
        if month in text and year in text:
            combined_list.append(a)
        
    for b in combined_list:
        titles.append(b.find('a').text)
        links.append(b.find('a',href=True)['href'])
        dates.append(b.find('time',class_='time').text)

def ecb():
    driver = webdriver.Chrome()
    driver.get('https://www.ecb.europa.eu/pub/pubbydate/html/index.en.html')

    # Reject cookies
    button = driver.find_element(By.XPATH,"//*[text()='I do not accept the use of cookies']")
    button.click()
    driver.implicitly_wait(5)

    # Get HTML code
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    div_element = soup.find('div', class_='lazy-load loaded')
    allDates = div_element.find_all('div',class_='date') # All dates
    allTitleBlocks = div_element.find_all('dd') # All title blocks
    dates_list = list()                                           # Need empty list to extract length of dates with current month and year
    links_list = list()
    titles_list = list()

    dates.append('ECB')
    links.append('ECB')
    titles.append('ECB')

    for a in allDates:
        if a.text.find(year) != -1 and a.text.find(month) != -1:
            dates_list.append(a.text)
            dates.append(a.text)                                  # Dates of current month and year

    preLink = 'https://www.ecb.europa.eu'
            
    for a in allTitleBlocks:
        titleBlock = a.find('div',class_='title')
        if titleBlock is not None:
            titles_list.append(titleBlock.find('a', href=True).text)   # All titles
            newLink = preLink + titleBlock.find('a', href=True)['href'] 
            links_list.append(newLink)                                 # All links
            
    links_list = links[0:len(dates_list)]                                   # Slice list to get same length as dates
    titles_list = titles[0:len(dates_list)]                                 # Indexes of dates, links, and titles match, so simple slicing will work

    for a in links_list:                                                # Append to global list
        links.append(a)
    for b in titles_list:
        titles.append(b)

def boe():
    driver = webdriver.Chrome()
    driver.get('https://www.bankofengland.co.uk/news/publications')
    driver.implicitly_wait(5)

    # Accept recommended cookies
    button = driver.find_element(By.XPATH,"//*[text()='Proceed with necessary cookies only']")
    button.click()
    driver.implicitly_wait(5)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    blocks = soup.find_all('div', class_='col3')           # Each block contains date, title, and link

    titles_list = list()
    links_list = list()
    dates_list = list()

    dates.append('BOE')
    links.append('BOE')
    titles.append('BOE')

    preLink = 'https://www.bankofengland.co.uk'

    for a in blocks:
        date = a.find('time',class_='release-date')
        if date is not None and date.text.find(month) != -1 and date.text.find(year) != -1:
            dates_list.append(date.text)                                                # Need to get length of dates to slice titles and year
            dates.append(date.text)                                                     # Dates with current month and year

        title = a.find('h3',class_='grid-view exclude-navigation')
        if title is not None:
            titles_list.append(title.text)                                                  # All titles

        link = a.find('a',href=True,class_='release release-pubs')
        if link is not None:
            newLink = preLink + link['href']
            links_list.append(newLink)                                                       # All links

    driver.quit()

    links_list2 = links_list[0:len(dates_list)]
    titles_list2 = titles_list[0:len(dates_list)]

    for a in links_list2:
        links.append(a)
    for b in titles_list2:
        titles.append(b)

def bcbs():
    url = 'https://www.bis.org/bcbs/publications.htm?m=2566'

    driver = webdriver.Chrome()  # Use Chrome or any other supported browser driver
    driver.get(url)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    aa = soup.find('tbody').find_all('tr')
    
    li = list()

    for a in aa:                                            # To get publications in 2023    
        if year in a.text:
                li.append(a)

    dates.append('BCBS')
    links.append('BCBS')
    titles.append('BCBS')

    preLink = 'https://www.bis.org'
                
    for b in li:
        titles.append(b.find('div',class_='title').text)
        newLink = preLink + b.find('a',class_='dark',href=True)['href']
        links.append(newLink)
        dates.append(b.find('td',class_='item_date').text)

    # Close the webdriver
    driver.quit()

def cgfs():
    url = 'https://www.bis.org/cgfs_publs/index.htm?m=2569'
    driver = webdriver.Chrome()  # Use Chrome or any other supported browser driver
    driver.get(url)
    html_content = driver.page_source

    li = list()
    soup = BeautifulSoup(html_content, "html.parser")
    try:
        aa = soup.find('tbody').find_all('tr')
    except:
        print("No results found for CGFS in this month.")

    dates.append('CGFS')
    titles.append('CGFS')
    links.append('CGFS')

    for a in aa:                                                    # To get publications in 2023    
        if year in a.text:
                li.append(a)

    preLink = 'https://www.bis.org'
                
    for b in li:
        titles.append(b.find('div',class_='title').text)
        newLink = preLink + b.find('a',class_='dark',href=True)['href']
        links.append(newLink)
        dates.append(b.find('td',class_='item_date').text)

    # Close the webdriver
    driver.quit()

def fsb():
    url = 'https://www.fsb.org/publications/'

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    results = soup.find_all('h3', class_='media-heading')
    li = list()

    dates.append('FSB')
    links.append('FSB')
    titles.append('FSB')

    for a in results:
        if month in a.find('span').text:
            li.append(a)

    for b in li:
        titles.append(b.find('a').text)
        links.append(b.find('a',href=True)['href'])
        dates.append(b.find('span', class_='media-date pull-right').text)

def main():
    us_fed()
    boj()
    ecb()
    boe()
    bcbs()
    cgfs()
    fsb()

main()
print(len(dates))
print(len(links))
print(len(titles))

d = {'Title':titles, 'Link':links,'Date':dates}
df = pd.DataFrame(data=d)
df.to_csv(r'C:\Users\65936\\OneDrive\Desktop\MAS\\{date}-{mth}.csv'.format(date=todayDate,mth=month))