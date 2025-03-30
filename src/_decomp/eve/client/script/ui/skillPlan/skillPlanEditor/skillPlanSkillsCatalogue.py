#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanEditor\skillPlanSkillsCatalogue.py
from carbonui import uiconst
from carbonui.control.button import Button
from eve.client.script.ui.skillPlan import skillPlanUISignals
from eve.client.script.ui.skillPlan.contents.skillEntryPrimaryButton import State
from eve.client.script.ui.skillPlan.skillsCatalogue.skillGroupSkillEntry import SkillGroupSkillEntry
from eve.client.script.ui.skillPlan.skillsCatalogue.skillGroupSkillsBrowser import SkillGroupSkillsBrowser
from eve.client.script.ui.skillPlan.skillsCatalogue.skillsCataloguePanel import SkillsCataloguePanel
from localization import GetByLabel
from skills import skillConst
from skills.skillConst import FILTER_SHOWALL

class EditorSkillEntryPrimaryButton(Button):
    default_iconSize = 24
    default_texturePath = 'res:/UI/Texture/classes/SkillPlan/buttonIcons/buttonIconPlus.png'
    default_soundClick = uiconst.SOUND_ADD_OR_USE

    def ApplyAttributes(self, attributes):
        super(EditorSkillEntryPrimaryButton, self).ApplyAttributes(attributes)
        self.skillPlan = attributes.skillPlan
        self.controller = attributes.get('skillController', None)
        self.func = self.OnClickFunc

    def SetSkillPlan(self, skillPlan):
        self.skillPlan = skillPlan

    def UpdateState(self):
        if not self.controller:
            return
        state = self._GetState()
        if state == State.CAN_ADD_TO_QUEUE:
            self.Enable()
        else:
            self.Disable()

    def _GetState(self):
        if not self.skillPlan:
            return State.CAN_ADD_TO_QUEUE
        else:
            currentLevelInPlan = self.skillPlan.GetHighestLevel(self.controller.GetTypeID())
            if currentLevelInPlan == skillConst.skill_max_level:
                return State.ALL_IN_QUEUE
            return State.CAN_ADD_TO_QUEUE

    def GetHint(self):
        if self.IsEnabled():
            return GetByLabel('UI/SkillPlan/AddSkillLevelToPlan', skillLevel=self._GetSkillLevel() or 1)
        else:
            return GetByLabel('UI/SkillPlan/AllLevelsInPlan')

    def _GetSkillLevel(self):
        if not self.skillPlan:
            return 1
        return self._GetNextLevel()

    def _GetNextLevel(self):
        return self.skillPlan.GetNextLevel(self.controller.GetTypeID())

    def OnClickFunc(self, *args):
        if self.skillPlan:
            nextLevel = self._GetNextLevel()
            self.skillPlan.AppendSkillRequirement(self.controller.GetTypeID(), nextLevel)


class EditorSkillGroupSkillEntry(SkillGroupSkillEntry):

    def ApplyAttributes(self, attributes):
        self.skillPlan = attributes.skillPlan
        super(EditorSkillGroupSkillEntry, self).ApplyAttributes(attributes)

    def SetSkillPlan(self, skillPlan):
        self.skillPlan = skillPlan
        self.primaryButton.SetSkillPlan(skillPlan)

    def _CreatePrimaryButton(self):
        if not self.showPrimaryButton or self.primaryButton is not None:
            return
        self.primaryButton = EditorSkillEntryPrimaryButton(parent=self, align=uiconst.TORIGHT, padLeft=8, skillController=self.controller, skillPlan=self.skillPlan)


class EditorSkillGroupSkillsBrowser(SkillGroupSkillsBrowser):

    def ApplyAttributes(self, attributes):
        self.skillPlan = attributes.skillPlan
        super(EditorSkillGroupSkillsBrowser, self).ApplyAttributes(attributes)

    def SetSkillPlan(self, skillPlan):
        self.skillPlan = skillPlan
        for entry in self.entries:
            entry.SetSkillPlan(self.skillPlan)

    def _ConstructEntry(self, controller, parent, i):
        return EditorSkillGroupSkillEntry(parent=parent, align=uiconst.TOLEFT_PROP, width=0.5, padRight=4 if i % self.numColumns else 20, controller=controller, showPrimaryButton=self.showPrimaryButton, skillPlan=self.skillPlan)


class SkillPlanEditorSkillsCataloguePanel(SkillsCataloguePanel):

    def ApplyAttributes(self, attributes):
        self.skillPlan = attributes.skillPlan
        super(SkillPlanEditorSkillsCataloguePanel, self).ApplyAttributes(attributes)
        skillPlanUISignals.on_skill_requirements_changed.connect(self.OnSkillRequirementsChanged)

    def SetSkillPlan(self, skillPlan):
        self.skillGroupSkillsBrowser.SetSkillPlan(skillPlan)

    def ConstructSkillGroupSkillsBrowser(self):
        self.skillGroupSkillsBrowser = EditorSkillGroupSkillsBrowser(parent=self, align=uiconst.TOALL, padding=(0, 20, 0, 10), showPrimaryButton=self.default_show_primary_buttons, skillPlan=self.skillPlan)

    def OnSkillRequirementsChanged(self, skillPlanID):
        if self.skillPlan and skillPlanID == self.skillPlan.GetID():
            self.skillGroupSkillsBrowser.UpdateEntryButtons()

    def OnSkillQueueChanged(self):
        pass

    def GetPrefsKeyAndSelect(self):
        configName = 'skillEditorCatalogueCombo'
        prefskey = ('char', 'ui', configName)
        selectValue = settings.char.ui.Get(configName, FILTER_SHOWALL)
        return (prefskey, selectValue)
