"This script takes individual BPS files and combines them into a single, composite csv"
import pandas as pd
import numpy as np

import os
from os import listdir
from os.path import isfile, join

# File path to USCB Building Permit Survey datasets.
dirPath = r"data\housing\uscb_bps"
# Create a list of files in the given directory
files = [f for f in listdir(dirPath) if isfile(join(dirPath, f))]

# Create a data storage container. This data will be written to CSV later.
storeData = {
    "YEAR":[], "METRIC": [], 
    "CSA":[],"CBSA":[],
    "Name":[],"Total":[],
    "1 Unit":[],"2 Units":[],
    "3 and 4 Units":[],"5 Units or More":[]
    }

for fileName in files:
    split_fileName = fileName.split("_")
    metric = split_fileName[-1].split('.')[0]
    year = fileName[0:4]

    print(year, metric)

    df = pd.read_csv(os.path.join(dirPath, fileName),encoding="utf-8")

    df_csa = df['CSA'].tolist()
    df_cbsa = df['CBSA'].tolist()
    df_cbsaName = df['Name'].tolist()
    df_cbsaTotal = df['Total'].tolist()
    df_1UnitTotal = df['1 Unit'].tolist()
    df_2UnitTotal = df['2 Units'].tolist()
    df_34UnitTotal = df['3 and 4 Units'].tolist()
    df_5PlusUnitTotal = df['5 Units or More'].tolist()

    for i, val in enumerate(df_csa):
        storeData["YEAR"].append(year)
        storeData["METRIC"].append(metric)
        storeData["CSA"].append(df_csa[i])
        storeData["CBSA"].append(df_cbsa[i])
        storeData["Name"].append(df_cbsaName[i])
        storeData["Total"].append(df_cbsaTotal[i])
        storeData["1 Unit"].append(df_1UnitTotal[i])
        storeData["2 Units"].append(df_2UnitTotal[i])
        storeData["3 and 4 Units"].append(df_34UnitTotal[i])
        storeData["5 Units or More"].append(df_5PlusUnitTotal[i])


df_composite = pd.DataFrame(storeData)
df_composite.to_csv(os.path.join(dirPath, 'compositeBPS.csv'), index=False)
print("DONE")