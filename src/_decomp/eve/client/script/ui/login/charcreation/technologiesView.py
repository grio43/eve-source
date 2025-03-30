#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\technologiesView.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from charactercreator.client.empireSelectionData import GetTechnologyData
from charactercreator.client.scalingUtils import GetBannerHeaderHeight, GetEnlistButtonWidth, GetEnlistButtonHeight, GetScaleFactor, GetBottomNavHeight
from eve.client.script.ui.login.charcreation.empireTechnologyViews.allegianceView import AllegianceView
from eve.client.script.ui.login.charcreation.empireTechnologyViews.propagandaView import PropagandaView
from eve.client.script.ui.login.charcreation.empireTechnologyViews.shipsView import ShipsView
from eve.client.script.ui.login.charcreation.empireTechnologyViews.weaponsView import WeaponsView
from eve.client.script.ui.login.charcreation.empireui.empireThemedButtons import GetSealHeight, EmpireThemedButton, EmpireThemedButtonState, EmpireThemedDecoration, GetEmpireThemedDecorationSize, BUTTON_TEXT_FONTSIZE_MIN_RES
from eve.client.script.ui.login.charcreation.label import CCLabel
from eve.client.script.ui.login.charcreation.technologyViewUtils import ARROW_TEXTURE, GetTechNavArrowSize, GetTechNavArrowIconSize, GetTechNavArrowSpacingSize, GetTechNavButtonSizeLarge, GetTechNavButtonSizeSmall, GetTechNavButtonFontsize, TechNavigationButton, ArrowTechButton
from eve.client.script.ui.util.uix import GetTextWidth
from eve.common.lib.appConst import raceAmarr, raceCaldari, raceGallente, raceMinmatar
from localization import GetByLabel
from math import pi
TECHNOLOGY_TITLE_OPACITY = 0.25
EMPIRE_SEAL_TOP = -24
EMPIRE_SEAL_OPACITY = 0.1
TECH_ORDER_TO_VIEW = {1: PropagandaView,
 2: ShipsView,
 3: WeaponsView,
 4: AllegianceView}
DEFAULT_TECH_EXAMPLE = 1
ENLIST_BUTTON_TOP = 10
ENLIST_BUTTON_TEXT_BY_RACE = {raceAmarr: 'UI/CharacterCreation/EnlistAmarr',
 raceCaldari: 'UI/CharacterCreation/EnlistCaldari',
 raceGallente: 'UI/CharacterCreation/EnlistGallente',
 raceMinmatar: 'UI/CharacterCreation/EnlistMinmatar'}
ENLIST_BUTTON_MIN_TEXT_PADDING = 10
ENLIST_FLARE_SOUND_INTRO = 'ui_es_enlist_flare_play'
ENLIST_FLARE_SOUND_OUTRO = 'ui_es_enlist_flare_stop'
ENLIST_MOUSEOVER_SOUND = 'ui_es_mouse_over_enlist_play'
ENLIST_MOUSEEXIT_SOUND = 'ui_es_mouse_over_enlist_stop'
ENLIST_POPUP_SOUND = 'ui_es_enlist_pop_up_play'
ENLIST_POPUP_END_SOUND = 'ui_es_enlist_pop_up_stop'
ENLIST_SOUND = 'ui_es_button_mouse_down_enlist_play'

