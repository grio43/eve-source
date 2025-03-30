#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\changesWarning.py
import carbonui
import eveformat
import eveicon
import evetypes
import mathext
from carbonui import TextColor
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from localization import GetByLabel
from sovereignty.client.sovHub.hubUtil import GetPowerStateNameFromState, GetIconTexturePathForReagent
from sovereignty.client.sovHub.upgradeChanges import GetChanges, GetPriorityChanges, GetStartupCost
from sovereignty.upgrades.const import POWER_STATE_OFFLINE, POWER_STATE_ONLINE

def LoadSaveBtnTooltipPanel(tooltipPanel, hubController):
    tooltipPanel.columns = 1
    content = _GetTooltipContent(hubController.installedUpgradesSimulated, hubController.originalInstalledUpgradeData, tooltipPanel)
    tooltipPanel.LoadStandardSpacing()
    if content is None:
        hint = GetByLabel('UI/Sovereignty/SovHub/HubWnd/NoChangesToSave')
        tooltipPanel.AddLabelMedium(text=hint, wrapWidth=240)
        return
    tooltipPanel.margin = (8, 16, 8, 16)


def _GetTooltipContent(currentUpgrades, originalUpgrades, parent):
    changesInOnline, newlyAdded, powerStateChanges = GetChanges(currentUpgrades, originalUpgrades, False)
    priorityChanges = GetPriorityChanges(currentUpgrades, originalUpgrades)
    if not changesInOnline and not newlyAdded and not powerStateChanges and not priorityChanges:
        return
    newlyPowerStateByTypeID = {x[0]:x[1] for x in newlyAdded}
    powerStateChangesByTypeID = {x[0]:x for x in powerStateChanges}
    priorityChangesByTypeID = {x[0]:x for x in priorityChanges}
    layoutGrid = LayoutGrid(parent=parent, columns=4, cellPadding=(8, 0), cellSpacing=(0, 8))
    for idx, nUpgrade in enumerate(currentUpgrades):
        nTypeID = nUpgrade.typeID
        stateTextList = []
        if nTypeID in newlyPowerStateByTypeID:
            powerState = newlyPowerStateByTypeID[nTypeID]
            stateTextList = ['New,', GetPowerStateText(powerState)]
        elif nTypeID in powerStateChangesByTypeID:
            _, oldState, newState = powerStateChangesByTypeID[nTypeID]
            stateTextList = [GetPowerStateText(oldState), u'\u2192', GetPowerStateText(newState)]
        prioChange = priorityChangesByTypeID.get(nTypeID, None)
        diffText, texturePath = GetDiffTextAndTexturePath(prioChange)
        if texturePath:
            sprite = Sprite(parent=layoutGrid, name='arrowSprite', align=carbonui.Align.CENTERLEFT, pos=(0, 0, 16, 16), texturePath=texturePath, color=eveColor.TUNGSTEN_GREY)
            carbonui.TextCustom(text=diffText, parent=sprite.parent, left=-5, align=carbonui.Align.CENTERLEFT, color=TextColor.SECONDARY, fontsize=10)
        else:
            layoutGrid.AddCell()
        carbonui.TextBody(text=idx + 1, parent=layoutGrid, align=carbonui.Align.CENTERLEFT)
        carbonui.TextBody(text=evetypes.GetName(nTypeID), parent=layoutGrid, align=carbonui.Align.CENTERLEFT)
        text = ' '.join(stateTextList)
        carbonui.TextBody(text=text, parent=layoutGrid, align=carbonui.Align.CENTERLEFT)

    startupCosts = GetStartupCost(currentUpgrades, originalUpgrades)
    added = False
    for typeID, cost in startupCosts:
        if added:
            text = ''
        else:
            label = carbonui.TextBody(text=' ', align=carbonui.Align.CENTERLEFT)
            layoutGrid.AddCell(label, colSpan=layoutGrid.columns)
            text = GetByLabel('UI/Sovereignty/SovHub/HubWnd/ColumnStartupCost')
        label = carbonui.TextBody(text=text, align=carbonui.Align.CENTERLEFT)
        layoutGrid.AddCell(label, colSpan=layoutGrid.columns - 1)
        cont = ContainerAutoSize(align=carbonui.Align.CENTERRIGHT)
        Sprite(parent=cont, name='reagentSprite', align=carbonui.Align.CENTERLEFT, pos=(0, 0, 16, 16), texturePath=GetIconTexturePathForReagent(typeID), color=eveColor.TUNGSTEN_GREY)
        carbonui.TextBody(parent=cont, text=cost, left=16, align=carbonui.Align.CENTERLEFT)
        layoutGrid.AddCell(cont, colSpan=layoutGrid.columns)
        added = True

    return layoutGrid


def GetDiffTextAndTexturePath(prioChange):
    texturePath = None
    diffText = ''
    if prioChange:
        _, beforeIdx, afterIdx = prioChange
        diff = afterIdx - beforeIdx
        if diff > 0:
            texturePath = eveicon.chevron_down
        elif diff < 0:
            texturePath = eveicon.chevron_up
        diffText = beforeIdx + 1
    return (diffText, texturePath)


def GetPowerStateText(powerState):
    powerStateName = GetPowerStateNameFromState(powerState)
    if powerState == POWER_STATE_ONLINE:
        return powerStateName
    if powerState == POWER_STATE_OFFLINE:
        return eveformat.color(powerStateName, eveColor.GUNMETAL_HEX)
    return eveformat.color(powerStateName, eveColor.DANGER_RED)


class ConfirmSovHubChanges(ScrollContainer):
    default_align = carbonui.Align.TOALL
    setWidth = True

    def ApplyAttributes(self, attributes):
        self._contentWidth = 0
        self._contentHeight = 0
        super(ConfirmSovHubChanges, self).ApplyAttributes(attributes)
        self.align = carbonui.Align.TOALL
        currentUpgrades = attributes.messageData['currentUpgrades']
        originalUpgrades = attributes.messageData['originalUpgrades']
        content = _GetTooltipContent(currentUpgrades, originalUpgrades, self)
        self._contentWidth, self._contentHeight = content.GetAbsoluteSize()

    def GetContentHeight(self):
        return mathext.clamp(self._contentHeight, 100, 300)

    def GetContentWidth(self):
        return mathext.clamp(self._contentWidth + 20, 300, 600)
