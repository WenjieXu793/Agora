#!/usr/bin/env python
# coding: utf-8

"""
Authors: Venkat Ramaraju, Jayanth Rao
Functionality implemented:
- Prepares data for model training from the yFinance API
Changes made by: Wenjie Xu
Changes made:
- yfinance did not support many of the required features. Found a new API called yahooquery that does.
"""

import pandas
from yahooquery import Ticker
import csv
import os
import pandas as pd

all_comps = pd.read_csv("output_csvs/final_db.csv", index_col=0)


def get_stock_metrics(company_df: pandas.DataFrame):
    """
    Populates a dataset using metrics for a group of tickers.
    :param company_df: Dataframe with list of stock tickers for which metrics need to be queried
    """
    # Selected columns (From feature selection)
    new_columns = ['beta', 'profitMargins', 'forwardEps', 'bookValue', 'heldPercentInstitutions',
                   'shortRatio', 'shortPercentOfFloat']
    with open("stock_metric_data_TEST.csv", mode='w', newline='') as file:
        file.write("Symbol,beta,profitMargins,forwardEps,bookValue,heldPercentInstitutions,shortRatio,shortPercentOfFloat\n")
    with open("NoMetrics.csv", mode='w', newline='') as file:
        file.write("Symbol\n")

    del company_df["Name"]
    del company_df["Buy"]
    del company_df["Analyst"]

    company_df = company_df.reindex(columns=company_df.columns.tolist() + new_columns)
    file_exists = os.path.isfile("stock_metric_data_TEST.csv")
    for column in new_columns:
        company_df[column] = None
    company_df.to_csv("stock_metric_data.csv")
    # Building the CSV
    total = len(company_df)
    i = 1
    for index, row in company_df.iterrows():
        
        symbol = ''.join(row["Symbol"].split())
        ticker = Ticker(symbol)
        data = ticker.key_stats

        print("Getting metrics for:", symbol, "      (", i, "/", total, ")")
        try:
                
            if data[symbol] != ("Quote not found for ticker symbol: ", symbol):
                #print(data[symbol])
                for col in new_columns:
                    if col in str(data):
                        
                        if data[symbol][col] is not None:
                            company_df.at[index, col] = round(data[symbol][col], 2)
                        else:
                            company_df.at[index, col] = None
            else:
                with open("NoMetrics.csv", mode='a', newline='') as csv_file: # Put stocks  that I couldnt find metrics for here.
                    writer = csv.writer(csv_file)
                    writer.writerow(symbol)
        except (KeyError, RuntimeError) as e:
            with open("NoMetrics.csv", mode='a', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(symbol)
            print(e, "was handled")
        company_df.loc[[i-1]].to_csv("stock_metric_data_TEST.csv", mode='a', header=not file_exists, index=False)
        print(company_df.loc[[i-1]])
        i+=1
    company_df.to_csv("stock_metric_data.csv")


def main():
    get_stock_metrics(all_comps)


if __name__ == "__main__":
    main()
