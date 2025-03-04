#!/usr/bin/env python3

"""
Authors: Venkat Ramaraju, Jayanth Rao
Functionality implemented:
- Retrieves aggregated polarities from sentiment analysis and compiles stock-table metrics generated by yfinance.
- Runs the picked machine learning model to generate overall dataset that will be used by the flask app at runtime.
Updated by: Wenjie Xu
Changes made:
- Updated some lines of code due to library updates.
- Kept Stock conversations for creating new or changing current features.
"""

# Libraries and Dependencies
import pandas as pd
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics
from sklearn.model_selection import train_test_split

pd.set_option("display.max_rows", None, "display.max_columns", None)

# Global data
aggregated_polarities = pd.read_csv("../Polarity_Analysis/aggregated_polarities.csv")
all_companies_data = pd.read_csv("output_csvs/final_db.csv")


def merge_polarities_with_all_stocks():
    """
    Merges the dataframes that were generated in previous steps to include the polarity analysis from the Sentiment
    Analysis component.
    """
    # append headline and convo polarity columns
    global aggregated_polarities
    global all_companies_data

    all_companies_data["headline_polarity"] = np.nan
    all_companies_data["convo_polarity"] = np.nan
    all_companies_data["last2PolarityDeltaConvo"] = np.nan
    all_companies_data["last2PolarityDeltaHead"] = np.nan
    all_companies_data["HeadlinesR2"] = np.nan
    all_companies_data["ConversationR2"] = np.nan
    all_companies_data["HeadlinePascal"] = np.nan
    all_companies_data["ConversationPascal"] = np.nan

    for index, row in aggregated_polarities.iterrows():
        company_row = all_companies_data.loc[all_companies_data["Symbol"] == row["Ticker"]]

        #all_companies_data["headline_polarity"][company_row.index.item()] = round(row["Headlines"], 2)
        #all_companies_data["convo_polarity"][company_row.index.item()] = round(row["Conversations"], 2)
        all_companies_data.loc[company_row.index.item(), "convo_polarity"] = round(row["Conversations"], 2)
        all_companies_data.loc[company_row.index.item(), "headline_polarity"] = round(row["Headlines"], 2)
        all_companies_data.loc[company_row.index.item(), "last2PolarityDeltaConvo"] = round(row["ConversationL2Delta"], 2)
        all_companies_data.loc[company_row.index.item(), "last2PolarityDeltaHead"] = round(row["HeadlinesL2Delta"], 2)
        all_companies_data.loc[company_row.index.item(), "HeadlinesR2"] = round(row["HeadlinesR2"], 2)
        all_companies_data.loc[company_row.index.item(), "ConversationR2"] = round(row["ConversationR2"], 2)
        all_companies_data.loc[company_row.index.item(), "HeadlinePascal"] = round(row["HeadlinePascal"], 2)
        all_companies_data.loc[company_row.index.item(), "ConversationPascal"] = round(row["ConversationPascal"], 2)


def fetch_metrics_for_all_stocks():
    """"
    Populates a dictionary with 8 metrics for 4400 stocks across NASDAQ and NYSE. This leverages the csv that was
    generated by the fetch_stock_metrics.py script.
    """
    # generate ticker stock metrics for all tickers in all_companies_data (~4400)
    global all_companies_data

    stock_metric_data = pd.read_csv("output_csvs/stock_metric_data.csv")

    metrics = ['beta', 'profitMargins', 'forwardEps', 'bookValue', 'heldPercentInstitutions',
               'shortRatio', 'shortPercentOfFloat']

    all_companies_data = all_companies_data.reindex(columns=all_companies_data.columns.tolist() + metrics)

    for index, row in stock_metric_data.iterrows():
        company_row = all_companies_data.loc[all_companies_data["Symbol"] == row["Symbol"]]

        #all_companies_data["beta"][company_row.index.item()] = row["beta"]
        #all_companies_data["profitMargins"][company_row.index.item()] = row["profitMargins"]
        #all_companies_data["forwardEps"][company_row.index.item()] = row["forwardEps"]
        #all_companies_data["bookValue"][company_row.index.item()] = row["bookValue"]
        #all_companies_data["heldPercentInstitutions"][company_row.index.item()] = row["heldPercentInstitutions"]
        #all_companies_data["shortRatio"][company_row.index.item()] = row["shortRatio"]
        #all_companies_data["shortPercentOfFloat"][company_row.index.item()] = row["shortPercentOfFloat"]
        
        all_companies_data.loc[company_row.index.item(), "beta"] = row["beta"]
        all_companies_data.loc[company_row.index.item(), "profitMargins"] = row["profitMargins"]
        all_companies_data.loc[company_row.index.item(), "forwardEps"] = row["forwardEps"]
        all_companies_data.loc[company_row.index.item(), "bookValue"] = row["bookValue"]
        all_companies_data.loc[company_row.index.item(), "heldPercentInstitutions"] = row["heldPercentInstitutions"]
        all_companies_data.loc[company_row.index.item(), "shortRatio"] = row["shortRatio"]
        all_companies_data.loc[company_row.index.item(), "shortPercentOfFloat"] = row["shortPercentOfFloat"]


