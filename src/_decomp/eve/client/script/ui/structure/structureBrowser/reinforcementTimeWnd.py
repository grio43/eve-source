#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\reinforcementTimeWnd.py
import gametime
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.primitives.container import Container
import carbonui.uiconst as uiconst
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.window import Window
from eve.client.script.ui.structure.deployment.deploymentCont import ReinforcementTimeCont
from eve.client.script.ui.structure.structureBrowser.controllers.reinforceTimersBundle import GetDayAndHourText
from localization import GetByLabel

class ReinforcementTimeWnd(Window):
    default_caption = 'UI/StructureBrowser/SetReinforcementTime'
    default_windowID = 'ReinforcementTimeWnd'
    default_width = 285
    default_height = 290
    default_minSize = (285, 290)
    default_left = '__center__'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.infoOnStructures = attributes.infoOnStructures
        mainCont = Container(parent=self.sr.main, padding=6, clipChildren=True)
        self.headerText = EveLabelMedium(name='headerText', parent=mainCont, align=uiconst.TOTOP, text='', state=uiconst.UI_NORMAL, padLeft=4)
        self.headerText.LoadTooltipPanel = self.LoadLabelTooltipPanel
        self.headerText.structureIDs = None
        text = GetByLabel('UI/StructureBrowser/ReinforcementTimeChangeDelay')
        self.delayText = EveLabelMedium(name='delayText', parent=mainCont, align=uiconst.TOTOP, text=text, state=uiconst.UI_NORMAL, padLeft=4)
        structureTypeIDs = self.GetStructureTypeIDs()
        self.reinforceTimeCont = ReinforcementTimeCont(parent=mainCont, name='reinforceTimeCont', align=uiconst.TOTOP, structureTypeIDs=structureTypeIDs)
        self.bottomText = EveLabelMedium(name='bottomText', parent=mainCont, align=uiconst.TOTOP, text='', state=uiconst.UI_NORMAL, padLeft=4, padTop=10)
        self.bottomTextTimes = EveLabelMedium(name='bottomTextTimes', parent=mainCont, align=uiconst.TOTOP, text='', state=uiconst.UI_NORMAL, padLeft=4)
        self.buttons = ButtonGroup(parent=self.sr.main, idx=0)
        self.buttons.AddButton(GetByLabel('UI/Commands/Apply'), self.ApplyChanges)
        self.buttons.AddButton(GetByLabel('UI/Commands/Cancel'), self.Cancel)
        reinforceTimers = attributes.reinforceTimers
        changedStructures = attributes.changedStructures
        doAllStructuresHavePendingChanges = attributes.doAllStructuresHavePendingChanges
        if self.infoOnStructures:
            self.LoadInfo(self.infoOnStructures, reinforceTimers, changedStructures, doAllStructuresHavePendingChanges)

    def GetStructureTypeIDs(self):
        typeIDs = set()
        for each in self.infoOnStructures:
            structureTypeID = each[2]
            typeIDs.add(structureTypeID)

        return typeIDs

    def LoadInfo(self, infoOnStructures, reinforceTimers, changedStructures, doAllStructuresHavePendingChanges):
        self.infoOnStructures = infoOnStructures
        numStructures = len(infoOnStructures)
        if numStructures == 1:
            structureID = infoOnStructures[0][0]
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(structureID)
            if structureInfo:
                structureLink = GetShowInfoLink(structureInfo.typeID, structureInfo.itemName, structureID)
                headerText = GetByLabel('UI/StructureBrowser/ChangingReinforcementTimeForStructure', structureLink=structureLink)
            else:
                headerText = GetByLabel('UI/StructureBrowser/ChangingReinforcementTimeForStructures', numStructures=numStructures)
        else:
            headerText = GetByLabel('UI/StructureBrowser/ChangingReinforcementTimeForStructures', numStructures=numStructures)
        self.headerText.text = headerText
        structureTypeIDs = self.GetStructureTypeIDs()
        self.reinforceTimeCont.LoadCont(reinforceTimers.GetReinforceWeekday(), reinforceTimers.GetReinforceHour(), structureTypeIDs=structureTypeIDs)
        bottomText, bottomTextTimes = self.GetBottomText(reinforceTimers, changedStructures, doAllStructuresHavePendingChanges)
        self.bottomText.text = bottomText
        self.bottomTextTimes.text = bottomTextTimes
        if len(changedStructures) > 1:
            self.bottomText.LoadTooltipPanel = lambda tooltipPanel, *args: self.LoadChangedTimesTooltipPanel(tooltipPanel, changedStructures)
        else:
            self.bottomText.LoadTooltipPanel = None
        self.SetWindowHeight()

    def SetWindowHeight(self):
        newHeight = self.sr.headerParent.height + 16
        newHeight += self.headerText.textheight
        newHeight += self.delayText.textheight
        w, h = self.reinforceTimeCont.GetAutoSize()
        newHeight += h
        newHeight += self.bottomText.padTop
        newHeight += self.bottomText.textheight
        newHeight += self.bottomTextTimes.textheight
        newHeight += self.buttons.height
        self.height = newHeight
        self.SetMinSize((self.default_minSize[0], newHeight))

    def GetBottomText(self, reinforceTimers, changedStructures, doAllStructuresHavePendingChanges):
        if not changedStructures:
            return ('', '')
        numChangedStructures = len(changedStructures)
        timeText = self.GetReinforcementChangeText(reinforceTimers, changedStructures)
        if numChangedStructures == 1:
            if doAllStructuresHavePendingChanges:
                text = GetByLabel('UI/StructureBrowser/NewReinforcementTimesPending')
                return (text, timeText)
            else:
                structureItemAndType = list(changedStructures)[0]
                _, link = self.GetStructureNameAndLink(structureItemAndType[0])
                text = GetByLabel('UI/StructureBrowser/NewReinforcementTimesPendingForAStructureWithLink', structureLink=link)
                return (text, timeText)
        text = GetByLabel('UI/StructureBrowser/NewReinforcementTimesPendingForSomeStructures', numStructures=numChangedStructures)
        if reinforceTimers.GetNextApply():
            if doAllStructuresHavePendingChanges:
                text = GetByLabel('UI/StructureBrowser/NewReinforcementTimesPendingForAllTheStructures')
        else:
            timeText = ''
        return (text, timeText)

    def GetReinforcementChangeText(self, reinforceTimers, changedStructures):
        nextDayText, nextHourText = GetDayAndHourText(reinforceTimers.GetNextReinforceDay(), reinforceTimers.GetNextReinforceHour())
        nextApply = reinforceTimers.GetNextApply()
        if nextApply < gametime.GetWallclockTime():
            pendingText = GetByLabel('UI/StructureBrowser/ChangesArePending')
        else:
            pendingText = '%s: %s' % (GetByLabel('UI/StructureBrowser/TakesEffect'), FmtDate(nextApply))
        whenText = GetByLabel('UI/StructureBrowser/PendingTimesHour', hour=nextHourText)
        text = '%s.<br>%s' % (whenText, pendingText)
        return text

    def LoadLabelTooltipPanel(self, tooltipPanel, label):
        if self.infoOnStructures is None or len(self.infoOnStructures) < 2:
            return
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.LoadGeneric1ColumnTemplate()
        structureIDs = {structureID for structureID, _, _ in self.infoOnStructures}
        self.AddStructureLinksToTooltipPanel(tooltipPanel, structureIDs)

    def AddStructureLinksToTooltipPanel(self, tooltipPanel, structureIDs):
        structureLinksList = []
        for eachID in structureIDs:
            link = self.GetStructureNameAndLink(eachID)
            if link:
                structureLinksList.append(link)

        structureLinksList = SortListOfTuples(structureLinksList)
        for eachLink in structureLinksList:
            tooltipPanel.AddLabelMedium(text=eachLink, state=uiconst.UI_NORMAL)

    def LoadChangedTimesTooltipPanel(self, tooltipPanel, changedStructures):
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.LoadGeneric1ColumnTemplate()
        self.AddStructureLinksToTooltipPanel(tooltipPanel, changedStructures)

    def GetStructureNameAndLink(self, structureID):
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(structureID)
        if not structureInfo:
            return
        structureName = structureInfo.itemName
        link = (structureName.lower(), GetShowInfoLink(structureInfo.typeID, structureName, structureID))
        return link

    def ApplyChanges(self, *args):
        reinforcementDay, reinforcementHour = self.reinforceTimeCont.GetReinforcementTime()
        sm.RemoteSvc('structureVulnerability').UpdateReinforceTimesFromClient(self.infoOnStructures, reinforcementDay, reinforcementHour)
        self.CloseByUser()

    def Cancel(self, *args):
        self.CloseByUser()
