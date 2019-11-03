# Molly - An intensive python package for study-booking system of CDUT Library

**This is one of the projects by Twikor. For more, take a step to my blog [Twikor's (twic.me)](https://twic.me).**

**Molly** is an open source package for python helping handling with the booking process of CDUT Library's study.

This branch is for python *2.7+*, If you are seeking for further support for python 3.5+, please check out branch *v2.0+*.

## Installation

First, install all the dependencies that are required for this package.
```
python -m pip install terminaltables beautifulsoup4
```
Then clone all the files to your computer(mostly a server for continuous support).

## Contents

|File|Detail|
|-|-|
|**dinner.py**|main library file that contains all the methods that you need to handle the boring works|
|**cafe.py**|main application file that automatically book a study for you in case you asked him to in advance|
|**kitchens.json**|the file containing all the information of the  studies in CDUT library|
|**credits.json**|the file containing login information|
|**recipe.json**|the configuration file for automatic study-booking application *cafe.py*|
|**coffeeGrounds.txt**|file recording all the essential logs from `cafe.py`|

## Configurations & Usages

### Login credits

Create a file named **credits.json** besides dinner.py with your login credentials in the following format:

```
{
    "user":"201901010101",
    "passwd":"010101"
}
```

### Dinner.py customizations

If you would like to use dinner directly in the terminal, simply navigate to the folder and import dinner, dinner.py will initialize itself automatically and then you are free to use all the methods.

Once the script is imported, it automatically detects the connection to the server. The script will exit automatically if the check fails.

Otherwise, you may need to set `standbyMode` to `True` if you are using it in script or `cafe.py` for convenience.

### Dinner.py api cheatsheet

#### init()

Initialize the library, including checking connection to the system, loading room information from file and so on.

|Return value|Type|Detail
|-|-|-|
|`True`|bool|\|
|`'Except_RemoteServerUnreachable'`|str|automatic connection test failed|
|`'Except_InvalidLoginCreditsFileFormat'`|str|\|
|`'Except_InvalidLoginCreditsFile'`|str|file not exists or permission error|
|`'Except_InvalidRoomInfoFileFormat'`|str|\|
|`'Except_InvalidRoomInfoFile'`|str|file not exists or permission error|

#### getRoomNumberById(roomNumber)

Return the `roomNumber` for the specific room with the `roomId`.

|Return value|Type|Detail|
|-|-|-|
|`roomNumber`|str|\|

#### getRoomIdByNumber(roomId)

Get the roomId for the specific room with the `roomNumber`.

|Return value|Type|Detail|
|-|-|-|
|`roomId`|int|\|

#### getFreshCookie()

Login to the system using the credentials in credits.json file, and return the fresh cookie.

|Return value|Type|Detail|
|-|-|-|
|`True`|bool|\|
|`'Except_RemoteServerUnreachable'`|str|connection test failure|

#### getUserInfoByCode(code = None, pretiffied = False):

Use the socket to filter fellow fellow companions. 

Accationally, you do not have to enter the full id number. For example:

To filter all the students in your class, use it like this `'2019060103'`. To filter all the students who are of the same major as yours, use it like this `'20190601'`.

|Parameter|Type|Default|Example|Detail|
|-|-|-|-|-|
|`code`|str|`None`|`'201906010326'`|the student id, not required to be completed|
|`prettified`|bool|`False`|True|whether to use the data to render a user-friendly table in terminal|

Defaultly return the booking information for a given id of a room in json format. If setting parameter 2 to True, it will use terminaltables to render a prettier user interface right in your browser.

#### getRoomBookingInfo(roomId, prettified = False)

|Parameter|Type|Default|Example|Detail|
|-|-|-|-|-|

Defaultly return the booking information for a given id of a room in json format. If setting parameter 2 to True, it will use terminaltables to render a prettier user interface right in your browser.

#### bookRoom(users, roomId, beginDay, beginTime, endDay, endTime)

|Parameter|Type|Default|Example|Detail|
|-|-|-|-|-|
|`users`|dic|`None`|`[201906010326,201606013028]`|users to share the room gathered in a dictionary|
|`roomId`|int|`None`|`125`|could be obtained using `getRoomIdByNumber()`|
|`beginDay`|str|None|`2019-11-02`|\|
|`beginTime`|str|None|`08:00:00`|\|
|`endDay`|str|None|`2019-11-02`|\|
|`endTime`|str|None|`10:00:00`|\|

For example,
```
bookRoom([201906010326,201906010328],97,"2019-10-13","17:02:00","2019-10-13","18:59:59")
```

|Return value|Type|Detail|
|-|-|-|
|`True`|bool|successfully booked the specified room|
|`<Error message>`|str|details of the failure|

#### renewRoom()

Renew the room which is currently used for further 2 hours if not occupied by other booking registries.

|Return value|Type|Detail|
|-|-|-|
|`True`|bool|successfully renewed the room which is currently using|
|`<Error message>`|str|details of the failure|

#### cancelRoom(bookingId)

|Parameter|Type|Default|Example|Detail|
|-|-|-|-|-|
|`bookingId`|int|`None`|393487|could be obtained using `getMyBookingInfo()`|

Cancel a room with the specific `bookingId` which could be got by using `getMyBookingInfo()` funcion.
Return `True` if successful, or error message if failed.

|Return value|Type|Detail|
|-|-|-|
|`True`|bool|successfully renewed the room which is currently using|
|`<Error message>`|str|details of the failure|

#### getMyBookingInfo(prettified = False)

|Parameter|Type|Default|Example|Detail|
|-|-|-|-|-|
|`prettified`|bool|`False`|True|whether to use the data to render a user-friendly table in terminal|

Refresh the cookie and make the query, then return the booking information of the current user.
Set parameter `prettified` to `True` to use terminal-tables which makes it easier to check the information returnded.

Notice that once you have signed up at the entrance of the study or the time(20 minutes) has passed without your signing-up, the entry will disappear from there. So you may have to use `getMyBookingHistory()` instead.

#### getMyBookingHistory()

|Parameter|Type|Default|Example|Detail|
|-|-|-|-|-|
|`prettified`|bool|False|`True`|whether to use the data to render a user-friendly table in terminal|
|`getEntriesNumber`|int|`10`|`35`|the number of history booking entries you want to obtain|

### Cafe.py automatic booking configurations

Creat a new file named **recipe.json**, where you are free to present your booking tasks to cafe.py like below:

```
[
    {
        "roomId":125,
        "users":[
            "201906010326"
        ],
        "startAt": "2019-11-03 09:40:00",
        "endAt": "2019-11-03 13:40:00",
        "triggerAt": "2019-10-28 00:01:10"
    },
    {
        "roomId":125,
        "users":[
            "201906010326",
            "201906010328"
        ],
        "startAt": "2019-11-04 09:40:00",
        "endAt": "2019-11-04 13:40:00",
        "triggerAt": "2019-10-29 00:01:10"
    }
]
```

|Parameter|Type|Example|Detail|
|-|-|-|-|
|`roomId`|int|125|\|
|`users`|dic|`[201906010326,201906010328]`|\|
|`startAt`|str|`'2019-11-03 09:40:00'`|`startDate+" "+startTime`|
|`endAt`|str|`'2019-11-03 13:40:00'`|`endDate+" "+endTime`|
|`triggerAt`|str|`'2019-11-03 09:40:00'`|\|

The default base configurations like debug mode, retry intervals are listed below, you are free to modify them in **cafe.py**.

|Parameter|Type|Default|Detail|
|-|-|-|-|
|`recipeFileName`|str|`"recipe.json"`|\|
|`refreshRecipeCycle`|int|`60`|\|
|`retryTimes`|int|`5`|\|
|`retryInterval`|int|`1`|\|
|`standbyInterval`|int|`1`|\|

The **cafe.py** will automatically absorb the configurations in **recipe.json**, put them into job queue and remove the file.

All the process logs could be found in **coffeeGounds.txt** for debugging purposes.

## Contributions

Notice: according to the license, you are required to make appropriate contributions to this project in case you run it. Check out [Toay's pre-mit license](https://toay.org/projects/pre-mit-license) for more information.

You can make contributions to this project in the following ways.

* complete the library file **dinner.py** by add functions or making optimizations
* complete the application file **cafe.py**
* making your application using library **dinner.py** and publish your project using the same license

## This and that

Thisn project is maintained by twikor at **[Toay laboratory](https://toay.org)**, a place where we enjoy making creative things. We hope the ones who think of themselves useful to a newly-founded non-profit studio for creators, please don't hesitate joining us.

For more information, please have a look at **[this](https://toay.org/about/sigining-up)**.