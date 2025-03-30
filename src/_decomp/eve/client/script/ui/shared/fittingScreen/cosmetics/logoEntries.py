#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\cosmetics\logoEntries.py
import blue
import uthread2
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionMedium
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect
from shipcosmetics.common.const import CosmeticsType
from localization import GetByLabel
FRAME_PADDING = 8
ENTRY_DEFAULT_HEIGHT = 124
LOGO_SIZE = 96
DELAY_BEFORE_SHOW_LOADING = 0.5

@Component(ButtonEffect(opacityIdle=0.0, opacityHover=0.2, opacityMouseDown=0.3, bgElementFunc=lambda parent, _: parent.highlightFill, audioOnEntry=uiconst.SOUND_ENTRY_HOVER, audioOnClick=uiconst.SOUND_ENTRY_SELECT))

class LogoEntry(Container):
    default_height = ENTRY_DEFAULT_HEIGHT
    default_state = uiconst.UI_NORMAL
    default_cosmeticsType = CosmeticsType.NONE

    def ApplyAttributes(self, attributes):
        super(LogoEntry, self).ApplyAttributes(attributes)
        self._loading = False
        self._loadingTasklet = None
        self._showLoadingTasklet = None
        self._isSelected = False
        self._logoData = None
        self.cosmeticsType = attributes.get('cosmeticsType', self.default_cosmeticsType)
        self._errorCallback = attributes.errorCallback
        self.ConstructLayout()

    def Close(self):
        self._ClearLoadingThread()
        super(LogoEntry, self).Close()

    def ConstructLayout(self):
        self.mainContainer = Container(name='mainContainer', parent=self)
        self.loadingContainer = Container(name='loadingContainer', parent=self)
        self.selectionFrame = Frame(name='selectionFrame', parent=self.mainContainer, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/Fitting/Heraldry/selectionFrame.png', color=eveColor.SUCCESS_GREEN, cornerSize=10, uiScaleVertices=True, fillCenter=False, padding=(-FRAME_PADDING,
         -FRAME_PADDING,
         -FRAME_PADDING,
         -FRAME_PADDING))
        self.selectionIcon = Sprite(name='selectionIcon', parent=self.mainContainer, align=uiconst.TOPRIGHT, texturePath='res:/UI/Texture/classes/SkillPlan/completedIcon.png', width=34, height=34)
        self.selectionIcon.display = False
        self.loadingWheel = LoadingWheel(name='loadingWheel', parent=self.loadingContainer, align=uiconst.CENTER, state=uiconst.UI_DISABLED, opacity=0.0)
        self.logoContainer = ContainerAutoSize(name='logoContainer', parent=self.mainContainer, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, padLeft=32)
        self.CreateLogoBackground()
        self.labelContainer = ContainerAutoSize(name='labelContainer', parent=self.mainContainer, align=uiconst.CENTERRIGHT, padRight=20, width=208)
        self.nameLabelWrapper = ContainerAutoSize(name='nameLabelWrapper', parent=self.labelContainer, align=uiconst.TOTOP)
        self.nameLabel = EveCaptionMedium(name='nameLabel', parent=self.nameLabelWrapper, align=uiconst.TOTOP, maxLines=2, padBottom=2)
        self.descriptionLabel = EveLabelMedium(name='descriptionLabel', parent=self.labelContainer, align=uiconst.TOTOP, color=Color.HextoRGBA('#B0B0B0'))
        self.highlightFill = FillThemeColored(name='highlightFill', parent=self.mainContainer, align=uiconst.TOALL, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)
        self.selectionFill = FillThemeColored(name='selectionFill', parent=self.mainContainer, align=uiconst.TOALL, state=uiconst.UI_DISABLED, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)
        self.backgroundFill = FillThemeColored(name='backgroundFill', parent=self.mainContainer, align=uiconst.TOALL, color=(0.0, 0.0, 0.0, 0.25))

    def CreateLogoBackground(self):
        self.logoBackground = Sprite(name='logoBackground', parent=self.logoContainer, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/Fitting/Heraldry/logoBackground.png', color=Color.HextoRGBA('#FFB845'), opacity=0.05, width=LOGO_SIZE, height=LOGO_SIZE)

    @property
    def logoData(self):
        return self._logoData

    @logoData.setter
    def logoData(self, value):
        self._logoData = value
        self.OnLogoDataChanged()

    def OnLogoDataChanged(self):
        self.UpdateDisplay()

    def UpdateDisplay(self):
        self.logoContainer.Flush()
        self.CreateLogoBackground()

    def OnClick(self, *args):
        if self.loading:
            return
        super(LogoEntry, self).OnClick(*args)

    @property
    def isSelected(self):
        return self._isSelected

    @isSelected.setter
    def isSelected(self, value):
        self._isSelected = value
        if self._isSelected:
            animations.FadeIn(self.selectionFill, endVal=0.2, duration=0.1, curveType=uiconst.ANIM_OVERSHOT)
            self.selectionFrame.state = uiconst.UI_DISABLED
            self.selectionIcon.display = True
        else:
            animations.FadeOut(self.selectionFill, duration=0.1)
            self.selectionFrame.state = uiconst.UI_HIDDEN
            self.selectionIcon.display = False

    @property
    def loading(self):
        return self._loading

    @loading.setter
    def loading(self, value):
        if value != self._loading:
            self._loading = value
        if self._loading:
            self._showLoadingTasklet = uthread2.StartTasklet(self._ShowLoadingThread)
        else:
            self._HideLoading()
            self._ClearLoadingThread()

    def IsEligible(self):
        raise NotImplementedError

    def Enable(self, *args):
        if self.loading:
            return
        if not self.IsEligible():
            return
        super(LogoEntry, self).Enable(*args)

    def _EnableLogo(self, license, groupIndex):
        if self.loading:
            return
        if sm.GetService('cosmeticsSvc').are_ship_emblems_disabled():
            return
        select = not self.isSelected
        sm.GetService('audio').SendUIEvent('fitting_window_emblem_select_play')
        self._loadingTasklet = uthread2.StartTasklet(self._EnableLogoThread, license, self.SLOT_INDEX, groupIndex, select)

    def _EnableLogoThread(self, license, slotIndex, groupIndex, enable):
        self.loading = True
        try:
            ok = sm.GetService('cosmeticsSvc').enable_ship_cosmetic_license(license=license, slotIndex=slotIndex, groupIndex=groupIndex, enable=enable)
            if ok:
                self.isSelected = enable
                sm.GetService('audio').SendUIEvent('fitting_window_emblem_select_play')
            else:
                self._errorCallback()
        except RuntimeError:
            self._errorCallback()
        finally:
            self.loading = False

    def _ShowLoadingThread(self):
        blue.synchro.SleepSim(DELAY_BEFORE_SHOW_LOADING * 1000)
        self._ShowLoading()

    def _ClearLoadingThread(self):
        if self._showLoadingTasklet is not None:
            self._showLoadingTasklet.Kill()
            self._showLoadingTasklet = None
        if self._loadingTasklet is not None:
            self._loadingTasklet.Kill()
            self._loadingTasklet = None

    def _ShowLoading(self):
        animations.FadeTo(self.mainContainer, self.mainContainer.opacity, 0.1, duration=0.1)
        animations.FadeTo(self.loadingWheel, self.loadingWheel.opacity, 1.0, duration=0.05)

    def _HideLoading(self):
        animations.FadeTo(self.mainContainer, self.mainContainer.opacity, 1.0, duration=0.1)
        animations.FadeTo(self.loadingWheel, self.loadingWheel.opacity, 0.0, duration=0.05)


class AllianceLogoEntry(LogoEntry):
    default_cosmeticsType = CosmeticsType.ALLIANCE_LOGO
    SLOT_INDEX = 1

    def UpdateDisplay(self):
        super(AllianceLogoEntry, self).UpdateDisplay()
        allianceID = eve.session.allianceid
        self.display = True if allianceID and self.logoData.existence.alliance is not None else False
        if not allianceID or not self.logoData.existence.alliance:
            return
        self.logoIcon = GetLogoIcon(name='logoIcon', parent=self.logoContainer, align=uiconst.TOPLEFT, itemID=allianceID)
        self.logoIcon.width = LOGO_SIZE
        self.logoIcon.height = LOGO_SIZE
        self.descriptionLabel.text = GetByLabel('UI/ShipCosmetics/AllianceEmblem')
        self.nameLabel.text = cfg.eveowners.Get(session.allianceid).name
        if self.logoData.eligibility.alliance:
            self.isSelected = True if self.logoData.selection.alliance else False
            self.Enable()
        else:
            self.isSelected = False
            self.Disable()

    def IsEligible(self):
        return self.logoData and self.logoData.eligibility.alliance

    def OnClick(self, *args):
        super(AllianceLogoEntry, self).OnClick(*args)
        self._EnableLogo(self.logoData.eligibility.alliance, self.logoData.eligibility.alliance.slotGroup)


class CorporationLogoEntry(LogoEntry):
    default_cosmeticsType = CosmeticsType.CORPORATION_LOGO
    SLOT_INDEX = 0

    def UpdateDisplay(self):
        super(CorporationLogoEntry, self).UpdateDisplay()
        self.display = self.logoData.existence.alliance is not None
        if not self.logoData.existence.alliance:
            return
        self.logoIcon = GetLogoIcon(name='logoIcon', itemID=eve.session.corpid, parent=self.logoContainer, align=uiconst.TOPLEFT)
        self.logoIcon.width = LOGO_SIZE
        self.logoIcon.height = LOGO_SIZE
        self.descriptionLabel.text = GetByLabel('UI/ShipCosmetics/CorporationEmblem')
        self.nameLabel.text = cfg.eveowners.Get(session.corpid).name
        if self.logoData.eligibility.corporation:
            self.isSelected = True if self.logoData.selection.corporation else False
            self.Enable()
        else:
            self.isSelected = False
            self.Disable()

    def IsEligible(self):
        return self.logoData and self.logoData.eligibility.corporation

    def OnClick(self, *args):
        super(CorporationLogoEntry, self).OnClick(*args)
        self._EnableLogo(self.logoData.eligibility.corporation, self.logoData.eligibility.corporation.slotGroup)
