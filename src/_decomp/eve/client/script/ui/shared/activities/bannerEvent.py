#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\activities\bannerEvent.py
import webbrowser
import eveexceptions
from carbonui import uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.shared.activities.activitiesUIConst import CHOICE_TOGGLE_AURUM_STORE_BY_CATEGORY_ID, CHOICE_TOGGLE_AURUM_STORE_BY_TYPE_IDS, CHOICE_OPEN_SEASON, CHOICE_URL
from localization import GetByLabel
from eve.client.script.ui.shared.message_bus.newsCarouselMessenger import NewsCarouselMessenger

def _OpenSeason(_):
    uicore.cmd.OpenSeason()
    return True


def _ToggleAurumStoreByCategoryID(activity):
    categoryID = activity.GetIntegerParameter()
    sm.GetService('vgsService').ToggleStore(categoryID)
    return True


def _GetAvailableTypeIds(typeIds):
    productTypeIds = set([ product.typeId for offer in sm.GetService('vgsService').GetStore().GetOffers().itervalues() if offer.canPurchase for product in offer.productQuantities.itervalues() ])
    return list(productTypeIds.intersection(typeIds))


def _ToggleAurumStoreByTypeIds(activity):
    typeIds = _GetAvailableTypeIds(set(activity.GetIntegerListParameter()))
    sm.GetService('vgsService').OpenStore(typeIds=typeIds)
    return True


def _OpenURL(activity):
    url = activity.GetUrl()
    if not url:
        return False
    header = GetByLabel('UI/NewActivitiesNotify/GoToWebsiteHeader')
    question = GetByLabel('UI/NewActivitiesNotify/GoToWebsiteQuestion')
    redirectStatus = False
    if url and eve.Message('CustomQuestion', {'header': header,
     'question': question}, uiconst.OKCANCEL) == uiconst.ID_OK:
        webbrowser.open_new(url)
        redirectStatus = True
    return redirectStatus


OPEN_DICT = {CHOICE_TOGGLE_AURUM_STORE_BY_CATEGORY_ID: _ToggleAurumStoreByCategoryID,
 CHOICE_TOGGLE_AURUM_STORE_BY_TYPE_IDS: _ToggleAurumStoreByTypeIds,
 CHOICE_OPEN_SEASON: _OpenSeason,
 CHOICE_URL: _OpenURL}

@eveexceptions.EatsExceptions('protoClientLogs')
def _LogAcknowledged(ad_id):
    message_bus = NewsCarouselMessenger(sm.GetService('publicGatewaySvc'))
    message_bus.acknowledged(ad_id)


def DoAction(activity):
    event = activity.GetEvent()
    if event is None:
        return False
    method = OPEN_DICT.get(event)
    if callable(method):
        _LogAcknowledged(activity.GetID())
        return method(activity)
    return False
