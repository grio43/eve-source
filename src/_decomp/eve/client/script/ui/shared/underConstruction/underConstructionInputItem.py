#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\underConstruction\underConstructionInputItem.py
import itertools
import evetypes
import mathext
from carbonui import TextColor, TextAlign
from carbonui import const as uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.common.script.util.eveFormat import FmtLP, FmtISK
from eveservices.menu import GetMenuService
from localization import GetByLabel

class InputItemController(object):

    def __init__(self, typeID, neededQty, iskRewards, lpRewards, isSelected = False):
        self.typeID = typeID
        self.neededQty = neededQty
        self.iskRewards = iskRewards
        self.lpRewards = lpRewards
        self.isSelected = isSelected
        self.qtyInCargo = 0
        self.unitsInContainer = 0
        self.currentValueIfSelected = 0
        self.isCompleted = False

    @property
    def maxToAdd(self):
        maxToAdd = max(0, min(self.qtyInCargo, self.neededQty - self.unitsInContainer))
        return maxToAdd


class UnderConstructionInputScrollEntry(SE_BaseClassCore):
    default_state = uiconst.UI_NORMAL
    default_padLeft = 2

    def ApplyAttributes(self, attributes):
        super(UnderConstructionInputScrollEntry, self).ApplyAttributes(attributes)
        self.inputItemController = attributes.itemController
        self.inputChangedCallback = attributes.inputChangedCallback
        qtyInCargo = attributes.qtyInCargo
        paddingValue = attributes.paddingValue
        self.ConstructLine()
        self.inputCont = None
        self.inputCont = UnderConstructionInputItem(parent=self, itemController=self.inputItemController, inputFieldChangedCallback=self.OnInputFieldChanged, qtyInCargo=qtyInCargo, callback=self.UpdateSize, paddingValue=paddingValue)

    def ConstructLine(self):
        lineWidth = 2
        lineCont = Container(parent=self, name='lineCont', align=uiconst.TOLEFT, width=lineWidth, left=-lineWidth, padBottom=1)
        self.leftLine = Line(parent=lineCont, align=uiconst.TOLEFT, weight=lineWidth, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, color=eveColor.WHITE, glowBrightness=0.5)
        self.leftLine.Hide()

    def UpdateEntry(self, unitsInContainer, qtyInCargo):
        self.inputItemController.unitsInContainer = unitsInContainer
        self.inputItemController.qtyInCargo = qtyInCargo
        self.RefreshUI()

    def RefreshUI(self):
        self.RefreshNumbers()
        self.UpdateEnabledLook()

    def UpdateCompletedState(self):
        if self.inputItemController.unitsInContainer >= self.inputItemController.neededQty:
            self.inputItemController.isCompleted = True
        else:
            self.inputItemController.isCompleted = False

    def RefreshNumbers(self):
        self.UpdateCompletedState()
        qtyInCargo = self.inputItemController.qtyInCargo
        maxToAdd = self.inputItemController.maxToAdd
        self.inputCont.inputEdit.SetMaxValue(maxToAdd)
        if not qtyInCargo or self.inputItemController.isCompleted:
            self.inputItemController.isSelected = False
        self.inputCont.RefreshNumbers()
        self.inputCont.UpdateGaugeProgress()

    def UpdateSize(self, *args):
        if self.inputCont:
            self.height = self.inputCont.height

    def UpdateEnabledLook(self):
        if self.inputItemController.isSelected:
            self.Select()
        else:
            self.Deselect()
        if self.inputItemController.isCompleted or self.inputItemController.qtyInCargo:
            self.opacity = 1.0
        else:
            self.opacity = 0.25
        self.UpdateLine()
        self.inputCont.UpdateInputHint()

    def OnClick(self, *args):
        if self.inputItemController.isCompleted:
            if self.inputItemController.isSelected:
                self.SetEntryDeselected()
                self.UpdateEnabledLook()
            return
        if not self.inputItemController.qtyInCargo:
            return
        if self.inputItemController.isSelected:
            self.SetEntryDeselected()
        else:
            self.SelectNonSelectedEntry()
        self.OnInputChanged()
        self.RefreshUI()

    def SetEntryDeselected(self):
        self.inputItemController.isSelected = False

    def SelectNonSelectedEntry(self):
        self.inputItemController.isSelected = True
        self.inputCont.UpdateEditFromSavedValue()

    def OnInputChanged(self):
        if self.inputChangedCallback:
            self.inputChangedCallback()

    def OnInputFieldChanged(self, *args):
        if self.inputCont.inputEdit.GetValue() and not self.inputItemController.isSelected:
            self.inputItemController.isSelected = True
        self.OnInputChanged()

    def GetInputQty(self):
        return self.inputCont.GetInputQty()

    def ShowHilite(self, animate = True):
        if self.inputItemController.isCompleted:
            return
        return super(UnderConstructionInputScrollEntry, self).ShowHilite(animate)

    def UpdateLine(self):
        if self.inputItemController.isSelected:
            self.leftLine.Show()
        else:
            self.leftLine.Hide()


