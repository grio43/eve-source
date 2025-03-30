#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelDungeonProgression.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from progression.client.objectivesContainer import ObjectivesContainer

class InfoPanelDungeonProgression(InfoPanelBase):
    default_name = 'InfoPanelDungeonProgression'
    hasSettings = False
    panelTypeID = infoPanelConst.PANEL_DUNGEON_PROGRESSION
    label = 'Dungeon Progression'
    default_iconTexturePath = 'res:/UI/Texture/Classes/DungeonMessaging/InfoPanelIcon.png'
    default_height = 120
    __notifyevents__ = ['OnProgressionAdvancedUpdateInfoPanel',
     'OnProgressionTaskCompleteUpdateInfoPanel',
     'OnProgressionTaskWidgetUpdateInfoPanel',
     'OnProgressionRoomJoinedUpdateInfoPanel']

    def ApplyAttributes(self, attributes):
        InfoPanelBase.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.progressionSvc = sm.GetService('progressionSvc')
        self.objectivesCont = None
        self._ConstructHeader()

    def ConstructNormal(self):
        self.mainCont.Flush()
        self.objectivesCont = ObjectivesContainer(parent=self.mainCont, align=uiconst.TOTOP, progressionSvc=self.progressionSvc, state=uiconst.UI_NORMAL)

    def ConstructCompact(self):
        pass

    def _ConstructHeader(self):
        PlaySound('messaging_system_conduit_play')
        self.header = self.headerCls(name='title', parent=self.headerCont, align=uiconst.CENTERLEFT, text=self.progressionSvc.get_progression_name())

    def OnProgressionRoomJoinedUpdateInfoPanel(self):
        if self.objectivesCont:
            self.objectivesCont.UpdateEntryRoomJoined()

    def OnProgressionAdvancedUpdateInfoPanel(self):
        self.objectivesCont.CompleteObjective(self.GetLastTaskCompleted())

    def OnProgressionTaskCompleteUpdateInfoPanel(self):
        pass

    def OnProgressionTaskWidgetUpdateInfoPanel(self):
        self.objectivesCont.UpdateWidgetObjective()

    def GetLastTaskCompleted(self):
        return self.progressionSvc.GetLastTaskCompleted()

    @staticmethod
    def IsAvailable():
        return sm.GetService('progressionSvc').IsInDungeon()