class EmpireTechnologiesView(Container):

    def ApplyAttributes(self, attributes):
        self.raceID = attributes.raceID
        self.stepContainer = attributes.stepContainer
        self.buttonContainer = attributes.buttonContainer
        self.technologyViewsTracker = attributes.Get('technologyViewsTracker')
        self.techView = None
        self.enlistButton = None
        self.enlistButtonDecoration = None
        self.isUpdatingTechView = False
        self.techNavigationContainer = None
        self.audioSvc = sm.GetService('audio')
        self.technologies = GetTechnologyData()
        self.firstTechOrder = self.technologies.GetFirstOrder()
        shouldGoBackToStart = attributes.Get('shouldGoBackToStart', True)
        self.techOrder = self._GetTechOrder(shouldGoBackToStart)
        self.PlayIntroSound()
        super(EmpireTechnologiesView, self).ApplyAttributes(attributes)
        hasDiscoveredSwitch = self.technologyViewsTracker.has_discovered_technology_switch()
        shouldMarkDiscovery = not shouldGoBackToStart and hasDiscoveredSwitch
        if shouldMarkDiscovery:
            self.technologyViewsTracker.mark_technology_switch_as_discovered()
        self.UpdateTechnologyView()

    def _GetTechOrder(self, shouldGoBackToStart):
        if shouldGoBackToStart:
            return self.firstTechOrder
        return self._GetTechOrderSetting()

    def _GetTechOrderSetting(self):
        return settings.user.ui.Get('last_viewed_tech', self.firstTechOrder)

    def _SetLastViewedTech(self):
        settings.user.ui.Set('last_viewed_tech', self.techOrder)
        self.technologyViewsTracker.mark_technology_as_viewed(self.raceID, self.techOrder)

    def SetTechNavigation(self):
        self.ClearUIElement(self.techNavigationContainer)
        techNavigationWidth = self._GetTechNavigationWidth()
        self.techNavigationContainer = Container(name='techNavigationContainer', align=uiconst.CENTERTOP, parent=self, width=techNavigationWidth, height=GetBannerHeaderHeight())
        arrowSize = GetTechNavArrowSize()
        arrowIconSize = GetTechNavArrowIconSize()
        arrowSpacingSize = GetTechNavArrowSpacingSize()
        self._AddTechNavLeftArrow(arrowSize, arrowIconSize, arrowSpacingSize)
        self._AddTechNavButtons()
        self._AddTechNavRightArrow(arrowSize, arrowIconSize, arrowSpacingSize)

    def _AddTechNavButtons(self):
        for techOrder in xrange(1, self.technologies.GetNumberOfTechs() + 1):
            isActive = techOrder == self.techOrder
            buttonSize = GetTechNavButtonSizeLarge() if isActive else GetTechNavButtonSizeSmall()
            tech = self.technologies.GetTech(techOrder)
            techIconTexture = tech.GetIconTexture()
            techNavigationButtonContainer = Container(name='techNavigationButtonContainer%d' % techOrder, align=uiconst.TOLEFT, parent=self.techNavigationContainer, width=buttonSize, height=buttonSize)
            TechNavigationButton(name='techNavigationButton%d' % techOrder, parent=techNavigationButtonContainer, align=uiconst.CENTER, width=buttonSize, height=buttonSize, order=techOrder, techSetter=self.SetTech, raceID=self.raceID, iconTexture=techIconTexture, iconSize=buttonSize, isActive=isActive)
            if isActive:
                techTitle = tech.GetTechTitle()
                bannerHeight = self.techNavigationContainer.height
                extraHeight = (buttonSize - bannerHeight) / 2
                labelTop = bannerHeight + extraHeight
                techTitleLabel = CCLabel(text=techTitle, name='techNavigationButtonTitle%d' % techOrder, parent=self.techNavigationContainer, align=uiconst.TOLEFT_NOPUSH, uppercase=1, bold=False, fontsize=GetTechNavButtonFontsize(), top=labelTop)
                techTitleLabel.left = -buttonSize / 2 - techTitleLabel.width / 2

    def _AddTechNavLeftArrow(self, arrowSize, arrowIconSize, arrowSpacingSize):
        leftArrowTechNavigationContainer = Container(name='leftArrowTechNavigationContainer', align=uiconst.TOLEFT, parent=self.techNavigationContainer, width=arrowSize, height=self.techNavigationContainer.height, padRight=arrowSpacingSize)
        if self.techOrder > 1:
            ArrowTechButton(name='leftArrow', parent=leftArrowTechNavigationContainer, align=uiconst.CENTER, width=arrowSize, height=arrowSize, iconTexture=ARROW_TEXTURE, iconSize=arrowIconSize, order=self.techOrder - 1, techSetter=self.SetTech, rotation=pi)

    def _AddTechNavRightArrow(self, arrowSize, arrowIconSize, arrowSpacingSize):
        rightArrowTechNavigationContainer = Container(name='rightArrowTechNavigationContainer', align=uiconst.TOLEFT, parent=self.techNavigationContainer, width=arrowSize, height=self.techNavigationContainer.height, padLeft=arrowSpacingSize)
        if self.techOrder < self.technologies.GetNumberOfTechs():
            ArrowTechButton(name='rightArrow', parent=rightArrowTechNavigationContainer, align=uiconst.CENTER, width=arrowSize, height=arrowSize, iconTexture=ARROW_TEXTURE, iconSize=arrowIconSize, order=self.techOrder + 1, techSetter=self.SetTech)

    def Enlist(self):
        self.audioSvc.SendUIEvent(ENLIST_SOUND)
        uicore.layer.charactercreation.controller.Approve()

    def SetEnlistButton(self):
        if self.enlistButton and not self.enlistButton.destroyed:
            self.enlistButton.Close()
        enlistButtonLabel = GetByLabel(ENLIST_BUTTON_TEXT_BY_RACE[self.raceID])
        enlistButtonLabelFontsize = BUTTON_TEXT_FONTSIZE_MIN_RES * GetScaleFactor()
        enlistButtonLabelWidth = GetTextWidth(strng=enlistButtonLabel, fontsize=enlistButtonLabelFontsize, hspace=0, uppercase=1)
        minWidth = enlistButtonLabelWidth + 2 * ENLIST_BUTTON_MIN_TEXT_PADDING
        enlistButtonWidth = max(minWidth, GetEnlistButtonWidth())
        enlistButtonTop = GetBottomNavHeight() - ENLIST_BUTTON_TOP - GetEnlistButtonHeight()
        self.enlistButton = EmpireThemedButton(name='EnlistButton', parent=self.buttonContainer, align=uiconst.CENTERBOTTOM, label=enlistButtonLabel.upper(), raceID=self.raceID, width=enlistButtonWidth, height=GetEnlistButtonHeight(), top=enlistButtonTop, buttonState=EmpireThemedButtonState.NORMAL, mouseOverSound=ENLIST_MOUSEOVER_SOUND, mouseExitSound=ENLIST_MOUSEEXIT_SOUND)
        self.enlistButton.OnClick = self.Enlist

    def SetEnlistButtonDecoration(self):
        if not self.enlistButtonDecoration:
            width, height = GetEmpireThemedDecorationSize()
            enlistButtonDecorationContainer = Container(name='EnlistButtonDecoration_Container', parent=self.buttonContainer, align=uiconst.TOTOP_NOPUSH, width=width, height=height, top=-GetSealHeight(), state=uiconst.UI_DISABLED)
            self.enlistButtonDecoration = EmpireThemedDecoration(name='EnlistButtonDecoration', parent=enlistButtonDecorationContainer, align=uiconst.CENTERTOP, width=width, height=height, flareSoundIntro=ENLIST_FLARE_SOUND_INTRO)
        enlistButtonState = EmpireThemedButtonState.NORMAL
        self.enlistButtonDecoration.UpdateDecoration(self.raceID, enlistButtonState)

    def UpdateTechnologyView(self):
        if self.isUpdatingTechView:
            return
        self.isUpdatingTechView = True
        self._SetLastViewedTech()
        technology = self.technologies.GetTech(self.techOrder)
        self.SetEnlistButtonDecoration()
        self.SetEnlistButton()
        self.SetTechNavigation()
        techExampleOrder = DEFAULT_TECH_EXAMPLE
        if self.techView:
            techExampleOrder = getattr(self.techView, 'techExampleOrder', DEFAULT_TECH_EXAMPLE)
        self.ClearUIElement(self.techView)
        techStepOrder = technology.GetTechStepOrder()
        techViewClass = TECH_ORDER_TO_VIEW[techStepOrder]
        self.techView = techViewClass(name='techView%d' % self.techOrder, parent=self, align=uiconst.ANCH_TOPLEFT, width=self.width, height=self.height - self.padTop, raceID=self.raceID, technology=technology, techExampleOrder=techExampleOrder, internalPadTop=GetBannerHeaderHeight())
        self.isUpdatingTechView = False

    def SetRace(self, raceID):
        super(EmpireTechnologiesView, self).SetRace(raceID)
        uicore.layer.charactercreation.controller.raceID = self.raceID
        if self.techView:
            self.UpdateTechnologyView()

    def SetTech(self, techOrder):
        if techOrder != self.techOrder:
            self.technologyViewsTracker.mark_technology_switch_as_discovered()
        self.SetTechAuto(techOrder)

    def SetTechAuto(self, techOrder):
        if techOrder == self.techOrder:
            return
        self.techOrder = techOrder
        self.PlayIntroSound()
        if self.techView:
            self.UpdateTechnologyView()

    def PlayIntroSound(self):
        technology = self.technologies.GetTech(self.techOrder)
        techStepOrder = technology.GetTechStepOrder()
        self.audioSvc.SendUIEvent('es_screen_2_%d_play' % techStepOrder)

    def ClearUIElement(self, uiElement):
        if uiElement and not uiElement.destroyed:
            uiElement.Close()

    def UpdateLayout(self, width, height):
        if width != self.width or height != self.height:
            self.width = width
            self.height = height
            self.UpdateTechnologyView()

    def _GetTechNavigationWidth(self):
        numberOfTechs = self.technologies.GetNumberOfTechs()
        arrowsWidth = 2 * GetTechNavArrowSize() + 2 * GetTechNavArrowSpacingSize()
        buttonsWidth = GetTechNavButtonSizeLarge() + max(0, numberOfTechs - 1) * GetTechNavButtonSizeSmall()
        return arrowsWidth + buttonsWidth
