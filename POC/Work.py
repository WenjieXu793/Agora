#!/usr/bin/env python
# coding: utf-8

# In[37]:


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.metrics import accuracy_score

from itertools import combinations
pd.set_option("display.max_rows", None, "display.max_columns", None)

import time


# In[20]:


def run_model(added_cols):
    training_df = pd.read_csv('recent_training_data.csv',index_col=[0])
    list_of_cols = [x for x in training_df.columns if x in ['Buy', 'Ticker', 'Headlines']]
    training_df['Headlines'] = training_df['Headlines'] * 2
    
    # Cols used in DF
    for to_be_added in added_cols:
        list_of_cols.append(to_be_added)

    training_df = training_df[list_of_cols]
    training_df = training_df.dropna()
#     Scaler = MinMaxScaler()
#     cols = [x for x in training_df.columns if x not in ['Buy', 'Ticker']]
#     training_df[cols] = Scaler.fit_transform(training_df[cols])
    
    # Creating training and testing datasets
    X_total = training_df[[x for x in training_df.columns if x not in ['Buy', 'Ticker']]]
    y_total = training_df['Buy']
    X_train, X_test, y_train, y_test = train_test_split(X_total, y_total, test_size=0.33, random_state=42)
    
    # Logistic Regression Mode
    LR = LogisticRegression(class_weight='balanced')
    try:
        LR = LR.fit(X_train, y_train)
    except Exception as e:
        return -1

    y_prediction = LR.predict(X_test)
    return accuracy_score(y_test, y_prediction)


# In[33]:


training_df = pd.read_csv('recent_training_data.csv',index_col=[0])
list_of_cols = [x for x in training_df.columns if x not in ['Buy', 'Ticker', 'Headlines']]

# training_df


# In[39]:


def subsets(nums):
        res=[]
        subset=[]
        def dfs(i):
            if i>= len(nums):
                res.append(subset.copy())
                return 
            subset.append(nums[i])
            dfs(i+1)
            
            subset.pop()
            dfs(i+1)
        dfs(0)        
        return res

arr = ['payoutRatio', 'beta', 'regularMarketVolume', 'profitMargins', '52WeekChange', 'forwardEps', 'bookValue', 'sharesShort', 'sharesPercentSharesOut', 'trailingEps', 'heldPercentInstitutions', 'heldPercentInsiders', 'mostRecentQuarter', 'nextFiscalYearEnd', 'shortRatio', 'enterpriseValue', 'earningsQuarterlyGrowth', 'sharesShortPriorMonth', 'shortPercentOfFloat', 'pegRatio']

# print(len(arr))

# In[40]:


# print(run_model(['earningsQuarterlyGrowth']))


# In[41]:


max_accuracy = 0
max_subset_cols = []
# result = subsets(arr)

# for permutation in result:
#     permutation_accuracy = run_model(permutation)
#     if permutation_accuracy > max_accuracy:
#         max_accuracy = permutation_accuracy
#         max_subset_cols = permutation.copy()

combs = []

for i in range(1, len(arr)+1):
    els = [list(x) for x in combinations(arr, i)]
    combs.extend(els)

max_accuracy = -100000

start_time = time.time()

i = 0

for comb in combs:
    i += 1
    acc = run_model(comb)
    print("Run:", i)
    print("Accuracy:", acc)
    print("Columns for model:", comb)
    print()
    if acc > max_accuracy:
        max_accuracy = acc
        max_subset_cols = comb

print(max_accuracy)
print(max_subset_cols)
print("TOTAL TIME:", (time.time() - start_time))
