#!/usr/bin/env python3
#-*- coding:utf-8 -*-

## An intensive python library for study-booking system of CDUT Library.
##
## This work is under Toay's PRE-MIT license with extra agreement that:
##  - to help protecting the server, rate limit must be setted below 1 rps
##
## Toay's PRE-MIT license is an open source license that simulates but has prerequisites in front of the MIT license.
##  - Take a step to https://toay.org/projects/pre-mit-license to know more.
##
## Author: twikor(@twic.me)

## Required essential packages/libraries:
##  - os, sys, socket, request, json, bs4/BeautifulSoup, terminaltables/AsciiTable

# import essential packages/libraries

import os, sys, socket, requests, json
from bs4 import BeautifulSoup
from terminaltables import AsciiTable

# basic configurations

standbyMode = True#set this to true if you whould like to init the library yourself

# function: make preparations, in case the configuration files are updated

def init(ignoreConnectionFault = False):
    global loginCredits, rooms, kitchens, idToNumber, numberToId, socketUrl

    # basic configurations are gathered here

    roomListFileName = 'kitchens.json'
    loginCreditsFileName = 'credits.json'

    socketIp = "202.115.142.139"
    socketPort = 81
    socketUrl = "http://202.115.142.139:81/"

    # firstly, try connecting to server, exit the script if failed

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.settimeout(2)
    connectionResult = connection.connect_ex((socketIp, socketPort))

    if connectionResult != 0:
        if (ignoreConnectionFault == False or standbyMode != True):
            print("remote server could not be connected, script exited :(")
            connection.close()
            sys.exit(0)
        else:
            print("remote server could not be connected, ignoring :(")
            connection.close()
            excepted = "Exception_RemoteServerUnreachable"
            return excepted
    else:
        # import login credits

        if (os.path.isfile('./credits.json') == True):

            creditsFromFile = open(loginCreditsFileName)

            try:
                loginCredits = json.load(creditsFromFile)
            except ValueError:
                if (standbyMode != True):
                    print("wrong login credits file format, script exited :(")
                    sys.exit(0)
                else:
                    excepted = 'Exception_InvalidRoomInfoFile'
                    return excepted
            except KeyboardInterrupt:
                if (standbyMode != True):
                    print("action canceled")
                else:
                    excepted = 'Command_CancelAction'
                    return excepted
                
                sys.exit(0)
            else:
                # import room information

                if (os.path.isfile('./kitchens.json') == True):

                    roomListFromFile = open(roomListFileName)

                    try:
                        rooms = json.load(roomListFromFile)
                    except ValueError:
                        if (standbyMode != True):
                            print("invalid login credits file format :(")
                            sys.exit(0)
                        else:
                            excepted = "Exception_InvalidLoginCreditsFileFormat"
                            return excepted
                    except KeyboardInterrupt:
                        excepted = 'Command_CancelAction'
                        return excepted
                    else:
                        # sort all kitchens by types

                        kitchens = {
                            'individual':[],
                            'group':[],
                            'multimedia':[]
                        }

                        for room in rooms:
                            if (room['type'] == 'individual'):
                                kitchens['individual'].append(room['roomId'])
                            elif (room['type'] == 'group'):
                                kitchens['group'].append(room['roomId'])
                            else:
                                kitchens['multimedia'].append(room['roomId'])

                        # pair id-number for kitchens

                        idToNumber = {}

                        for room in rooms:
                            idToNumber[room['roomId']] = room['roomNumber']

                        # pair number-id for kitchens

                        numberToId = {}

                        for room in rooms:
                            numberToId[room['roomNumber']] = room['roomId']

                        return True

                else:
                    if (standbyMode != True):
                        print("invalid room information file :(")
                        sys.exit(0)
                    else:
                        excepted = 'Exception_InvalidRoomInfoFile'
                        return excepted

        else:
            if (standbyMode != True):
                print("invalid login credits file :(")
                sys.exit(0)
            else:
                excepted = 'Exception_InvalidLoginCreditsFile'
                return excepted

