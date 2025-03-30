#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evelink\client\handlers\local_service\endpoints.py
import uuid
from carbon.common.script.sys.serviceManager import ServiceManager
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
from evelink.client.handlers.local_service.parse import parse, int_optional

class EndpointRegistry(object):
    __instance = None

    def __init__(self):
        if self.__instance is not None:
            raise RuntimeError('Multiple instances of EndpointRegistry not allowed')
        self._endpoints = {}

    @staticmethod
    def instance():
        if EndpointRegistry.__instance is None:
            EndpointRegistry.__instance = EndpointRegistry()
        return EndpointRegistry.__instance

    def register(self, _f = None, **kwargs):

        def deco(f):
            self._endpoints[f.__name__] = (f, dict(kwargs))
            return f

        if _f:
            return deco(_f)
        return deco

    def resolve(self, method, **kwargs):
        endpoint_func, argument_types = self._endpoints[method]
        parsed = parse(kwargs, **argument_types)
        return endpoint_func(**parsed)


register = EndpointRegistry.instance().register

def get_service(name):
    service_manager = ServiceManager.Instance()
    return service_manager.GetService(name)


@register
def ShowRedeemUI():
    get_service('vgsService').ShowRedeemUI()


@register
def ShowBuyOmega():
    get_service('vgsService').ShowBuyOmegaInStore()


@register
def ShowOutstandingTab():
    get_service('monitor').ShowOutstandingTab()


@register(flag=int_optional, constellationID=int_optional, taleID=int_optional, open=bool)
def ShowIncursionTab(**kwargs):
    get_service('journal').ShowIncursionTab(**kwargs)


@register(status=int, forCorp=bool)
def ShowContracts(**kwargs):
    get_service('contracts').ShowContracts(**kwargs)


@register
def OpenIgnoreList():
    get_service('contracts').OpenIgnoreList()


@register
def OpenCreateContract():
    get_service('contracts').OpenCreateContract()


@register(view=int, reset=bool, typeID=int_optional, contractType=int)
def OpenAvailableTab(**kwargs):
    get_service('contracts').OpenAvailableTab(**kwargs)


@register(contractType=int, isCorp=bool)
def OpenAssignedToMe(**kwargs):
    get_service('contracts').OpenAssignedToMe(**kwargs)


@register
def CloseTransmission():
    get_service('transmission').CloseTransmission()


@register(id=int, isAlliance=bool)
def EditBulletin(**kwargs):
    get_service('corp').EditBulletin(**kwargs)


@register(id=int)
def DeleteBulletin(**kwargs):
    get_service('corp').DeleteBulletin(**kwargs)


@register(id=int)
def ShowCorpDetails():
    get_service('corpui').Show(CorpPanel.MY_CORPORATION)


@register(agentID=int, actionID=int, closeWindowOnClick=bool)
def AgentDoAction(**kwargs):
    get_service('agents').DoAction(**kwargs)


@register(agentID=int, charID=int, contentID=int)
def PopupMissionJournal(**kwargs):
    get_service('agents').PopupMission(**kwargs)


@register(agentID=int, charID=int, contentID=int)
def ShowMissionObjectives(**kwargs):
    get_service('agents').ShowMissionObjectives(**kwargs)


@register(agentID=int, charID=int_optional, dungeonID=int)
def PopupDungeonShipRestrictionList(**kwargs):
    get_service('agents').PopupDungeonShipRestrictionList(**kwargs)


@register(typeID=int)
def BuyStationAsk(**kwargs):
    get_service('marketutils').BuyStationAsk(**kwargs)


@register(typeID=int, orderID=int_optional, silently=bool)
def ShowMarketDetails(**kwargs):
    get_service('marketutils').ShowMarketDetails(**kwargs)


@register(marketGroupID=int)
def ShowMarketGroup(**kwargs):
    get_service('marketutils').ShowMarketGroupWithTypes(**kwargs)


@register(typeID=int, orderID=int)
def MatchOrder(**kwargs):
    get_service('marketutils').MatchOrder(**kwargs)


@register(subMethod=str, typeID=int_optional, orderID=int_optional)
def ProcessMarketRequest(**kwargs):
    get_service('marketutils').ProcessRequest(**kwargs)


@register(itemID=int)
def WarpTo(**kwargs):
    get_service('insider').WarpTo(**kwargs)


@register(destination=str)
def TravelTo(**kwargs):
    get_service('insider').TravelTo(**kwargs)


@register
def OpenMilitia():
    get_service('cmd').OpenMilitia()


@register
def OpenInsurgencyDashboard():
    get_service('cmd').OpenInsurgencyDashboard()


@register
def OpenFWInfoTab():
    get_service('cmd').OpenFWInfoTab()


@register(linkNum=int, windowID=str, windowInstanceID=str)
def OnBreadcrumbTextClicked(**kwargs):
    get_service('inv').OnBreadcrumbTextClicked(**kwargs)


@register(stationID=int)
def ShowAssets(**kwargs):
    get_service('assets').Show(**kwargs)


@register
def ShowPetition():
    get_service('petition').Show()


@register(action=str, key=str, name=str)
def ShowCopyCatIGB(**kwargs):
    get_service('copycat').igb(**kwargs)


@register
def OpenAgency():
    get_service('agencyNew').OpenWindow()


@register(contentGroupID=int, itemID=int_optional)
def AgencyOpenAndShow(**kwargs):
    get_service('agencyNew').OpenWindow(**kwargs)


@register(contentGroupID=int, itemID=int, videoID=int, videoPath=str)
def AgencyOpenAndShowHelpVideo(**kwargs):
    agencySvc = get_service('agencyNew')
    agencySvc.OpenWindow(**kwargs)
    agencySvc.LogHelpVideoLinkClicked(kwargs.get('videoPath', ''))


@register
def ShowPayableCorpBills():
    from eve.client.script.ui.shared.neocom.wallet.walletWnd import WalletWindow
    WalletWindow.OpenWalletOnPayableCorpBills()


@register(typeID=int, itemID=int_optional, new=bool, parentID=int_optional, selectTabType=int_optional)
def ShowInfo(**kwargs):
    get_service('info').ShowInfo(**kwargs)


@register(goal_id_int=int)
def OpenGoal(**kwargs):
    from jobboard.client import open_corporation_goal
    goal_id = uuid.UUID(int=kwargs['goal_id_int'])
    open_corporation_goal(goal_id)


@register(goal_id_int=int)
def OpenDailyGoal(**kwargs):
    from jobboard.client import open_daily_goal
    goal_id = uuid.UUID(int=kwargs['goal_id_int'])
    open_daily_goal(goal_id)
