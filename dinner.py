#!/usr/bin/env python
#-*- coding:utf-8 -*-

## A python library for study-booking system of CDUT Library.
##
## This work is under Toay's PRE-MIT license with extra agreement that:
##  - to help protecting the server, rate limit must be setted below 1 rps
##
## Toay's PRE-MIT license is an open source license that simulates but has prerequisites in front of the MIT license.
##  - Take a step to https://toay.org/projects/pre-mit-license to know more.
##
## Author: twikor(@twic.me)

## Required essential packages/libraries:
##  - sys, socket, request, json, bs4/BeautifulSoup, terminaltables/AsciiTable

# import essential packages/libraries

import sys, socket, requests, json
from bs4 import BeautifulSoup
from terminaltables import AsciiTable

# basic configurations are gathered here

roomListFileName = 'kitchens.json'
loginCreditsFileName = 'credits.json'

socketIp = "202.115.142.139"
socketPort = 81
socketUrl = "http://202.115.142.139:81/"

# firstly, try connecting to server, exit the script if failed

connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connection.settimeout(2)
connectionResult = connection.connect_ex((socketIp,socketPort))

if connectionResult != 0:
    print "remote server could not be connected, script exited :("
    connection.close()
    sys.exit(0)

# import login credits

creditsFromFile = open(loginCreditsFileName)
loginCredits = json.load(creditsFromFile)

# import room information

roomListFromFile = open(roomListFileName)
rooms = json.load(roomListFromFile)

# function: login to get the cookie

def getFreshCookie():
    global cookies

    loginUrl = socketUrl + "login"
    parameter = loginCredits
    loginResponse = requests.post(loginUrl, params = parameter)
    cookies = loginResponse.cookies

    return cookies

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

# function: get room number by id

def getRoomNumberById(roomId):
    return idToNumber[roomId]

# function: get room id by number

def getRoomIdByNumber(roomNumber):
    return numberToId[roomNumber]

# function: get the booking info for a specific room

def getRoomBookingInfo(roomId = None, prettified = False):
    cookies = getFreshCookie()
    if (roomId == None):
        print "lacking parameters, function getRoomBookingInfo exited :("
        return False
    else:
        getRoomBookingInfoUrl = socketUrl + "datafeed"
        parameters = {'method':'list', 'id':roomId}
        getRoomBookingInfoResponse = requests.get(getRoomBookingInfoUrl, params = parameters)
        roomBookingInfo = getRoomBookingInfoResponse
        roomBookingInfoDict = roomBookingInfo.json()

        if (prettified == False):
            roomBookingInfoJsonText = json.dumps(roomBookingInfoDict, ensure_ascii = False)
            return roomBookingInfoJsonText
        else:
            roomBookingInfoDict = json.load(roomBookingInfoDict)
#            tableData = ['']
#            for bookedKitchens in bookingInfoJson:

# function: get the detailed booking information for a specific room

def getRoomBookingInfoDetailed(roomId = None, prettified = False):
    cookies = getFreshCookie()
    if (roomId == None):
        print "lacking parameters, function getRoomBookingInfoDetailed exited :("
        return False
    else:
        getRoomBookingInfoDetailedUrl = socketUrl + "trainingroomnote"
        parameters = {'roomid':roomId}
        getRoomBookingInfoDetailedResponse = requests.get(getRoomBookingInfoDetailedUrl, params = parameters, cookies = cookies)
        roomBookingInfoDetailed = getRoomBookingInfoDetailedResponse
        roomBookingInfoDetailedText = roomBookingInfoDetailed.text

        # processing with soup

        soup = BeautifulSoup(roomBookingInfoDetailedText, 'html.parser')
        roomBookingInfoDetailedPrettified = soup.prettify()
        plate = soup.find('table', attrs = {'class':'table_type_7 responsive_table full_width t_align_l'})
        registries = plate.find_all('tr')
        registriesParsed = []
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
            roomBookingInfoDetailedJsonText = json.dumps(registriesParsed, ensure_ascii = False)
            return roomBookingInfoDetailedJsonText
        else:
            roomBookingRegistries = registriesParsed
            tableData = [['Start Date', 'Start Time', 'End Date', 'End Time', 'Submitted At', 'Submitted By']]
            for roomBookingRegistry in roomBookingRegistries:
                tableData.append([roomBookingRegistry['startDate'], roomBookingRegistry['startTime'], roomBookingRegistry['endDate'], roomBookingRegistry['endTime'], roomBookingRegistry['submittedAt'], roomBookingRegistry['submittedBy']])
            tableTitle = ' Detailed booking information for <' + roomBookingRegistries[0]['roomName'] + '> '
            generateTable = AsciiTable(tableData, tableTitle)
            return generateTable.table

# function: get the detailed booking info for all rooms

