import csv
import os
from os import listdir
from os.path import isfile, join
######################################################################################
script_dir = os.path.dirname(os.path.abspath(__file__))
split_dir = str(script_dir).split("/")
idx_src = split_dir.index("src")
parent_dir = split_dir[idx_src-1]
######################################################################################
dirpath = r"/Volumes/Macintosh HD - Data/00_Data/Geospatial/USGS/Features"
outputPath = r"/Volumes/Macintosh HD - Data/00_Data/Geospatial/USGS/Features_csv"
files = list(listdir(os.path.join(dirpath)))
for fileName in files:
    fileName_split = fileName.split('.')
    ext = fileName_split[1]
    if ext == 'txt':
        print(fileName)
######################################################################################
        write_dataOut = open(os.path.join(outputPath, fileName_split[0]+'.csv'), 'w',newline='', encoding='utf-8')
        writer_dataOut = csv.writer(write_dataOut)
        writer_dataOut.writerow([
            'FEATURE_ID', 'FEATURE_NAME', 'FEATURE_CLASS', 'STATE_ALPHA', 'STATE_NUMERIC', 'COUNTY_NAME', 'COUNTY_NUMERIC',
            'PRIMARY_LAT_DMS', 'PRIM_LONG_DMS', 'PRIM_LAT_DEC', 'PRIM_LONG_DEC', 'SOURCE_LAT_DMS', 'SOURCE_LONG_DMS', 
            'SOURCE_LAT_DEC', 'SOURCE_LONG_DEC'
            ])
############################################# #########################################
        with open(os.path.join(dirpath, fileName), "r", encoding="utf-8") as file:
            next(file)
            for line in file:
                items = line.strip().split('|')
                clean_items = [item.strip() for item in items]
                writer_dataOut.writerow(clean_items)
######################################################################################