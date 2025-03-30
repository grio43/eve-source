#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\sys\eveAlert.py
import svc

class Alert(svc.alert):
    __guid__ = 'svc.eveAlert'
    __replaceservice__ = 'alert'

    def _GetSessionInfo(self):
        if session:
            return (session.userid,
             session.charid,
             session.solarsystemid2,
             session.stationid)
        return (None, None, None, None)