def generate_predictions():
    """
    Runs the pickled machine learning model on the final dataset that is generated from the workflow. The output from
    this method is used to create the overall dataset that is read in at runtime from the flask application.
    """
    global all_companies_data

    training_rows = all_companies_data[~all_companies_data['headline_polarity'].isnull() &
                                       ~all_companies_data['convo_polarity'].isnull()].drop(columns=['last2PolarityDeltaHead', 'last2PolarityDeltaConvo','ConversationR2','HeadlinesR2','HeadlinePascal','ConversationPascal'])

    del training_rows['Unnamed: 0']
    del training_rows['Name']
    del training_rows['Analyst']

    all_companies_data["agora_pred"] = np.nan

    training_rows = training_rows.dropna()

    # load the pre-trained model
    lr_model = pickle.load(open('pickle_model.sav', 'rb'))

    training_rows['headline_polarity'] = training_rows['headline_polarity'] * 2
    training_rows['convo_polarity'] = training_rows['convo_polarity'] * 2

    x_total = training_rows[[x for x in training_rows.columns if x not in ['Buy', 'Symbol']]]
    y_total = training_rows["Buy"]

    X_train, X_test, y_train, y_test = train_test_split(x_total, y_total, test_size=0.33, random_state=42)

    # get the predictions for all stocks with headlines/convos
    predictions = lr_model.predict(x_total)

    y_predictions = lr_model.predict(X_test)
    test_acc_score = metrics.accuracy_score(y_test, y_predictions)

    # create a confusion matrix
    cm = metrics.confusion_matrix(y_total, predictions)
    plt.figure(figsize=(9, 9))
    sns.heatmap(cm, annot=True, fmt=".1f", linewidths=.5, square=True, cmap='Blues_r')
    plt.ylabel('Actual Ratings')
    plt.xlabel('Predicted Ratings')
    all_sample_title = 'Accuracy Score: {0}'.format(test_acc_score)
    plt.title(all_sample_title, size=15)
    plt.show()

    training_rows["agora_pred"] = predictions

    # append to the full dataset
    for index, row in training_rows.iterrows():
        company_row = all_companies_data.loc[all_companies_data["Symbol"] == row["Symbol"]]
        #all_companies_data["agora_pred"][company_row.index.item()] = row["agora_pred"]
        all_companies_data.loc[company_row.index.item(), "agora_pred"] = row["agora_pred"]


def cleanup_conversations():
    """
    Clean up conversations file to keep repository lighter.
    """
    conversations_dir = '../Data_Collection/Conversations'
    for f in os.listdir(conversations_dir):
        if f.endswith('csv'):
            os.remove(os.path.join(conversations_dir, f))


def main():
    global all_companies_data
    # take aggregated_polarities.csv from /Polarity_Analysis/ and append to overall company list
    merge_polarities_with_all_stocks()

    # fetch the stock metrics for each of the stocks
    fetch_metrics_for_all_stocks()

    # at this point, all_companies_data should have the 7 stock metrics + headline/convo polarities
    # generate ML predictions for the tickers that have headline/convo polarities
    generate_predictions()

    # output of overall dataset
    all_companies_data.to_csv("final_dataset.csv")
    
    # Clean up conversations file to keep repository lighter
    # WX Changes: kept conversations so that other features can be created.
    #cleanup_conversations()


if __name__ == "__main__":
    main()
