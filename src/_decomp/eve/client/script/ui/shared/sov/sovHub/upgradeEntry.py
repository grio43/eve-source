#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\upgradeEntry.py
from collections import OrderedDict
import carbonui
import eveicon
import evetypes
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.dragdrop.dragdata import TypeDragData
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.various_unsorted import GetAttrs
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
import carbonui.const as uiconst
from eve.client.script.ui.control.toggleSwitch import ToggleSwitchCompact
from eveexceptions import ExceptionEater
from eveservices.menu import GetMenuService
from localization import GetByLabel
from carbonui.uicore import uicore
SPRITE_SIZE = 12
MOVE_SPRITE_SIZE = 16
AVAILABLE_WIDTH = 430

class ColumnInfo(object):

    def __init__(self, labelPath, hintPath, useMinWidth = True):
        self._labelPath = labelPath
        self._hintPath = hintPath
        self._useMinWidth = useMinWidth

    @property
    def columnText(self):
        if self._labelPath > 0:
            return GetByLabel(self._labelPath)
        else:
            return ' ' * abs(self._labelPath)

    @property
    def hintText(self):
        if self._hintPath:
            return GetByLabel(self._hintPath)

    @property
    def useMinWidth(self):
        return self._useMinWidth


class UpgradeEntry(BaseListEntryCustomColumns):
    default_name = 'UpgradeEntry'
    isDragObject = True
    default_height = 24
    headerInfo = d = OrderedDict()
    d['priority'] = ColumnInfo('UI/Sovereignty/SovHub/HubWnd/ColumnPriority', 'Tooltips/StructureUI/SovHubPriority')
    d['upgrade'] = ColumnInfo('UI/Sovereignty/SovHub/HubWnd/ColumnUpgrade', 'Tooltips/StructureUI/SovHubInstalledUpgrades', False)
    d['power'] = ColumnInfo('UI/Sovereignty/SovHub/HubWnd/ColumnPowerAllocation', 'Tooltips/StructureUI/SovHubAllocation')
    d['workforce'] = ColumnInfo('UI/Sovereignty/SovHub/HubWnd/ColumnWorkforceAllocation', 'Tooltips/StructureUI/SovHubAllocation')
    d['upkeep'] = ColumnInfo('UI/Sovereignty/SovHub/HubWnd/ColumnUpkeep', 'Tooltips/StructureUI/SovHubUpkeep')
    d['startup'] = ColumnInfo('UI/Sovereignty/SovHub/HubWnd/ColumnStartupCost', 'Tooltips/StructureUI/SovHubStartup')
    d['gauge'] = ColumnInfo(-1, None)
    d['state'] = ColumnInfo('UI/Sovereignty/SovHub/HubWnd/ColumnState', 'Tooltips/StructureUI/SovHubState')
    d['trash'] = ColumnInfo(-2, None)

    def ApplyAttributes(self, attributes):
        self._resourcesMissingFill = None
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.posIndicatorLine = PosIndicatorLine(parent=self, align=uiconst.TOTOP_NOPUSH, height=3)
        self.entryController = self.node.entryController
        self.hubController = self.node.hubController
        self.AddAnchoredIcons()
        self.AddPriority()
        self.AddUpgradeName()
        self.AddPowerAllocation()
        self.AddWorkForceAllocation()
        self.AddUpkeep()
        self.AddStartup()
        self.AddStateGauge()
        self.AddOnlineState()
        self.UpdateOnlineState()
        self.AddTrashColumn()
        self.UpdateEffectiveState()

    def AddAnchoredIcons(self):
        self.moveSprite = Sprite(parent=self, align=carbonui.Align.CENTERLEFT, pos=(0,
         0,
         MOVE_SPRITE_SIZE,
         MOVE_SPRITE_SIZE), texturePath=eveicon.caret_up_down, pickState=carbonui.PickState.ON, hint=GetByLabel('UI/Sovereignty/SovHub/Upgrades/MoveUpgrades'), color=eveColor.TUNGSTEN_GREY)
        self.moveSprite.GetDragData = self.GetDragData
        self.moveSprite.isDragObject = True
        self.moveSprite.Hide()
        self.deleteSprite = ButtonIcon(parent=self, align=carbonui.Align.CENTERRIGHT, width=16, height=16, iconSize=16, texturePath=self.entryController.GetRemoveTexturePath(), hint=GetByLabel('UI/Sovereignty/SovHub/Upgrades/DeleteUpgrade'), func=self.entryController.DeleteUpgrade)
        self.deleteSprite.Hide()

    def AddPriority(self):
        self.priortyCol = self.AddColumnContainer()
        self.priorityLabel = carbonui.TextBody(name='priorityLabel', parent=self.priortyCol, text=self.entryController.priorityText, align=carbonui.Align.CENTERRIGHT, left=SPRITE_SIZE + 8)

    def AddUpgradeName(self):
        self.upgradeNameCol = self.AddColumnContainer()
        self.groupSprite = Sprite(parent=self.upgradeNameCol, align=carbonui.Align.CENTERLEFT, pos=(0,
         0,
         SPRITE_SIZE,
         SPRITE_SIZE), texturePath=self.entryController.typeListTexture, color=eveColor.TUNGSTEN_GREY)
        self.upgradeNameLabel = carbonui.TextBody(name='upgradeName', parent=self.upgradeNameCol, text=self.entryController.name, align=carbonui.Align.CENTERLEFT, left=SPRITE_SIZE + 8)

    def AddPowerAllocation(self):
        self.powerCol = self.AddColumnContainer()
        self.powerSprite = Sprite(parent=self.powerCol, align=carbonui.Align.CENTERLEFT, pos=(0,
         0,
         SPRITE_SIZE,
         SPRITE_SIZE), texturePath=eveicon.power, color=eveColor.TUNGSTEN_GREY)
        self.powerLabel = carbonui.TextBody(name='powerLabel', parent=self.powerCol, text=self.entryController.powerText, align=carbonui.Align.CENTERLEFT, left=self.powerSprite.width)

    def AddWorkForceAllocation(self):
        self.workforceCol = self.AddColumnContainer()
        self.workforceSprite = Sprite(parent=self.workforceCol, align=carbonui.Align.CENTERLEFT, pos=(0,
         0,
         SPRITE_SIZE,
         SPRITE_SIZE), texturePath=eveicon.workforce, color=eveColor.TUNGSTEN_GREY)
        self.workforceLabel = carbonui.TextBody(name='workforceLabel', parent=self.workforceCol, text=self.entryController.workforceText, align=carbonui.Align.CENTERLEFT, left=self.workforceSprite.width)

    def AddUpkeep(self):
        self.upkeepCol = self.AddColumnContainer()
        fuelTexturePath = self.entryController.fuelTexturePath
        self.uppkeepSprite = Sprite(parent=self.upkeepCol, align=carbonui.Align.CENTERLEFT, pos=(uiconst.LABELTABMARGIN,
         0,
         SPRITE_SIZE,
         SPRITE_SIZE), texturePath=fuelTexturePath, color=eveColor.TUNGSTEN_GREY)
        self.uppkeepSprite.hint = evetypes.GetName(self.entryController.fuelTypeID)
        self.upkeepLabel = carbonui.TextBody(name='upkeepLabel', parent=self.upkeepCol, text=self.entryController.upkeepText, align=carbonui.Align.CENTERLEFT, left=self.uppkeepSprite.left + self.uppkeepSprite.width)

    def AddOnlineState(self):
        self.onlineStateCol = self.AddColumnContainer()
        self.onlineStateLabel = carbonui.TextBody(name='upkeepLabel', parent=self.onlineStateCol, text='', align=carbonui.Align.CENTERLEFT, left=uiconst.LABELTABMARGIN)
        self.onlineStateLabel.pickState = carbonui.PickState.ON

    def AddStartup(self):
        self.startupCol = self.AddColumnContainer()
        fuelTexturePath = self.entryController.fuelTexturePath
        self.startupSprite = Sprite(parent=self.startupCol, align=carbonui.Align.CENTERLEFT, pos=(uiconst.LABELTABMARGIN,
         0,
         SPRITE_SIZE,
         SPRITE_SIZE), texturePath=fuelTexturePath, color=eveColor.TUNGSTEN_GREY)
        self.startupSprite.hint = evetypes.GetName(self.entryController.fuelTypeID)
        self.startupLabel = carbonui.TextBody(name='startupLabel', parent=self.startupCol, text=self.entryController.startupText, align=carbonui.Align.CENTERLEFT, left=self.startupSprite.left + self.startupSprite.width)

    def AddStateGauge(self):
        col = self.AddColumnContainer()
        self.onlineToggle = ToggleSwitchCompact(parent=col, checked=self.entryController.isConfiguredOnline, align=carbonui.Align.CENTER)
        self.onlineToggle.on_switch_changed.connect(self.ChangeOnlineState)

    def ConstructResourcesMissingFill(self):
        if not self._resourcesMissingFill or self._resourcesMissingFill.destroyed:
            self._resourcesMissingFill = Fill(name='_resourcesMissingFill', bgParent=self, color=eveColor.DANGER_RED[:3] + (0.0,))

    def OnColumnResize(self, newCols):
        for i, width in enumerate(newCols):
            self.columns[i].width = width - 1

    @classmethod
    def GetHeaders(cls):
        return [ x.columnText for x in cls.headerInfo.itervalues() ]

    @classmethod
    def GetHeaderText(cls, i):
        key = cls.headerInfo.keys()[i]
        headerInfo = cls.headerInfo[key]
        return headerInfo.columnText

    @classmethod
    def GetHeadersHint(cls, i):
        key = cls.headerInfo.keys()[i]
        headerInfo = cls.headerInfo[key]
        return headerInfo.hintText

    def GetDragData(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)
        dragData = [UpgradeTypeDragData(self.sr.node.typeID, self.sr.node.idx)]
        return dragData

    def OnMouseEnter(self, *args):
        showRed = self.entryController.installedUpgradeData.isInRestrictedPowerState
        self._showHilite = not showRed
        super(UpgradeEntry, self).OnMouseEnter(args)
        self.moveSprite.Show()
        self.deleteSprite.Show()
        if showRed:
            self.UpdateResourcesMissingFill(True)

    def OnMouseExit(self, *args):
        self._showHilite = True
        super(UpgradeEntry, self).OnMouseExit(args)
        self.moveSprite.Hide()
        self.deleteSprite.Hide()
        self.UpdateResourcesMissingFill(False)

    def OnDropData(self, dragObj, nodes, *args):
        self.posIndicatorLine.HidePosIndicator()
        if GetAttrs(self, 'parent', 'OnDropData'):
            self.parent.OnDropData(dragObj, nodes, idx=self.sr.node.idx)

    def OnDragEnter(self, dragObj, nodes, *args):
        dropError = self.hubController.GetDropError(nodes[0])
        if dropError:
            color = eveColor.DANGER_RED
        else:
            color = eveColor.ICE_WHITE
        self.posIndicatorLine.ShowPosIndicator(color)

    def OnDragExit(self, *args):
        self.posIndicatorLine.HidePosIndicator()

    def UpdateResourcesMissingFill(self, on):
        if on:
            self.ConstructResourcesMissingFill()
            animations.FadeIn(self._resourcesMissingFill, endVal=0.1)
        else:
            if not self._resourcesMissingFill or self._resourcesMissingFill.destroyed:
                return
            animations.FadeOut(self._resourcesMissingFill)

    def ChangeOnlineState(self, *args):
        newState = not self.entryController.isConfiguredOnline
        self.hubController.SetOnlineState(self.entryController.typeID, newState)

    def UpdateOnlineState(self):
        if self.entryController.isConfiguredOnline:
            self.onlineToggle.SetChecked(True, False)
        else:
            self.onlineToggle.SetChecked(False, False)
        if self.entryController.isPowerStateFunctional:
            newOpacity = 1.0
        else:
            newOpacity = 0.5
        for element in [self.priortyCol,
         self.upgradeNameCol,
         self.powerCol,
         self.workforceCol,
         self.upkeepCol,
         self.startupCol,
         self.onlineStateCol]:
            element.opacity = newOpacity

    def AddTrashColumn(self):
        col = self.AddColumnContainer()

    def UpdateEffectiveState(self):
        text, hint = self.entryController.GetOnlineStateTextAndHints()
        self.onlineStateLabel.text = text
        self.onlineStateLabel.hint = hint
        entryTextColor = self.entryController.GetEntryTextColor()
        self.priorityLabel.SetRGBA(*entryTextColor)
        self.groupSprite.SetRGBA(*entryTextColor)
        self.upgradeNameLabel.SetRGBA(*entryTextColor)
        self.priorityLabel.SetRGBA(*entryTextColor)
        self.powerSprite.SetRGBA(*self.entryController.GetPowerColor(eveColor.TUNGSTEN_GREY))
        self.powerLabel.SetRGBA(*self.entryController.GetPowerColor())
        self.workforceSprite.SetRGBA(*self.entryController.GetWorkforceColor(eveColor.TUNGSTEN_GREY))
        self.workforceLabel.SetRGBA(*self.entryController.GetWorkforceColor())
        self.uppkeepSprite.SetRGBA(*self.entryController.GetReagentColor(eveColor.TUNGSTEN_GREY))
        self.upkeepLabel.SetRGBA(*self.entryController.GetReagentColor())
        self.startupSprite.SetRGBA(*self.entryController.GetReagentStartupColor(eveColor.TUNGSTEN_GREY))
        self.startupLabel.SetRGBA(*self.entryController.GetReagentStartupColor())

    def GetMenu(self):
        typeID = self.entryController.typeID
        itemID = self.entryController.itemID
        return GetMenuService().GetMenuFromItemIDTypeID(itemID, typeID, includeMarketDetails=True)

    @staticmethod
    def GetColWidths(node, idx = None):
        if node.decoClass != UpgradeEntry:
            return
        LABEL_PARAMS = (EVE_MEDIUM_FONTSIZE, 0, 0)
        controller = node.entryController

        def GetWidthFor(idx):
            if idx == 0:
                return 16 + uicore.font.MeasureTabstops([(controller.priorityText,) + LABEL_PARAMS])[0]
            if idx == 1:
                return SPRITE_SIZE + 8 + uicore.font.MeasureTabstops([(controller.name,) + LABEL_PARAMS])[0]
            if idx == 2:
                return SPRITE_SIZE + uicore.font.MeasureTabstops([(controller.powerText,) + LABEL_PARAMS])[0]
            if idx == 3:
                return SPRITE_SIZE + uicore.font.MeasureTabstops([(controller.workforceText,) + LABEL_PARAMS])[0]
            if idx == 4:
                return SPRITE_SIZE + uicore.font.MeasureTabstops([(controller.upkeepText,) + LABEL_PARAMS])[0]
            if idx == 5:
                return SPRITE_SIZE + uicore.font.MeasureTabstops([(controller.startupText,) + LABEL_PARAMS])[0]
            if idx == 6:
                return 40
            if idx == 7:
                text, _ = controller.GetOnlineStateTextAndHints()
                return uicore.font.MeasureTabstops([(text,) + LABEL_PARAMS])[0]
            if idx == 8:
                return 20
            return 50

        if idx is None:
            colWidths = [ GetWidthFor(i) for i in xrange(len(UpgradeEntry.headerInfo)) ]
            return colWidths
        return [GetWidthFor(idx)]

    def Close(self):
        with ExceptionEater('Closing UpgradeEntry'):
            self.onlineToggle.on_switch_changed.disconnect(self.ChangeOnlineState)
            self.entryController = None
            self.hubController = None
        super(UpgradeEntry, self).Close()


