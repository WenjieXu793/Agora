#!/usr/bin/env python3

"""
Authors: Venkat Ramaraju, Jayanth Rao
Functionality implemented:
- Scraper that retrieves conversations from multiple online web sources
- Formats and outputs conversations in a Pandas table
"""

# Libraries and Dependencies
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from headlines_scraper import create_array, output
import numpy as np


def get_yahoo_conversations(stock):
    url = "https://finance.yahoo.com/quote/" + stock + "/community?p=" + stock

    # Selenium Web Driver to click load more button and continue to retrieve conversation
    option = webdriver.ChromeOptions()
    option.add_argument('headless')     # Runs without opening browser
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)
    driver.get(url)

    i = 0
    while i < 20:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="canvass-0-CanvassApplet"]/div/button'))).click()

        i += 1

    # Retrieving soup after load more button is clicked
    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.quit()

    return create_array(soup.find_all('div', class_='C($c-fuji-grey-l) Mb(2px) Fz(14px) Lh(20px) Pend(8px)'))


def get_all_conversations(stock):
    """
    Gets conversations from various sources, concatenates the arrays of conversations, cleans up the text and returns
    the overall array.
    :param stock: Name of stock ticker.
    :return: Overall array of conversations from various sources after cleaning (Removal of punctuations).
    """

    yahoo_conversations = np.array(get_yahoo_conversations(stock))

    return list(np.concatenate(yahoo_conversations, axis=None))


def main():
    # Tickers and companies
    stocks = ["TSLA", "NFLX", "AAPL"]

    for stock in stocks:
        overall_conversations = get_all_conversations(stock)
        output(overall_conversations, stock, "conversations")


if __name__ == "__main__":
    main()
