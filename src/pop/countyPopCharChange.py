'''
SUMLEV", " STATE", " COUNTY", " STNAME", " CTYNAME", " YEAR",
"POPESTIMATE", " POPEST_MALE", "POPEST_FEM", "UNDER5_TOT", 
"UNDER5_MALE", "UNDER5_FEM", "AGE513_TOT", "AGE513_MALE", 
"AGE513_FEM", "AGE1417_TOT", "AGE1417_MALE", "AGE1417_FEM", 
"AGE1824_TOT", "AGE1824_MALE", "AGE1824_FEM", "AGE16PLUS_TOT", 
"AGE16PLUS_MALE", "AGE16PLUS_FEM", "AGE18PLUS_TOT", "AGE18PLUS_MALE", 
"AGE18PLUS_FEM", "AGE1544_TOT", "AGE1544_MALE", "AGE1544_FEM", 
"AGE2544_TOT", "AGE2544_MALE", "AGE2544_FEM", "AGE4564_TOT", 
"AGE4564_MALE", "AGE4564_FEM", "AGE65PLUS_TOT", "AGE65PLUS_MALE", 
"AGE65PLUS_FEM", "AGE04_TOT", "AGE04_MALE", "AGE04_FEM", "AGE59_TOT", 
"AGE59_MALE", "AGE59_FEM", "AGE1014_TOT", "AGE1014_MALE", "AGE1014_FEM", 
"AGE1519_TOT", "AGE1519_MALE", "AGE1519_FEM", "AGE2024_TOT", 
"AGE2024_MALE", "AGE2024_FEM", "AGE2529_TOT", "AGE2529_MALE", "AGE2529_FEM", 
"AGE3034_TOT", "AGE3034_MALE", "AGE3034_FEM", "AGE3539_TOT", "AGE3539_MALE", 
"AGE3539_FEM", "AGE4044_TOT", "AGE4044_MALE", "AGE4044_FEM", "AGE4549_TOT", 
"AGE4549_MALE", "AGE4549_FEM", "AGE5054_TOT", "AGE5054_MALE", "AGE5054_FEM", 
"AGE5559_TOT", "AGE5559_MALE", "AGE5559_FEM", "AGE6064_TOT", "AGE6064_MALE", 
"AGE6064_FEM", "AGE6569_TOT", "AGE6569_MALE", "AGE6569_FEM", "AGE7074_TOT", 
"AGE7074_MALE", "AGE7074_FEM", "AGE7579_TOT", "AGE7579_MALE", "AGE7579_FEM", 
"AGE8084_TOT", "AGE8084_MALE", "AGE8084_FEM", "AGE85PLUS_TOT", "AGE85PLUS_MALE", 
"AGE85PLUS_FEM", "MEDIAN_AGE_TOT", "MEDIAN_AGE_MALE", "MEDIAN_AGE_FEM"
'''

import fiona
import pandas as pd
import os
import numpy as np
import json

df = pd.read_csv(os.path.join('data', 'population', 'cc-est2023-agesex-all-utf8.csv'), encoding="utf-8")
headers = df.columns.tolist()
#df['GEOID'] = df['STATE'].astype(str) + df['COUNTY'].astype(str)

def pad_string(input_str, length):
    length
    """
    Pads a string with leading zeros to ensure it has a specified length.
    :param input_str: The input string (or number).
    :param length: The desired length of the output string (default is 3).
    :return: Zero-padded string.
    """
    input_str = str(input_str)
    return input_str.zfill(length)

geoids = []
for stateCode, countyCode in zip(df['STATE'].astype(str), df['COUNTY'].astype(str)):
    stateCode_padded = pad_string(stateCode, 2)
    countyCode_padded = pad_string(countyCode, 3)
    geoids.append(stateCode_padded+countyCode_padded)

df['GEOID'] = geoids

for item in df['GEOID']:
    print(item)
targetProperties = {
    "POPESTIMATE":{"property": "popestimate_mean_yoy_prct_change"},
    "UNDER5_TOT":{"property": "under5_mean_yoy_prct_change"},
    "AGE513_TOT":{"property": "age513_mean_yoy_prct_change"},
    "AGE1417_TOT":{"property": "age1417_mean_yoy_prct_change"},
    "AGE1824_TOT":{"property": "age1824_mean_yoy_prct_change"},
    "AGE16PLUS_TOT":{"property": "age16plus_mean_yoy_prct_change"},
    "AGE2544_TOT":{"property": "age2544_mean_yoy_prct_change"},
    "AGE4564_TOT":{"property": "age4564_mean_yoy_prct_change"},
    "AGE65PLUS_TOT":{"property": "age65plus_mean_yoy_prct_change"}
}

# selectHeaders to hold the original headers used in the data
selectHeaders = []
for key, item in targetProperties.items():
    selectHeaders.append(key)

geojson_path = os.path.join(r'data', 'popTemp.geojson' )

fc = {
    "type": "FeatureCollection",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::4269" } },
    "features": []
}

################################################################################
with fiona.open(geojson_path, mode="r") as src:
    print("Total Features:", len(src))
    print("Schema:", src.schema)

    for feature in src:

        updatedFeature = {
            "type": "Feature",
            "properties": {
                feature["properties"]["geoid"],
                feature["properties"]["csafp"],
                feature["properties"]["cbsafp"],
                feature["properties"]["geoidfq"],
                feature["properties"]["name"],
                feature["properties"]["namelsad"],
                feature["properties"]["counties"]
            },
            "geometry": {
                "type": feature["geometry"]["type"],
                "coordinates": feature["geometry"]["coordinates"]
            }
        }

        for propKey in feature["properties"]:
            updatedFeature["properties"][propKey] = feature["properties"][propKey]

        for header in selectHeaders:
            updatedFeature['properties'][header] = [0, 0, 0, 0, 0]

        for countyGeoid in updatedFeature["properties"]["counties"]:
            df_filtered = df[df['GEOID'] == str(countyGeoid)]
            years = list(df_filtered['YEAR'])
            if len(years) != 0:
                for header in selectHeaders:
                    try:
                        for i, val in enumerate(list(df_filtered[header])):
                            updatedFeature["properties"][header][i]+=val
                        storePrctDelta = []
                        for i in range(1, len(updatedFeature["properties"][header])-1):
                            v1 = updatedFeature["properties"][header][i-1]
                            v2  = updatedFeature["properties"][header][i]
                            prctDelta = ((v2-v1)/v1)*100
                            storePrctDelta.append(prctDelta)
                        meanPrctDelta = np.mean(storePrctDelta)
                        updatedFeature["properties"][targetProperties[header]["property"]] = meanPrctDelta
                    except Exception as e:
                        continue
                
            else:
                print("NO MATCH: ", updatedFeature["properties"]["name"])

        for header in selectHeaders:
            del updatedFeature["properties"][header]

        fc["features"].append(updatedFeature)

with open(os.path.join(r'data', 'interum', 'pop.geojson'), "w", encoding='utf-8') as output_json:
	output_json.write(json.dumps(fc, indent=1, ensure_ascii=True))

print('DONE')




