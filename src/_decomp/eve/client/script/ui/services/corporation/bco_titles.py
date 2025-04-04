#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\corporation\bco_titles.py
import math
import localization
from carbon.common.script.sys.row import Row
from eve.client.script.ui.services.corporation.bco_base import BaseCorpObject
from eve.client.script.ui.shared.neocom.corporation import corpUISignals

class TitlesO(BaseCorpObject):
    __guid__ = 'corpObject.titles'

    def __init__(self, boundObject):
        BaseCorpObject.__init__(self, boundObject)
        self.titles = None

    def DoSessionChanging(self, isRemote, session, change):
        if 'corpid' in change:
            self.titles = None

    def Reset(self):
        self.titles = None

    def OnTitleChanged(self, corpID, titleID, change):
        try:
            if self.titles is None:
                return
            bAdd, bRemove = self.GetAddRemoveFromChange(change)
            key = titleID
            if bAdd:
                header = None
                for example in self.titles.itervalues():
                    header = example.header
                    break

                if header is None:
                    header = change.keys()
                line = []
                for columnName in header:
                    line.append(change[columnName][1])

                title = Row(header, line)
                self.titles[key] = title
            elif bRemove:
                if self.titles.has_key(key):
                    del self.titles[key]
            elif self.titles.has_key(key):
                title = self.titles[key]
                for columnName in change.iterkeys():
                    setattr(title, columnName, change[columnName][1])

                self.titles[key] = title
        finally:
            corpUISignals.on_title_changed(corpID, titleID, change)

    def GetTitles(self):
        if self.titles is None:
            self.titles = self.GetCorpRegistry().GetTitles()
            for title in (t for t in self.titles.itervalues() if not t.titleName):
                num = int(math.log(title.titleID, 2) + 1)
                title.titleName = localization.GetByLabel('UI/Corporations/Common/TitleUntitled', index=num)
                self.titles[title.titleID] = title

        return self.titles

    def UpdateTitle(self, titleID, titleName, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther):
        self.GetCorpRegistry().UpdateTitle(titleID, titleName, roles, grantableRoles, rolesAtHQ, grantableRolesAtHQ, rolesAtBase, grantableRolesAtBase, rolesAtOther, grantableRolesAtOther)

    def UpdateTitles(self, titles):
        self.GetCorpRegistry().UpdateTitles(titles)

    def DeleteTitle(self, titleID):
        self.GetCorpRegistry().DeleteTitle(titleID)
