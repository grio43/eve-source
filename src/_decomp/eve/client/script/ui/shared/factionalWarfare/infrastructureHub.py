#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\infrastructureHub.py
import math
from math import pi
import carbonui.const as uiconst
import eveformat
import localization
import blue
import uthread
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.window.segment.underlay import WindowSegmentUnderlay
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from carbonui.control.window import Window
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.factionalWarfare.fwSystemBenefitIcon import FWSystemBenefitIcon
from eve.common.lib import appConst
from eve.common.script.util import facwarCommon
from eveexceptions import UserError

class FWInfrastructureHub(Window):
    __guid__ = 'form.FWInfrastructureHub'
    __notifyevents__ = ['OnSolarSystemLPChange', 'OnCharacterLPBalanceChange_Local']
    default_windowID = 'FWInfrastructureHub'
    default_fixedWidth = 510
    default_fixedHeight = 650
    default_iconNum = 'res:/ui/Texture/WindowIcons/factionalwarfare.png'
    default_caption = 'UI/FactionWarfare/IHub/IHubWndCaption'
    PADSIDE = 0
    PADTOP = 10

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.itemID = attributes.Get('itemID')
        self.facwar = sm.GetService('facwar')
        lpPool = self.facwar.GetSolarSystemLPs(session.solarsystemid2)
        topCont = Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, height=40, padding=(self.PADSIDE,
         self.PADTOP,
         self.PADSIDE,
         self.PADSIDE))
        mainCont = ContainerAutoSize(name='mainCont', parent=self.sr.main, align=uiconst.TOTOP, padTop=16)
        bottomCont = Container(name='bottomCont', parent=self.sr.main, align=uiconst.TOBOTTOM, height=90, padTop=self.PADTOP)
        eveLabel.EveLabelLarge(parent=topCont, text=localization.GetByLabel('UI/FactionWarfare/IHub/SystemUpgradePanel', systemName=cfg.evelocations.Get(session.solarsystemid2).name), align=uiconst.TOPLEFT, top=5)
        eveLabel.EveLabelLarge(parent=topCont, text=localization.GetByLabel('UI/FactionWarfare/IHub/TotalLP'), align=uiconst.TOPRIGHT, top=5)
        self.lpPoolLabel = eveLabel.EveCaptionSmall(parent=topCont, align=uiconst.TOPRIGHT, top=25)
        limits = const.facwarSolarSystemUpgradeThresholds
        self.upgradeBars = []
        for i in xrange(1, 7):
            bar = FWUpgradeLevelCont(parent=mainCont, align=uiconst.TOTOP, padding=(self.PADSIDE,
             0,
             0,
             10), lowerLimit=limits[i - 1], upperLimit=limits[i], lpAmount=lpPool, level=i, idx=0)
            self.upgradeBars.append(bar)

        self.bottomGradient = WindowSegmentUnderlay(bgParent=bottomCont, padding=self._get_bottom_segment_padding())
        self.bottomFlashEffect = Fill(bgParent=bottomCont, padding=self._get_bottom_segment_padding(), opacity=0.0, color=eveThemeColor.THEME_ACCENT, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3)
        bottomMainCont = Container(name='bottomMainCont', parent=bottomCont, align=uiconst.TOTOP, height=100)
        self.myLPLabel = eveLabel.Label(parent=bottomMainCont, text=self.GetLPOwnedLabel(), align=uiconst.TOPLEFT, left=self.PADSIDE, top=self.PADTOP)
        self.bottomBottomCont = Container(name='bottomBottom', align=uiconst.TOPLEFT, pos=(self.PADSIDE,
         40,
         self._fixedWidth,
         25), parent=bottomMainCont)
        self.donateAmountEdit = SingleLineEditInteger(parent=self.bottomBottomCont, name='donateAmountEdit', align=uiconst.TOLEFT, setvalue=0, width=155, OnReturn=self.OnDonateLPBtn, OnChange=self.OnDonateValueChanged)
        self.donateBtn = Button(parent=self.bottomBottomCont, align=uiconst.TOLEFT, func=self.OnDonateLPBtn, label=localization.GetByLabel('UI/FactionWarfare/IHub/DonateLPs'), padLeft=4)
        self.donationReceivedLabel = eveLabel.EveCaptionMedium(name='donationReceivedLabel', parent=bottomMainCont, align=uiconst.TOPLEFT, text=localization.GetByLabel('UI/FactionWarfare/IHub/DonationReceived'), left=self.PADSIDE, top=50, opacity=0.0)
        self.bottomTaxCont = Container(name='bottomTax', align=uiconst.TOPLEFT, pos=(self.PADSIDE,
         73,
         400,
         25), parent=bottomMainCont)
        self.myLPToIhubLabel = None
        factionID = self.facwar.GetSystemOccupier(session.solarsystemid)
        self.myLPTaxLabel = eveLabel.Label(name='myLPTaxLabel', parent=self.bottomTaxCont, text=localization.GetByLabel('UI/FactionWarfare/IHub/maintenanceTax', tax=int(facwarCommon.GetDonationTax(factionID) * 100)), align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, left=5)
        self.SetLPPoolAmount(lpPool)
        self.UpdateMyLPAmount()
        self.UpdateMyLPToIHubLabel()
        if facwarCommon.IsOccupierFWFaction(factionID):
            self.donateBtn.Enable()
            self.donateAmountEdit.Enable()
        else:
            self.donateBtn.Disable()
            self.donateAmountEdit.Disable()
        uthread.new(self.CheckOpenThread)
        self.on_content_padding_changed.connect(self._on_content_padding_changed)

    def _get_bottom_segment_padding(self):
        pad_left, _, pad_right, pad_bottom = self.content_padding
        return (-pad_left,
         0,
         -pad_right,
         -pad_bottom)

    def _update_bottom_segment_padding(self):
        if self.bottomGradient:
            self.bottomGradient.padding = self._get_bottom_segment_padding()
        if self.bottomFlashEffect:
            self.bottomFlashEffect.padding = self._get_bottom_segment_padding()

    def _on_content_padding_changed(self, window):
        self._update_bottom_segment_padding()

    def UpdateMyLPToIHubLabel(self, refreshTax = False):
        lpAmount = self.donateAmountEdit.GetValue()
        donationTax = facwarCommon.GetDonationTax(session.warfactionid)
        tax = math.ceil(donationTax * lpAmount)
        if self.myLPToIhubLabel:
            self.myLPToIhubLabel.Close()
        self.myLPToIhubLabel = eveLabel.Label(name='myLPToIhubLabel', parent=self.bottomTaxCont, align=uiconst.TOLEFT, idx=0, text=localization.GetByLabel('UI/FactionWarfare/IHub/TotalDonated', loyaltyPoints=localization.formatters.FormatNumeric(int(lpAmount - tax), useGrouping=True)))
        if refreshTax:
            if self.myLPTaxLabel:
                self.myLPTaxLabel.Close()
            self.myLPTaxLabel = eveLabel.Label(name='myLPTaxLabel', parent=self.bottomTaxCont, text=localization.GetByLabel('UI/FactionWarfare/IHub/maintenanceTax', tax=int(donationTax * 100)), align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, left=5)
        self.myLPTaxLabel.hint = localization.GetByLabel('UI/FactionWarfare/LPAmount', lps=tax)

    def GetLPOwnedLabel(self):
        factionID = self.facwar.GetSystemOccupier(session.solarsystemid)
        militiaCorpID = self.facwar.GetFactionMilitiaCorporation(factionID)
        amount = self.GetMyLPs()
        return localization.GetByLabel('UI/FactionWarfare/IHub/LPOwned', LPCount=localization.formatters.FormatNumeric(amount, useGrouping=True), corpName=cfg.eveowners.Get(militiaCorpID).name)

    def CheckOpenThread(self):
        bp = sm.GetService('michelle').GetBallpark()
        while not self.destroyed:
            blue.synchro.SleepWallclock(1000)
            distance = bp.GetSurfaceDist(session.shipid, self.itemID)
            if distance > const.facwarIHubInteractDist:
                self.Close()

    def OnSessionChanged(self, *args):
        self.Close()

    def OnCharacterLPBalanceChange_Local(self, *args, **kwargs):
        self.UpdateMyLPAmount()

    def SetLPPoolAmount(self, amount):
        self.lpPoolLabel.SetText(localization.formatters.FormatNumeric(amount, useGrouping=True))

    def UpdateMyLPAmount(self):
        amount = self.GetMyLPs()
        self.myLPLabel.SetText(self.GetLPOwnedLabel())
        self.donateAmountEdit.SetMinValue(appConst.facwarMinLPDonation)
        self.donateAmountEdit.SetMaxValue(amount)

    def OnDonateValueChanged(self, value):
        uthread.new(self.UpdateMyLPToIHubLabel)

    def OnDonateLPBtn(self, *args):
        if not self.bottomBottomCont.pickState:
            return
        pointsToDonate = self.donateAmountEdit.GetValue()
        if not pointsToDonate:
            return
        donationTax = facwarCommon.GetDonationTax(session.warfactionid)
        pointsToIHub = int(pointsToDonate - pointsToDonate * donationTax)
        try:
            self.facwar.DonateLPsToSolarSystem(pointsToDonate, pointsToIHub)
        except UserError as e:
            if e.msg == 'FacWarDonationTaxChanged':
                self.facwar.objectCaching.InvalidateCachedMethodCalls([('map', 'GetFacWarZoneInfo', (session.warfactionid,))])
                self.UpdateMyLPToIHubLabel(refreshTax=True)
                if uicore.Message('FacWarDonationTaxChanged', e.dict, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
                    newPointsToIhub = int(pointsToDonate * (1 - e.dict['taxNow'] / 100.0))
                    try:
                        self.facwar.DonateLPsToSolarSystem(pointsToDonate, newPointsToIhub)
                    except UserError as e:
                        if e.msg == 'FacWarDonationTaxChanged':
                            return
                        raise

                else:
                    return
            else:
                raise

        self.donateAmountEdit.SetValue('0')
        uicore.animations.FadeIn(self.bottomFlashEffect, endVal=0.3, duration=0.3)
        self.bottomBottomCont.Disable()
        uicore.animations.FadeOut(self.bottomBottomCont, duration=0.1)
        self.bottomTaxCont.Disable()
        uicore.animations.FadeOut(self.bottomTaxCont, duration=0.1)
        blue.synchro.Sleep(300)
        uicore.animations.MoveInFromBottom(self.donationReceivedLabel, amount=5, duration=0.15)
        uicore.animations.FadeIn(self.donationReceivedLabel, sleep=True, duration=0.5)
        blue.synchro.Sleep(5000)
        uicore.animations.FadeOut(self.bottomFlashEffect, duration=0.3, sleep=True)
        uicore.animations.FadeOut(self.donationReceivedLabel, sleep=True, duration=0.3)
        uicore.animations.FadeIn(self.bottomBottomCont, duration=0.3)
        self.bottomBottomCont.Enable()
        uicore.animations.FadeIn(self.bottomTaxCont, duration=0.3)
        self.bottomTaxCont.Enable()

    def OnSolarSystemLPChange(self, oldPoints, newPoints):
        self.SetLPPoolAmount(newPoints)
        myLPs = self.GetMyLPs()
        self.donateAmountEdit.SetMinValue(appConst.facwarMinLPDonation)
        self.donateAmountEdit.SetMaxValue(myLPs)
        self.UpdateMyLPAmount()
        if newPoints > oldPoints:
            for bar in self.upgradeBars:
                bar.SetLPAmount(newPoints)

        else:
            for bar in reversed(self.upgradeBars):
                bar.SetLPAmount(newPoints)

    def GetMyLPs(self):
        militiaCorpID = self.facwar.GetFactionMilitiaCorporation(session.warfactionid)
        return sm.GetService('loyaltyPointsWalletSvc').GetCharacterWalletLPBalance(militiaCorpID)


class FWUpgradeLevelCont(Container):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_height = 60
    default_opacity = 0.0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.lowerLimit = attributes.lowerLimit
        self.upperLimit = attributes.upperLimit
        self.lpAmount = attributes.lpAmount
        self.lastAmount = 0
        self.level = attributes.level
        self.facwar = sm.GetService('facwar')
        self.leftCont = Container(name='leftCont', parent=self, align=uiconst.TOLEFT_PROP, width=0.75)
        self.rightCont = Container(name='rightCont', parent=self)
        self.bgFrame = Frame(bgParent=self.leftCont, frameConst=uiconst.FRAME_BORDER1_CORNER1, color=(1.0, 1.0, 1.0, 0.5))
        self.bgGradient = GradientSprite(bgParent=self.leftCont, rotation=-pi / 2)
        levelName = eveLabel.EveCaptionLarge(parent=self.leftCont, text=self.GetLevelName(), top=5, left=10)
        if self.level == 6:
            levelName.fontsize = 16
        self.progressGauge = Gauge(parent=self.leftCont, value=0.0, color=(0.0, 0.31, 0.4, 1.0), backgroundColor=(0.1, 0.1, 0.1, 1.0), align=uiconst.TOBOTTOM, gaugeHeight=15, padding=2, opacity=0.0)
        self.progressGauge.GetHint = self.GetProgressGaugeHint
        self.iconCont = Container(name='iconCont', parent=self.leftCont, align=uiconst.TOPRIGHT, pos=(10, 4, 300, 20))
        self.ConstructIcons()
        self.checkboxSprite = Sprite(name='checkboxSprite', parent=self.rightCont, align=uiconst.CENTERLEFT, pos=(15, 0, 16, 16))
        eveLabel.EveLabelLarge(parent=self.rightCont, text=localization.formatters.FormatNumeric(self.upperLimit, useGrouping=True), align=uiconst.CENTERLEFT, left=60)
        self.SetLPAmount(self.lpAmount, init=True)

    def GetProgressGaugeHint(self):
        if self.lpAmount > self.lowerLimit and self.lpAmount < self.upperLimit:
            return localization.GetByLabel('UI/FactionWarfare/IHub/LevelUnlockHint', num=self.lpAmount - self.lowerLimit, numTotal=self.upperLimit - self.lowerLimit)

    def ConstructIcons(self):
        benefits = self.facwar.GetSystemUpgradeLevelBenefits(self.level)
        for benefitType, benefitValue in benefits:
            FWSystemBenefitIcon(parent=self.iconCont, align=uiconst.TORIGHT, height=self.iconCont.height, padLeft=12, benefitType=benefitType, benefitValue=benefitValue)

    def GetLevelName(self):
        if self.level == 6:
            return localization.GetByLabel('UI/FactionWarfare/IHub/Buffer')
        return eveformat.number_roman(self.level, zero_text='N/A')

    def SetLPAmount(self, lpAmount, init = False):
        self.lastAmount = self.lpAmount
        self.lpAmount = lpAmount
        if not init:
            if self.lpAmount < self.lowerLimit and self.lastAmount < self.lowerLimit:
                return
            if self.lpAmount >= self.upperLimit and self.lastAmount >= self.upperLimit:
                return
        if self.lpAmount >= self.upperLimit:
            uicore.animations.FadeIn(self)
            self.bgGradient.SetGradient([(0, (0.3, 0.5, 0.3))], [(0, 0.2), (1.0, 0.7)])
            self.HideBar(init=init)
            self.SetBGFrameColor((0.0, 0.4, 0.0, 0.3), init)
            self.checkboxSprite.texturePath = 'res:/UI/Texture/icons/38_16_193.png'
            self.checkboxSprite.opacity = 1.0
            self.iconCont.opacity = 1.0
        elif self.lpAmount >= self.lowerLimit:
            uicore.animations.FadeIn(self)
            self.ShowBar(init=init)
            self.bgGradient.SetGradient([(0, (0.3, 0.3, 0.3))], [(0, 0.2), (1.0, 0.7)])
            self.SetBGFrameColor(Color.GetGrayRGBA(0.5, 0.3), init)
            self.checkboxSprite.texturePath = 'res:/UI/Texture/classes/FWInfrastructureHub/smallCircle.png'
            self.checkboxSprite.opacity = 0.3
            self.iconCont.opacity = 0.3
        else:
            uicore.animations.FadeTo(self, self.opacity, 0.3)
            self.bgGradient.SetGradient([(0, (0.3, 0.3, 0.3))], [(0, 0.2), (1.0, 0.7)])
            self.HideBar(init=init)
            self.SetBGFrameColor(Color.GetGrayRGBA(0.5, 0.3), init)
            self.checkboxSprite.texturePath = 'res:/UI/Texture/classes/FWInfrastructureHub/smallCircle.png'
            self.checkboxSprite.opacity = 1.0
            self.iconCont.opacity = 1.0

    def SetBGFrameColor(self, color, init):
        color = Color.GetGrayRGBA(0.5, 0.3)
        if not init:
            uicore.animations.SpColorMorphTo(self.bgFrame, endColor=color)
        else:
            self.bgFrame.color = color

    def ShowBar(self, init = False):
        if self.lastAmount and self.lastAmount > self.lpAmount:
            self.progressGauge.SetValueInstantly(self.GetLastValue())
        if init:
            self.progressGauge.opacity = 1.0
        else:
            uicore.animations.FadeIn(self.progressGauge)
        self.progressGauge.SetValue(self.GetValue())

    def HideBar(self, init = False):
        if not init:
            self.progressGauge.SetValueInstantly(self.GetLastValue())
            self.progressGauge.SetValue(self.GetValue())
            if self.progressGauge.opacity < 1.0:
                uicore.animations.FadeIn(self.progressGauge, duration=0.1, sleep=True)
            uicore.animations.FadeOut(self.progressGauge, sleep=True)

    def GetValue(self):
        value = (self.lpAmount - self.lowerLimit) / float(self.upperLimit - self.lowerLimit)
        return max(0.0, min(value, 1.0))

    def GetLastValue(self):
        value = (self.lastAmount - self.lowerLimit) / float(self.upperLimit - self.lowerLimit)
        return max(0.0, min(value, 1.0))
