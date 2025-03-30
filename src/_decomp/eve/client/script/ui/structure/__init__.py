#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\__init__.py


def ChangeSignalConnect(signalAndCallbackList, connect = True):
    for signal, callback in signalAndCallbackList:
        if connect:
            signal.connect(callback)
        else:
            signal.disconnect(callback)
