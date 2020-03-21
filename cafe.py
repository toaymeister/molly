#!/usr/bin/env python3
#-*- coding:utf-8 -*-

## A simple but powerful application for automatic study-booking for the library of CDUT.
##
## This work is under Toay's PRE-MIT license with extra agreement that:
##  - to help protecting the server, rate limit must be setted below 1 rps
##
## Toay's PRE-MIT license is an open source license that simulates but has prerequisites in front of the MIT license.
##  - Take a step to https://toay.org/projects/pre-mit-license to know more.
##
## Author: twikor(@twic.me)

## Required essential packages/libraries:
##  - sys, datetime, time, json
##  - twikor/modiner ~ v2.0+

# import essential packages/libraries

import os, sys, datetime, time, json
import dinner as D

# basic settings

debugMode = True#set true to display runtime log

recipeFile = "./recipe.json"
shelfDirectory = "./shelf/"

retryTimes = 5
retryInterval = 1
standbyInterval = 0.5

# customizable actions triggered under a certain condition

def bindSuccess(details = None):
    return True

def bindFailure(details = None):
    return True

# function: output status when in standby mode

def sweetsOut(outputContent):
    if (debugMode == True):
        print("[Molly " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] " + outputContent)

# function: storing of the log data

def beansOut(coffeeBeans):

    # output operation status

    if (coffeeBeans != None):
        if (os.path.isfile('./beans.txt') == False):
            os.system('touch beans.txt')
        
        coffeeBeansFile = open('beans.txt', 'a')
        contentLineToWrite = str("[Molly " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] " + coffeeBeans + '\n')
        coffeeBeansFile.write(contentLineToWrite)
        coffeeBeansFile.close()

# load and convert recipe from file to task queue directory

def storeNewCups(): 

    coffees = []

    # import pre-booking configurations

    if (os.path.isfile(recipeFile) == True):

        sweets = "INFO: task-importing operation started"
        sweetsOut(sweets)
        coffeeBeans = "INFO: task-importing operation started"
        beansOut(coffeeBeans)

        recipeFromFile = open(recipeFile)

        # json file is easily wrong in format, so placed the exception handler
        try:
            toImportTasks = json.load(recipeFromFile)
        except ValueError:
            sweets = "ERROR: task-importing operation failed for invalid recipe file, operation canceled"
            sweetsOut(sweets)
            coffeeBeans = "ERROR: task-importing operation failed for invalid recipe file, operation canceled"
            beansOut(coffeeBeans)
        else:
            for toImportTaskIndex, toImportTask in enumerate(toImportTasks):
                toImportTaskTriggerAt = toImportTask['triggerAt']
                toImportTaskTriggerAtTimeStructure = time.strptime(toImportTaskTriggerAt,"%Y-%m-%d %H:%M:%S")
                toImportTaskId = time.strftime("%Y%m%d%H%M%S", toImportTaskTriggerAtTimeStructure)
                toImportTask['taskId'] = toImportTaskId
                toImportTask['attemptedTimes'] = 0

                coffeeBeans = "INFO: imported task with id [" + toImportTask['taskId'] + "], details: " + json.dumps(toImportTask, ensure_ascii = False)
                beansOut(coffeeBeans)
                
                coffees.append(toImportTask)

            if (os.path.exists(shelfDirectory) == False):
                os.system("mkdir " + shelfDirectory)

            for coffee in coffees:

                taskFileName = coffee['taskId']

                os.system("touch " + shelfDirectory + taskFileName)

                coffee = json.dumps(coffee, ensure_ascii = False)

                coffeeFile = open(shelfDirectory + taskFileName, 'a')
                contentLineToWrite = str(coffee)
                coffeeFile.write(coffee)
                coffeeFile.close()

            os.system('rm ' + recipeFile)

            sweets = "INFO: task imported successfully"
            sweetsOut(sweets)
            coffeeBeans = "INFO: task imported successfully"
            beansOut(coffeeBeans)

    return True

def fetchStoredCoffeesList():

    coffeeList = os.listdir(shelfDirectory)
    coffeeList.sort()
    coffeeList.reverse()

    return coffeeList

def fetchStoredCoffee(coffeeId):

    cooffeeFile = open(shelfDirectory + coffeeId)
    storedCoffee = json.load(cooffeeFile)

    return storedCoffee

# make preparations

if (os.path.isfile('./beans.txt') == False):
    os.system('touch ./beans.txt')
    
if (os.path.exists(shelfDirectory) == False):
    os.system("mkdir " + shelfDirectory)

# start the main loop

