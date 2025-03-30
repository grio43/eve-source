#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loginrewards\client\util.py
from eve.common.lib.vgsConst import CATEGORYTAG_GAMETIME

def open_vgs_to_buy_omega_time(*args):
    sm.GetService('vgsService').OpenStore(categoryTag=CATEGORYTAG_GAMETIME)
