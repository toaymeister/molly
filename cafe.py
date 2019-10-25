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

# load recipe from file to task queue

coffees = []

def getHotCoffees(): 
    global coffees

    # import pre-booking configurations

    if (os.path.isfile('./recipe.json') == True):

        recipeFromFile = open(recipeFileName)
        toImportTasks = json.load(recipeFromFile)

        if (coffees == []):
            for toImportTaskIndex, toImportTask in enumerate(toImportTasks):
                #toImportTask['taskIndex'] = toImportTaskIndex
                idHashSource = str(str(toImportTask['roomId']) + toImportTask['startAt'] + toImportTask['endAt'] + toImportTask['triggerAt'])
                idHash = hashlib.md5(idHashSource)
                toImportTask['taskId'] = idHash.hexdigest()
                toImportTask['attemptedTimes'] = 0
                coffees.append(toImportTask)

            leftOverContent = "[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] " + json.dumps(coffees, ensure_ascii = False) + "\n"

            if (os.path.isfile('./leftOver.txt') == False):
                os.system('touch leftOver.txt')

            leftOverFile = open('leftOver.txt', 'a')
            leftOverFile.write(leftOverContent)
            leftOverFile.close()

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
                    sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] WARNING: dulplicated task id [" + toImportTask['taskId'] + "]")

            leftOverContent = "[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] " + json.dumps(coffees, ensure_ascii = False) + "\n"

            if (os.path.isfile('./leftOver.txt') == False):
                os.system('touch leftOver.txt')

            leftOverFile = open('leftOver.txt', 'a')
            leftOverFile.write(leftOverContent)
            leftOverFile.close()


        os.system('rm recipe.json')
        return coffees
        
    else:
        return coffees

# get current date time

currentDateTime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
currentDate = time.strftime('%Y-%m-%d',time.localtime(time.time()))
currentTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
currentTimestamp = int(time.time())

# function: output status when in standby mode

def sweetOut(outputContent):
    if (debugMode == True):
        print outputContent

# function: storing of the booking status data

def collectCoffeeGrounds(coffeeGrounds):

    # output booking status

    if (coffeeGrounds != None):
        if (os.path.isfile('./coffeeGrounds.txt') == False):
            os.system('touch coffeeGrounds.txt')
        
        coffeeGroundsFile = open('coffeeGrounds.txt', 'a')
        contentLineToWrite = str(coffeeGrounds + '\n')
        coffeeGroundsFile.write(contentLineToWrite)
        coffeeGroundsFile.close()

# start the main loop

sleepCounter = 0
sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: importing tasks from file")
coffees = getHotCoffees()
sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: importing operation finished successfully")

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
                sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: task with id [" + str(coffeeId) + "] is currently waiting to be triggered")
            else:

                if (attemptedTimes == 0):
                    sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: task with id [" + str(coffeeId) + "] is started successfully")
                    collectCoffeeGrounds("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: task with id [" + str(coffeeId) + "] is started successfully")

                if (attemptedTimes <= retryTimes):
                    returnValue = False
                    while (returnValue != True):
                        currentDateTime = time.strftime('%m-%d %H:%M:%S',time.localtime(time.time()))
                        sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: trying processing task with id [" + str(coffeeId) + "] for the [" + str(attemptedTimes + 1) + "] time")
                        returnValue = D.bookRoom(users, roomId, startAtDate, startAtTime, endAtDate, endAtTime)
                        sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: trying operation completed")
                        if (returnValue != True):
                            sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] ERROR: unable to process task with id [" + str(coffeeId) + "], details: " + returnValue)
                            collectCoffeeGrounds("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] ERROR: unable to process task with id [" + str(coffeeId) + "], details: " + returnValue.decode('utf8'))
                        else:
                            sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: successfully processed task with id [" + str(coffeeId) + "]")
                            collectCoffeeGrounds("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: successfully processed task with id [" + str(coffeeId) + "]")
                            coffees.pop(coffeeIndex)
                            break

                        attemptedTimes = attemptedTimes + 1
                        time.sleep(retryInterval)
                        if (attemptedTimes >= retryTimes):
                            sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] WARNING: trying operation for task with id [" + str(coffeeId) + "] reached limit, skipping")
                            collectCoffeeGrounds("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] WARNING: trying operation for task with id [" + str(coffeeId) + "] reached limit, task skipped")
                            coffees.pop(coffeeIndex)
                            break

    sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: checking for tasks in queue")

    time.sleep(standbyInterval)
    sleepCounter = sleepCounter + 1

    if (sleepCounter >= refreshRecipeCycle):
        sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: importing tasks from file")
        coffees = getHotCoffees()
        sweetOut("[MoCafe " + time.strftime('%m-%d %H:%M:%S',time.localtime(time.time())) + "] INFO: importing operation finished successfully")
        sleepCounter = 0