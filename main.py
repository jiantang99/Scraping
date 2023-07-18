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
organisations = list()

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
month = monthDict[datetime.now().month-1]
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
        mth, day, yr = map(int, matched_date.split('/'))                # Using regex to filter out date. Since date on website uses numerical date instead of string.
        if mth == datetime.now().month-1 and yr == int(year):
                dates_list.append(matched_date)
                dates.append(matched_date)

    for a in links_list[0:len(dates_list)]:
        links.append(a)
    for b in titles_list[0:len(dates_list)]:
        titles.append(b)
        organisations.append('US FED')
    

    # d = {'Title': titles_list,'Link':links_list,'Date':dates_list}
    # df = pd.DataFrame(data=d)
    # df.to_csv(r'C:\Users\65936\\OneDrive\Desktop\MAS\\USFED_new.csv')

def boj():
    url = 'https://www.boj.or.jp/en/whatsnew/index.htm'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    aa = soup.find_all('li', class_='news_list-li')
    combined_list=list()

    baseLink = 'https://www.boj.or.jp'

    titles_list= list()
    links_list= list()
    dates_list= list()

    for a in aa:
        text = a.find('time',class_='time').text
        if 'June' in text and '2023' in text:
            combined_list.append(a)

    for b in combined_list:
        titles_list.append(b.find('a').text)
        fullLink = baseLink + b.find('a',href=True)['href']
        links_list.append(fullLink)
        dates_list.append(b.find('time',class_='time').text)
        
    listZip = list(zip(titles_list, links_list, dates_list))
    noDupeListZip = list(dict.fromkeys(listZip))
    for t, l, d in noDupeListZip:
        titles.append(t)
        links.append(l)
        dates.append(d)
        organisations.append('BOJ')

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
    driver.quit()

    titles_list = list()
    links_list = list()
    dates_list = list()

    for a in allDates:
        if a.text.find(year) != -1 and a.text.find(month) != -1:
            dates_list.append(a.text)
            dates.append(a.text)                                  # All dates

    preLink = 'https://www.ecb.europa.eu'
            
    for a in allTitleBlocks:
        titleBlock = a.find('div',class_='title')
        if titleBlock is not None:
            titles_list.append(titleBlock.find('a', href=True).text)   # All titles
            newLink = preLink + titleBlock.find('a', href=True)['href'] 
            links_list.append(newLink)                                 # All links
            
    for b in links_list[0:len(dates_list)]:
        links.append(b)                                   # Slice list to get same length as dates
    for c in titles_list[0:len(dates_list)]:
        organisations.append('ECB')
        titles.append(c)                                 # Indexes of dates, links, and titles match, so simple slicing will work

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
        organisations.append('BOE')
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

    monthDictv2 = {	1:'Jan',                           # Need new dictionary since this website uses short form of months. E.g., July = Jul
            2:'Feb',
            3:'Mar',
            4:'Apr',
            5:'May',
            6:'Jun',
            7:'Jul',
            8:'Aug',
            9:'Sep',
            10:'Oct',
            11:'Nov',
            12:'Dec'		}
    
    monthv2 = monthDictv2[datetime.now().month-1]

    preLink = 'https://www.bis.org'
                
    for b in li:
        if year in b.find('td',class_='item_date').text and monthv2 in b.find('td',class_='item_date').text:
            titles.append(b.find('div',class_='title').text)
            newLink = preLink + b.find('a',class_='dark',href=True)['href']
            links.append(newLink)
            dates.append(b.find('td',class_='item_date').text)
            organisations.append('BCBS')

    # Close the webdriver
    driver.quit()

def cgfs():
    url = 'https://www.bis.org/cgfs_publs/index.htm?m=2569'

    # Set up the Selenium webdriver (make sure you have the appropriate driver installed)
    driver = webdriver.Chrome()  # Use Chrome or any other supported browser driver

    # Open the webpage
    driver.get(url)

    # Retrieve the complete HTML content
    html_content = driver.page_source

    li = list()
    titles_list = list()
    links_list = list()
    dates_list = list()

    # Now you can parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    aa = soup.find('tbody').find_all('tr')

    # To get publications in 2023
    for a in aa:    
        if year in a.text:
                li.append(a)

    monthDictv2 = {	1:'Jan',                           # Need new dictionary since this website uses short form of months. E.g., July = Jul
        2:'Feb',
        3:'Mar',
        4:'Apr',
        5:'May',
        6:'Jun',
        7:'Jul',
        8:'Aug',
        9:'Sep',
        10:'Oct',
        11:'Nov',
        12:'Dec'		}
    
    monthv2 = monthDictv2[datetime.now().month-1]

    preLink = 'https://www.bis.org'
                
    for b in li:
        if year in b.find('td',class_='item_date').text and monthv2 in b.find('td',class_='item_date').text:
            titles_list.append(b.find('div',class_='title').text)
            newLink = preLink + b.find('a',class_='dark',href=True)['href']
            links_list.append(newLink)
            dates_list.append(b.find('td',class_='item_date').text)

    # Close the webdriver
    driver.quit()

    for a in titles_list:
        titles.append(a)
    for b in links_list:
        links.append(b)
    for c in dates_list:
        dates.append(c)
        organisations.append('BCBS')

