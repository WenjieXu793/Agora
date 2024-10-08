"""
Author: Wenjie Xu    
Description:
- Created to test changes made to headline scraper code. 
"""
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
#ticker = 'pg'
import hl_dict_creator

hl_list = hl_dict_creator.get_yahoo_headlines("aapl")
for hl in hl_list:
    hl_tuple = (hl['title'], hl['url'], hl['publisher'])
    print('title', hl['title'])
    print('url', hl['url'])
    print(hl['date'])
    print()
