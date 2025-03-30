#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\fitting.py
import dynamicitemattributes
import evetypes
import localization
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.entries.generic import Generic, events
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fittingScreen import FITTING_OWNER_COMMUNITY, FITTING_OWNER_CORP, FITTING_OWNER_ALLIANCE
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from eveservices.menu import GetMenuService

class FittingEntry(Generic):
    __guid__ = 'listentry.FittingEntry'
    isDragObject = True

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes

    def Startup(self, *args):
        parent = Container(name='parent', parent=self, align=uiconst.TOALL, pos=(0, 0, 16, 0))
        self.sr.have = Icon(parent=self, align=uiconst.CENTERRIGHT, left=0, top=0, height=16, width=16)
        self.sr.ownerTypeIcon = Sprite(parent=parent, align=uiconst.CENTERLEFT, left=0, top=0, height=9, width=9)
        self.sr.ownerTypeIcon.display = False
        self.sr.label = EveLabelMedium(parent=parent, left=5, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT)
        self.sr.label.autoFadeSides = 16
        for eventName in events:
            setattr(self.sr, eventName, None)

    def Load(self, node):
        Generic.Load(self, node)
        hasSkill = self.HasSkill(node)
        if hasSkill:
            iconNum = 'ui_38_16_193'
            hint = localization.GetByLabel('UI/Control/Entries/FittingSkillOK')
        else:
            iconNum = 'ui_38_16_194'
            hint = localization.GetByLabel('UI/Control/Entries/FittingSkillMissing')
        self.sr.have.LoadIcon(iconNum, ignoreSize=True)
        self.sr.have.SetSize(16, 16)
        self.sr.have.hint = hint
        self.sr.label.Update()
        if node.ownerType in (FITTING_OWNER_CORP, FITTING_OWNER_COMMUNITY, FITTING_OWNER_ALLIANCE):
            if node.ownerType == FITTING_OWNER_ALLIANCE:
                texturePath = 'res:/UI/Texture/classes/Fitting/iconAllianceSmall.png'
                hintPath = 'UI/Fitting/AllianceFittingHint'
            elif node.ownerType == FITTING_OWNER_CORP:
                texturePath = 'res:/UI/Texture/classes/FlagIcon/2.png'
                hintPath = 'UI/Fitting/CorpFittingHint'
            else:
                texturePath = 'res:/UI/Texture/classes/Fitting/iconCommunityFitsSmall.png'
                hintPath = 'UI/Fitting/CommunityFittingHint'
            self.sr.ownerTypeIcon.SetTexturePath(texturePath)
            self.sr.ownerTypeIcon.left = self.sr.label.left - 5
            self.sr.ownerTypeIcon.display = True
            self.sr.ownerTypeIcon.hint = localization.GetByLabel(hintPath)
        if node.ownerType is not None:
            self.sr.label.left += 9

    def GetHeight(self, *args):
        node, width = args
        if node.Get('vspace', None):
            node.height = uix.GetTextHeight(node.label, maxLines=1) + node.vspace
        else:
            node.height = uix.GetTextHeight(node.label, maxLines=1) + 4
        return node.height

    def HasSkill(self, node):
        return sm.StartService('fittingSvc').HasSkillForFit(node.fitting)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        fitting = self.sr.node.fitting
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=fitting.name, bold=True)
        tooltipPanel.AddLabelSmall(text=evetypes.GetName(fitting.shipTypeID), bold=True)
        if fitting.description:
            tooltipPanel.AddLabelSmall(text=fitting.description, wrapWidth=200)
        savedDate = getattr(fitting, 'savedDate', None)
        if savedDate:
            saveDateText = localization.GetByLabel('UI/Fitting/FittingLastSavedHint', timestamp=FmtDate(savedDate))
            tooltipPanel.AddLabelMedium(text=saveDateText)


class FittingModuleEntry(Item):
    __guid__ = 'listentry.FittingModuleEntry'

    def Startup(self, *args):
        super(FittingModuleEntry, self).Startup(*args)
        self.labelCont.padRight = 32
        self.padLeft = 2
        self.sr.haveIcon = Icon(parent=self, align=uiconst.CENTERRIGHT, pos=(18, 0, 16, 16))
        self.hints = [localization.GetByLabel('UI/Control/Entries/FittingModuleSkillMissing'), localization.GetByLabel('UI/Control/Entries/FittingModuleSkillOK')]

    def HasSkill(self, node):
        if node.effectID == const.effectRigSlot:
            return True
        godma = sm.StartService('godma')
        return godma.CheckSkillRequirementsForType(node.typeID)

    def Load(self, node):
        super(FittingModuleEntry, self).Load(node)
        isObsolete = node.get('isObsolete', False)
        if isObsolete:
            if getattr(self, 'invalidGroupBG', None) is None:
                self.invalidGroupBG = ErrorFrame(bgParent=self, padding=(2, 2, 2, 2), color=(1, 0, 0, 0.1), opacityLow=0.1, opacityHigh=0.2)
                self.invalidGroupBG.Show()
            texturePath = 'res:/ui/texture/icons/44_32_7.png'
            self.sr.haveIcon.LoadIcon(texturePath, ignoreSize=True)
            self.sr.haveIcon.SetRGBA(1.0, 0.1, 0.1, 0.8)
            self.sr.haveIcon.hint = localization.GetByLabel('UI/Fitting/TypeIsObsolete')
        else:
            hasSkill = self.HasSkill(node)
            if hasSkill:
                iconNum = 'ui_38_16_193'
            else:
                iconNum = 'ui_38_16_194'
            hint = self.hints[hasSkill]
            self.sr.haveIcon.LoadIcon(iconNum, ignoreSize=True)
            self.sr.haveIcon.hint = hint
            if not node.isValidGroup and getattr(self, 'invalidGroupBG', None) is None:
                self.invalidGroupBG = ErrorFrame(bgParent=self, padding=(2, 2, 2, 2), color=(1, 0, 0, 0.1), opacityLow=0.1, opacityHigh=0.2)
                self.invalidGroupBG.Show()
            elif dynamicitemattributes.IsDynamicType(node.typeID):
                if getattr(self, 'errorFrame', None) is None:
                    self.errorFrame = ErrorFrame(bgParent=self, padding=(2, 2, 2, 2), color=(1.0, 0.35, 0.0), opacityLow=0.1, opacityHigh=0.2)
                    self.errorFrame.Show()
                texturePath = 'res:/ui/texture/icons/44_32_7.png'
                self.sr.haveIcon.LoadIcon(texturePath, ignoreSize=True)
                self.sr.haveIcon.SetRGBA(1.0, 0.1, 0.1, 0.8)
                self.sr.haveIcon.hint = localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/AbyssalModuleWarning')
        self.labelCont.padRight = 16 if self.sr.infoicon.state == uiconst.UI_HIDDEN else 32

    def GetMenu(self):
        if self.sr.node and self.sr.node.Get('GetMenu', None):
            return self.sr.node.GetMenu(self)
        if getattr(self, 'itemID', None) or getattr(self, 'typeID', None):
            return GetMenuService().GetMenuFromItemIDTypeID(getattr(self, 'itemID', None), getattr(self, 'typeID', None), includeMarketDetails=True)
        return []
