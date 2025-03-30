#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\securityOfficeWindow.py
import math
from carbonui.primitives.frame import Frame
from collections import defaultdict
import localization
import uthread
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import TextAlign, TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from crimewatch.const import securityLevelsPerTagType
from crimewatch.util import CalculateTagRequirementsForSecIncrease
from eve.client.script.ui.control import eveIcon, eveLabel
from carbonui.control.button import Button
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.station.securityOfficeConst import BAR_HEIGHT, BAR_PADDING, BAR_WIDTH, BOX_WIDTH, DRAGBAR_COLOR_NOTAVAILABLE, SEC_BAND_DATA, SEC_METER_HEIGHT, SLIDER_COLOR_AVAILABLE, SLIDER_COLOR_AVAILABLE_ALT, SLIDER_COLOR_CURRENT, SLIDER_COLOR_NOTAVAILABLE, SLIDER_COLOR_NOTAVAILABLE_ALT, SLIDER_COLOR_WANTED, SLIDER_COLOR_WANTED_ALT, TAG_BUCKETS, WINDOW_HEIGHT, WINDOW_WIDTH
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from eveservices.menu import GetMenuService

def GetBucketAndRatioForSec(secStatus):
    for i, data in enumerate(TAG_BUCKETS):
        if data.minSec <= secStatus < data.maxSec:
            leftover = secStatus - data.minSec
            ratio = leftover / (data.maxSec - data.minSec)
            return (i, leftover, ratio)

    return (len(TAG_BUCKETS) - 1, secStatus - TAG_BUCKETS[-1].minSec, 1.0)


