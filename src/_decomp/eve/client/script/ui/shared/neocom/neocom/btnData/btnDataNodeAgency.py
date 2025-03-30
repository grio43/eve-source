#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataNodeAgency.py
from eve.client.script.ui.shared.agencyNew import agencyBookmarks
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupProvider
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNode import BtnDataNode

class BtnDataNodeAgency(BtnDataNode):

    def GetMenu(self):
        from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
        m = BtnDataNode.GetMenu(self)
        m.append(None)
        for contentGroupID in agencyBookmarks.GetBookmarks():
            contentGroup = contentGroupProvider.GetContentGroup(contentGroupID)
            m.append((contentGroup.GetName(), AgencyWndNew.OpenAndShowContentGroup, (contentGroupID,)))

        return m
