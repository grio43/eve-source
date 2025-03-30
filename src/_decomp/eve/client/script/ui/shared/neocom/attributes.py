#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\attributes.py
import blue
from carbon.common.script.util.format import FmtDate
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from characterskills.attribute import ATTRIBUTEBONUS_BY_ATTRIBUTEID
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from dogma.effects import IsBoosterSkillAccelerator
from eve.client.script.ui.control import eveIcon, eveLabel
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from eve.client.script.ui.control.clickableboxbar import ClickableBoxBar
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.common.lib import appConst as const
from eveexceptions import UserError
from fsdBuiltData.common.iconIDs import GetIconFile
import uthread
import carbonui.const as uiconst
import localization
import evetypes

class AttributeRespecWindow(Window):
    __guid__ = 'form.attributeRespecWindow'
    default_windowID = 'attributerespecification'
    default_iconNum = 'res:/ui/Texture/WindowIcons/attributes.png'
    default_minSize = (450, 450)
    default_captionLabelPath = 'UI/CharacterSheet/CharacterSheetWindow/Attributes/NeuralRemapping'

    def ApplyAttributes(self, attributes):
        super(AttributeRespecWindow, self).ApplyAttributes(attributes)
        self.readOnly = attributes.readOnly
        self.MakeUnResizeable()
        self.godma = sm.StartService('godma')
        self.skillHandler = sm.StartService('skills').GetSkillHandler()
        self.main_cont = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, callback=self._on_main_cont_size_changed, only_use_callback_when_size_changes=True)
        self.attributes = [const.attributePerception,
         const.attributeMemory,
         const.attributeWillpower,
         const.attributeIntelligence,
         const.attributeCharisma]
        self.implantTypes = [19540,
         19551,
         19553,
         19554,
         19555]
        self.attributeIcons = ['ui_22_32_5',
         'ui_22_32_4',
         'ui_22_32_2',
         'ui_22_32_3',
         'ui_22_32_1']
        self.attributeLabels = [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributePerception'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributeMemory'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributeWillpower'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributeIntelligence'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributeCharisma')]
        self.currentAttributes = {}
        self.implantModifier = {}
        self.unspentPts = 0
        self.ConstructLayout()
        self.Load()

    def Load(self, *args):
        if not eve.session.charid or self.destroyed:
            return
        dogmaLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
        skillSvc = sm.StartService('skills')
        dogmaStaticMgr = dogmaLM.dogmaStaticMgr
        attrDict = skillSvc.GetCharacterAttributes()
        unspentPts = const.respecTotalRespecPoints
        for x in xrange(0, 5):
            attr = self.attributes[x]
            if attr in attrDict:
                attrValue = attrDict[attr]
                implantBonus = 0
                implants = skillSvc.GetImplants()
                boosters = skillSvc.GetBoosters()
                for implantSlot, implant in implants.iteritems():
                    implantBonus += dogmaStaticMgr.GetTypeAttribute2(implant.typeID, ATTRIBUTEBONUS_BY_ATTRIBUTEID[attr])

                boosterBonus = 0
                for boosterTypeID, boosterRecord in boosters.iteritems():
                    if IsBoosterSkillAccelerator(dogmaStaticMgr, boosterRecord):
                        boosterBonus += dogmaStaticMgr.GetTypeAttribute2(boosterRecord.boosterTypeID, ATTRIBUTEBONUS_BY_ATTRIBUTEID[attr])

                attrValue -= implantBonus
                attrValue -= boosterBonus
                if attrValue > const.respecMaximumAttributeValue:
                    attrValue = const.respecMaximumAttributeValue
                if attrValue < const.respecMinimumAttributeValue:
                    attrValue = const.respecMinimumAttributeValue
                self.currentAttributes[attr] = attrValue
                self.respecBar[x].SetValue(attrValue - const.respecMinimumAttributeValue)
                unspentPts -= attrValue
            totalAttributesText = localization.formatters.FormatNumeric(int(self.currentAttributes[attr]) + implantBonus, decimalPlaces=0)
            self.totalLabels[x].text = totalAttributesText
            self.implantModifier[x] = implantBonus
            label, icon = self.implantLabels[x]
            if implantBonus == 0:
                icon.SetAlpha(0.5)
                label.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/ImplantBonusZero')
                label.SetAlpha(0.5)
            else:
                label.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/ImplantBonus', implantBonus=int(implantBonus))

        if not self.readOnly:
            self.unspentPts = unspentPts
            self.sr.unassignedBar.SetValue(unspentPts)
            unspentPtsText = localization.formatters.FormatNumeric(self.unspentPts, decimalPlaces=0)
            self.availableLabel.text = unspentPtsText
            if self.unspentPts <= 0:
                self.sr.saveWarningText.state = uiconst.UI_HIDDEN
            else:
                self.sr.saveWarningText.state = uiconst.UI_DISABLED

    def ConstructLayout(self):
        self.implantLabels = []
        self.respecBar = []
        self.totalLabels = []
        iconsize = 32
        buttonSize = 24
        boxWidth = 6
        boxHeight = 12
        boxMargin = 1
        boxSpacing = 1
        numBoxes = const.respecMaximumAttributeValue - const.respecMinimumAttributeValue
        barWidth = numBoxes * boxSpacing + 2 * boxMargin + numBoxes * boxWidth - 1
        barHeight = boxHeight + 2 * boxMargin
        backgroundColor = (0.0, 0.0, 0.0, 0.0)
        colorDict = {ClickableBoxBar.COLOR_UNSELECTED: (0.2, 0.2, 0.2, 1.0),
         ClickableBoxBar.COLOR_SELECTED: (0.2, 0.8, 0.2, 1.0)}
        MoreInfoIcon(parent=self.header.extra_content, align=uiconst.CENTERLEFT, hint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/CharacterRespecMessage'))
        if self.readOnly:
            columns = 7
        else:
            columns = 9
        gridParent = ContainerAutoSize(parent=self.main_cont, align=uiconst.TOTOP)
        self.mainGrid = LayoutGrid(parent=gridParent, align=uiconst.CENTERTOP, columns=columns, cellPadding=4, OnGridSizeChanged=self._on_main_grid_size_changed)
        for labelPath, colSpan in (('UI/CharacterSheet/CharacterSheetWindow/NavScroll/Attributes', 2),
         ('UI/CharacterSheet/CharacterSheetWindow/Attributes/BaseStatPoints', 1),
         ('UI/CharacterSheet/CharacterSheetWindow/Attributes/CharacterImplants', 2),
         ('UI/CharacterSheet/CharacterSheetWindow/Attributes/RemappableStat', 1 if self.readOnly else 3),
         ('UI/CharacterSheet/CharacterSheetWindow/Attributes/StatTotal', 1)):
            label = EveLabelMedium(text=localization.GetByLabel(labelPath), align=uiconst.CENTER)
            self.mainGrid.AddCell(cellObject=label, colSpan=colSpan, cellPadding=(10, 2, 10, 2))

        line = Line(align=uiconst.TOTOP)
        self.mainGrid.AddCell(cellObject=line, colSpan=self.mainGrid.columns)
        for x in xrange(5):
            eveIcon.Icon(parent=self.mainGrid, width=iconsize, height=iconsize, size=iconsize, icon=self.attributeIcons[x], align=uiconst.TOPLEFT)
            EveLabelMedium(text=self.attributeLabels[x], parent=self.mainGrid, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
            minText = localization.formatters.FormatNumeric(const.respecMinimumAttributeValue, decimalPlaces=0)
            EveLabelMedium(text=minText, parent=self.mainGrid, state=uiconst.UI_DISABLED, align=uiconst.CENTER, bold=True)
            icon = eveIcon.Icon(parent=self.mainGrid, width=32, height=32, size=32, icon=GetIconFile(evetypes.GetIconID(self.implantTypes[x])), align=uiconst.TOPLEFT, ignoreSize=True)
            implantLabel = EveLabelMedium(text='0', parent=self.mainGrid, align=uiconst.CENTERLEFT)
            self.implantLabels.append((implantLabel, icon))
            if not self.readOnly:
                minusText = localization.GetByLabel('UI/Common/Buttons/Minus')
                Button(parent=self.mainGrid, label=minusText, fixedwidth=buttonSize, func=self.DecreaseAttribute, args=(x,), align=uiconst.CENTERRIGHT)
            bar = Container(parent=self.mainGrid, align=uiconst.CENTER, width=barWidth, height=barHeight, state=uiconst.UI_PICKCHILDREN)
            bar = ClickableBoxBar(parent=bar, numBoxes=numBoxes, boxWidth=boxWidth, boxHeight=boxHeight, boxMargin=boxMargin, boxSpacing=boxSpacing, backgroundColor=backgroundColor, colorDict=colorDict)
            bar.OnValueChanged = self.OnMemberBoxClick
            bar.OnAttemptBoxClicked = self.ValidateBoxClick
            self.respecBar.append(bar)
            if not self.readOnly:
                plusText = localization.GetByLabel('UI/Common/Buttons/Plus')
                Button(parent=self.mainGrid, label=plusText, fixedwidth=buttonSize, func=self.IncreaseAttribute, args=(x,), align=uiconst.CENTERLEFT)
            totalLabel = EveLabelMedium(text='0', parent=self.mainGrid, left=8, align=uiconst.CENTERRIGHT, bold=True)
            self.totalLabels.append(totalLabel)

        if not self.readOnly:
            line = Line(align=uiconst.TOTOP)
            self.mainGrid.AddCell(cellObject=line, colSpan=self.mainGrid.columns)
            textObj = EveLabelMedium(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/UnassignedAttributePoints'))
            self.mainGrid.AddCell(cellObject=textObj, colSpan=6)
            numBoxes = const.respecTotalRespecPoints - const.respecMinimumAttributeValue * 5
            barWidth = numBoxes * boxSpacing + 2 * boxMargin + numBoxes * boxWidth - 1
            unassignedBarParent = Container(align=uiconst.TOPLEFT, width=barWidth, height=barHeight, state=uiconst.UI_PICKCHILDREN)
            self.mainGrid.AddCell(cellObject=unassignedBarParent, colSpan=2)
            self.sr.unassignedBar = ClickableBoxBar(parent=unassignedBarParent, numBoxes=numBoxes, boxWidth=boxWidth, boxHeight=boxHeight, boxMargin=boxMargin, boxSpacing=boxSpacing, backgroundColor=backgroundColor, colorDict=colorDict, readonly=True, hintFormat='UI/CharacterSheet/CharacterSheetWindow/Attributes/UnassignedPointsHint')
            self.availableLabel = EveLabelMedium(parent=self.mainGrid, align=uiconst.CENTERRIGHT, left=8)
            self.mainGrid.FillRow()
            self.sr.saveWarningText = EveLabelMedium(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/CannotSaveUnassignedPoints'), color=(1.0, 0.0, 0.0, 0.9))
            self.mainGrid.AddCell(cellObject=self.sr.saveWarningText, colSpan=self.mainGrid.columns)
        if not self.readOnly:
            ButtonGroup(btns=[[localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/SaveStatChanges'),
              self.SaveChanges,
              (),
              None], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
              self.CloseByUser,
              (),
              None]], parent=self.main_cont, align=uiconst.TOTOP)

    def OnMainGridSizeChanged(self, width, height, *args, **kwds):
        self.SetMinSize([width + 12, height + self.headerText.height + 110], refresh=1)

    def _on_main_cont_size_changed(self):
        _, height = self.GetWindowSizeForContentSize(height=self.main_cont.height)
        self.SetMinSize(size=(self.GetMinWidth(), height), refresh=True)

    def _on_main_grid_size_changed(self, width, height):
        width, _ = self.GetWindowSizeForContentSize(width=width)
        self.SetMinSize(size=(width, self.GetMinHeight()), refresh=True)

    def SaveChanges(self, *args):
        totalAttrs = 0
        newAttributes = {}
        for x in xrange(0, 5):
            newAttributes[self.attributes[x]] = const.respecMinimumAttributeValue + self.respecBar[x].GetValue()

        for attrValue in newAttributes.itervalues():
            if attrValue < const.respecMinimumAttributeValue:
                raise UserError('RespecAttributesTooLow')
            elif attrValue > const.respecMaximumAttributeValue:
                raise UserError('RespecAttributesTooHigh')
            totalAttrs += attrValue

        if totalAttrs != const.respecTotalRespecPoints or self.sr.unassignedBar.GetValue() > 0:
            self.sr.saveWarningText.state = uiconst.UI_DISABLED
            raise UserError('RespecAttributesMisallocated')
        allSame = True
        for attr in self.attributes:
            if int(self.currentAttributes[attr]) != int(newAttributes[attr]):
                allSame = False
                break

        if not allSame:
            respecInfo = sm.GetService('skills').GetRespecInfo()
            freeRespecs = respecInfo['freeRespecs']
            if respecInfo['nextTimedRespec'] is None or respecInfo['nextTimedRespec'] <= blue.os.GetWallclockTime():
                if eve.Message('ConfirmRespec2', {'months': int(const.respecTimeInterval / const.MONTH30)}, uiconst.YESNO) != uiconst.ID_YES:
                    return
            elif freeRespecs > 0:
                if eve.Message('ConfirmRespecFree', {'freerespecs': int(respecInfo['freeRespecs']) - 1}, uiconst.YESNO) != uiconst.ID_YES:
                    return
            else:
                raise UserError('RespecTooSoon', {'nextTime': respecInfo['nextTimedRespec']})
            self.skillHandler.RespecCharacter(newAttributes)
        self.CloseByUser()

    def IncreaseAttribute(self, attribute, *args):
        if self.respecBar[attribute].GetValue() >= const.respecMaximumAttributeValue - const.respecMinimumAttributeValue:
            return
        if self.unspentPts <= 0:
            raise UserError('RespecCannotIncrementNotEnoughPoints')
        if not self.respecBar[attribute].Increment():
            raise UserError('RespecAttributesTooHigh')

    def DecreaseAttribute(self, attribute, *args):
        if self.respecBar[attribute].GetValue() <= 0:
            return
        if not self.respecBar[attribute].Decrement():
            raise UserError('RespecAttributesTooLow')

    def ValidateBoxClick(self, oldValue, newValue):
        if self.readOnly:
            return False
        if oldValue >= newValue:
            return True
        if self.unspentPts < newValue - oldValue:
            return False
        return True

    def OnMemberBoxClick(self, oldValue, newValue):
        if oldValue is None or oldValue == newValue:
            return
        if self.readOnly:
            return
        self.unspentPts -= newValue - oldValue
        self.sr.unassignedBar.SetValue(self.unspentPts)
        unspentPtsText = localization.formatters.FormatNumeric(self.unspentPts, decimalPlaces=0)
        self.availableLabel.text = unspentPtsText
        for x in xrange(0, 5):
            totalPts = const.respecMinimumAttributeValue + self.respecBar[x].GetValue() + self.implantModifier[x]
            totalPtsText = localization.formatters.FormatNumeric(int(totalPts), decimalPlaces=0)
            self.totalLabels[x].text = totalPtsText

        if self.unspentPts <= 0:
            self.sr.saveWarningText.state = uiconst.UI_HIDDEN


class AttributeRespecEntry(SE_BaseClassCore):
    __guid__ = 'listentry.AttributeRespec'
    default_showHilite = False

    def Startup(self, *args):
        self.OnSelectCallback = None
        self.sr.label = eveLabel.EveLabelSmall(parent=self, left=8, top=4, text=localization.GetByLabel('UI/Neocom/NextDNAModification'), maxLines=1)
        self.sr.respecTime = eveLabel.EveLabelMedium(parent=self, left=8, top=18, text='', maxLines=1)
        self.sr.numberOfRemaps = eveLabel.EveLabelMedium(parent=self, state=uiconst.UI_HIDDEN, left=8, top=38, text='', maxLines=1)
        self.sr.respecButton = Button(parent=self, label=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/RemapStatsNow'), align=uiconst.TOPRIGHT, func=self.OpenRespecWindow, args=(False,))
        self.hint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/CharacterSheetHint')

    def Load(self, node):
        self.sr.node = node
        freeRespecs = node.Get('freeRespecs', 0)
        nextRespecTime = node.Get('nextTimedRespec', None)
        canRemap = False
        if nextRespecTime is None or nextRespecTime <= blue.os.GetWallclockTime():
            self.sr.respecTime.text = localization.GetByLabel('UI/Generic/Now')
            canRemap = True
        else:
            self.sr.respecTime.text = FmtDate(node.nextTimedRespec)
            self.refreshThread = uthread.new(self.RefreshThread)
        if freeRespecs > 0:
            canRemap = True
            lbl = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/BonusRemapsAvailable', remapsAvailable=freeRespecs)
            self.sr.numberOfRemaps.text = lbl
            if nextRespecTime is not None and nextRespecTime > blue.os.GetWallclockTime():
                self.hint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/CharacterSheetHintFree')
            else:
                self.hint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/CharacterSheetHintFreeTimed')
            self.sr.numberOfRemaps.state = uiconst.UI_DISABLED
        if not canRemap:
            self.sr.respecButton.SetLabel(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/AttributesOverview'))
            self.sr.respecButton.args = (True,)

    def OpenRespecWindow(self, readOnly, *args):
        wnd = AttributeRespecWindow.GetIfOpen()
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
        else:
            AttributeRespecWindow.Open(readOnly=readOnly)

    def RefreshThread(self):
        if not self or self.destroyed:
            return
        sleepMsec = max(self.sr.node.nextTimedRespec - blue.os.GetWallclockTime(), 0) / 10000L
        sleepMsec = min(sleepMsec, 60000)
        while sleepMsec > 0:
            blue.pyos.synchro.SleepWallclock(sleepMsec)
            if not self or self.destroyed:
                return
            sleepMsec = max(self.sr.node.nextTimedRespec - blue.os.GetWallclockTime(), 0) / 10000L
            sleepMsec = min(sleepMsec, 60000)

        if not self or self.destroyed:
            return
        self.sr.respecButton.state = uiconst.UI_NORMAL
        self.sr.respecTime.text = localization.GetByLabel('UI/Generic/Now')