class SecurityOfficeWindow(Window):
    __notifyevents__ = ['OnSecurityForTagSelectionChanged',
     'OnSecurityStatusUpdate',
     'OnItemChange',
     'OnAccountChange']
    default_windowID = 'securityoffice'
    default_fixedHeight = WINDOW_HEIGHT
    default_fixedWidth = WINDOW_WIDTH
    default_captionLabelPath = 'UI/SecurityOffice/StationServiceName'
    default_iconNum = 'res:/UI/Texture/WindowIcons/concord.png'
    default_scope = uiconst.SCOPE_STATION
    default_isStackable = False

    def ApplyAttributes(self, attributes):
        super(SecurityOfficeWindow, self).ApplyAttributes(attributes)
        self.crimewatchSvc = sm.GetService('crimewatchSvc')
        self.godmaSvc = sm.GetService('godma')
        self.walletSvc = sm.GetService('wallet')
        self.topParent = ContainerAutoSize(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, clipChildren=True, padding=(0, 10, 0, 10))
        self.currentSecurityStatus = 0
        self.targetSecurityStatus = 0
        self.ConstructLayout()

    def ConstructTopCont(self):
        eveLabel.EveCaptionMedium(name='caption', parent=self.topParent, text=localization.GetByLabel('UI/SecurityOffice/HeaderCaption'), align=uiconst.TOTOP, textAlign=TextAlign.CENTER)
        eveLabel.EveLabelMedium(name='subcaption', parent=self.topParent, text=localization.GetByLabel('UI/SecurityOffice/WindowSubheaderDescription'), align=uiconst.TOTOP, textAlign=TextAlign.CENTER, color=TextColor.SECONDARY)

    def ConstructLayout(self):
        self.ConstructTopCont()
        self.securityTagBar = SecurityTagBar(parent=self.sr.main)
        bottomContainer = Container(name='bottomContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, height=40)
        self.iskCostText = eveLabel.EveLabelMediumBold(parent=bottomContainer, align=uiconst.CENTERLEFT, left=8)
        self.submitButton = Button(parent=bottomContainer, align=uiconst.CENTERRIGHT, left=8, label=localization.GetByLabel('UI/SecurityOffice/ExchangeTags'), func=self.Submit)
        self.CreateTextFeedback()

    def CreateTextFeedback(self):
        self.pveText = eveLabel.EveLabelMedium(parent=self.sr.main, name='goodEffectText', align=uiconst.CENTERBOTTOM, top=66)
        self.pvpText = eveLabel.EveLabelMedium(parent=self.sr.main, name='badEffectText', align=uiconst.CENTERBOTTOM, top=48)

    def OnSecurityForTagSelectionChanged(self, targetSecurityStatus, tagsToSpend, sufficientTags):
        self.targetSecurityStatus = targetSecurityStatus
        self.currentSecurityStatus = self.crimewatchSvc.GetMySecurityStatus()
        noSelection = targetSecurityStatus == self.currentSecurityStatus
        if noSelection:
            self.submitButton.Disable()
        else:
            self.submitButton.Enable()
        iskTotal = 0
        for typeID, quantity in tagsToSpend.iteritems():
            iskTotal += self.godmaSvc.GetTypeAttribute(typeID, const.attributeSecurityProcessingFee, 0) * quantity

        myBalance = self.walletSvc.GetWealth()
        text = localization.GetByLabel('UI/SecurityOffice/AdditionalCost', cost=iskTotal)
        if myBalance < iskTotal:
            text = '<font color=%s>%s</font>' % (SEC_BAND_DATA[3].color.GetHex(), text)
            self.submitButton.Disable()
        elif not noSelection:
            self.submitButton.Enable()
        if not sufficientTags:
            self.submitButton.Disable()
        self.iskCostText.SetText(text)
        for data in SEC_BAND_DATA:
            if data.minSec <= targetSecurityStatus < data.maxSec:
                self.pvpText.SetText(localization.GetByLabel(data.pvpHintLabel))
                self.pveText.SetText(localization.GetByLabel(data.pveHintLable))
                break
        else:
            data = SEC_BAND_DATA[-1]
            self.pvpText.SetText(localization.GetByLabel(data.pvpHintLabel))
            self.pveText.SetText(localization.GetByLabel(data.pveHintLable))

    def Submit(self, button):
        try:
            eveMoniker.CharGetCrimewatchLocation().ApplyTagsForSecStatus(self.targetSecurityStatus, self.currentSecurityStatus)
        finally:
            self.UpdateSecurityTagBar()

    def OnItemChange(self, item, change, location):
        if item.typeID in securityLevelsPerTagType:
            if item.locationID == session.stationid or change.get(const.ixLocationID) == session.stationid:
                self.UpdateSecurityTagBar()

    def UpdateSecurityTagBar(self):
        self.updateTimer = AutoTimer(100, self._UpdateSecurityTagBar)

    def _UpdateSecurityTagBar(self):
        self.updateTimer = None
        self.securityTagBar.UpdateCurrentSecAndTags(self.targetSecurityStatus)

    def OnSecurityStatusUpdate(self, newSecurityStatus):
        self.UpdateSecurityTagBar()

    def OnAccountChange(self, accountKey, ownerID, balance):
        if accountKey == 'cash' and ownerID == session.charid:
            self.UpdateSecurityTagBar()


class SecurityTagBar(Container):
    default_height = 120
    default_width = BAR_WIDTH
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_PICKCHILDREN
    default_padLeft = 0
    default_padRight = 0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.crimewatchSvc = sm.GetService('crimewatchSvc')
        self.securityOfficeSvc = sm.GetService('securityOfficeSvc')
        self.isDragging = False
        self.CreateDragBar()
        self.CreateBar()
        self.CreateSlider()
        uthread.new(self.SetCurrentSecStatus, self.crimewatchSvc.GetMySecurityStatus())

    def GetSecAtMouseOffset(self, mouseOffset):
        bucketIndex = int(mouseOffset) / BOX_WIDTH
        if bucketIndex >= len(TAG_BUCKETS):
            return 10.0
        elif bucketIndex < 0:
            return -10.0
        else:
            leftover = mouseOffset % BOX_WIDTH
            ratio = leftover / float(BOX_WIDTH)
            data = TAG_BUCKETS[bucketIndex]
            return data.minSec + ratio * (data.maxSec - data.minSec)

    def SetCurrentSecStatus(self, currentSecurityStatus, mouseOffset = 0):
        self.currentSecStatus = currentSecurityStatus
        bucketIndex, leftover, ratio = GetBucketAndRatioForSec(currentSecurityStatus)
        offset = bucketIndex * BOX_WIDTH + ratio * BOX_WIDTH
        for fill in self.sliderContainer.children[1:]:
            fill.width = 0

        self.sliderContainer.children[0].width = offset
        self.locator.left = offset + BAR_PADDING - self.locator.width / 2
        targetSecurityStatus = self.GetSecAtMouseOffset(mouseOffset)
        tags = self.securityOfficeSvc.GetTagsInHangar()
        tagsToSpend = defaultdict(int)
        altCount = 0
        secTarget = currentSecurityStatus
        tempOffset = offset
        targetOffset = offset
        targetSliceSec = currentSecurityStatus
        sufficientTags = True
        if bucketIndex < 4:
            allTagsNeeded = CalculateTagRequirementsForSecIncrease(currentSecurityStatus, TAG_BUCKETS[-1].minSec)
            for i in xrange(bucketIndex, 4):
                data = TAG_BUCKETS[i]
                numTagsNeeded = allTagsNeeded.get(data.typeID, 0)
                numTagsOwned = min(tags.get(data.typeID, 0), numTagsNeeded)
                for n in xrange(numTagsNeeded):
                    secTarget += const.securityGainPerTag
                    _bucketIndex, _leftover, _ratio = GetBucketAndRatioForSec(secTarget)
                    newOffset = _bucketIndex * BOX_WIDTH + _ratio * BOX_WIDTH
                    sliceWidth = newOffset - tempOffset
                    altColor = altCount % 2 == 1
                    sliceIsWanted = targetSecurityStatus > secTarget
                    tagIsAvailable = n < numTagsOwned
                    if sliceIsWanted:
                        if tagIsAvailable:
                            color = SLIDER_COLOR_WANTED if altColor else SLIDER_COLOR_WANTED_ALT
                        else:
                            color = SLIDER_COLOR_NOTAVAILABLE if altColor else SLIDER_COLOR_NOTAVAILABLE_ALT
                            sufficientTags = False
                        tagsToSpend[data.typeID] += 1
                        targetSliceSec = secTarget
                        targetOffset = newOffset
                    elif tagIsAvailable:
                        color = SLIDER_COLOR_AVAILABLE if altColor else SLIDER_COLOR_AVAILABLE_ALT
                    else:
                        color = None
                    fill = self.sliderContainer.children[1 + altCount]
                    if color is None:
                        fill.color.SetAlpha(0)
                    else:
                        fill.SetRGBA(*color)
                        self.SetDragBarColor(color)
                    fill.width = sliceWidth
                    tempOffset = newOffset
                    altCount += 1

        if sufficientTags:
            self.SetDragBarColor(None)
        else:
            self.SetDragBarColor(DRAGBAR_COLOR_NOTAVAILABLE)
        self.locator.left = targetOffset + BAR_PADDING - self.locator.width / 2
        self.sliderSecText.SetText('%2.1f' % targetSliceSec)
        if targetOffset == 0:
            self.sliderSecText.SetAlign(uiconst.BOTTOMLEFT)
        elif targetOffset == BAR_WIDTH:
            self.sliderSecText.SetAlign(uiconst.BOTTOMRIGHT)
        else:
            self.sliderSecText.SetAlign(uiconst.CENTERBOTTOM)
        for i, data in enumerate(TAG_BUCKETS):
            if data.typeID is not None:
                quantity = tagsToSpend[data.typeID]
                self.buckets[i].SetQuantity(quantity)

        sm.ScatterEvent('OnSecurityForTagSelectionChanged', targetSliceSec, tagsToSpend, sufficientTags)

    def CreateBar(self):
        self.barContainer = Container(name='barContainer', parent=self, align=uiconst.TOTOP, height=BAR_HEIGHT, padTop=20, padLeft=BAR_PADDING, padRight=BAR_PADDING)
        Frame(parent=self.barContainer, color=(0.5, 0.5, 0.5, 0.5), offset=1)
        eveLabel.EveLabelSmallBold(parent=self.barContainer, align=uiconst.TOPLEFT, text='-10', padTop=3, left=1, color=(1, 1, 1, 1))
        eveLabel.EveLabelSmallBold(parent=self.barContainer, align=uiconst.TOPRIGHT, text='-8', padTop=3, left=4 * BOX_WIDTH - 3, color=(1, 1, 1, 1))
        eveLabel.EveLabelSmallBold(parent=self.barContainer, align=uiconst.TOPRIGHT, text='-5', padTop=3, left=3 * BOX_WIDTH - 3, color=(1, 1, 1, 1))
        eveLabel.EveLabelSmallBold(parent=self.barContainer, align=uiconst.TOPRIGHT, text='-2', padTop=3, left=2 * BOX_WIDTH - 3, color=(1, 1, 1, 1))
        eveLabel.EveLabelSmallBold(parent=self.barContainer, align=uiconst.TOPRIGHT, text='0', padTop=3, left=BOX_WIDTH - 3, color=(1, 1, 1, 1))
        eveLabel.EveLabelSmallBold(parent=self.barContainer, align=uiconst.TOPRIGHT, text='10', padTop=3, left=1, color=(1, 1, 1, 1))
        bucketContainer = Container(name='bucketContainer', parent=self.barContainer, align=uiconst.TOPLEFT, height=BAR_HEIGHT, width=BAR_WIDTH)
        self.buckets = []
        for data in TAG_BUCKETS:
            if data.typeID is None:
                bucket = LastBucket(parent=bucketContainer)
            else:
                bucket = BucketOfTags(parent=bucketContainer, name='bucket_%s' % data.typeID, typeID=data.typeID, minSec=data.minSec, maxSec=data.maxSec)
            self.buckets.append(bucket)

        self.sliderContainer = Container(name='sliderContainer', parent=self.barContainer, align=uiconst.TOALL)

    def CreateDragBar(self):
        self.locator = Container(name='locator', parent=self, align=uiconst.TOPLEFT, left=0, width=8, height=self.height, state=uiconst.UI_NORMAL, padLeft=0, cursor=uiconst.UICURSOR_LEFT_RIGHT_DRAG)
        self.locator.OnMouseDown = (self.OnSliderMouseDown, self.locator)
        self.locator.OnMouseMove = (self.OnSliderMouseMove, self.locator)
        Fill(parent=self.locator, color=(1, 1, 1, 1), height=82, width=2, align=uiconst.CENTER)
        Sprite(name='topTriangle', parent=self.locator, texturePath='res:/ui/texture/icons/105_32_15.png', align=uiconst.CENTER, rotation=math.pi / 2, width=32, height=32, top=-43, state=uiconst.UI_DISABLED)
        Sprite(name='bottomTriangle', parent=self.locator, texturePath='res:/ui/texture/icons/105_32_15.png', align=uiconst.CENTER, rotation=-math.pi / 2, width=32, height=32, top=43, state=uiconst.UI_DISABLED)
        self.sliderSecText = eveLabel.EveLabelLargeBold(parent=self.locator, name='secStatus', align=uiconst.CENTERBOTTOM, top=-4)

    def SetDragBarColor(self, color = None):
        if color is None:
            color = Color.WHITE
        self.locator.children[0].SetRGBA(*color)
        self.locator.children[1].SetRGBA(*color)
        self.locator.children[2].SetRGBA(*color)

    def CreateSlider(self):
        for x in xrange(21):
            Fill(parent=self.sliderContainer, align=uiconst.TOLEFT, width=0, display=True)

        self.sliderContainer.children[0].SetRGBA(*SLIDER_COLOR_CURRENT)

    def OnSliderMouseDown(self, *args):
        self.isDragging = True

    def OnSliderMouseMove(self, *args):
        if not (self.isDragging and uicore.uilib.leftbtn):
            self.isDragging = False
            return
        x, y = self.barContainer.GetAbsolutePosition()
        offset = uicore.uilib.x - x
        self.SetCurrentSecStatus(self.crimewatchSvc.GetMySecurityStatus(), offset)

    def UpdateCurrentSecAndTags(self, targetSecurityStatus):
        bucketIndex, leftover, ratio = GetBucketAndRatioForSec(targetSecurityStatus)
        offset = bucketIndex * BOX_WIDTH + ratio * BOX_WIDTH
        currentSecurityStatus = self.crimewatchSvc.GetMySecurityStatus()
        if targetSecurityStatus != currentSecurityStatus:
            offset += 1
        self.SetCurrentSecStatus(currentSecurityStatus, offset)


class BucketOfTags(Container):
    default_width = BOX_WIDTH
    default_align = uiconst.TOLEFT
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.minSec = attributes.minSec
        self.maxSec = attributes.maxSec
        self.secRange = self.maxSec - self.minSec
        self.typeID = attributes.typeID
        self.numSecSections = int(self.secRange / 0.5)
        sectionWidth = self.width / self.numSecSections
        Line(parent=self, align=uiconst.TORIGHT, color=(0, 0, 0, 0.5))
        icon = eveIcon.Icon(parent=self, typeID=self.typeID, size=48, align=uiconst.CENTER, ignoreSize=True, OnClick=self.OnIconClick, state=uiconst.UI_NORMAL)
        icon.GetMenu = lambda : GetMenuService().GetMenuFromItemIDTypeID(None, self.typeID, includeMarketDetails=True)
        secMeter = Container(parent=self, align=uiconst.TOTOP, height=SEC_METER_HEIGHT)
        for n in xrange(self.numSecSections):
            sec = self.minSec + n * const.securityGainPerTag
            for data in SEC_BAND_DATA:
                if sec < data.maxSec:
                    break

            if data.altColor is not None and n % 2 == 1:
                color = data.altColor
            else:
                color = data.color
            Fill(parent=secMeter, align=uiconst.TOLEFT, width=sectionWidth, color=color.GetRGBA(), hint=localization.GetByLabel(data.pveHintLable) + '<br>' + localization.GetByLabel(data.pvpHintLabel), state=uiconst.UI_NORMAL)

        self.quantitySpentText = eveLabel.EveLabelSmallBold(parent=self, align=uiconst.CENTER, top=30, color=(1, 1, 1, 1))
        self.SetQuantity(0)

    def SetQuantity(self, quantity):
        self.quantitySpentText.SetText(str(quantity))

    def OnIconClick(self):
        sm.GetService('info').ShowInfo(self.typeID)


class LastBucket(Container):
    default_width = BOX_WIDTH + 2
    default_align = uiconst.TOLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        data = SEC_BAND_DATA[-1]
        Fill(parent=self, align=uiconst.TOTOP, height=SEC_METER_HEIGHT, color=data.color.GetRGBA(), hint=localization.GetByLabel(data.pveHintLable) + '<br>' + localization.GetByLabel(data.pvpHintLabel), state=uiconst.UI_NORMAL)