if (standbyMode != True):
    init()

# function: get room number by id

def getRoomNumberById(roomId):
    return idToNumber[roomId]

# function: get room id by number

def getRoomIdByNumber(roomNumber):
    return numberToId[roomNumber]

# function: login to get the cookie

def getFreshCookie():
    global cookies

    loginUrl = socketUrl + "login"
    parameter = loginCredits

    try:
        loginResponse = requests.post(loginUrl, params = parameter, timeout = 10)
    except requests.exceptions.RequestException:
        excepted = "Exception_ConnectionTimeOut"
        return excepted
    except KeyboardInterrupt:
        excepted = 'Command_CancelAction'
        return excepted
    else:
        cookies = loginResponse.cookies
        return cookies

# function: get reader's info by its code

def getUserInfoByCode(code = None, pretiffied = False):
    if (code == None):
        print("lacking parameters, function getUserInfoByCode exited :(")
        return False
    else:
        getUserInfoUrl = socketUrl + "trainingroominfor/search"
        parameters = {'searchkay':'CardNo', 'searchtype':'1', 'searchvalue':code}

        try:
            getUserInfoResponse = requests.post(getUserInfoUrl, params = parameters, timeout = 10)
        except requests.exceptions.RequestException:
            excepted = "Exception_ConnectionTimeOut"
            return excepted
        except KeyboardInterrupt:
            excepted = 'Command_CancelAction'
            return excepted
        else:
            userInfo = getUserInfoResponse
            userInfoDict = userInfo.json()
            userRegistries = []
            for user in userInfoDict:
                userRegistry = {
                    'userCode':user['usercode'],
                    'userName':user['username'],
                    'userUnit':user['userunit'],
                    'userType':user['usertype']
                }
                userRegistries.append(userRegistry)

            if (pretiffied == False):
                return userRegistries
            else:
                tableData = [['User Code', 'User Name', 'User Unit', 'User Type']]
                for userRegistry in userRegistries:
                    tableData.append([userRegistry['userCode'], userRegistry['userName'], userRegistry['userUnit'], userRegistry['userType']])
                tableTitle = ' Detailed user information for <' + code + '> '

                generateTable = AsciiTable(tableData, tableTitle)
                return generateTable.table

# function: get the detailed booking information for a specific room

