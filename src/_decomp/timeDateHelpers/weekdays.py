#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\timeDateHelpers\weekdays.py
DAY_NAME_TEXT = ['/Carbon/UI/Common/Days/Monday',
 '/Carbon/UI/Common/Days/Tuesday',
 '/Carbon/UI/Common/Days/Wednesday',
 '/Carbon/UI/Common/Days/Thursday',
 '/Carbon/UI/Common/Days/Friday',
 '/Carbon/UI/Common/Days/Saturday',
 '/Carbon/UI/Common/Days/Sunday']

def GetLabelPathForWeekday(weekday):
    return DAY_NAME_TEXT[weekday]
