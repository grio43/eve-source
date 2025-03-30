#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skilltrading\banner.py
import blue
import evetypes
import inventorycommon.typeHelpers
import localization
import uthread
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
import dogma.const as dogmaConst
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveCaptionMedium, EveLabelMedium, EveLabelMediumBold
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.utilButtons.marketDetailsButton import ShowMarketDetailsButton
from eve.client.script.ui.shared.neocom.skillConst import COLOR_UNALLOCATED_1
from eve.client.script.ui.shared.vgs.button import BuyButtonAur
from eve.common.script.util.eveFormat import FmtISKAndRound
from inventorycommon import const as invconst
from localization.formatters.timeIntervalFormatters import FormatTimeIntervalShortWritten

class SkillInjectorBanner(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(SkillInjectorBanner, self).ApplyAttributes(attributes)
        self.injectorTypeID = attributes.Get('typeID', invconst.typeSkillInjector)
        self.ConstructLayout()
        self._UpdateEstimatedInjectorPrice()
        self._UpdateMainText()
        uthread.new(self._UpdateEstimatedTimeSaved)

    def ConstructLayout(self):
        topCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT, padTop=6)
        Icon(parent=topCont, align=uiconst.TOPLEFT, left=4, typeID=self.injectorTypeID, size=32, state=uiconst.UI_DISABLED)
        EveLabelMedium(parent=topCont, align=uiconst.TOPLEFT, left=40, text=evetypes.GetName(self.injectorTypeID))
        self.priceLabel = EveLabelMedium(parent=topCont, align=uiconst.TOPLEFT, top=14, left=40, color=TextColor.SECONDARY)
        infoBtnCont = ContainerAutoSize(parent=topCont, align=uiconst.CENTERRIGHT)
        InfoIcon(parent=infoBtnCont, typeID=self.injectorTypeID, align=uiconst.TOPLEFT, hint=localization.GetByLabel('UI/Commands/ShowInfo'))
        ShowMarketDetailsButton(parent=infoBtnCont, align=uiconst.TOPLEFT, left=24, width=16, height=16, typeID=self.injectorTypeID)
        self.mainLabel = EveLabelMedium(parent=self, align=uiconst.TOTOP, padding=(8, 4, 8, 4))
        self.estimatedTimeSavedLabel = EveLabelMedium(parent=self, align=uiconst.TOTOP, padding=(8, 4, 8, 4))

    def _UpdateEstimatedInjectorPrice(self):
        price = inventorycommon.typeHelpers.GetAveragePrice(self.injectorTypeID)
        if price is None or price <= 0:
            price = localization.GetByLabel('UI/Common/Unknown')
        else:
            price = FmtISKAndRound(price, False)
        text = localization.GetByLabel('UI/SkillTrading/EstimatedPrice', price=price)
        self.priceLabel.SetText(text)

    def _UpdateMainText(self):
        points = sm.GetService('skills').GetSkillPointAmountFromInjectors(self.injectorTypeID, quantity=1)
        color = Color.RGBtoHex(*COLOR_UNALLOCATED_1)
        text = localization.GetByLabel('UI/SkillTrading/InjectorBannerMainText', injector=self.injectorTypeID, points=points, color=color)
        self.mainLabel.SetText(text)

    def _UpdateEstimatedTimeSaved(self):
        points = sm.GetService('skills').GetSkillPointAmountFromInjectors(self.injectorTypeID, quantity=1)
        timeSaved = sm.GetService('skillqueue').GetTimeSavedByUnallocatedPoints(points)
        if timeSaved:
            timeSavedFormattedText = localization.GetByLabel('UI/SkillTrading/EstimatedTimeSaved', timeSaved=long(timeSaved), color='0xFF328FA8')
            self.estimatedTimeSavedLabel.SetText(timeSavedFormattedText)
        else:
            self.estimatedTimeSavedLabel.Close()