def getRoomBookingInfo(roomId = None, prettified = False, detailed = False):
    cookies = getFreshCookie()
    if (roomId == None):
        print("lacking parameters, function getRoomBookingInfo exited :(")
        return False
    else:
        getRoomBookingInfoUrl = socketUrl + "trainingroomnote"
        parameters = {'roomid':roomId}

        try:
            getRoomBookingInfoResponse = requests.get(getRoomBookingInfoUrl, params = parameters, cookies = cookies, timeout = 10)
        except requests.exceptions.RequestException:
            excepted = 'Exception_ConnectionTimeOut'
            return excepted
        except KeyboardInterrupt:
            excepted = 'Command_CancelAction'
            return excepted
        else:
            roomBookingInfo = getRoomBookingInfoResponse
            roomBookingInfoText = roomBookingInfo.text

            # processing with soup

            soup = BeautifulSoup(roomBookingInfoText, 'html.parser')
            roomBookingInfoPrettified = soup.prettify()
            plate = soup.find('table', attrs = {'class':'table_type_7 responsive_table full_width t_align_l'})
            registries = plate.find_all('tr')
            registriesParsed = []

            if (detailed == True):

                registriesCount = 0
                for registry in registries:
                    if (registriesCount != 0):
                        userInfo = getUserInfoByCode(registry.contents[13])
                        userInfo = userInfo[0]

                        userName = userInfo['userName']
                        userUnit = userInfo['userUnit']
                        userType = userInfo['userType']

                        registryParsed = {
                            'roomName':registry.contents[1].string,
                            'startDate':registry.contents[3].string,
                            'startTime':registry.contents[5].string,
                            'endDate':registry.contents[9].string,
                            'endTime':registry.contents[7].string,
                            'submittedAt':registry.contents[11].string,
                            'userCode':registry.contents[13].string,
                            'userName':userName,
                            'userUnit':userUnit,
                            'userType':userType
                        }
                        registriesParsed.append(registryParsed)
                    registriesCount = registriesCount + 1

            else:

                for registry in registries:
                    registryParsed = {
                        'roomName':registry.contents[1].string,
                        'startDate':registry.contents[3].string,
                        'startTime':registry.contents[5].string,
                        'endDate':registry.contents[9].string,
                        'endTime':registry.contents[7].string,
                        'submittedAt':registry.contents[11].string,
                        'submittedBy':registry.contents[13].string
                    }
                    registriesParsed.append(registryParsed)
                registriesParsed.pop(0)

            if (prettified == False):
                roomBookingInfoJsonText = json.dumps(registriesParsed, ensure_ascii = False)
                return roomBookingInfoJsonText
            else:
                roomBookingRegistries = registriesParsed

                if (detailed == True):

                    tableData = [['Start Date', 'Start Time', 'End Date', 'End Time', 'Submitted At', 'User Code', 'User Name', 'User Unit', 'User Type']]
                    for roomBookingRegistry in roomBookingRegistries:
                        tableData.append([roomBookingRegistry['startDate'], roomBookingRegistry['startTime'], roomBookingRegistry['endDate'], roomBookingRegistry['endTime'], roomBookingRegistry['submittedAt'], roomBookingRegistry['userCode'], roomBookingRegistry['userName'], roomBookingRegistry['userUnit'], roomBookingRegistry['userType']])
                    tableTitle = ' Detailed booking information for <' + roomBookingRegistries[0]['roomName'] + '> '

                else:

                    tableData = [['Start Date', 'Start Time', 'End Date', 'End Time', 'Submitted At', 'Submitted By']]
                    for roomBookingRegistry in roomBookingRegistries:
                        tableData.append([roomBookingRegistry['startDate'], roomBookingRegistry['startTime'], roomBookingRegistry['endDate'], roomBookingRegistry['endTime'], roomBookingRegistry['submittedAt'], roomBookingRegistry['submittedBy']])
                    tableTitle = ' Detailed booking information for <' + roomBookingRegistries[0]['roomName'] + '> '

                generateTable = AsciiTable(tableData, tableTitle)
                return generateTable.table

# function: book a room using the cookie got freshly

def bookRoom(users = None, roomId = None, beginDay = None, beginTime = None, endDay = None, endTime = None):
    cookies = getFreshCookie()
    if ((users == None) or (roomId == None) or (beginDay == None) or (beginTime == None) or (endDay == None) or (endTime == None)):
        print("lacking parameters, function bookRoom exited :(")
        return False
    else:
        userList = []
        for user in users:
            user = str(user)
            userList.append({"usercode":user})
        bookRoomUrl = socketUrl + "trainingroominfor/save"
        body = {"cardid":loginCredits['user'], "roomid":roomId, "beginday":beginDay, "begintime":beginTime, "endday":endDay, "endtime":endTime, "besknote":"dinnerByTwikor", "email":"", "userpho":"0", "usemovepho":"1", "users":userList}
        body = json.dumps(body)
        headers = {"content-type": "application/json; charset=UTF-8"}

        try:
            bookRoomResponse = requests.post(bookRoomUrl, headers = headers, data = body, cookies = cookies, timeout = 10)
        except requests.exceptions.RequestException:
            excepted = 'Exception_ConnectionTimeOut'
            return excepted
        except KeyboardInterrupt:
            excepted = 'Command_CancelAction'
            return excepted
        else:
            bookRoomResult = bookRoomResponse
            bookRoomResultList = bookRoomResult.json()
            bookRoomResultText = json.dumps(bookRoomResultList, ensure_ascii = False)
            expectedStateIncludes = '预约成功'
            expectedStateIncludes = expectedStateIncludes#.decode('utf8')
            returnedState = bookRoomResultList['state']
            if expectedStateIncludes in returnedState:
                return True
            else:
                errorMessage = returnedState
            return errorMessage

