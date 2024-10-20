#!/usr/bin/env python3

"""
Authors: Venkat Ramaraju, Jayanth Rao
Functionality implemented:
- Generates and aggregates polarities across headlines and conversations
Changes made by: Wenjie Xu
Changes made:
- No longer uses twitter
- When no conversation sentiment is present, then use sentiment of entire stock market.
"""

# Libraries and Dependencies
import os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('vader_lexicon')
#import tweepy

# Global Variables
sia = SentimentIntensityAnalyzer()
lemmatizer = WordNetLemmatizer()
conversations_map = {}
conversation_delta = {}
headlines_map = {}
headlines_delta = {}
convoSentimentSumCount=[0.0,0.0]
convoSentimentSumCountL2D=[0.0,0.0]


def update_stock_terminology():
    """
    Creates dictionary with updated terminologies for SentimentIntensityAnalyzer. Includes positive and negative words,
    along with polarized words with weights. Used to improve VADER accuracy.
    """
    stock_lexicon = {}
    csv_df = pd.read_csv('setup_csvs/polarized_stock_lex.csv')
    for index, row in csv_df.iterrows():
        stock_lexicon[row['word']] = row['polarity']

    # Updates existing dictionary with stock-related terms
    resulting_lex = {}
    resulting_lex.update(stock_lexicon)
    resulting_lex.update(sia.lexicon)
    sia.lexicon = resulting_lex


def get_headline_sentiments():
    """
    Analyze polarities of the given stock tickers, based on terminologies inserted in SentimentIntensityAnalyzer.
    Prints out the aggregated results to CSV.
    """
    headlines_csv = pd.read_csv("../Data_Collection/headlines.csv")
    headlines_csv['Date'] = pd.to_datetime(headlines_csv['Date'])
    sum_of_polarities = {}
    count_of_headlines = {}

    # Aggregates data across headlines
    for index, row in headlines_csv.iterrows():
        try:
            lemma_text = lemmatizer.lemmatize(str(row['Headline']))
            scores = sia.polarity_scores(lemma_text)
            row["Polarity"] = scores["compound"]

            if row['Ticker'] not in sum_of_polarities:
                sum_of_polarities[row['Ticker']] = scores["compound"]
                count_of_headlines[row['Ticker']] = 1
                latestHeadline = row['Headline']
                latestDate = row['Date']
                latest = scores["compound"]
                headlines_delta[row['Ticker']] = 0 
                flag = True
            else:
                if flag:
                    latestDate2 = row['Date']
                    flag = False
                    headlines_delta[row['Ticker']] = latest-scores["compound"]
                if latestDate <= row['Date'] and not latestHeadline == row['Headline']:
                    headlines_delta[row['Ticker']] = scores["compound"] - latest
                    latestHeadline = row['Headline']
                    latestDate2 = latestDate
                    latest = scores["compound"]
                    latestDate = row['Date']
                elif latestDate2 < row['Date'] and not latestHeadline == row['Headline']:
                    headlines_delta[row['Ticker']] = latest-scores["compound"]
                    latestDate2 = row['Date']
                    
                sum_of_polarities[row['Ticker']] = sum_of_polarities[row['Ticker']] + scores["compound"]
                count_of_headlines[row['Ticker']] = count_of_headlines[row['Ticker']] + 1
        except RuntimeError as e:
            print(e, "was handled")

    for ticker in sum_of_polarities:
        headlines_map[ticker] = sum_of_polarities[ticker]/count_of_headlines[ticker]