try:

    while(True):

        # heartbeats

        currentDateTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        currentDate = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        currentTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
        currentTimestamp = int(time.time())

        # first, see whether there are tasks to do

        sweets = "INFO: checking task queue for operation"
        sweetsOut(sweets)

        coffees = fetchStoredCoffeesList()

        if (fetchStoredCoffeesList() != []):

            for index, coffeeId in enumerate(coffees):
                taskTriggerAt = coffeeId
                taskTriggerAtTimeStructure = time.strptime(taskTriggerAt, "%Y%m%d%H%M%S")
                taskTriggerAtTimeStamp = time.mktime(taskTriggerAtTimeStructure)

                if (int(currentTimestamp) - int(taskTriggerAtTimeStamp) < 0):
                    sweets = "INFO: task with id [" + str(coffeeId) + "] is currently waiting to be triggered"
                    sweetsOut(sweets)
                else:

                    coffee = fetchStoredCoffee(coffeeId)

                    attemptedTimes = coffee['attemptedTimes']
                    expectedTimeStructure = time.strptime(coffee['triggerAt'], "%Y-%m-%d %H:%M:%S")
                    expectedTimeStamp = int(time.mktime(expectedTimeStructure))
                    currentTimeStamp = int(time.time())
                    users = coffee['users']
                    roomId = coffee['roomId']
                    startAt = coffee['startAt']
                    startAtArray = startAt.split(" ")
                    startAtDate = startAtArray[0]
                    startAtTime = startAtArray[1]
                    endAt = coffee['endAt']
                    endAtArray = endAt.split(" ")
                    endAtDate = endAtArray[0]
                    endAtTime = endAtArray[1]

                    if (attemptedTimes == 0):
                        sweets = "INFO: task with id [" + str(coffeeId) + "] is started successfully"
                        sweetsOut(sweets)
                        coffeeBeans = "INFO: task with id [" + str(coffeeId) + "] is started successfully"
                        beansOut(coffeeBeans)

                    if (attemptedTimes <= retryTimes):
                        returnValue = False
                        while (returnValue != True):
                            currentDateTime = time.strftime('%m-%d %H:%M:%S',time.localtime(time.time()))
                            sweets = "INFO: trying operation execute-bookRoom for task with id [" + str(coffeeId) + "] for the [" + str(attemptedTimes + 1) + "] time"
                            sweetsOut(sweets)
                            D.init(True)
                            returnValue = D.bookRoom(users, roomId, startAtDate, startAtTime, endAtDate, endAtTime)
                            sweets = "INFO: operation completed"
                            sweetsOut(sweets)
                            if (returnValue != True):
                                sweets = "ERROR: unable to process operation for task with id [" + str(coffeeId) + "], details: " + returnValue
                                sweetsOut(sweets)
                                coffeeBeans = "ERROR: unable to process operation for task with id [" + str(coffeeId) + "], details: " + returnValue#.decode('utf8')
                                beansOut(coffeeBeans)
                            else:
                                sweets = "INFO: successfully processed operation for task with id [" + str(coffeeId) + "]"
                                sweetsOut(sweets)
                                coffeeBeans = "SUCCESS: successfully processed operation for task with id [" + str(coffeeId) + "]"
                                beansOut(coffeeBeans)

                                successDetailsParsed = {"users":users, "roomId":roomId, "startAt":startAt, "endAt":endAt}
                                successDetailsText = json.dumps(successDetailsParsed, ensure_ascii = False)
                                bindSuccess(successDetailsText)

                                coffees.pop(coffeeIndex)
                                break

                            attemptedTimes = attemptedTimes + 1
                            time.sleep(retryInterval)
                            if (attemptedTimes >= retryTimes):
                                sweets = "WARNING: trying operation execute-bookRoom for task with id [" + str(coffeeId) + "] reached limit, task skipped"
                                sweetsOut(sweets)
                                coffeeBeans = "WARNING: trying operation execute-bookRoom for task with id [" + str(coffeeId) + "] reached limit, task skipped"
                                beansOut(coffeeBeans)

                                failureDetailsParsed = {"users":users, "roomId":roomId, "startAt":startAt, "endAt":endAt, "errorMessage":returnValue}
                                failureDetailsText = json.dumps(failureDetailsParsed, ensure_ascii = False)
                                bindFailure(failureDetailsText)

                                os.system("rm " + shelfDirectory + coffeeId)
                                break

        else:

            sweets = "INFO: task queue empty"
            sweetsOut(sweets)

        # then, check and import new tasks

        storeNewCups()

        # lastly, have a rest for a while
        time.sleep(standbyInterval)

except KeyboardInterrupt:
    
    sweets = "INFO: process terminated, bye :)"
    sweetsOut(sweets)