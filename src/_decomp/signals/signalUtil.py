#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\signals\signalUtil.py


def ChangeSignalConnect(signalAndCallbackList, connect = True):
    for signal, callback in signalAndCallbackList:
        if connect:
            signal.connect(callback)
        else:
            signal.disconnect(callback)


def ConnectSignals(signalAndCallbackList):
    for signal, callback in signalAndCallbackList:
        signal.connect(callback)


def DisconnectSignals(signalAndCallbackList):
    for signal, callback in signalAndCallbackList:
        signal.disconnect(callback)
