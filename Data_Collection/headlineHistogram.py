"""
Authors: Wenjie Xu
Functionality implemented:
- Creates a histogram to show the age of headline sentiment data pulled.
"""

import pandas as pd
import matplotlib.pyplot as plt

file_path = "headlines.csv" 
df = pd.read_csv(file_path, parse_dates=['Date'])

headline_counts = df['Date'].value_counts().sort_index()
# print(headline_counts[:10])
# print(headline_counts[-5:])

plt.figure(figsize=(12, 6))
plt.bar(headline_counts.index, headline_counts.values, width=0.8)
plt.xlabel("Date")
plt.ylabel("Number of Headlines")
plt.title("Number of Headlines Over Time")
plt.xticks(rotation=45)
plt.savefig("Histogram of Age of Headlines.png")