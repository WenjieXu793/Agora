#!/usr/bin/env python
# coding: utf-8

"""
Authors: Wenjie Xu
Functionality implemented:
- Appends to a file instead of rewriting it in case of connection errors with the first script.
"""

import pandas
from yahooquery import Ticker
import csv
import os
import pandas as pd
import time

all_comps = pd.read_csv("output_csvs/final_db.csv", index_col=0)


def get_stock_metrics(company_df: pandas.DataFrame):
    """
    Populates a dataset using metrics for a group of tickers.
    :param company_df: Dataframe with list of stock tickers for which metrics need to be queried
    """
    # Selected columns (From feature selection)
    new_columns = ['beta', 'profitMargins', 'forwardEps', 'bookValue', 'heldPercentInstitutions',
                   'shortRatio', 'shortPercentOfFloat']

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
    i = 4089
    while i-1< total:
        index = i-1
        row = company_df.loc[i-1]
        
        symbol = ''.join(row["Symbol"].split())
        

        print("Getting metrics for:", symbol, "      (", i, "/", total, ")")
        try:
            ticker = Ticker(symbol)
            data = ticker.key_stats
                
            if data[symbol] != ("Quote not found for ticker symbol: ", symbol):
                #print(data[symbol])
                for col in new_columns:
                    if col in str(data):
                        
                        if data[symbol][col] is not None:
                            company_df.at[index, col] = round(data[symbol][col], 2)
                        else:
                            company_df.at[index, col] = None
            else:
                with open("NoMetrics.csv", mode='a', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(symbol)
        except ConnectionError as e:
            print(e, "handled")
            time.sleep(5)
            continue
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
