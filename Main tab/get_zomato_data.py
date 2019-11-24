# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 22:15:50 2019

@author: Brandon
"""

import requests
from pandas.io.json import json_normalize
import pandas as pd


def get_zomato_data(start=0,entity_id=289,radius=5000,count=20):
    locationUrlFromLatLong = "https://developers.zomato.com/api/v2.1/search?entity_id={}&entity_type=city&start={}&radius={}&cuisines=25&count={}&sort=rating".format(entity_id,start,radius,count)
    header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "user_key": "532463959546b2bb3e50ef3609d45797"}
    response = requests.get(locationUrlFromLatLong, headers=header)
    jsfile=response.json()
    database=json_normalize(jsfile['restaurants'])
    if database.empty==0:
        return jsfile['results_found'],database
    else:
        raise Exception('result for entity_id={} has been exhausted'.format(entity_id))


def get_zomato_full_list(entity_id=289,radius=5000):
    i=0
    maxrecord,database=get_zomato_data(entity_id=entity_id,radius=5000)
    print("There are {} records has been found".format(maxrecord))
    if maxrecord>100:
        print("Only the first 100 records will be downloaded")
    maxrecord=min(100,maxrecord)
    while i<=maxrecord:
        database=database.append(get_zomato_data(start=i)[1],ignore_index=True)
        print("{} records has been loaded".format(i+20))
        if i+40<maxrecord:
            i+=20
        else:
            database=database.append(get_zomato_data(start=i+20,count=maxrecord-i)[1],ignore_index=True)
            print("{} records has been loaded".format(maxrecord))
            return database
    return database