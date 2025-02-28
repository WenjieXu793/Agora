#!/usr/bin/env python3

"""
Authors: Venkat Ramaraju, Jayanth Rao
Functionality implemented:
- Scraper that retrieves conversations from multiple online web sources
- Formats and outputs conversations in a Pandas table
Changes made by: Wenjie Xu
Changes made:
- Removed no longer used libraries
- Source changed from yahoo finance to seeking alpha due to yahoo employing ways to discourage web scraping
- Records date of conversations for future processing.
"""

# Libraries and Dependencies
import demoji
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
from pathlib import Path
from selenium.webdriver.chrome.service import Service
import time

# Setup
demoji.download_codes()


def get_seeking_alpha_conversations(stock): 
    """
    Parses seeking alpha finance conversations page to get conversations related to the stock.
    """
    option = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

    # Open the webpage
    url = 'https://seekingalpha.com/symbol/' + stock + '/comments'
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    req = requests.get('https://seekingalpha.com/symbol/' + stock + '/comments')
    soup = BeautifulSoup(req.content, 'html.parser')
    driver.quit()
    stonk = soup.findAll(class_ = 'mb-12 break-words md:text-medium-3-r')
    dates = soup.findAll(class_ = 'wlPdr flex items-center whitespace-nowrap text-right text-small-r text-black-35')
    stockComments = []
    sCommDates = []
    finDates = []

    for s in stonk: #Parses comments and dates
        stockComments.append(s.get_text())
    for d in dates:
        sCommDates.append(d.get_text())
    for d in sCommDates: #gets date
        if d[0:1]=="Y": #If the 
            finDates.append(datetime.today())
        elif(d[0:1] !="V" and d[-1] != "M"): #Parses out the time using 'M' in AM/PM. Parses out View using V
            finDates.append(datetime.strptime(str(d), '%b. %d, %Y'))
        
    return stockComments, finDates


def get_all_conversations(stock):
    """
    Gets conversations from various sources, concatenates the arrays of conversations, cleans up the text and returns
    the overall array.
    :param stock: Name of stock ticker.
    :return: Overall array of conversations from various sources after cleaning (Removal of punctuations).
    """
    seeking_alpha_conversations, dates = get_seeking_alpha_conversations(stock)
    ret = []
    if len(seeking_alpha_conversations) == 0:
        return []
    for i in range(len(dates)):
        ret.append([seeking_alpha_conversations[i],dates[i]])
    return ret


def output(overall_data, stock):
    """
    Prints out the pandas dataframe after removing duplicates.
    :param overall_data: Array of headlines/conversations after retrieving from respective web sources, in text form.
    :param stock: Name of the stock for which all the above data is being retrieved.
    :return None.
    """
    # Removes duplicates by first converting to hash set (Stores only unique values), then converts back to list
    # overall_data = list(set(overall_data))
    file_path = str(Path(__file__).resolve().parents[1]) + '/Conversations/' + stock.upper() + '_conversations.csv'

    if len(overall_data) > 0:
        # Formatting current dataframe, merging with previously existing (if it exists)
        title = 'Conversation'
        dates = 'Date'
        overall_dataframe = pd.DataFrame(overall_data, columns=[title, dates])
        overall_dataframe[title] = overall_dataframe[title].apply(demoji.replace)
        overall_dataframe.to_csv(file_path, index=False)
    else:
        print("Invalid ticker/company or no headlines/conversations available.")


def main():
    # Tickers and companies
    stocks_df = pd.read_csv("../companies.csv")
    stocks_dict = {}

    for index, row in stocks_df.iterrows():
        stocks_dict.update(
            {row["Symbol"]: row["Company"]}
        )

    tickers = list(stocks_dict.keys())
    total = len(tickers)
    i = 0
 
    for stock in tickers:
        print("\n\n===================================================================")
        print("Getting conversations for:", stock, "    (", i+1, "/", total, ")")  #To show the progress of the scraping
        i+=1
        try:
            overall_conversations = get_all_conversations(stock)
            output(overall_conversations, stock)
        except RuntimeError as e:
            print(e, "was handled")


if __name__ == "__main__":
    main()
