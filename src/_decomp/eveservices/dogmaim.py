#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveservices\dogmaim.py


def GetDogmaIMService():
    return sm.GetService('dogmaIM')


def StartDogmaIMService():
    return sm.StartService('dogmaIM')
