#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\util.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupSeasons
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
import uthread2

def _OpenSeasonsUI():
    wnd = AgencyWndNew.GetIfOpen()
    seasonSvc = sm.GetService('seasonService')
    if wnd and wnd.GetSelectedContentType() == agencyConst.CONTENTTYPE_SEASONS:
        wnd.Close()
    elif seasonSvc.is_season_active() or seasonSvc.is_selection_needed():
        AgencyWndNew.OpenAndShowContentGroup(contentGroupID=contentGroupSeasons, itemID=None)


def OpenSeasonsWindow():
    uthread2.StartTasklet(_OpenSeasonsUI)
