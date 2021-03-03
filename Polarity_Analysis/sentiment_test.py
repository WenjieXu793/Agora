from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import os
from nltk.stem import WordNetLemmatizer

##############################################################
# TODO:
#   - Start looking at what a weighted average would look like
##############################################################

# Global Variables
sia = SentimentIntensityAnalyzer()
lemmatizer = WordNetLemmatizer()


def update_stock_terminology():
    """
    Creates dictionary with updated terminologies for SentimentIntensityAnalyzer. Includes positive and negative words,
    along with polarized words with weights. Used to improve VADER accuracy
    """
    stock_lexicon = {}
    csv_df = pd.read_csv('setup_csvs/new_stock_lex.csv')
    for index, row in csv_df.iterrows():
        stock_lexicon[row['Item']] = row['Polarity']

    csv_df = pd.read_csv('setup_csvs/modified_stock_lex.csv')
    for index, row in csv_df.iterrows():
        stock_lexicon[row['Word']] = row['Polarity']

    resulting_lex = {}
    resulting_lex.update(stock_lexicon)
    resulting_lex.update(sia.lexicon)
    sia.lexicon = resulting_lex


def get_sentiments():
    """
    Analyze polarities of the given stock tickers, based on  terminologies inserted in SentimentIntensityAnalyzer.
    Prints out the analysis.
    """
    file_path = "../Data_Collection/CSV_Results/"
    
    all_csv_results = [f for f in os.listdir("../Data_Collection/CSV_Results/") if f.endswith("csv")]
    print("Analysis:\n")
    for csv in all_csv_results:
        csv_df = pd.read_csv(file_path + csv)
        csv_df["Polarity"] = ""

        avg = 0.0
        rows = 0
        zero, positive, negative = 0, 0, 0

        for index, row in csv_df.iterrows():
            lemma_text = lemmatizer.lemmatize(row[csv_df.columns[0]])
            scores = sia.polarity_scores(lemma_text)
            row["Polarity"] = scores["compound"]  # compound field shows a holistic view of the derived sentiment

            if row["Polarity"] == 0.0:
                zero += 1
            elif row["Polarity"] > 0.0:
                positive += 1
            else:
                negative += 1

            avg += row["Polarity"]
            rows += 1

        file_name = csv.split(".")[0] + "_+_polarity"
    
        csv_df.to_csv(f"../Polarity_Analysis/csvs_with_polarity/{file_name}.csv")

        # Analysis
        print(csv.split(".")[0].split("_")[0], csv.split(".")[0].split("_")[1])
        print("Average Sentiment: ", round(avg/rows, 3))
        print("Positive : ", round((positive/rows)*100, 2), "%")
        print("Negative : ", round((negative/rows)*100, 2), "%")
        print("Zero: ", round((zero/rows)*100, 2), "%")
        print()


def main():
    update_stock_terminology()
    get_sentiments()


if __name__ == "__main__":
    main()