class AlphaInjectorBanner(ContainerAutoSize):
    INJECTOR_TYPE = invconst.typeAlphaTrainingInjector

    def ApplyAttributes(self, attributes):
        super(AlphaInjectorBanner, self).ApplyAttributes(attributes)
        self.ConstructLayout()
        uthread.new(self._UpdateEstimatedInjectorPrice)

    def ConstructLayout(self):
        topCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT, padTop=6)
        Icon(parent=topCont, align=uiconst.TOPLEFT, left=4, typeID=self.INJECTOR_TYPE, size=32, state=uiconst.UI_DISABLED)
        EveLabelMedium(parent=topCont, align=uiconst.TOPLEFT, left=40, text=evetypes.GetName(self.INJECTOR_TYPE))
        self.priceLabel = EveLabelMedium(parent=topCont, align=uiconst.TOPLEFT, top=14, left=40, color=TextColor.SECONDARY)
        infoBtnCont = ContainerAutoSize(parent=topCont, align=uiconst.CENTERRIGHT)
        InfoIcon(parent=infoBtnCont, typeID=self.INJECTOR_TYPE, align=uiconst.TOPLEFT, hint=localization.GetByLabel('UI/Commands/ShowInfo'))
        ShowMarketDetailsButton(parent=infoBtnCont, align=uiconst.TOPLEFT, left=24, width=16, height=16, typeID=self.INJECTOR_TYPE)
        EveLabelMedium(parent=self, align=uiconst.TOTOP, padding=(8, 4, 8, 4), text=localization.GetByLabel('UI/SkillTrading/AlphaInjectorBannerText', type=self.INJECTOR_TYPE, color=Color.RGBtoHex(*COLOR_UNALLOCATED_1), points=sm.GetService('skills').GetSkillPointAmountFromInjectors(self.INJECTOR_TYPE, quantity=1)))
        bottomCont = Container(parent=self, align=uiconst.TOTOP, height=50, padding=(8, 0, 8, 8))
        nextInjection = sm.GetService('skills').GetNextAlphaInjectionDateTime()
        if nextInjection > blue.os.GetWallclockTime():
            timerCont = ContainerAutoSize(parent=bottomCont, align=uiconst.BOTTOMLEFT, alignMode=uiconst.CENTERTOP)
            timerCaption = EveLabelMedium(name='timerCaption', parent=bottomCont, align=uiconst.TOPLEFT, text=localization.GetByLabel('UI/SkillTrading/NextInjectionAvailableIn'))
            timerCont.width = timerCaption.textwidth
            timerLabel = EveCaptionMedium(name='timerLabel', parent=bottomCont, align=uiconst.BOTTOMLEFT, maxWidth=180)
            uthread.new(self._UpdateNextInjectionTime, timerLabel, nextInjection)
        BuyButtonAur(parent=bottomCont, align=uiconst.BOTTOMRIGHT, top=8, types=[self.INJECTOR_TYPE])

    def _UpdateEstimatedInjectorPrice(self):
        price = inventorycommon.typeHelpers.GetAveragePrice(self.INJECTOR_TYPE)
        if price is None or price <= 0:
            price = localization.GetByLabel('UI/Common/Unknown')
        else:
            price = FmtISKAndRound(price, False)
        text = localization.GetByLabel('UI/SkillTrading/EstimatedPrice', price=price)
        self.priceLabel.SetText(text)

    def _UpdateNextInjectionTime(self, label, nextInjection):
        color = Color.RGBtoHex(*COLOR_UNALLOCATED_1)
        template = u'<center><color={color}>{timeLeft}</color></center>'
        while not label.destroyed:
            timeLeft = nextInjection - blue.os.GetWallclockTime()
            if timeLeft <= 0:
                label.Close()
                return
            text = template.format(color=color, timeLeft=FormatTimeIntervalShortWritten(timeLeft))
            label.SetText(text)
            blue.synchro.SleepWallclock(1000)


class NonDiminishingInjectionBoosterBanner(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(NonDiminishingInjectionBoosterBanner, self).ApplyAttributes(attributes)
        godma = sm.GetService('godma')
        self.typeID = attributes.typeID
        self.quantity = attributes.quantity
        numberOfUses = godma.GetTypeAttribute(self.typeID, dogmaConst.attributeNonDiminishingSkillInjectorUses, 0)
        labelText = localization.GetByLabel('UI/Skills/TotalNonDiminishingInjectionsForBooster', injections=int(numberOfUses))
        self.content = ContainerAutoSize(parent=self, align=uiconst.CENTER, margin=(12, 8, 12, 8))
        self.title = EveLabelMediumBold(parent=self.content, align=uiconst.TOPLEFT, text=self.GetNameAndQuantityText())
        self.title.Layout()
        self.label = EveLabelMedium(parent=self.content, align=uiconst.TOPLEFT, width=200, text=labelText, padTop=self.title.height + 5)
        self.label.Layout()

    def GetNameAndQuantityText(self):
        name = evetypes.GetName(self.typeID)
        if self.quantity > 1:
            return localization.GetByLabel('UI/Inventory/QuantityAndName', quantity=self.quantity, name=name)
        else:
            return name