# function: renew the current room using the cookie got freshly

def renewRoom():
    cookies = getFreshCookie()
    renewRoomUrl = socketUrl + "trainingroominfor/renew"

    try:
        renewRoomResponse = requests.get(renewRoomUrl, cookies = cookies, timeout = 10)
    except requests.exceptions.RequestException:
        excepted = 'Exception_ConnectionTimeOut'
        return excepted
    except KeyboardInterrupt:
        excepted = 'Command_CancelAction'
        return excepted
    else:
        renewRoomResult = renewRoomResponse
        renewRoomResultList = renewRoomResult.json()
        expectState = '续借成功'
        expectState = expectState#.decode('utf8')
        returnedState = renewRoomResultList['state']

        if (returnedState == expectState):
            return True
        else:
            errorMessage = returnedState
        return errorMessage

# function: cancel a specific room using the cookie got freshly

def cancelRoom(bookingId = None):
    cookies = getFreshCookie()
    if (bookingId == None):
        print("lacking parameters, function cancelRoom exited :(")
        return False
    else:
        cancelRoomUrl = socketUrl + "trainingroombeskinfor/deletemore"
        parameters = {'deleteid':bookingId}

        try:
            cancelRoomResponse = requests.get(cancelRoomUrl, params = parameters, cookies = cookies, timeout = 10)
        except requests.exceptions.RequestException:
            excepted = 'Exception_ConnectionTimeOut'
            return excepted
        except KeyboardInterrupt:
            excepted = 'Command_CancelAction'
            return excepted
        else:
            cancelRoomResult = cancelRoomResponse
            cancelRoomResultList = cancelRoomResult.json()
            cancelRoomResultJsonText = json.dumps(cancelRoomResultList, ensure_ascii = False)
            expectMessage = '删除成功'
            expectMessage = expectMessage#.decode('utf8')
            returnedMessage = cancelRoomResultList['msg']

            if (returnedMessage == expectMessage):
                return True
            else:
                errorMessage = returnedMessage
                return errorMessage

# function: get my own booking information using the cookie got freshly

