#!/usr/bin/env python
#-*- coding:utf-8 -*-

## A simple but powerful application for study-booking in the library of CDUT.
##
## This work is under Toay's PRE-MIT license with extra agreement that:
##  - to help protecting the server, rate limit must be setted below 1 rps
##
## Toay's PRE-MIT license is an open source license that simulates but has prerequisites in front of the MIT license.
##  - Take a step to https://toay.org/projects/pre-mit-license to know more.
##
## Author: twikor(@twic.me)

## Required essential packages/libraries:
##  - sys, datetime, time, socket, request, json, bs4/BeautifulSoup, terminaltables/AsciiTable

# import essential packages/libraries

import sys, socket, requests, json
from bs4 import BeautifulSoup
import dinner as D

# basic configurations are gathered here

recipeFileName = "recipe.json"
refreshRecipeCycle = 600#second(s)

# function: reload recipe from file

def getFreshRecipe(): 
    global dishes
    # import pre-booking configurations

    recipeFromFile = open(recipeFileName)
    dishes = json.load(recipeFromFile)

# get current date time

currentDateTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
currentDate = time.strftime('%Y-%m-%d',time.localtime(time.time()))
currentTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
currentTimestamp = int(time.time())

