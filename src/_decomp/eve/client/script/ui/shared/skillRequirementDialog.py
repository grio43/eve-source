#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\skillRequirementDialog.py
import evetypes
import localization
from carbonui import Align, ButtonVariant, uiconst, TextBody, TextColor, TextHeader
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.button import Button
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.shared.tooltip.skill_requirement import AddSkillRequirements, AddTrainingTimeForType, AddSkillAction, GetActivityTextForType

def prompt_missing_skill_requirements(typeID):
    wnd = SkillRequirementDialog.Open(typeID=typeID)
    if wnd.ShowModal() == 1:
        return wnd.result
    else:
        return None


class SkillRequirementDialog(Window):
    default_name = 'SkillRequirementDialog'
    default_windowID = 'skill_requirement_dialog'
    default_iconNum = 'res:/UI/Texture/WindowIcons/info.png'
    default_captionLabelPath = 'UI/Generic/Information'
    default_width = 300
    default_height = 300
    default_minSize = (default_width, default_height)
    default_isStackable = False

    def ApplyAttributes(self, attributes):
        super(SkillRequirementDialog, self).ApplyAttributes(attributes)
        self.show_window_controls = False
        self.MakeUnResizeable()
        itemTypeID = attributes.typeID
        skillSvc = sm.GetService('skills')
        requiredSkills = skillSvc.GetSkillsMissingToUseItemRecursive(itemTypeID)
        requiredSkillsList = [ (typeID, level) for typeID, level in requiredSkills.iteritems() ]
        missingSkillBooks = skillSvc.GetSkillBooksMissingFromList(requiredSkills)
        totalMissingSkillLevels = skillSvc.GetTotalMissingSkillLevelsToUseItem(itemTypeID)
        self.grid = None
        self._main_container = main = ContainerAutoSize(parent=self.content, align=Align.TOTOP, callback=self._on_content_size_changed)
        self.headerCont = Container(parent=main, align=Align.TOTOP, height=80)
        self.typeIcon = ItemIcon(name='icon', parent=self.headerCont, typeID=itemTypeID, pos=(0, 0, 64, 64))
        self.typeNameLabel = TextHeader(parent=self.headerCont, text=evetypes.GetName(itemTypeID), pos=(80, 10, 0, 0))
        TextBody(parent=main, align=Align.TOTOP, color=TextColor.SECONDARY, text=localization.GetByLabel('Tooltips/SkillPlanner/SkillsRequiredToPerformActivity', doActivity=GetActivityTextForType(itemTypeID)), padBottom=5)
        gridContainer = ContainerAutoSize(parent=main, align=Align.TOTOP)
        self.grid = LayoutGrid(columns=2, state=uiconst.UI_NORMAL, parent=gridContainer)
        AddSkillRequirements(self.grid, requiredSkillsList, missingSkillBooks, totalMissingSkillLevels)
        AddTrainingTimeForType(self.grid, itemTypeID, on_click=self.Close)
        AddSkillAction(self.grid, itemTypeID, on_click_callback=self._confirm)
        button_group = ButtonGroup(parent=main, align=Align.TOTOP, button_size_mode=ButtonSizeMode.STRETCH, padTop=8)
        Button(parent=button_group, label=localization.GetByLabel('Achievements/AuraText/laterButton'), func=self._confirm, variant=ButtonVariant.GHOST)

    def _confirm(self, *args, **kwargs):
        self.Close()

    def _on_content_size_changed(self):
        if not self.grid:
            return
        self.width, self.height = self.GetWindowSizeForContentSize(width=self.grid.width, height=self._main_container.height)