def getMyBookingInfo(prettified = False):
    cookies = getFreshCookie()
    getMyBookingInfoUrl = socketUrl + "trainingroombeskinfor"

    try:
        getMyBookingInfoResponse = requests.get(getMyBookingInfoUrl, cookies = cookies, timeout = 10)
    except requests.exceptions.RequestException:
        excepted = 'Exception_ConnectionTimeOut'
        return excepted
    except KeyboardInterrupt:
        excepted = 'Command_CancelAction'
        return excepted
    else:
        myBookingInfo = getMyBookingInfoResponse
        myBookingInfoText = myBookingInfo.text

        # processing with soup

        soup = BeautifulSoup(myBookingInfoText, 'html.parser')
        myBookingInfoPrettified = soup.prettify()
        plate = soup.find_all('script', attrs = {'type':'text/javascript'})
        plateSource = plate[14].text
        registriesText = plateSource[plateSource.find('var moreroombesklist = ')+23:plateSource.find(';\r\n  createoneroomview()')]
        registries = json.loads(registriesText)
        registriesParsed = []
        for registry in registries:
            registryParsed = {
                'startDate':registry['useday'],
                'endDate':registry['useendday'],
                'roomName':registry['roomname'],
                'startTime':registry['begintime'],
                'isChecked':registry['isCheck'],
                'endTime':registry['endtime'],
                'roomId':registry['roomid'],
                'bookingId':registry['id'],
                'submittedAt':registry['committime']
            }
            registriesParsed.append(registryParsed)

        if (prettified == False):
            myBookingInfoDetailedParsed = json.dumps(registriesParsed, ensure_ascii = False)
            return myBookingInfoDetailedParsed
        else:
            myBookingRegistries = registriesParsed
            tableData = [['Room Name', 'Room Id', 'Book Id', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Submitted At', 'Is Checked']]
            for myBookingRegistry in myBookingRegistries:
                tableData.append([myBookingRegistry['roomName'], myBookingRegistry['roomId'], myBookingRegistry['bookingId'], myBookingRegistry['startDate'], myBookingRegistry['startTime'], myBookingRegistry['endDate'], myBookingRegistry['endTime'], myBookingRegistry['submittedAt'], myBookingRegistry['isChecked']])
            tableTitle = ' My study booking information '
            generateTable = AsciiTable(tableData, tableTitle)
            return generateTable.table
    
# funcion: get my own booking history using the cookie got freshly

def getMyBookingHistory(prettified = False, getEntriesNumber = 10):
    cookies = getFreshCookie()
    getMyBookingHistoryUrl = socketUrl + "moretraingroombesklog"
    
    expectedPageOffset = (getEntriesNumber // 10) * 10
    currentPageOffset = 0

    myBookingHistoryRegistries = []

    while (currentPageOffset <= expectedPageOffset):

        parameters = {'pager.offset':currentPageOffset}

        try:
            getMyBookingHistoryResponse = requests.get(getMyBookingHistoryUrl, params = parameters, cookies = cookies, timeout = 10)
        except requests.exceptions.RequestException:
            excepted = 'Exception_ConnectionTimeOut'
            break
        except KeyboardInterrupt:
            excepted = 'Command_CancelAction'
            break
        else:
            excepted = ''
            currentPageRegistriesParsed = []
            myBookingHistory = getMyBookingHistoryResponse
            myBookingHistoryText = myBookingHistory.text

            # processing with soup

            soup = BeautifulSoup(myBookingHistoryText, 'html.parser')
            myBookingHistoryTextPrettified = soup.prettify()
            plate = soup.find('table', attrs = {'class':'table_type_7 responsive_table full_width t_align_l'})
            currentPageRegistries = plate.find_all('tr')
            for currentPageRegistry in currentPageRegistries:
                currentPageRegistryParsed = {
                    'roomName':currentPageRegistry.contents[3].string,
                    'submittedAt':currentPageRegistry.contents[5].string,
                    'startDate':currentPageRegistry.contents[7].string,
                    'startTime':currentPageRegistry.contents[9].string,
                    'endDate':currentPageRegistry.contents[11].string,
                    'endTime':currentPageRegistry.contents[13].string
                }
                currentPageRegistriesParsed.append(currentPageRegistryParsed)
            currentPageRegistriesParsed.pop(0)

            myBookingHistoryRegistries = myBookingHistoryRegistries + currentPageRegistriesParsed

            registriesCount = len(myBookingHistoryRegistries)
            toPop = registriesCount - getEntriesNumber
            hasPopped = 0
            while (hasPopped < toPop):
                myBookingHistoryRegistries.pop()
                hasPopped = hasPopped + 1

            currentPageOffset = currentPageOffset + 10

    if (excepted.startswith('Except') == False):
        if (prettified == False):
            myBookingHistoryJsonText = json.dumps(myBookingHistoryRegistries, ensure_ascii = False)
            return myBookingHistoryJsonText
        else:
            tableData = [['Room Name', 'Submitted At', 'Start Date', 'Start Time', 'End Date', 'End Time']]
            for myBookingHistoryRegistry in myBookingHistoryRegistries:
                tableData.append([myBookingHistoryRegistry['roomName'], myBookingHistoryRegistry['submittedAt'], myBookingHistoryRegistry['startDate'], myBookingHistoryRegistry['startTime'], myBookingHistoryRegistry['endDate'], myBookingHistoryRegistry['endTime']])
            tableTitle = ' My booking history '
            generateTable = AsciiTable(tableData, tableTitle)
            return generateTable.table
    else:
        return excepted
