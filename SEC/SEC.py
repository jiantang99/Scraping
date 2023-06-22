#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from datetime import datetime
import os


# In[3]:


href_list = list()
date_list = list()

url = 'https://www.sec.gov/news/speeches-statements'
base = 'https://www.sec.gov'
response = requests.get(url)
soup = soup(response.content, 'html.parser')

# Find the <body> element
body = soup.find('tbody')


# Find all the <a> elements within the <tbody> element and extract the href values
href_values = [a['href'] for a in body.find_all('a', href=True)]

# Find all the elements with class = datetime
datetime_elements = soup.find_all(class_='datetime')
datetime_values = [element.get_text() for element in datetime_elements]


# Get the current date and time
current_datetime = datetime.now()
current_month = current_datetime.strftime('%B')
current_year = str(current_datetime.year)

# Append to List
for href,dt in zip(href_values,datetime_values):
  if "/news" in href and current_month in dt and current_year in dt:
    link = base + href
    href_list.append(link)
    date_list.append(dt)


df = pd.DataFrame( { "Organisation": ["SEC" for i in href_list],
                    "Date" : date_list,
                    "Link" : href_list })

current = os.getcwd().replace("\\", "/")
file_path = "/Downloads/"
# Save to Downloads Folder
save_string = "SEC_updates.xlsx"
df.to_excel(save_string, index = False)


# In[ ]:




