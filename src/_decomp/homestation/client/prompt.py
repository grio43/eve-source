#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\prompt.py
import dogma.const
import evetypes
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.uicore import uicore
from homestation.session import get_global_session

def prompt_set_home_station_remotely():
    response = uicore.Message('AskSetHomeStationRemotely', buttons=uiconst.YESNO)
    return response == uiconst.ID_YES


def prompt_self_destruct_clone(home_station_id):
    key = 'AskStationSelfDestruct'
    message_args = {'station': home_station_id}
    implants = _get_destructible_implants()
    if implants:
        key = 'AskStationSelfDestructImplants'
        message_args['items'] = ''.join((u'<t>- {}<br>'.format(evetypes.GetName(implant)) for implant in implants))
    response = uicore.Message(key, message_args, buttons=uiconst.YESNO)
    return response == uiconst.ID_YES


def _get_destructible_implants():
    godma = ServiceManager.Instance().GetService('godma')
    implants = godma.GetItem(get_global_session().charid).implants
    return [ implant.typeID for implant in implants if _is_destructible(implant.typeID) ]


def _is_destructible(type_id):
    godma = ServiceManager.Instance().GetService('godma')
    return godma.GetTypeAttribute2(type_id, dogma.const.attributeNonDestructible) == 0.0