def fsb():
    url = 'https://www.fsb.org/publications/'

    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    results = soup.find_all('h3', class_='media-heading')
    li = list()

    for a in results:
        if month in a.find('span').text:
            li.append(a)

    for b in li:
        titles.append(b.find('a').text)
        links.append(b.find('a',href=True)['href'])
        dates.append(b.find('span', class_='media-date pull-right').text)
        organisations.append('FSB')

def isitc():
    dates_list = list()
    links_list = list()
    titles_list = list()

    driver = webdriver.Chrome()
    driver.get('https://isitc.org/news/in-the-news/')

    driver.implicitly_wait(5)

    # Get HTML code
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    driver.close()

    blocks = soup.find_all('div', class_='isitc-news-item')
    baseLink = 'https://isitc.org'

    for a in blocks:
        if month in a.find('h4').text.strip() and year in a.find('h4').text.strip(): 
            dates_list.append(a.find('h4').text.strip())
            titles_list.append(a.find('h3').text.strip())
            fullLink = baseLink + a.find('h3').find('a',href=True)['href']
            links_list.append(fullLink)

    for a in titles_list:
        titles.append(a)
    for b in links_list:
        links.append(b)
    for c in dates_list:
        dates.append(c)
        organisations.append('ISITC')
    
def fasb():
    titles_list = list()
    links_list = list()
    dates_list = list()

    url = 'https://www.fasb.org/Page/PageContent?PageId=/news-media/inthenews.html'

    try:
        page = requests.get(url) 
    except Exception as e:    
        print('Error with FASB link')
            
    soup = BeautifulSoup(page.text, "html.parser")
    blocks = soup.find('div', class_='year year-{yr}'.format(yr=year))

    for a in blocks.find_all('a'):
        titles_list.append(a.text)
        links_list.append(a['href'])
        
    pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2},\s\d{4}"
        
    for b in blocks:
        if re.search(pattern, b.text, re.MULTILINE) and len(b) > 5 and month in b and year in b:
            dates_list.append(b)
            
    for a in titles_list[0:len(dates_list)]:
        titles.append(a)
    for b in links_list[0:len(dates_list)]:
        links.append(b)
    for c in dates_list:
        dates.append(c)
        organisations.append('FASB')

def iso():
    url = 'https://www.iso.org/events_archive/x/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    blocks = soup.find_all('div', class_='media clearfix square')

    dates_list = list()
    links_list = list()
    titles_list = list()

    baseLink = 'https://www.iso.org'

    for a in blocks:
        date = a.find('time',class_='updated').text
        if month in date and year in date:
            t = (a.find('span', class_='entry-name').text)
            dates_list.append(date)
            titles_list.append(t)
            if 'https' not in a.find('div',class_='h5').find('a',href=True)['href']:
                fullLink = baseLink + a.find('div',class_='h5').find('a',href=True)['href']
                links_list.append(fullLink)
            else:
                links_list.append(a.find('a',href=True)['href'])

    for a in links_list[0:len(dates_list)]:
        links.append(a)
    for b in titles_list[0:len(dates_list)]:
        titles.append(b)
    for c in dates_list:
        dates.append(c)
        organisations.append('ISO')

def finra():
    base = "https://www.finra.org"
    url = 'https://www.finra.org/rules-guidance/notices'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    target_blank_links = soup.find_all('a', target='_blank')
    href_values = [link['href'] for link in target_blank_links]

    datetime_elements = soup.find_all(class_='datetime')
    datetime_values = [element.get_text() for element in datetime_elements]


    td_elements = soup.find_all("td", class_="views-field views-field-field-notice-title-tx")


    # Get the current date and time
    current_datetime = datetime.now()
    current_month = current_datetime.strftime('%B')

    container = dict()
    title_list = list()

    #Add into dictionary
    for href, dt in zip(href_values, datetime_values):
        if month in dt and year in dt:
            string = base + href
            container[string] = dt
        
        
    for td in td_elements:
        div = td.find("div")
        if div is not None:
            content = div.get_text(strip=True)
            title_list.append(content)
            
    title_list = title_list[:len(container.values())]

    for a in title_list:
        titles.append(a)
    for b in container.values():
        dates.append(b)
    for c in container.keys():
        links.append(c)
        organisations.append('FINRA')

def enisa():
    url = "https://www.enisa.europa.eu/news"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    link_elements = soup.find_all("a", class_="news-latest-link")
    date_elements = soup.find_all(class_="news-latest-date")
    title_element = soup.find_all(class_ = "news-latest-title")

    href_list = list()
    date_list = list()
    title_list = list()

    # Print the extracted links and dates
    for link, date, title in zip(link_elements, date_elements,title_element):
        href = link.get("href")
        dt = date.text.strip()
        t = title.text.strip()
        if year in dt and month in dt:
            href_list.append(href)
            date_list.append(dt)
            title_list.append(t)

    for a in title_list:
        titles.append(a)
    for b in href_list:
        links.append(b)
    for c in date_list:
        dates.append(c)
        organisations.append('ENISA')

