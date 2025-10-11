import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv(r"Trader_Workstation/Udemy/Part3/eurusd.csv")

df.plot(figsize=(12,8), title = "EUR/USD", fontsize=12)

# Compute log returns on the 'price' column
df["returns"] = np.log(df["price"] / df["price"].shift(1))