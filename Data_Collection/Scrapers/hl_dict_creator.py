#!/usr/bin/env python3

"""
Authors: Venkat Ramaraju, Jayanth Rao
Functionality implemented:
- methods to fetch headlines as a list from each news publication
Changes made by: Wenjie Xu
Changes made:
- Depricated some headline scrapers due to the sites employing ways to make scraping difficult.
- Depricated other headlines for lack of headline relevancy or not including a date feature.
- Made changes to other headline scrapers as the older code no longer works or other alternatives work better.
- Saved date feature of the headlines
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import dateparser
import time
import yfinance as yf

# Global data
nasdaq = pd.read_csv("nasdaq.csv", index_col=False)
nyse = pd.read_csv("nyse.csv", index_col=False)

nasdaq = nasdaq[['Symbol', 'Name']]
nyse = nyse[['Symbol', 'Name']]


# Each method below gathers and formats headlines for a specific stock ticker on a different website. At the end,
# is aggregated for sentiment analysis. We populate the dataset with the headline, and the link to it (so it can
# be clicked on in the interface).

def get_reuters_headlines(ticker: str, company_name:str):#depricate due to lack of relevancy, inability to search with ticker
    url = 'https://www.reuters.com/site-search/?query=' + ticker

    html_page = requests.get(url).text
    soup = BeautifulSoup(html_page, 'lxml')

    h3_tags = soup.find_all('h3', class_='search-result-title')
    print(list(h3_tags))
    reuters_hls = []

    for h3 in h3_tags:
        try:
            a = h3.find('a')
            hl_dict = {
                "ticker": ticker,
                "title": a.contents[0].replace("&amp;", "").strip(),
                "url": "https://reuters.com" + a.get('href'),
                "publisher": "Reuters"
            }
            reuters_hls.append(hl_dict)
        except Exception as e:
            print("Reuters:", e)
            continue

    deduped = []
    temp_hls = []
    for i in reuters_hls:
        if i['title'] not in temp_hls:
            temp_hls.append(i['title'])
            deduped.append(i)

    return deduped


def get_morningstar_headlines(ticker): #prohibits web scraping but does not actively enforce preventions
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    #print(requests.get('https://www.morningstar.com/stocks/xnys/pg/news', headers=headers).status_code)

    url = 'https://www.morningstar.com/stocks/xnas/' + ticker.lower() + '/news'
    #try xnys with stock that didn't work
    response = requests.get(url,headers=headers)


    if response.status_code//100 == 4:
        url = 'https://www.morningstar.com/stocks/xnys/' + ticker.lower() + '/news'
        print('morningstar(xnas) 404 for', ticker)
        response = requests.get(url,headers=headers)
    if(response.status_code//100 == 4):
        print('morningstar(xnys) 404 for', ticker, 'Failed.. Next')

    html_page = response.text
    soup = BeautifulSoup(html_page, 'lxml')

    links = soup.find_all('a', class_="mdc-link__mdc mdc-link--no-underline__mdc")
    times = soup.find_all('time',class_="mdc-locked-text__mdc mdc-date")

    ms_hls = []
    for i in range(len(links)):
        try:
            headlineDate = datetime.strptime(str(times[i].get('datetime')), "%Y-%m-%dT%H:%M:%S.%fZ")
            href = links[i].get('href')
            title = links[i].contents[0].strip()
            hl_dict = {
                "ticker": ticker,
                "title": title.replace("&amp;", "").strip(),
                "url": "https://morningstar.com" + href,
                "publisher": "Morningstar",
                "date" : headlineDate
            }

            ms_hls.append(hl_dict)
        except Exception as e:
            print("MS:", e)
            continue

    deduped = []
    temp_hls = []
    for i in ms_hls:
        if i['title'] not in temp_hls:
            temp_hls.append(i['title'])
            deduped.append(i)
    return deduped


def get_google_finance_headlines(ticker): #Depricate due to not allowing scraping and also makes it difficult.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    url = 'https://www.google.com/finance/quote/' + ticker.upper() + ":NASDAQ"
    #try xnys with stock that didn't work
    response = requests.get(url,headers=headers)

    if response.status_code//100 == 4:
        url = 'https://www.google.com/finance/quote/' + ticker.upper() + ":NYSE"
        print('google(nasdaq) 404 for', ticker)
        response = requests.get(url,headers=headers)
    if(response.status_code//100 == 4):
        print('google(nyse) 404 for', ticker, 'Failed.. Next')
    time.sleep(5)
    html_page = response.text
    soup = BeautifulSoup(html_page, 'lxml')

    sections = soup.find_all('div', class_='z4rs2b')
    
    print(sections)
    gf_hls = []
    for sec in sections:
        try:
            link = sec.find('a', {'rel': 'noopener noreferrer'})
            title = link.find('div', class_='Yfwt5').contents[0].strip()

            hl_dict = {
                "ticker": ticker,
                "title": title.replace("\n", "").replace("&amp;", "").strip(),
                "url": link.get('href'),
                "publisher": "Google Finance"
            }

            gf_hls.append(hl_dict)
        except Exception as e:
            print("GF:", e)
            continue

    deduped = []
    temp_hls = []
    for i in gf_hls:
        if i['title'] not in temp_hls:
            temp_hls.append(i['title'])
            deduped.append(i)

    return deduped


def get_business_insider_headlines(ticker): #prohibits web scraping but does not actively enforce preventions
    url = 'https://markets.businessinsider.com/stocks/' + ticker.lower() + '-stock'

    html_page = requests.get(url).text
    soup = BeautifulSoup(html_page, 'lxml')

    olinks = soup.find_all('a', class_="instrument-stories__link")
    times = soup.find_all('time', class_="instrument-stories__date")
    links=[]
    hrefs=[]
    for l in olinks:
        if len(l.get_text())!=0 and l.get('href') not in hrefs:
            hrefs.append(l.get('href'))
            links.append(l)
    bi_hls = []
    for i in range(len(links)):
        try:
            headlineDate = datetime.strptime(str(times[i].get('datetime')), '%Y-%m-%d %H:%M')
            
            if links[i].get('href')[0] == '/':
                link = "https://markets.businessinsider.com" + links[i].get('href')
            else:
                link = links[i].get('href')
                
            #if (datetime.now() - headlineDate).days <= 7:
            hl_dict = {
                "ticker": ticker,
                "title": links[i].contents[0].replace("&amp;", "").strip(),
                "url": link,
                "publisher": "Business Insider",
                "date" : headlineDate
            }
            bi_hls.append(hl_dict)
                
        except Exception as e:
            print("BI:", e)
            continue

    deduped = []
    temp_hls = []
    for i in bi_hls:
        if i['title'] not in temp_hls:
            temp_hls.append(i['title'])
            deduped.append(i)

    return deduped


def get_cnn_headlines(ticker):#prohibits web scraping but does not actively enforce preventions
    url = 'https://money.cnn.com/quote/news/news.html?symb=' + ticker

    html_page = requests.get(url).text
    soup = BeautifulSoup(html_page, 'lxml')

    links = soup.find_all('a', class_="markets-company-news__item")

    cnn_hls = []

    for link in links:
        try:
            hl_dict = {
                "ticker": ticker,
                "title": link.find('span', class_='markets-company-news__item--title').contents[0].replace("&amp;", "").strip(),
                "url": link.get('href'),
                "publisher": "CNN",
                "date" : datetime.strptime(str(link.find('span', class_='markets-company-news__item--day').contents[0]),"%b %d").replace(year=datetime.now().year)
            }

            cnn_hls.append(hl_dict)
        except Exception as e:
            print("CNN:", e)
            continue

    deduped = []
    temp_hls = []
    for i in cnn_hls:
        if i['title'] not in temp_hls:
            temp_hls.append(i['title'])
            deduped.append(i)

    return deduped

#switched to API instead
def get_yahoo_headlines(ticker):   #Try headlines api. also -https://stackoverflow.com/questions/46922415/does-yahoo-finance-ban-web-scrapy-or-not
    
    stock = yf.Ticker(ticker)
    
    news = stock.news
    
    yf_hls = []
    
    for item in news:
        try:
            hl_dict = {
                "ticker": ticker,
                "title": item['title'].replace("&amp;", "").strip(),
                "url": item['link'],
                "publisher": "Yahoo! Finance",
                "date" : datetime.fromtimestamp(item['providerPublishTime'])
            }

            yf_hls.append(hl_dict)
        except Exception as e:
            print("YF:", e)
            continue

    return yf_hls


def get_cnbc_headlines(ticker): #prohibits web scraping but does not actively enforce preventions
    url = 'https://www.cnbc.com/quotes/'+ticker.upper()+'?qsearchterm=' + ticker.lower()

    html_page = requests.get(url).text
    soup = BeautifulSoup(html_page, 'lxml')
    links = soup.find_all("a", class_="LatestNews-headline")
    dates = soup.find_all("time", class_="LatestNews-timestamp")

    cnbc_hls = []
    for i in range(len(links)):
        try:
            hl_dict = {
                "ticker": ticker,
                "title": links[i].contents[0].replace("&amp;", "").strip(),
                "url": links[i].get('href'),
                "publisher": "CNBC",
                "date": dateparser.parse(dates[i].contents[0])
            }

            cnbc_hls.append(hl_dict)
        except Exception as e:
            print("CNBC:", e)
            continue

    return cnbc_hls

