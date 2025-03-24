import fiona
import pandas as pd
import numpy as np
import json

import os
################################################################################
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import calcDeltas
################################################################################
df = pd.read_csv(os.path.join('data', 'population', 'cbsa-est2023-alldata-utf8.csv'), encoding="utf-8")
headers = df.columns.tolist()

#CBSA,MDIV,STCOU,NAME,LSAD,ESTIMATESBASE2020,RESIDUAL2020,RESIDUAL2021,RESIDUAL2022,RESIDUAL2023

headerCategories = {"POPESTIMATE":[], "NPOPCHG":[], "BIRTHS":[], "DEATHS":[], "NATURALCHG":[], "INTERNATIONALMIG":[], "DOMESTICMIG":[], "NETMIG":[], "RESIDUAL":[]}
for headerCategory, headerLst in headerCategories.items():
    for i in range(2020,2024):
        header = headerCategory+str(i)
        headerLst.append(header)
################################################################################
fc = {
    "type": "FeatureCollection",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::4269" } },
    "features": []
}

geojson_path = os.path.join(r'data', 'cbsaTabulationAreas.geojson' )
cbsaGeoids = []
with fiona.open(geojson_path, mode="r") as src:
    print("Total Features:", len(src))
    print("Schema:", src.schema)

    for feature in src:
        properties = feature["properties"]
        geoid = properties["geoid"]
        cbsaGeoids.append(str(geoid))

        newFeature = {
            "type": "Feature",
            "properties": {
                "geoid": geoid,
                "name": feature["properties"]["name"],
                "namelsad": feature["properties"]["namelsad"],
                "POPESTIMATE":[],
                "NPOPCHG":[],
                "BIRTHS":[],
                "DEATHS":[],
                "NATURALCHG":[],
                "INTERNATIONALMIG":[],
                "DOMESTICMIG":[],
                "NETMIG":[],
                "RESIDUAL":[]
            },
            "geometry": {
                "type": feature["geometry"]["type"],
                "coordinates": feature["geometry"]["coordinates"]
            }
        }

        fc["features"].append(newFeature)
######################################################################################
def is_nan(value):
    return np.isnan(value)

def is_infinity(value):
    return np.isinf(value)

def check_vals(vals):
    returnVals = []
    for val in vals:
        if is_nan(val):
            val = 0
        elif is_infinity(val):
            val = 0
        returnVals.append(val)
    return returnVals
######################################################################################
for i, geoid in enumerate(df["CBSA"]):
    geoid = str(geoid)
    print(geoid)
    
    lsad = df["LSAD"][i]
    cbsaName = df["NAME"][i]

    if geoid in cbsaGeoids:
        featureIdx = cbsaGeoids.index(geoid)
        
        if lsad == "Metropolitan Statistical Area" and str(geoid) in cbsaGeoids:
            for headerCategory, headerLst in headerCategories.items():
                for h in headerLst:
                    val = df[h][i]
                    fc["features"][featureIdx]["properties"][headerCategory].append(val)

                yoyDeltas = calcDeltas(fc["features"][featureIdx]["properties"][headerCategory])
                meanPrctDelta, meanDelta = 0, 0
                if len(yoyDeltas["prct_deltas"]) != 0:
                    meanPrctDelta = np.mean(yoyDeltas["prct_deltas"])
                    meanDelta = np.mean(yoyDeltas["deltas"])
                values = check_vals([meanPrctDelta, meanDelta])
                fc["features"][featureIdx]["properties"][headerCategory.lower()+"_prctChange"] = round((values[0]),2)
                fc["features"][featureIdx]["properties"][headerCategory.lower()+"_avgChange"] = round((values[1]),2)

                #del fc["features"][featureIdx]["properties"][headerCategory]

def json_serialize(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    else:
        raise TypeError(f"Type {type(obj)} not serializable")
######################################################################################
with open(os.path.join(r'data', 'interum', 'popComp.geojson'), "w", encoding='utf-8') as output_json:
	output_json.write(json.dumps(fc, indent=1, default=json_serialize, ensure_ascii=True))
######################################################################################
print("DONE")