#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\cloneUpgradeWindow.py
import carbonui.const as uiconst
import evetypes
import inventorycommon.const as invconst
import uthread
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from clonegrade.const import COLOR_OMEGA_ORANGE, COLOR_OMEGA_GOLD, COLOR_OMEGA_BG
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.plex.textures import PLEX_32_SOLID_WHITE
from eve.client.script.ui.shared.cloneGrade import REASON_DEFAULT
from eve.client.script.ui.shared.cloneGrade.upgradeButton import UpgradeButton
from eve.client.script.ui.shared.cloneGrade.baseClonesStateWindow import BaseCloneStateWindow, VIDEO_WIDTH
from eveexceptions.exceptionEater import ExceptionEater
from localization import GetByLabel
from notifications.common.formatters.plexDonation import LinkifyOwner
STATE_UPGRADE = 'upgradeFromAlpha'
STATE_FANFARE = 'upgradeFanfare'
STATE_EXTEND = 'extendSubscription'
ICON_OPACITY_HOVER = 0.7
ICON_OPACITY_IDLE = 1.0
VIDEOOPACITY_IDLE = 0.5
VIDEOOPACITY_HOVER = 0.8

class CloneUpgradeWindow(BaseCloneStateWindow):
    default_windowID = 'CloneUpgradeWindow'
    default_width = 540
    default_fixedWidth = 540
    default_height = 680
    default_fixedHeight = 680

    def ApplyAttributes(self, attributes):
        showFanfare = attributes.showFanfare
        self.giftData = attributes.giftData
        self.origin = attributes.get('origin', None)
        self.reason = attributes.get('reason', None) or REASON_DEFAULT
        self.UpdateState(showFanfare)
        self._glow = 0.0
        self.continueButton = None
        attributes['analyticID'] = 'omega_upgrade_window_old' if not showFanfare else None
        BaseCloneStateWindow.ApplyAttributes(self, attributes)
        sm.GetService('audio').SendUIEvent('upgrade_menu_window_play')
        if not showFanfare:
            self._LogWindowOpened()
        if self.giftData:
            self.UpdateToGiftLayout()

    def UpdateToGiftLayout(self):
        self.upgradeLabel.SetText(GetByLabel('UI/CloneState/GiftingSuccessful'))
        Label(name='GiftingContext', parent=self.mainCont, align=uiconst.CENTERTOP, state=uiconst.UI_NORMAL, text=GetByLabel('UI/CloneState/GiftingContext', senderName=LinkifyOwner(self.giftData['senderCharID'])), uppercase=True, bold=True, color=COLOR_OMEGA_ORANGE, top=200 if self.giftData['message'] else 365, width=self.width)
        if self.giftData['message']:
            self.omegaIcon.SetPosition(0, 15)
            self.bgVideo.SetPosition(0, -250)
            self.upgradeLabel.SetPosition(0, 100)
            Container(name='textBackground', parent=self.mainCont, align=uiconst.CENTERTOP, pos=(0, 112, 330, 115), bgColor=(0, 0, 0, 0.4))
            messageLabel = Label(name='giftingMessage', parent=self.mainCont, align=uiconst.CENTER, text='<center>%s</center>' % self.giftData['message'], uppercase=True, bold=True, color=COLOR_OMEGA_ORANGE, width=350, top=-25, fontsize=15)
            Container(name='textBackground', parent=self.mainCont, align=uiconst.CENTER, pos=(0,
             -25,
             messageLabel.width + 20,
             messageLabel.height + 20), bgColor=(0, 0, 0, 0.4))
        else:
            self.omegaIcon.SetPosition(0, 180)
            self.bgVideo.SetPosition(0, -86)
            self.upgradeLabel.SetPosition(0, 266)

    def ConstructLayout(self):
        self.omegaIcon = Sprite(name='omegaIcon', parent=self.sr.main, align=uiconst.CENTERTOP, pos=(0, 180, 110, 110), opacity=ICON_OPACITY_IDLE, texturePath='res:/UI/Texture/Classes/CloneGrade/Omega_128.png')
        self.mainCont = Container(name='mainCont', parent=self.sr.main, opacity=0.0)

    def Close(self, *args, **kwds):
        BaseCloneStateWindow.Close(self, *args, **kwds)
        sm.GetService('audio').SendUIEvent('upgrade_menu_window_stop')

    def LoadContent(self, animate = True):
        if animate:
            duration = 0.6
            animations.FadeOut(self.mainCont, duration=duration)
            animations.MorphScalar(self, 'glow', self.glow, 0.0, duration=duration, sleep=True)
        self.mainCont.Flush()
        self.ConstructUpgradeButton()
        self.ConstructPlexContainer()
        self.ConstructBenefitEntries()
        if self.windowState == STATE_FANFARE:
            self.ConstructContinueButton()
        self.AnimEntry()

    def ConstructContinueButton(self):
        self.continueButton = UpgradeButton(parent=self.mainCont, align=uiconst.CENTERBOTTOM, pos=(0, 20, 150, 41), onClick=self.CloseByUser, text=GetByLabel('UI/Agents/Dialogue/Buttons/Continue'), opacity=0.0)

    def ConstructPlexContainer(self):
        if self.windowState != STATE_FANFARE:
            PlexContainer(parent=self.mainCont, align=uiconst.CENTERTOP, top=360)

    def ConstructUpgradeButton(self):
        if self.windowState == STATE_FANFARE:
            self.upgradeLabel = Label(parent=self.mainCont, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, text=GetByLabel('UI/CloneState/UpgradeSuccessful'), uppercase=True, bold=True, color=COLOR_OMEGA_ORANGE, top=296, width=self.width)
        else:
            if self.windowState == STATE_UPGRADE:
                text = GetByLabel('UI/CloneState/UpgradeToOmega')
            else:
                text = GetByLabel('UI/CloneState/ExtendSubscription')
            UpgradeButton(parent=self.mainCont, align=uiconst.CENTERTOP, pos=(0, 300, 350, 41), onMouseEnterCallback=self.OnUpgradeButtonMouseEnter, onMouseExitCallback=self.OnUpgradeButtonMouseExit, onClick=self.OnUpgradeButtonClick, text=text, analyticID='upgrade_omega_secure_old')

    def OnUpgradeButtonClick(self, *args):
        sm.GetService('cloneGradeSvc').UpgradeCloneAction(self.origin, self.reason)

    def UpdateState(self, showFanfare = False):
        if showFanfare:
            self.windowState = STATE_FANFARE
        elif sm.GetService('cloneGradeSvc').IsOmega():
            self.windowState = STATE_EXTEND
        else:
            self.windowState = STATE_UPGRADE

    def OnShowFanfare(self):
        self.windowState = STATE_FANFARE
        self.LoadContent(animate=True)

    def AnimEntry(self):
        duration = 0.6
        animations.FadeTo(self.mainCont, self.mainCont.opacity, 1.0, duration=duration)
        if self.windowState == STATE_FANFARE:
            timeOffset = 1.2
            animations.MorphScalar(self, 'glow', 15.0, 2.0, duration=1.2)
            for i, benefitEntry in enumerate(self.benefitCont.children):
                try:
                    benefitEntry.AnimEntry(0.5, i * 0.15 + timeOffset)
                except AttributeError:
                    pass

            animations.FadeTo(self.continueButton, 0.0, 1.0, duration=0.6, timeOffset=1.6)
        else:
            timeOffset = 0.0
            animations.MorphScalar(self, 'glow', self.glow, 0.5, duration=2.0)
            for i, benefitEntry in enumerate(self.benefitCont.children):
                try:
                    benefitEntry.AnimEntry(0.5, i * 0.07)
                except AttributeError:
                    pass

        animations.FadeTo(self.bottomCont, 0.0, 1.0, duration=0.6, timeOffset=timeOffset)

    def OnUpgradeButtonMouseEnter(self):
        animations.MorphScalar(self, 'glow', self.glow, 1.0, duration=0.25)

    def OnUpgradeButtonMouseExit(self):
        animations.MorphScalar(self, 'glow', self.glow, 0.5, duration=0.15)

    def ConstructBenefitEntries(self):
        top = 80 if self.windowState == STATE_FANFARE else 50
        self.bottomCont = Container(name='bottomCont', parent=self.mainCont, align=uiconst.CENTERBOTTOM, pos=(0,
         top,
         450,
         190), bgColor=(0, 0, 0, 0.4))
        self.benefitCont = ContainerAutoSize(parent=self.bottomCont, align=uiconst.CENTER, width=400)
        for text, hint, texturePath in self.GetBenefits():
            BenefitEntry(parent=self.benefitCont, align=uiconst.TOTOP, height=40, text=text, hint=hint, texturePath=texturePath, opacity=0.0, windowState=self.windowState)

    def GetBenefits(self):
        return ((GetByLabel('UI/CloneState/BenefitAllShipsAndModules', numShips=self.GetNumShipsInGame()), GetByLabel('UI/CloneState/BenefitAllShipsAndModulesHint'), 'res:/UI/Texture/classes/cloneGrade/benefits/allShipsAndModules.png'),
         (GetByLabel('UI/CloneState/BenefitAllSkills', numSkills=self.GetNumSkillsInGame()), GetByLabel('UI/CloneState/BenefitAllSkillsHint'), 'res:/UI/Texture/classes/cloneGrade/benefits/allSkills.png'),
         (GetByLabel('UI/CloneState/BenefitFasterTraining'), GetByLabel('UI/CloneState/BenefitFasterTrainingHint'), 'res:/UI/Texture/classes/cloneGrade/benefits/fasterTraining.png'),
         (GetByLabel('UI/CloneState/BenefitTriglavianShips'), GetByLabel('UI/CloneState/BenefitTriglavianShipsHint'), 'res:/UI/Texture/classes/cloneGrade/benefits/triglavianSkills.png'))

    def GetNumSkillsInGame(self):
        return self._GetNumTypesInGroup(invconst.categorySkill)

    def GetNumShipsInGame(self):
        return self._GetNumTypesInGroup(invconst.categoryShip)

    def _GetNumTypesInGroup(self, categoryID):
        typeIDs = evetypes.GetTypeIDsByCategory(categoryID)
        return len([ typeID for typeID in typeIDs if evetypes.IsPublished(typeID) ])

    @classmethod
    def ShowFanfare(cls, giftData = None):
        wnd = cls.GetIfOpen()
        if wnd:
            wnd.OnShowFanfare()
        else:
            cls.Open(showFanfare=True, giftData=giftData)

    @property
    def glow(self):
        return self._glow

    @glow.setter
    def glow(self, value):
        self._glow = value
        self.bgVideo.opacity = 0.5 + 0.3 * value
        self.omegaIcon.opacity = max(1.0 - 0.3 * value, 0.7)
        self.bgVideo.width = VIDEO_WIDTH * (1.0 + 0.25 * value)
        self.bgSprite.effectOpacity = -0.6 + 0.4 * value

    def _LogWindowOpened(self):
        with ExceptionEater('eventLog'):
            uthread.new(sm.ProxySvc('eventLog').LogClientEvent, 'trial', ['origin', 'reason'], 'ShowCloneUpgradeWindow', self.origin, self.reason)