class UnderConstructionInputItem(ContainerAutoSize):
    default_align = uiconst.TOTOP
    default_minHeight = 88
    default_alignMode = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        super(UnderConstructionInputItem, self).ApplyAttributes(attributes)
        self.inputItemController = attributes.itemController
        self.inputFieldChangedCallback = attributes.inputFieldChangedCallback
        self.paddingValue = attributes.paddingValue or 0
        qtyInCargo = attributes.qtyInCargo
        self.ConstructTypeIcon()
        self.ConstructInput(qtyInCargo)
        self.ConstructLabels()

    def ConstructTypeIcon(self):
        iconSize = 64
        gaugeSize = iconSize + 10
        leftCont = Container(parent=self, name='leftCont', align=uiconst.TOLEFT, width=gaugeSize, left=10)
        self.iconGaugeCont = IconGaugeCont(parent=leftCont, align=uiconst.CENTERLEFT, pos=(0,
         0,
         gaugeSize,
         gaugeSize), gaugeSize=gaugeSize, iconSize=iconSize, typeID=self.inputItemController.typeID)

    def ConstructInput(self, qtyInCargo):
        rightPad = self.paddingValue + 10
        rightCont = Container(parent=self, name='rightCont', align=uiconst.TORIGHT, width=100, left=rightPad)
        self.inputEdit = SingleLineEditInteger(parent=rightCont, width=100, OnChange=self.OnInputFieldChanged, setvalue=qtyInCargo, align=uiconst.CENTERRIGHT)
        self.successLabel = EveLabelMedium(parent=rightCont, align=uiconst.CENTER, text=GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/MaterialCompleted'), color=TextColor.SUCCESS)
        self.successLabel.display = False

    def ConstructLabels(self):
        textCont = ContainerAutoSize(parent=self, name='textCont', align=uiconst.TOTOP, padLeft=12)
        EveLabelMedium(parent=textCont, align=uiconst.TOTOP, text=evetypes.GetName(self.inputItemController.typeID), autoFadeSides=16, top=16)
        gridParent = ContainerAutoSize(parent=textCont, name='gridParent', align=uiconst.TOTOP, top=10, padBottom=10)
        grid = LayoutGrid(parent=gridParent, align=uiconst.TOPLEFT, columns=2, cellSpacing=(24, 0))
        lpRewardsText = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/LpPayout') if self.inputItemController.lpRewards else ''
        EveLabelMedium(parent=grid, text=lpRewardsText, color=TextColor.SECONDARY)
        iskRewardsText = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/IskPayout') if self.inputItemController.iskRewards else ''
        EveLabelMedium(parent=grid, text=iskRewardsText, color=TextColor.SECONDARY)
        iskList = [self.inputItemController.iskRewards] if self.inputItemController.iskRewards else []
        for lpCorpAndAmountt, iskValue in itertools.izip_longest(self.inputItemController.lpRewards.items(), iskList, fillvalue=None):
            if lpCorpAndAmountt:
                corpID, lpAmount = lpCorpAndAmountt
                lpText = FmtLP(lpAmount)
                lpHint = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/NumLpFromCorp', numLP=lpAmount, corpName=cfg.eveowners.Get(corpID).name)
                labelState = uiconst.UI_NORMAL
            else:
                lpText = ''
                lpHint = ''
                labelState = uiconst.UI_DISABLED
            lpLabel = EveLabelMedium(parent=grid, text=lpText, state=labelState)
            lpLabel.hint = lpHint
            if iskValue:
                iskText = FmtISK(iskValue)
            else:
                iskText = ''
            EveLabelMedium(parent=grid, text=iskText)

    def RefreshNumbers(self):
        maxToAdd = self.inputItemController.maxToAdd
        self.inputEdit.SetMaxValue(maxToAdd)
        if self.inputItemController.isCompleted:
            self.inputEdit.SetValue(0, False)
            self.inputEdit.Hide()
            self.successLabel.display = True
        else:
            self.inputEdit.Show()
            self.successLabel.display = False
            if self.inputItemController.isSelected:
                value = self.GetInputQty()
                self.inputItemController.currentValueIfSelected = min(value, maxToAdd)
                if value > maxToAdd:
                    self.inputEdit.SetValue(maxToAdd, False)
            else:
                self.inputEdit.SetValue(0, False)

    def UpdateGaugeProgress(self):
        unitsInWnd = self.GetInputQty()
        self.iconGaugeCont.SetProgress(self.inputItemController.unitsInContainer, self.inputItemController.neededQty, unitsInWnd)

    def GetInputQty(self):
        if self.inputItemController.isSelected:
            return self.inputEdit.GetValue()
        return 0

    def OnInputFieldChanged(self, *args):
        if self.inputFieldChangedCallback:
            self.inputFieldChangedCallback(*args)

    def UpdateInputHint(self):
        if self.inputItemController.qtyInCargo:
            hint = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/NumUnitsInCargo', qty=self.inputItemController.qtyInCargo)
        else:
            hint = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/NoSuchItemInCargo')
        self.inputEdit.hint = hint

    def UpdateEditFromSavedValue(self):
        self.inputEdit.SetValue(self.inputItemController.currentValueIfSelected, False)


class IconGaugeCont(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(IconGaugeCont, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        iconSize = attributes.iconSize
        gaugeSize = attributes.gaugeSize
        self.progressLabel = EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, text='', textAlign=TextAlign.CENTER)
        self.progressLabel.Hide()
        self.progressLabel.maxWidth = iconSize + 8
        self.typeCont = Container(parent=self, name='typeCont', align=uiconst.CENTER, pos=(0,
         0,
         iconSize,
         iconSize))
        typeIcon = Sprite(parent=self.typeCont, name='typeIcon', align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, pos=(0,
         0,
         iconSize,
         iconSize))
        sm.GetService('photo').GetIconByType(typeIcon, self.typeID)
        gaugeCont = Container(parent=self, name='gaugeCont', pos=(0,
         0,
         gaugeSize,
         gaugeSize), align=uiconst.CENTERRIGHT)
        self.gauge = GaugeCircular(parent=gaugeCont, colorStart=eveColor.CRYO_BLUE, colorEnd=eveColor.CRYO_BLUE, radius=gaugeSize / 2, align=uiconst.CENTER, state=uiconst.UI_DISABLED, colorBg=(0, 0, 0, 0), showMarker=False)
        self.inWndGauge = GaugeCircular(parent=gaugeCont, radius=gaugeSize / 2, colorStart=eveColor.SILVER_GREY, colorEnd=eveColor.SILVER_GREY, align=uiconst.CENTER, state=uiconst.UI_DISABLED, showMarker=False)

    def OnClick(self, *args):
        return sm.GetService('info').ShowInfo(self.typeID)

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(None, self.typeID)

    def SetProgress(self, unitsInContainer, neededQty, unitsInWnd):
        progress = float(unitsInContainer) / neededQty if neededQty else 0
        self.gauge.SetValue(progress)
        progressText = GetByLabel('UI/Inflight/SpaceComponents/UnderConstruction/ItemProgressUnits', currentQty=unitsInContainer, requiredQty=neededQty)
        self.progressLabel.SetText(progressText)
        progressWithInput = mathext.clamp(float(unitsInContainer + unitsInWnd) / neededQty if neededQty else 0, 0, 1)
        self.inWndGauge.SetValue(progressWithInput)
        if unitsInContainer == neededQty:
            if self.gauge.colorStart != eveColor.SUCCESS_GREEN or self.gauge.colorEnd != eveColor.SUCCESS_GREEN:
                self.gauge.SetColor(eveColor.SUCCESS_GREEN, eveColor.SUCCESS_GREEN)

    def OnMouseEnter(self, *args):
        self.progressLabel.Show()
        self.typeCont.opacity = 0.25

    def OnMouseExit(self, *args):
        self.progressLabel.Hide()
        self.typeCont.opacity = 1.0
