import pandas as pd
import matplotlib.pyplot as plt
import os

directory = "./Conversations"

dfs = []

for filename in os.listdir(directory):
    if filename.endswith(".csv") and filename != ".gitkeep":
        file_path = os.path.join(directory, filename)
        df = pd.read_csv(file_path, parse_dates=['Date'])
        dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)

conversation_counts = combined_df['Date'].value_counts().sort_index()
# print(conversation_counts[:10])
# print(conversation_counts[-10:])

plt.figure(figsize=(12, 6))
plt.bar(conversation_counts.index, conversation_counts.values, width=0.8)
plt.xlabel("Date")
plt.ylabel("Number of Conversations")
plt.title("Number of Conversations Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("Histogram of Age of Conversations.png")