class BenefitEntry(Container):
    default_name = 'BenefitEntry'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        texturePath = attributes.texturePath
        text = attributes.text
        self.hint = attributes.hint
        self.windowState = attributes.windowState
        if self.windowState != STATE_UPGRADE:
            texturePath = 'res:/UI/Texture/Classes/MissionTracker/tracker_check.png'
            size = 20
            color = COLOR_OMEGA_GOLD
        else:
            size = 32
            color = COLOR_OMEGA_BG
        self.icon = Sprite(name='icon', parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, texturePath=texturePath, pos=(0,
         0,
         size,
         size), color=color)
        Label(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=text, fontsize=14, left=50)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=self.hint, wrapWidth=250)

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2

    def AnimEntry(self, duration = 0.3, timeOffset = None):
        animations.FadeIn(self, duration=duration, timeOffset=timeOffset)
        if self.windowState == STATE_FANFARE:
            animations.FadeTo(self.icon, 10.0, 1.0, duration=duration, timeOffset=timeOffset)


class PlexContainer(ContainerAutoSize):
    default_name = 'PlexContainer'
    default_state = uiconst.UI_NORMAL
    analyticID = 'upgrade_omega_nes_old'

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.icon = GlowSprite(name='icon', parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, texturePath=PLEX_32_SOLID_WHITE, pos=(0, 0, 32, 32))
        self.label = Label(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=GetByLabel('UI/CloneState/UsePlexToUpgrade'), fontsize=18, left=34, color=eveColor.WHITE)

    def OnMouseEnter(self, *args):
        self.icon.OnMouseEnter()
        animations.FadeTo(self.label, self.label.opacity, 1.2, duration=0.1)

    def OnMouseExit(self, *args):
        self.icon.OnMouseExit()
        animations.FadeTo(self.label, self.label.opacity, 1.0, duration=0.3)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/CloneState/UsePlexToUpgradeHint'), wrapWidth=250)

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2

    def OnClick(self):
        from carbonui.loggers.buttonLogger import log_button_clicked
        from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
        log_button_clicked(self)
        CharacterSheetWindow.OpenPLEX()
