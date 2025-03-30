#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\tanking.py
from behaviors.actions.tanking import ActiveTank
from brennivin.itertoolsext import Bundle

def CreateTankingBehavior():
    return ActiveTank(Bundle(name='Active Tanking'))
