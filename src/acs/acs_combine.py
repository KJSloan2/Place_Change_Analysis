import pandas as pd
import json
import numpy as np
import os
import fiona
import sys
######################################################################################
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import json_serialize
######################################################################################
placeGeojson = os.path.join(r'data', 'geographic', 'tl_2024_48_place.geojson' )

fc = {
    "type": "FeatureCollection",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::4269" } },
    "features": []
}

fc_geoids = []
with fiona.open(placeGeojson, mode="r") as placeGeojson:
    for i, feature in enumerate(placeGeojson):
        properties = feature["properties"]
        geoid  = properties["GEOID"]
        fc_geoids.append(geoid)
       
        newFeature = {
            "type": "Feature",
            "properties": {
                "STATEFP": properties["STATEFP"],
                "PLACEFP": properties["PLACEFP"],
                "PLACENS": properties["PLACENS"],
                "GEOID": properties["GEOID"],
                "GEOIDFQ": properties["GEOIDFQ"],
                "NAME": properties["NAME"],
                "NAMELSAD": properties["NAMELSAD"],
                "LSAD": properties["LSAD"],
                "CLASSFP": properties["CLASSFP"],
                "PCICBSA": properties["PCICBSA"],
                "MTFCC": properties["MTFCC"],
                "FUNCSTAT": properties["FUNCSTAT"],
                "ALAND": properties["ALAND"],
                "AWATER": properties["AWATER"],
                "INTPTLAT": properties["INTPTLAT"],
                "INTPTLON": properties["INTPTLON"],
                "acs_schema": ["avg_prct_change", "slope", "slope_direction"]
            },
            "geometry": {
                "type": feature["geometry"]["type"],
                "coordinates": feature["geometry"]["coordinates"]
            }
        }
        fc["features"].append(newFeature)

######################################################################################
acsFileDesignations = {
    'dp03': ['ACSDP5Y','DP03'],
    's0101': ['ACSST5Y','S0101'],
    's2801': ['ACSST5Y','S2801'],
    }

for fileKey, fileDesignations in acsFileDesignations.items():
    filePath = os.path.join(r"data", "interum", str(fileKey)+".json")
    with open(filePath, 'r') as jsonFile:
        placeData = json.load(jsonFile)
        for placeObj in placeData:
            placeGeoid = placeObj["geoid"]
            if placeGeoid in fc_geoids:
                idx = fc_geoids.index(placeGeoid)

                for acsKey, acsObj in placeObj[fileKey].items():
                    if acsObj["valid"] == True:
                        fc["features"][idx]["properties"][acsKey+"_acp"] = acsObj["avg_prct_change"]
                        fc["features"][idx]["properties"][acsKey+"_slope"] = acsObj["slope"]

######################################################################################
with open(os.path.join(r"data", "interum", "acsComposite.geojson"), "w", encoding='utf-8') as output_geojson:
    output_geojson.write(json.dumps(fc, indent=1, default=json_serialize, ensure_ascii=False))

print("DONE")