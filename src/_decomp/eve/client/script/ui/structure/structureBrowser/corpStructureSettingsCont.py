#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\corpStructureSettingsCont.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from localization import GetByLabel
from eve.client.script.ui.structure.deployment.deploymentCont import ReinforcementTimeCont
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from carbonui.button.group import ButtonGroup

class CorpStructureSettingsCont(Container):
    default_name = 'CorpStructureSettingsCont'
    TAB_ID = 'CORPSTRUCTURESETTINGS'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.structureBrowserController = attributes.structureBrowserController
        self.isInitialized = False

    def OnTabSelect(self):
        self.structureBrowserController.SetTabSelected(self.TAB_ID)
        self.LoadPanel()

    def LoadPanel(self):
        if self.isInitialized:
            return
        reinforceCont = Container(parent=self, padding=6, clipChildren=True)
        headerCont = Container(parent=reinforceCont, name='headerCont', align=uiconst.TOTOP, height=16, padTop=10)
        headerText = GetByLabel('UI/StructureBrowser/DefaultReinforcement')
        reinforceTimeHeader = EveLabelLarge(text=headerText, parent=headerCont, align=uiconst.CENTERLEFT, top=2, left=4)
        defaultReinforcementHint = GetByLabel('UI/StructureBrowser/DefaultReinforcementHint')
        helpIconLeft = reinforceTimeHeader.left + reinforceTimeHeader.textwidth + 2
        MoreInfoIcon(parent=headerCont, hint=defaultReinforcementHint, left=helpIconLeft, align=uiconst.CENTERLEFT)
        reinforceWeekday, reinforceHour = sm.GetService('corp').GetStructureReinforceDefault()
        self.reinforcementTimeCont = ReinforcementTimeCont(parent=reinforceCont, name='reinforcementTimeCont', align=uiconst.TOTOP, left=8, padRight=8)
        self.reinforcementTimeCont.LoadCont(reinforceWeekday, reinforceHour)
        buttons = ButtonGroup(parent=reinforceCont, idx=0)
        buttons.AddButton(GetByLabel('UI/Commands/Apply'), self._ApplyReinforceChanges)
        self.isInitialized = True

    def _ApplyReinforceChanges(self, *args):
        reinforceWeekday, reinforceHour = self.reinforcementTimeCont.GetReinforcementTime()
        sm.GetService('corp').SetStructureReinforceDefault(reinforceHour)
