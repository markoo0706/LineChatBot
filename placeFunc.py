# -*- coding: utf-8 -*-
"""google_mapDB_ver2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ff2O6CCbGlcOF9hzjEk3yqo9pk-cPbAq
"""

import googlemaps
import requests
import pandas as pd
import time
from restaurant_tag import run_classification

PLACE_API_KEY = 'AIzaSyAfxiZ36COzkAF__lM05Er6teR2fYMmZog'

def findNearBy(lat, lng, radius = 1000, PLACE_API_KEY = PLACE_API_KEY):
  url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(lat)+','+str(lng)+'&radius='+str(radius)+'&type=restaurant&language=zh-TW&key='+PLACE_API_KEY
  payload={}
  headers = {}
  response = requests.request("GET", url, headers=headers, data=payload)

  try:
    nextPageToken = response.json()["next_page_token"]
    ifNextPage = True
  except:
    ifNextPage = False
  results = response.json()['results']
  PLACE_INFO = [[results[x]['place_id'], results[x]['geometry']['location']['lat'], results[x]['geometry']['location']['lng'], results[x]['photos'][0]["photo_reference"], results[x]['rating']] for x in range(len(results))]

  while(ifNextPage):
    time.sleep(2)
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(lat)+','+str(lng)+'&radius='+str(radius)+'&type=restaurant&language=zh-TW&key='+PLACE_API_KEY+'&pagetoken='+nextPageToken
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    try:
      nextPageToken = response.json()["next_page_token"]
    except:
      ifNextPage = False
    results = response.json()['results']

    for x in range(len(results)):
      try:
        PLACE_INFO.extend([[results[x]['place_id'], results[x]['geometry']['location']['lat'], results[x]['geometry']['location']['lng'], results[x]['photos'][0]["photo_reference"], results[x]['rating']]])
      except:
        pass

  return PLACE_INFO

def findDetail(place_id, lat, lng, photo_reference, rating, PLACE_API_KEY = PLACE_API_KEY):
  url = 'https://maps.googleapis.com/maps/api/place/details/json?place_id='+str(place_id)+'&language=zh-TW&key='+PLACE_API_KEY
  payload = {}
  headers = {}
  response = requests.request("GET", url, headers=headers, data=payload)
  results = response.json()['result']
  Address = results['formatted_address']

  Name = results['name']
  Open_hour =  results['opening_hours']['weekday_text']
  Review = results['reviews']

  d = dict()
  d['place_id'] = place_id
  d['lat'] = lat
  d['lng'] = lng
  d['photo_refernce'] = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=' + photo_reference+ '&key=' + PLACE_API_KEY
  d['rating'] = rating
  d['address'] = Address
  d['open_hour'] = Open_hour
  d['review'] = Review

  return Name, d

def findRestaurant(lat, lng):
  places = findNearBy(lat, lng)
  restaurant_INFO = dict()
  for place_id, lat, lng, photo_reference, rating in places:
    try:
      name, d = findDetail(place_id, lat, lng, photo_reference, rating)
      if len(name) >= 40:
          name = name[:30] + "..."
          print(name)
      restaurant_INFO[name] = d
      restaurant_INFO[name]['name'] = name
      restaurant_INFO[name]['type'] = run_classification(d['review'], name)
    except:
      pass
  return restaurant_INFO

