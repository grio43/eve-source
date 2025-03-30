#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\views\outputFramedContainers.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.const import CENTERRIGHT, TOALL, UI_NORMAL, UI_DISABLED
from carbonui import Density
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.environment import invControllers as invCtrl
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.themeColored import FrameThemeColored, FillThemeColored
from eve.client.script.ui.shared.industry.industryUIConst import GetJobColor
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
from eve.client.script.ui.shared.industry.views.industryCaptionLabel import IndustryCaptionLabel
from eve.client.script.ui.shared.inventory.invWindow import Inventory
import industry
from eve.common.script.util import industryCommon
import localization
import carbonui.const as uiconst
import telemetry
from localization import GetByLabel
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
OPACITY_IDLE = 0.02
OPACITY_HOVER = 0.06
OPACITY_FRAME = 0.1
COLOR_FRAME = (0.12, 0.12, 0.12, 1.0)

class BaseFramedContainer(Container):
    default_state = UI_NORMAL
    default_width = 304
    default_height = 44

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.jobData = attributes.jobData
        self.oldJobData = None
        self.pattern = Frame(parent=self, texturePath='res:/UI/Texture/Classes/Industry/Output/boxPattern.png', align=TOALL, state=UI_DISABLED, opacity=0.0, cornerSize=5)
        FrameThemeColored(parent=self, state=UI_DISABLED, align=TOALL, opacity=0.3)
        FillThemeColored(bgParent=self, opacity=0.5)
        self.contentCont = Container(name='contentCont', parent=self)
        self.errorFrame = ErrorFrame(bgParent=self, padding=1)
        self.openInventoryBtn = ButtonIcon(name='openInventoryBtn ', parent=self, align=uiconst.TOPRIGHT, pos=(1, 1, 21, 21), iconSize=16, texturePath='res:/UI/Texture/Vgs/Search_icon.png', func=self.OnOpenInventoryBtn)
        self.UpdateState()
        self.AnimEntry()

    def GetInvControllersAndLocations(self):
        if self.jobData:
            return self.jobData.GetLocationsInvControllersAndLocations()
        return []

    def OnNewJobData(self, jobData):
        self.oldJobData = self.jobData
        self.jobData = jobData
        if jobData:
            self.jobData.on_updated.connect(self.OnJobDataUpdated)
        self.UpdateState()
        self.AnimEntry()

    def AnimEntry(self):
        color = GetJobColor(self.jobData)
        uicore.animations.SpColorMorphTo(self.pattern, self.pattern.GetRGBA(), color, duration=0.3)

    def OnJobDataUpdated(self, jobData):
        self.oldJobData = self.jobData
        self.UpdateState()

    def OnOpenInventoryBtn(self, *args):
        pass


class FacilityContainer(BaseFramedContainer):
    default_name = 'facilityContainer'

    def ApplyAttributes(self, attributes):
        BaseFramedContainer.ApplyAttributes(self, attributes)
        self.labelCont = Container(parent=self.contentCont, align=uiconst.CENTERLEFT, left=8, width=237, height=38)
        IndustryCaptionLabel(parent=self.labelCont, align=uiconst.TOPLEFT, text=localization.GetByLabel('UI/Industry/Facility'))
        self.label = EveLabelSmall(parent=self.labelCont, align=uiconst.TOPLEFT, top=16, autoFadeSides=10)
        self.icon = Icon(name='installationIcon', parent=self.contentCont, align=CENTERRIGHT, state=UI_DISABLED, pos=(1, 0, 43, 42))
        self.removeIcon = Sprite(parent=self.contentCont, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, texturePath='res:/ui/texture/icons/73_16_45.png', pos=(46, 2, 12, 12), color=Color.RED, opacity=0.0)

    @telemetry.ZONE_METHOD
    def UpdateState(self):
        if self.jobData:
            if self.jobData.facilityID:
                self.icon.Show()
                self.icon.LoadIconByTypeID(typeID=self.jobData.GetFacilityType(), ignoreSize=True)
                self.label.text = self.jobData.GetFacilityName()
                if self.IsFacilityChanged():
                    uicore.animations.FadeTo(self.labelCont, 0.0, 1.0, duration=0.6)
            else:
                self.icon.Hide()
                self.label.text = localization.GetByLabel('UI/Industry/NoneSelected')
            if self.IsInPreviewMode():
                self.errorFrame.Show()
            else:
                self.errorFrame.Hide()

    def GetMenu(self):
        if self.jobData.facility:
            return GetMenuService().GetMenuFromItemIDTypeID(self.jobData.facility.facilityID, self.jobData.facility.typeID)

    def OnMouseEnter(self):
        BaseFramedContainer.OnMouseEnter(self)
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        if self.IsInPreviewMode():
            uicore.animations.FadeIn(self.removeIcon, duration=0.3)

    def OnMouseExit(self):
        BaseFramedContainer.OnMouseExit(self)
        uicore.animations.FadeOut(self.removeIcon, duration=0.3)

    def OnClick(self, *args):
        if not self.jobData:
            return
        if self.IsInPreviewMode():
            facilityID = self.jobData.blueprint.facilityID
            if facilityID:
                self.jobData.facility = sm.GetService('facilitySvc').GetFacility(facilityID)
            else:
                self.jobData.facility = None
            uicore.animations.FadeOut(self.removeIcon, duration=0.1)
        elif self.jobData.facility:
            sm.GetService('info').ShowInfo(self.jobData.facility.typeID, self.jobData.facility.facilityID)
            PlaySound(uiconst.SOUND_BUTTON_CLICK)

    def IsInPreviewMode(self):
        if not self.jobData:
            return False
        if self.jobData.facility is None:
            return False
        return self.jobData.blueprint.facilityID != self.jobData.facility.facilityID

    def GetHint(self):
        if self.IsInPreviewMode():
            return localization.GetByLabel('UI/Industry/PreviewModeHint')

    def IsFacilityChanged(self):
        if not self.oldJobData:
            return False
        if not self.jobData.facility or not self.oldJobData.facility:
            return False
        return self.jobData.facility.facilityID != self.oldJobData.facility.facilityID