class PosIndicatorLine(Container):

    def ApplyAttributes(self, attributes):
        super(PosIndicatorLine, self).ApplyAttributes(attributes)
        self.line = None

    def CheckConstructPosIndicatorLine(self):
        if not self.line:
            self.line = Line(parent=self, align=uiconst.TOTOP_NOPUSH, weight=2, state=uiconst.UI_DISABLED, opacity=0.0, idx=0)

    def ShowPosIndicator(self, color = None):
        self.CheckConstructPosIndicatorLine()
        color = color or eveColor.ICE_WHITE
        self.line.SetRGBA(*color)

    def HidePosIndicator(self):
        if self.line:
            self.line.opacity = 0.0


class UpgradeTypeDragData(TypeDragData):

    def __init__(self, typeID, idx):
        super(UpgradeTypeDragData, self).__init__(typeID)
        self.idx = idx


class UpgradeLastEntry(SE_BaseClassCore):
    __guid__ = 'UpgradeLastEntry'
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.posIndicator = PosIndicatorLine(parent=self)

    def Load(self, node):
        pass

    def ShowIndicator(self, color):
        self.posIndicator.ShowPosIndicator(color)

    def HideIndicator(self):
        self.posIndicator.HidePosIndicator()

    def GetDynamicHeight(self, width):
        return 2
