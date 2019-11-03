 #!/usr/bin/env python
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
##  - molly/dinner

# import essential packages/libraries

import os, sys, datetime, time, json, hashlib
import dinner as D

reload(sys)
sys.setdefaultencoding('utf8')

# basic configurations are gathered here

debugMode = True#set true to display runtime log

recipeFileName = "recipe.json"
refreshRecipeCycle = 60#time(s)
retryTimes = 5
retryInterval = 1
standbyInterval = 1

# function: output status when in standby mode

def sweetOut(outputContent):
    if (debugMode == True):
        print "[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] " + outputContent

# function: storing of the log data

def collectCoffeeGrounds(coffeeGrounds):

    # output booking status

    if (coffeeGrounds != None):
        if (os.path.isfile('./coffeeGrounds.txt') == False):
            os.system('touch coffeeGrounds.txt')
        
        coffeeGroundsFile = open('coffeeGrounds.txt', 'a')
        contentLineToWrite = str("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] " + coffeeGrounds + '\n')
        coffeeGroundsFile.write(contentLineToWrite)
        coffeeGroundsFile.close()

# load recipe from file to task queue

coffees = []

def getHotCoffees(): 
    global coffees

    # import pre-booking configurations

    if (os.path.isfile('./recipe.json') == True):

        sweet = "INFO: started task-importing operation"
        sweetOut(sweet)
        coffeeGrounds = "INFO: started task-importing operation"
        collectCoffeeGrounds(coffeeGrounds)

        recipeFromFile = open(recipeFileName)

        try:
            toImportTasks = json.load(recipeFromFile)
        except ValueError:
            sweet = "ERROR: task-importing operation failed for invalid recipe file, operation canceled"
            sweetOut(sweet)
            coffeeGrounds = "ERROR: task-importing operation failed for invalid recipe file, operation canceled"
            collectCoffeeGrounds(coffeeGrounds)
        else:
            if (coffees == []):
                for toImportTaskIndex, toImportTask in enumerate(toImportTasks):
                    #toImportTask['taskIndex'] = toImportTaskIndex
                    idHashSource = str(str(toImportTask['roomId']) + toImportTask['startAt'] + toImportTask['endAt'] + toImportTask['triggerAt'])
                    idHash = hashlib.md5(idHashSource)
                    toImportTask['taskId'] = idHash.hexdigest()
                    toImportTask['attemptedTimes'] = 0

                    coffeeGrounds = "INFO: imported task with id [" + toImportTask['taskId'] + "], details: " + json.dumps(toImportTask, ensure_ascii = False)
                    collectCoffeeGrounds(coffeeGrounds)
                    
                    coffees.append(toImportTask)

            else:
                for toImportTaskIndex, toImportTask in enumerate(toImportTasks):
                    coffeesInQueue = len(coffees)
                    #toImportTask['taskIndex'] = coffeesInQueue
                    idHashSource = str(str(toImportTask['roomId']) + toImportTask['startAt'] + toImportTask['endAt'] + toImportTask['triggerAt'])
                    idHash = hashlib.md5(idHashSource)
                    toImportTask['taskId'] = idHash.hexdigest()

                    taskIdList = []
                    for coffee in coffees:
                        taskIdList.append(coffee['taskId'])

                    if (toImportTask['taskId'] not in taskIdList):
                        toImportTask['attemptedTimes'] = 0
                        coffees.append(toImportTask)
                    else:
                        sweet = "WARNING: dulplicated task id [" + toImportTask['taskId'] + "]"
                        sweetOut(sweet)
                        coffeeGrounds = "WARNING: dulplicated task id [" + toImportTask['taskId'] + "]"
                        collectCoffeeGrounds(coffeeGrounds)

                coffeeGrounds = "INFO: task id: [" + toImportTask['taskId'] + "], details: " + json.dumps(coffees, ensure_ascii = False)
                collectCoffeeGrounds(coffeeGrounds)

            os.system('rm recipe.json')

            sweet = "INFO: task imported successfully"
            sweetOut(sweet)
            coffeeGrounds = "INFO: task imported successfully"
            collectCoffeeGrounds(coffeeGrounds)
            return coffees

    else:

        sweet = "INFO: no file to load tasks from, operation skipped"
        sweetOut(sweet)

        return coffees