class InventorySelectionContainer(BaseFramedContainer):
    default_name = 'InventoryOutputContainer'
    CAPTION_TEXT = None

    def ApplyAttributes(self, attributes):
        BaseFramedContainer.ApplyAttributes(self, attributes)
        self.locationByInvID = {}
        labelCont = ContainerAutoSize(name='labelCont', parent=self.contentCont, align=uiconst.TOTOP, padTop=3)
        self.label = IndustryCaptionLabel(parent=labelCont, left=5, align=uiconst.CENTERLEFT, text=localization.GetByLabel(self.CAPTION_TEXT))
        self.combo = IndustryOutputCombo(parent=self.contentCont, align=uiconst.TOBOTTOM, callback=self.OnCombo, height=22)
        self.invController = None

    @telemetry.ZONE_METHOD
    def OnCombo(self, comboBox, key, value):
        invID = self.combo.GetValue()
        if not invID:
            return
        self.invController = invCtrl.GetInvCtrlFromInvID(invID)
        self.SetLocation(self.locationByInvID[invID])

    def UpdateState(self):
        if not self.jobData:
            return
        if not self.IsVisible() or not self.jobData.locations:
            self.Hide()
            return
        self.Show()
        options = []
        selectedInvID = None
        self.locationByInvID = {}
        locationData = self.GetInvControllersAndLocations()
        if not self.jobData:
            return
        for invController, location in locationData:
            self.locationByInvID[invController.GetInvID()] = location
            isContainer = isinstance(invController, invCtrl.StationContainer)
            indentLevel = int(isContainer)
            options.append((invController.GetName(),
             invController.GetInvID(),
             None,
             invController.GetIconName(),
             indentLevel))
            if location == self.GetLocation():
                selectedInvID = invController.GetInvID()
                self.invController = invController

        self.combo.LoadOptions(options, select=selectedInvID)
        if self.jobData.IsInstalled():
            self.combo.Disable()
        else:
            self.combo.Enable()

    def GetMenu(self):
        self.invController.GetMenu()

    def OnDropData(self, dragSource, dragData):
        self.invController.OnDropData(dragData)

    def OnOpenInventoryBtn(self, *args):
        if not self.invController:
            return
        if self.jobData.ownerID == session.corpid and session.stationid:
            invCtrl.StationCorpHangar().GetItems()
        Inventory.OpenOrShow(self.invController.GetInvID())
        PlaySound(uiconst.SOUND_BUTTON_CLICK)

    def GetLocation(self):
        pass

    def SetLocation(self):
        pass


class InventoryOutputContainer(InventorySelectionContainer):
    CAPTION_TEXT = 'UI/Industry/OutputLocation'

    @telemetry.ZONE_METHOD
    def SetLocation(self, location):
        if self.jobData:
            self.jobData.outputLocation = location

    @telemetry.ZONE_METHOD
    def GetLocation(self):
        if self.jobData:
            return self.jobData.outputLocation

    def GetInvControllersAndLocations(self):
        ret = []
        for controller, location in super(self.__class__, self).GetInvControllersAndLocations():
            if not industryCommon.CheckLocationCapacity(self.jobData, location.typeID):
                continue
            ret.append((controller, location))

        return ret

    def IsVisible(self):
        if not self.jobData:
            return False
        if self.jobData.status > industry.STATUS_UNSUBMITTED:
            return False
        if not self.jobData.blueprint.blueprintID:
            return False
        return True


class InventoryInputContainer(InventorySelectionContainer):
    CAPTION_TEXT = 'UI/Industry/InputMaterialLocation'

    @telemetry.ZONE_METHOD
    def SetLocation(self, location):
        if self.jobData:
            self.jobData.inputLocation = location

    @telemetry.ZONE_METHOD
    def GetLocation(self):
        if self.jobData:
            return self.jobData.inputLocation

    def IsVisible(self):
        if not self.jobData:
            return False
        if not bool(self.jobData.materials):
            return False
        if self.jobData.status > industry.STATUS_UNSUBMITTED:
            return False
        return True


class IndustryOutputCombo(Combo):
    default_noChoiceLabel = GetByLabel('UI/Industry/NoInventoryContainersFound')
    default_density = Density.COMPACT

    def Prepare_ActiveFrame_(self):
        self.sr.activeframe = Frame(name='__activeframe', parent=self, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, idx=0, color=(1.0, 1.0, 1.0, 0.0))

    def Disable(self, *args):
        Combo.Disable(self, *args)
        self.sr.expanderParent.Hide()

    def Enable(self, *args):
        Combo.Enable(self, *args)
        self.sr.expanderParent.Show()
