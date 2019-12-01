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

# import essential packages/libraries

import os, sys, datetime, time, json
from terminaltables import AsciiTable

# initialize assets

configurations = []
configurationsToStore = {}

while (True):

    # basic settings

    operationInitialDelay = 10
    shelfDirectory = "./shelf/"
    creditsFile = "./credits.json"
    recipeFile = "./recipe.json"
    
    welcomeWords = "-----\n\
Molly pre-configuration file generator\n\
By twikor@(twic.me)\n\
\n"

    os.system("clear")
    print(welcomeWords + "\
Operation Menu:\n\
    1. add configuration entry\n\
    2. view configuration entries\n\
    3. port to configurations file\n\
    4. port configurations to task queue\n\
    q. exit\n\
ctrl + c to return to this menu\n\
Force exit? try using duble ctrl + c twice\n\
-----")

    try:

        print("[#]Input task id")
        taskId = input(" : ")

        if (taskId == "1"):

            os.system("clear")
            print(welcomeWords + "\
Operation: add configuration entry\n\
-----")

            print("[1/5]Input room id")
            roomId = input(" : ")

            user = None
            userList = []
            print("[2/5]Input user ('' to finish, 'r' to refill)")
            while (user != ""):
                user = input(" : ")
                userList.append(user)
                if (user == "r"):
                    userList = []
                    print(" [*]Input cleared, continue")
            if (userList != []):
                userList.pop(-1)
                print("[3/5]Specify period start-time (%H%M%S)")
            periodStart = input(" : ")
            print("[4/5]Specify period end-time (%H%M%S)")
            periodEnd = input(" : ")
            #applyToList = input("Specify the dates you want to apply the period to (JSON, (%Y%m%d)): ")

            applyTo = None
            applyToList = []

            print("[5/5]Specify dates to apply the period to ('' to finish, 'r' to refill)")
            while (applyTo != ""):
                applyTo = input(" : ")
                applyToList.append(applyTo)
                if (applyTo == "r"):
                    applyToList = []
                    print(" [*]Input cleared, continue")

            if (applyToList != []):
                applyToList.pop(-1)

            currentTimestamp = int(time.time())

            for applyToDate in applyToList:
                startAtTimeStructure = time.strptime(str(applyToDate) + str(periodStart), "%Y%m%d%H%M%S")
                startAtTimeStamp = time.mktime(startAtTimeStructure)
                startAtTime = time.strftime('%Y-%m-%d %H:%M:%S', startAtTimeStructure)

                endAtTimeStructure = time.strptime(applyToDate + periodEnd, "%Y%m%d%H%M%S")
                endAtTimeStamp = time.mktime(endAtTimeStructure)
                endAtTime = time.strftime('%Y-%m-%d %H:%M:%S', endAtTimeStructure)

                triggerAtDate = time.strftime("%Y%m%d", time.localtime(startAtTimeStamp - 6 * 24 * 3600))

                operationDelay = operationInitialDelay
                configurationToStore = {"roomId": roomId, "users": userList, "startAt": startAtTime, "endAt": endAtTime}
                if (triggerAtDate not in configurationsToStore):
                    configurationsToStore[triggerAtDate] = []
                    operationDelay = operationInitialDelay
                else:
                    countSameTriggerAtDateRegistries = len(configurationsToStore[triggerAtDate])
                    operationDelay = operationInitialDelay + countSameTriggerAtDateRegistries * 20
                
                configurationToStore["triggerAt"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.mktime(time.strptime(triggerAtDate, "%Y%m%d")) + operationDelay))
                configurationsToStore[triggerAtDate].append(configurationToStore)

            configurations = []
            for configurationTriggerDateGroup in configurationsToStore.values():
                for index, configuration in enumerate(configurationTriggerDateGroup):
                    configurations.append(configurationTriggerDateGroup[index])

        elif (taskId == "2"):

            os.system("clear")
            print(welcomeWords + "\
Operation: view configuration entries\n\
-----")

            tableData = [['RoomId', 'User', 'StartAt', 'EndAt', 'TriggerAt']]
            for configuration in configurations:
                tableData.append([configuration['roomId'], configuration['users'], configuration['startAt'], configuration['endAt'], configuration['triggerAt']])
            tableTitle = " Configuration entries in stock "
            generateTable = AsciiTable(tableData, tableTitle)
            print(generateTable.table)
            print("[*]Use operation 3 to stage all entries to the file, or operation 4 to stage directly to task queue")

        elif (taskId == "3"):

            os.system("clear")
            print(welcomeWords + "\
Operation: port to configurations file\n\
-----")

            if (configurations == []):
                print("[*]No task in stock, you have to add them before porting")
            else:
                if (os.path.isfile(recipeFile) == True):
                    print("[*]Recipe file already exists, override? ['Y' to continue/any other to cancel]")
                    confirmAction = input(" : ")
                    if (confirmAction != "Y"):
                        print("[*]Operation canceled")
                    else:
                        try:
                            os.system("rm " + recipeFile)
                        except:
                            print("[*]Error removing recipe file")
                        else:
                            print("[*]Successfully removed old recipe file")

                try:
                
                    os.system('touch ' + recipeFile)

                    recipeFile = open(recipeFile, 'a')
                    recipeList = configurations
                    recipeJson = json.dumps(recipeList, ensure_ascii = False)
                    recipeFile.write(recipeJson)
                    recipeFile.close()

                except:
                    print("[*]Error porting to recipe file")
                else:
                    print("[*]Successfully ported entries to recipe file")
                    print("[*]Clean up? ('Y' to continue, any other to cancel)")
                    confirmAction = input(" : ")
                    if (confirmAction == "Y"):
                        configurations = []
                        configurationsToStore = {}

        elif (taskId == "4"):

            os.system("clear")
            print(welcomeWords + "\
Operation: port configurations to task queue\n\
-----")

            print("Porting to task queue may influence standby tasks and can be hard to reverse, confirm? ('Y' to continue, any other to cancel)")
            confirmAction = input(" : ")
            if (confirmAction == "Y"):
                
                coffees = []
                toImportTasks = configurations
                for toImportTaskIndex, toImportTask in enumerate(toImportTasks):
                    toImportTaskTriggerAt = toImportTask['triggerAt']
                    toImportTaskTriggerAtTimeStructure = time.strptime(toImportTaskTriggerAt,"%Y-%m-%d %H:%M:%S")
                    toImportTaskId = time.strftime("%Y%m%d%H%M%S", toImportTaskTriggerAtTimeStructure)
                    toImportTask['taskId'] = toImportTaskId
                    toImportTask['attemptedTimes'] = 0

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

            else:
                print("[*]Operation canceled")
        elif (taskId == "q"):
            print("[#]Bye :)")
            break
        else:
            print("[#]Task not found")

        print("[#]Process finished")
        print("[#]To return to menu use ctrl + c, automatically return in 300 seconds")
        time.sleep(300)
    except KeyboardInterrupt:
        print("\n[#]Signal received, returning to menu :)")
        time.sleep(0.5)
