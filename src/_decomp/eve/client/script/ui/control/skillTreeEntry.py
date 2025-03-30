#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\skillTreeEntry.py
from carbonui import const as uiconst
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.skillTreeCont import SkillTreeCont

class SkillTreeEntry(Generic):
    __guid__ = 'listentry.SkillTreeEntry'
    default_showHilite = True
    isDragObject = True

    def ApplyAttributes(self, attributes):
        super(SkillTreeEntry, self).ApplyAttributes(attributes)
        self.initialized = False
        self.skillService = sm.GetService('skills')
        self.infoService = sm.GetService('info')

    def Load(self, data):
        super(SkillTreeEntry, self).Load(data)
        indent = 15 * data.indent - 11
        if not getattr(self, 'skillTreeCont', None):
            self.skillTreeCont = SkillTreeCont(parent=self, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, height=0, typeID=data.typeID, requiredLevel=data.lvl, indent=indent)

    def GetHeight(self, *args):
        return 28

    def OnDblClick(self, *args):
        self.skillTreeCont.OnDblClick()

    def GetMenu(self):
        return self.skillTreeCont.GetMenu()

    def GetDragData(self, *args):
        return self.skillTreeCont.GetDragData()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        self.skillTreeCont.LoadTooltipPanel(tooltipPanel)
