# analysis/merge_fares.py

import pandas as pd

ixigo = pd.read_csv("fare_data.csv")
duffel = pd.read_csv("fare_data_duffel.csv")

print("Ixigo rows:", len(ixigo))
print("Duffel rows:", len(duffel))
print("Merge pipeline placeholder")