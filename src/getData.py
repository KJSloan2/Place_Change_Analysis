import pandas as pd
import json
import numpy as np
import os
import re
import fiona
######################################################################################
script_dir = os.path.dirname(os.path.abspath(__file__))
split_dir = str(script_dir).split("/")
idx_src = split_dir.index("src")
parent_dir = split_dir[idx_src-1]
######################################################################################
fileName_metaData = 'ACSDP5Y2022.DP03-Column-Metadata.csv'
filePath_metaData = os.path.join(r'data', 'dp03', fileName_metaData)
df_metaData = pd.read_csv(filePath_metaData, encoding="utf-8")
metaData_headers = list(df_metaData['Column Name'])
######################################################################################
def filter_headers(values):
    pattern = re.compile(r'.*\dE$')
    return [value for value in values if pattern.match(value)]

estimateHeaders = filter_headers(metaData_headers)
######################################################################################
placeGeojson = os.path.join(r'data', 'geographic', 'tl_2024_48_place.geojson' )
######################################################################################
placeData = {}
with fiona.open(placeGeojson, mode="r") as src:
    for i, feature in enumerate(src):
        properties = feature["properties"]
        geoid  = properties["GEOID"]
        placeFeature = {"geoid":geoid, "acs_dpo3":{}}
        for header in estimateHeaders:
            placeFeature["acs_dpo3"][header] = {"year_ref":[], "estimates":[]}
        placeData[geoid] = placeFeature
######################################################################################
analysisYears = [2023, 2022, 2021, 2020, 2019]
######################################################################################
for year in analysisYears:
    fileName = 'ACSDP5Y'+str(year)+'.DP03-Data.csv'
    filePath = os.path.join(r'data', 'dp03', fileName)
    df = pd.read_csv(filePath, encoding="utf-8")
    df_filtered = df.drop(index=0).reset_index(drop=True)
    #df_filtered = df.iloc[1:].reset_index(drop=True)
    df_geoids = list(df_filtered['GEO_ID'])
    for header in estimateHeaders:
        try:
            data = list(df_filtered[header])
            for i, estimate in enumerate(data):
                #"1600000US4800100"
                parse_geoid = df_geoids[i].split("US")
                geoid = str(parse_geoid[1]).strip()
                #if isinstance(estimate, (int, float)):
                try:
                    estimate = int(estimate)
                    placeData[geoid]["acs_dpo3"][header]["estimates"].append(estimate)
                    placeData[geoid]["acs_dpo3"][header]["year_ref"].append(year)
                except:
                    continue
        except Exception as e:
            print(e)
            continue
######################################################################################
def calc_prct_change(d):
    percent_changes = []
    
    for i in range(1, len(d)):
        if d[i - 1] == 0:
            percent_changes.append(None)  # Avoid division by zero, append None or an appropriate placeholder
        else:
            percent_change = ((d[i] - d[i - 1]) / d[i - 1]) * 100
            percent_changes.append(percent_change)
    
    valid_changes = [pc for pc in percent_changes if pc is not None]
    average_percent_change = sum(valid_changes) / len(valid_changes) if valid_changes else None
    
    return percent_changes, average_percent_change

######################################################################################
output = []
for geoid, item in placeData.items():
    summary = {'geoid': geoid, "acs_dpo3": {}}
    for dataKey, estimatesData in item["acs_dpo3"].items():
        summary["acs_dpo3"][dataKey] = {}
        estimates = estimatesData["estimates"]
        percent_changes, avg_percent_change = None, None
        if len(estimates) > 1:
            percent_changes, avg_percent_change = calc_prct_change(estimates)
        summary["acs_dpo3"][dataKey]["percent_changes"] =  percent_changes
        summary["acs_dpo3"][dataKey]["avg_percent_change"] =  avg_percent_change
    output.append(summary)
######################################################################################
with open(os.path.join(r'data', 'placeACS.json'), "w", encoding='utf-8') as placeACS:
	placeACS.write(json.dumps(output, indent=1, ensure_ascii=True))
######################################################################################
print("DONE")