def sec():
    url = 'https://www.sec.gov/news/speeches-statements'
    try:
        page = requests.get(url)
    except:
        print("Something is wrong with SEC link.")
    soup = BeautifulSoup(page.text, "html.parser")
    # blocks = soup.find_all('tr',class_=re.compile(r'speeches-list-page-row\s+(odd|even)'))
    blocks = soup.find('tbody')

    links_list = list()
    dates_list = list()
    titles_list = list()

    baseLink = 'https://www.sec.gov'

    dateBlock = blocks.find_all('time',class_='datetime')
    for a in dateBlock:
        aa = a.text.strip()
        if month in aa and year in aa:
            dates_list.append(aa)

    titlesAndLinks = blocks.find_all('a',href=True)
    for b in titlesAndLinks:
        titles_list.append(b.text.strip())
        fullLink = baseLink + b['href']
        links_list.append(fullLink)

    for i in titles_list[0:len(dates_list)]:
        titles.append(i)
    for j in links_list[0:len(dates_list)]:
        links.append(j)
    for q in dates_list:
        dates.append(q)
        organisations.append('SEC')

def eba():
    url = "https://www.eba.europa.eu/all-news-and-press-releases?page="
    counter = 0
    track = True
    href_list = list()
    date_list = list()
    title_list = list()
    base = "https://www.eba.europa.eu"

    # Send a GET request to the website
    while track:
        # link to page number
        track = False
        concat = url + str(counter)
        response = requests.get(concat)

        # Create a BeautifulSoup object to parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all <a> elements with class="list-group-item"
        link_elements = soup.find_all("a", class_="list-group-item")

        # Find all <div> elements with class="list-group-item SecondaryInfo"
        info_elements = soup.find_all("p", class_="list-group-item-text SecondaryInfo")
        
        title_elements = soup.find_all("h3", class_ ="list-group-item-heading")

        # Iterate over the extracted elements
        for link, info,title in zip(link_elements, info_elements,title_elements):
            href = link.get("href")
            text = info.text.strip()
            d = text[:10]
            date_object = datetime.strptime(d, "%d/%m/%Y")
            formatted_date = date_object.strftime("%d %B %Y")
            if year in formatted_date and month in formatted_date:
                track = True
                href_list.append(base+href)
                date_list.append(formatted_date)
                title_list.append(title.text.strip())
        counter += 1

    for a in title_list:
        titles.append(a)
    for b in date_list:
        dates.append(b)
    for c in href_list:
        links.append(c)
        organisations.append('EBA')

def ncsc():
    driver = webdriver.Chrome()

    # Open the URL
    url = "https://www.ncsc.gov.uk/section/keep-up-to-date/reports-advisories"
    driver.get(url)
    driver.implicitly_wait(5)
    button = driver.find_element(By.XPATH,"//*[text()='Accept optional cookies']")
    button.click()
    driver.implicitly_wait(5)

    # Get HTML code
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    div_element = soup.find_all('div', class_='pcf-article-content-item')
    driver.close()

    for a in div_element:
        if month in a.find('ul',class_='meta').text and year in a.find('ul',class_='meta').text:
            titles.append(a.find('h4', class_='pcf-results-item__title').text)
            links.append(a.find('a',href=True)['href'])
            dates.append(a.find('ul',class_='meta').text)
            organisations.append('NCSC')

def pra():
    url = "https://www.bankofengland.co.uk/news/prudential-regulation"

    # Set up the Selenium driver
    driver = webdriver.Chrome()

    driver.get(url)
    driver.implicitly_wait(5)
    button = driver.find_element(By.XPATH,"//button[contains(@class,'cookie__button btn btn-default btn-neutral')]")
    button.click()
    driver.implicitly_wait(5)

    # Get HTML code
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    div_element = soup.find_all('div', class_='col3')
    driver.close()

    baseLink = 'https://www.bankofengland.co.uk'

    for a in div_element:
        if a.find('time',class_='release-date') is not None:
            if month in a.find('time',class_='release-date').text and year in a.find('time',class_='release-date').text:
                titles.append(a.find('h3',class_='list exclude-navigation').text)
                fullLink = baseLink + a.find('a',href=True)['href']
                links.append(fullLink)
                dates.append(a.find('time',class_='release-date').text)
                organisations.append('PRA')




def main():
    us_fed()
    boj()
    ecb()
    boe()
    bcbs()
    cgfs()
    fsb()
    isitc()
    fasb()
    iso()
    finra()
    sec()
    enisa()
    eba()
    ncsc()
    pra()

main()
print(len(dates))
print(len(links))
print(len(titles))

d = {'Organisation': organisations, 'Title':titles, 'Link':links,'Date':dates}
df = pd.DataFrame(data=d)
df.to_csv(r'C:\Users\65936\\OneDrive\Desktop\MAS\\{date}.csv'.format(date=todayDate))