def generate_aggregated_csv():
    """
    Generates a CSV with the aggregated polarities of headlines for the group of stocks that are being analyzed. In
    the case where no conversations are available for a given stock, we default to Twitter conversations for our
    analysis.
    """
    aggregated_df = pd.DataFrame(columns=["Ticker", "Conversations", "Headlines"])

    # Outputs aggregated headlines and conversations to a CSV.
    for ticker, headlines_polarity in headlines_map.items():
        try:
            if ticker in conversations_map:
                if conversations_map[ticker] == -5:
                    polarity = convoSentimentSumCount[0]/convoSentimentSumCount[1]
                    convoL2D = convoSentimentSumCountL2D[0]/convoSentimentSumCountL2D[1]
                else:
                    polarity = conversations_map[ticker]
                    convoL2D = conversation_delta[ticker]
            else:
                polarity = convoSentimentSumCount[0]/convoSentimentSumCount[1]
                convoL2D = convoSentimentSumCountL2D[0]/convoSentimentSumCountL2D[1]
            row = {"Ticker": ticker, "Conversations": polarity, "Headlines": headlines_polarity, "HeadlinesL2Delta": headlines_delta[ticker], "ConversationL2Delta": convoL2D}
            aggregated_df = aggregated_df._append(row, ignore_index=True)
        except RuntimeError as e:
            print(e, "was handled")

    aggregated_df.to_csv("aggregated_polarities.csv")


def get_conversation_sentiments():
    """
    Generates a CSV with the aggregated polarities of conversations for the group of stocks that are being analyzed.
    """
    list_of_conversations = [f for f in os.listdir('../Data_Collection/Conversations/') if f.endswith('.csv')]
    sum_of_polarities = {}
    count_of_conversations = {}

    # Aggregates data across conversations
    for ticker_csv in list_of_conversations:
        conversations_csv = pd.read_csv('../Data_Collection/Conversations/' + str(ticker_csv))
        conversations_csv['Date'] = pd.to_datetime(conversations_csv['Date'])
        ticker = ticker_csv.split("_")[0].upper()
        for index, row in conversations_csv.iterrows():
            try:
                lemma_text = lemmatizer.lemmatize(str(row['Conversation']))
                scores = sia.polarity_scores(lemma_text)
                row["Polarity"] = scores["compound"]

                if ticker not in sum_of_polarities:
                    sum_of_polarities[ticker] = scores["compound"]
                    count_of_conversations[ticker] = 1
                    latest = scores["compound"]
                    conversation_delta[ticker] = 0 
                    flag = True
                else:
                    if flag: #since conversations are already ordered by date.
                        conversation_delta[ticker] = latest - scores["compound"]
                        flag = False
                    sum_of_polarities[ticker] = sum_of_polarities[ticker] + scores["compound"]
                    count_of_conversations[ticker] = count_of_conversations[ticker] + 1
            except RuntimeError as e:
                print(e, "was handled")

        if count_of_conversations[ticker] > 0:
            conversations_map[ticker] = sum_of_polarities[ticker]/count_of_conversations[ticker]
            convoSentimentSumCount[0] += conversations_map[ticker]
            convoSentimentSumCount[1] += 1
            convoSentimentSumCountL2D[0] += conversation_delta[ticker]
            convoSentimentSumCountL2D[1] += 1
        else:
            conversations_map[ticker] = -5 #arbitrary number outside possible range of sentiment scores


def twitter_sentiment(ticker):
    """
    Gathers 100 tweets related to a specific stock ticker and runs the VADER sentiment analysis model on it to
    generate a polarity scores.
    :param ticker: Name of stock ticker.
    :return: Aggregated polarity value for conversations on twitter.
    """

    # Credentials
    api_key = ""
    api_secret_key = ""
    access_token = ""
    access_token_secret = ""

    # API calls
    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    stock = "$" + ticker
    search_results = api.search(q=stock, count=100)

    # Aggregating data
    print("Conversations on ", stock)
    polarity_sum = 0
    count = 0
    for tweet in search_results:
        lemma_text = lemmatizer.lemmatize(str(tweet.text))
        scores = sia.polarity_scores(lemma_text)
        polarity_sum += scores["compound"]
        count += 1

    return polarity_sum/count


def main():
    update_stock_terminology()
    get_headline_sentiments()
    get_conversation_sentiments()
    generate_aggregated_csv()


if __name__ == "__main__":
    main()