# get current date time

currentDateTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
currentDate = time.strftime('%Y-%m-%d',time.localtime(time.time()))
currentTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
currentTimestamp = int(time.time())

# start the main loop

sleepCounter = 0
coffees = getHotCoffees()

while(True):

    if (coffees != []):

        for coffeeIndex, coffee in enumerate(coffees):
            coffeeId = coffee['taskId']
            attemptedTimes = coffee['attemptedTimes']
            expectedTimeArray = time.strptime(coffee['triggerAt'], "%Y-%m-%d %H:%M:%S")
            expectedTimeStamp = int(time.mktime(expectedTimeArray))
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

            # do cycle-based routines

            if (int(time.time()) - int(time.mktime(expectedTimeArray)) < 0):#timeComparison = currentTimestamp - expectedTimeStamp
                sweet = "INFO: task with id [" + str(coffeeId) + "] is currently waiting to be triggered"
                sweetOut(sweet)
            else:

                if (attemptedTimes == 0):
                    sweet = "INFO: task with id [" + str(coffeeId) + "] is started successfully"
                    sweetOut(sweet)
                    coffeeGrounds = "INFO: task with id [" + str(coffeeId) + "] is started successfully"
                    collectCoffeeGrounds(coffeeGrounds)

                if (attemptedTimes <= retryTimes):
                    returnValue = False
                    while (returnValue != True):
                        currentDateTime = time.strftime('%m-%d %H:%M:%S',time.localtime(time.time()))
                        sweet = "INFO: trying operation execute-bookRoom for task with id [" + str(coffeeId) + "] for the [" + str(attemptedTimes + 1) + "] time"
                        sweetOut(sweet)
                        D.init(True)
                        returnValue = D.bookRoom(users, roomId, startAtDate, startAtTime, endAtDate, endAtTime)
                        sweet = "INFO: operation completed"
                        sweetOut(sweet)
                        if (returnValue != True):
                            sweet = "ERROR: unable to process operation for task with id [" + str(coffeeId) + "], details: " + returnValue
                            sweetOut(sweet)
                            coffeeGrounds = "ERROR: unable to process operation for task with id [" + str(coffeeId) + "], details: " + returnValue.decode('utf8')
                            collectCoffeeGrounds(coffeeGrounds)
                        else:
                            sweet = "INFO: successfully processed operation for task with id [" + str(coffeeId) + "]"
                            sweetOut(sweet)
                            coffeeGrounds = "INFO: successfully processed operation for task with id [" + str(coffeeId) + "]"
                            collectCoffeeGrounds(coffeeGrounds)
                            coffees.pop(coffeeIndex)
                            break

                        attemptedTimes = attemptedTimes + 1
                        time.sleep(retryInterval)
                        if (attemptedTimes >= retryTimes):
                            sweet = "WARNING: trying operation execute-bookRoom for task with id [" + str(coffeeId) + "] reached limit, task skipped"
                            sweetOut(sweet)
                            coffeeGrounds = "WARNING: trying operation execute-bookRoom for task with id [" + str(coffeeId) + "] reached limit, task skipped"
                            collectCoffeeGrounds(coffeeGrounds)
                            coffees.pop(coffeeIndex)
                            break

    sweet = "INFO: checking tasks in queue for operation"
    sweetOut(sweet)

    time.sleep(standbyInterval)
    sleepCounter = sleepCounter + 1

    if (sleepCounter >= refreshRecipeCycle):
        coffees = getHotCoffees()
        sleepCounter = 0