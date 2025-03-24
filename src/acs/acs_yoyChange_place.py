import pandas as pd
import json
import numpy as np
import os
import re
import fiona
import csv
import sys
######################################################################################
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import calc_yoy_change
from utils import calc_slope
######################################################################################
script_dir = os.path.dirname(os.path.abspath(__file__))
split_dir = str(script_dir).split("/")
idx_src = split_dir.index("src")
parent_dir = split_dir[idx_src-1]
######################################################################################
placeGeojson = os.path.join(r'data', 'geographic', 'tl_2024_48_place.geojson' )
######################################################################################
analysisYears = [2019, 2020, 2021, 2022, 2023]
######################################################################################
def filter_headers(values):
    pattern = re.compile(r'.*\dE$')
    return [value for value in values if pattern.match(value)]
######################################################################################
acsFileDesignations = {
    'dp03': ['ACSDP5Y','DP03'],
    's0101': ['ACSST5Y','S0101'],
    's2801': ['ACSST5Y','S2801'],
    }
with fiona.open(placeGeojson, mode="r") as placeGeojson:
    for fileKey, fileDesignations in acsFileDesignations.items():
        print(fileKey)
        
        fileName_metaData = fileDesignations[0]+str(analysisYears[3])+"."+fileDesignations[1]+'-Column-Metadata.csv'
        filePath_metaData = os.path.join(r'data', 'demographic', 'uscb_acs', fileKey, fileName_metaData)
        df_metaData = pd.read_csv(filePath_metaData, encoding="utf-8")
        metaData_headers = list(df_metaData['Column Name'])
        estimateHeaders = filter_headers(metaData_headers)

        placeData = {}
        for i, feature in enumerate(placeGeojson):
            properties = feature["properties"]
            geoid  = properties["GEOID"]
            placeFeature = {"geoid":geoid, fileKey:{}}
            for header in estimateHeaders:
                placeFeature[fileKey][header] = {"year_ref":[], "estimates":[]}
            placeData[geoid] = placeFeature
        ##############################################################################
        for year in analysisYears:
            print(fileKey, year)
            fileName = fileDesignations[0]+str(year)+'.'+fileDesignations[1]+'-Data.csv'
            filePath = os.path.join(r'data', 'demographic', 'uscb_acs', fileKey, fileName)
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
                            placeData[geoid][fileKey][header]["estimates"].append(estimate)
                            placeData[geoid][fileKey][header]["year_ref"].append(year)
                        except:
                            continue
                except Exception as e:
                    print(e)
                    continue
        ##########################################################################
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
        ##########################################################################
        outputData = []
        print(fileKey, "calculating YoY changes")
        for geoid, item in placeData.items():
            summary = {'geoid': geoid, fileKey: {}}
            for dataKey, estimatesData in item[fileKey].items():
                summary[fileKey][dataKey] = {}
                estimates = estimatesData["estimates"]
                percent_changes, avg_percent_change, slope, slope_direction = None, None,  None, None
                if len(estimates) > 1:
                    percent_changes, avg_percent_change = calc_prct_change(estimates)
                    slope = calc_slope(estimates)
                    if slope >0:
                        slope_direction = 1
                    elif slope <0:
                        slope_direction = -1
                    elif slope == 0:
                        slope_direction = 0
                #summary[fileKey][dataKey]["percent_changes"] =  percent_changes
                if avg_percent_change is not None:
                    avg_percent_change = round((avg_percent_change),2)
                    #summary[fileKey][dataKey]["percent_changes"] =  percent_changes
                    summary[fileKey][dataKey]["valid"] =  True
                else:
                    summary[fileKey][dataKey]["valid"] =  False

                summary[fileKey][dataKey]["avg_prct_change"] = avg_percent_change
                summary[fileKey][dataKey]["slope"] = slope
                summary[fileKey][dataKey]["slope_direction"] = slope_direction

            outputData.append(summary)
        ##############################################################################
        print(fileKey, "writing to json")
        with open(os.path.join(r'data', 'interum', fileKey+'.json'), "w", encoding='utf-8') as outputJson:
            outputJson.write(json.dumps(outputData, indent=1, ensure_ascii=True))
        ##############################################################################
print("DONE")