def getAllBookingInfoDetailed():
    global kitchens
    if (type == None):
        print "lacking parameters, function getAllBookingInfoDetailed exited :("
        return False
    else:
        allBookingInfoDetailed = []
        for room in kitchens:
            allBookingInfoDetailed.append(getBookingInfoDetailed(room['roomId']))
    return allBookingInfoDetailed

# function: book a room using the cookie got when initialized

def bookRoom(users = None, roomId = None, beginDay = None, beginTime = None, endDay = None, endTime = None):
    cookies = getFreshCookie()
    if ((users == Node) or (roomId == None) or (beginDay == None) or (beginTime == None) or (endDay == None) or (endTime == None)):
        print "lacking parameters, function bookRoom exited :("
        return False
    else:
        bookRoomUrl = socketUrl + "trainingroominfor/save"
        parameters = {"cardid":loginCredits['user'], "roomid":roomId, "beginday":beginDay, "begintime":beginTime, "endday":endDay, "endtime":endTime, "besknote":"", "email":"", "userpho":"0", "usemovepho":"1", "users":users}
        parameters = json.dumps(parameters)
        #sparameters = parameters.decode('utf-8')
        headers = {"content-type": "application/json; charset=UTF-8"}
        bookRoomResponse = requests.post(bookRoomUrl, headers = headers, params = parameters, cookies = cookies)
        bookRoomResult = bookRoomResponse
        print bookRoomResult
        bookRoomResultList = bookRoomResult.json()
        bookRoomResultText = json.dumps(bookRoomResultList, ensure_ascii = False)
        return bookRoomResultText

# function: renew the current room using the cookie got when initialized

def renewRoom():
    cookies = getFreshCookie()
    renewRoomUrl = socketUrl + "trainingroominfor/renew"
    renewRoomResponse = requests.get(renewRoomUrl, cookies = cookies)
    renewRoomResult = renewRoomResponse
    renewRoomResultList = renewRoomResult.json()
    expectState = '续借成功'
    expectState = expectState.decode('utf8')
    returnedState = renewRoomResultList['state']

    if (returnedState == expectState):
        return True
    else:
        errorMessage = renewRoomResultList['state']
        return errorMessage

# function: cancel a specific room using the cookie got when initialized

def cancelRoom(bookId = None):
    cookies = getFreshCookie()
    if (bookId == None):
        print "lacking parameters, function cancelRoom exited :("
        return False
    else:
        cancelRoomUrl = socketUrl + "trainingroombeskinfor/deletemore"
        parameters = {'deleteid':bookId}
        cancelRoomResponse = requests.get(cancelRoomUrl, params = parameters, cookies = cookies)
        cancelRoomResult = cancelRoomResponse
        cancelRoomResultList = cancelRoomResult.json()
        cancelRoomResultJsonText = json.dumps(cancelRoomResultList, ensure_ascii = False)
        expectMessage = '取消成功'
        expectMessage = expectMessage.decode('utf8')
        returnedMessage = cancelRoomResultList['msg']

        if (returnedMessage == expectMessage):
            return True
        else:
            errorMessage = cancelRoomResultList['msg']
            return errorMessage

# function: get my own booking information using the cookie got when initialized

def getMyBookingInfo(prettified = False):
    cookies = getFreshCookie()
    getMyBookingInfoUrl = socketUrl + "trainingroombeskinfor"
    getMyBookingInfoResponse = requests.get(getMyBookingInfoUrl, cookies = cookies)
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
            'startDate':registries[0]['useday'],
            'endDate':registries[0]['useendday'],
            'roomName':registries[0]['roomname'],
            'startTime':registries[0]['begintime'],
            'isChecked':registries[0]['isCheck'],
            'endTime':registries[0]['endtime'],
            'roomId':registries[0]['roomid'],
            'bookId':registries[0]['id'],
            'submittedAt':registries[0]['committime']
        }
        registriesParsed.append(registryParsed)

    if (prettified == False):
        myBookingInfoDetailedParsed = json.dumps(registriesParsed, ensure_ascii = False)
        return myBookingInfoDetailedParsed
    else:
        myBookingRegistries = registriesParsed
        tableData = [['Room Name', 'Room Id', 'Book Id', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Submitted At', 'Is Checked']]
        for myBookingRegistry in myBookingRegistries:
            tableData.append([myBookingRegistry['roomName'], myBookingRegistry['roomId'], myBookingRegistry['bookId'], myBookingRegistry['startDate'], myBookingRegistry['startTime'], myBookingRegistry['endDate'], myBookingRegistry['endTime'], myBookingRegistry['submittedAt'], myBookingRegistry['isChecked']])
        tableTitle = ' My study booking information '
        generateTable = AsciiTable(tableData, tableTitle)
        return generateTable.table