import fiona
import pandas as pd
import numpy as np
import json

import os
from os import listdir
from os.path import isfile, join
################################################################################
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import calc_yoy_change
from utils import check_vals
######################################################################################
df_composite = pd.read_csv(os.path.join(r"data", "housing", "uscb_bps", "compositeBPS.csv"),encoding="utf-8")
#YEAR,METRIC,CSA,CBSA,Name,Total,1 Unit,2 Units,3 and 4 Units,5 Units or More
######################################################################################
fc = {
    "type": "FeatureCollection",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::4269" } },
    "features": []
}
######################################################################################
with fiona.open(os.path.join(r"data", "geographic", "cbsaTabulationAreas.geojson"), mode="r") as src:
    for i, feature in enumerate(src):
        properties = feature["properties"]
        geoid = properties["geoid"]
        name = properties["name"]
        namelsad = properties["namelsad"]
        geometry = feature["geometry"]

        newFeature = {
            "type": "Feature",
            "properties": {
                "geoid": geoid, "name": name, "namelsad": namelsad,
                "u_total":[], "u_1unit":[], "u_2units":[], "u_34units":[], "u_5plusUnits":[],
                "v_total":[], "v_1unit":[], "v_2units":[], "v_34units":[], "v_5plusUnits":[]
            },
            "geometry": {"type": geometry["type"], "coordinates": geometry["coordinates"]}
        }

        fc["features"].append(newFeature)
######################################################################################
df_composite['CBSA'] = df_composite['CBSA'].astype(str)
df_composite['YEAR'] = df_composite['YEAR'].astype(str)
######################################################################################
years = [2019, 2020, 2021, 2022, 2023, 2024]
categoryKeys = {"u":"units", "v":"values"}
propKeys = {
    "total":"Total", "1unit":"1 Unit",
    "2units":"2 Units", "34units":"3 and 4 Units", 
    "5plusUnits":"5 Units or More" }

for i, feature in enumerate(fc["features"]):
    # Itterate between measuring permit unit counts and values
    for categoryKey, categoryLabel in categoryKeys.items():
        # Itterate through each year in the analysis period
        for year in years:
            try:
                df_composite_filtered = df_composite[
                    (df_composite['CBSA'] == str(feature["properties"]["geoid"])) &
                    (df_composite['YEAR'] == str(year)) &
                    (df_composite['METRIC'] == categoryLabel)
                ]
                if not df_composite.empty:
                    for propKey, propLabel in propKeys.items():
                        try:
                            fc["features"][i]["properties"][categoryKey+"_"+propKey].append(df_composite_filtered[propLabel].values)
                        except Exception as e1:
                            print(e1)
                            continue
                            
            except Exception as e2:
                print(e2)
                continue

        for propKey, propLabel in propKeys.items():
            yoyDeltas = calc_yoy_change(fc["features"][i]["properties"][categoryKey+"_"+propKey])
            meanPrctDelta, meanDelta = 0, 0

            if len(yoyDeltas["prct_deltas"]) != 0:
                print(yoyDeltas["prct_deltas"], yoyDeltas["deltas"])
                meanPrctDelta = np.mean(yoyDeltas["prct_deltas"])
                meanDelta = np.mean(yoyDeltas["deltas"])

            values = check_vals([meanPrctDelta, meanDelta])

            fc["features"][i]["properties"][categoryKey+"_"+propKey+"_prctChange"] = round((values[0]),2)
            fc["features"][i]["properties"][categoryKey+"_"+propKey+"_avgChange"] = round((values[1]),2)

            del fc["features"][i]["properties"][categoryKey+"_"+propKey]

######################################################################################
with open(os.path.join(r'data', 'interum', 'bps.geojson'), "w", encoding='utf-8') as output_json:
	output_json.write(json.dumps(fc, indent=1, ensure_ascii=True))
######################################################################################
print("DONE")