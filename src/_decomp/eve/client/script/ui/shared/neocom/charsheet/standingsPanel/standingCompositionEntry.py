#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanel\standingCompositionEntry.py
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.shared.standings.standingsUtil import GetStandingChangeFormatted
from localization import GetByLabel

class StandingCompositionEntry(BaseListEntryCustomColumns):

    def ApplyAttributes(self, attributes):
        super(StandingCompositionEntry, self).ApplyAttributes(attributes)
        self.composition = self.node.composition
        self.ConstructLayout()

    def ConstructLayout(self):
        iconCont = self.AddColumnContainer()
        texturePath = sm.GetService('photo').GetPortrait(self.composition.ownerID, 32)
        Sprite(name='icon', parent=iconCont, align=uiconst.CENTER, texturePath=texturePath, pos=(0, 0, 32, 32))
        ownerName = cfg.eveowners.Get(self.composition.ownerID).ownerName
        self.AddColumnText(ownerName)
        self.AddColumnText(GetStandingChangeFormatted(round(self.composition.standing, 2)))

    @staticmethod
    def GetDynamicHeight(node, width):
        return 30

    @staticmethod
    def GetDefaultColumnWidth():
        return {'': 32,
         GetByLabel('UI/Common/Name'): 100,
         GetByLabel('UI/Common/Standing'): 60}

    @staticmethod
    def GetColumnSortValues(composition):
        return (None, composition.ownerID, composition.standing)

    @staticmethod
    def GetHeaders():
        return ('', GetByLabel('UI/Common/Name'), GetByLabel('UI/Common/Standing'))
