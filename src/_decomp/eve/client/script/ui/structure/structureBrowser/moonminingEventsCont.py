#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\moonminingEventsCont.py
import gametime
import log
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.eveLabel import EveLabelLarge, Label
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.scrollUtil import TabFinder
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from eve.client.script.ui.moonmining import DAY_NAME_TEXT
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.structure.structureBrowser import browserUIConst
from eveservices.menu import GetMenuService
from localization import GetByLabel
import blue
from carbonui.uicore import uicore
from localization.formatters import FormatTimeIntervalShortWritten
from signals.signalUtil import ChangeSignalConnect

class MoonminingEventsCont(Container):
    default_name = 'MoonminingEventsCont'
    TAB_ID = 'MOONMINING'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.allStructuresProfileController = sm.GetService('structureControllers').GetAllStructuresProfileController()
        self.structureBrowserController = attributes.structureBrowserController
        self.myStructureControllersByID = {x.GetItemID():x for x in self.structureBrowserController.GetMyStructures()}
        self.isInitialized = False
        self.ChangeSignalConnection()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.structureBrowserController.on_profile_selected, self.OnProfileSelected)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnProfileSelected(self, profileID):
        if self.structureBrowserController.GetSelectedTab() == self.TAB_ID:
            self.LoadProfile(profileID)

    def LoadProfile(self, profileID):
        self.UpdateScroll()

    def OnTabSelect(self):
        self.structureBrowserController.SetTabSelected(self.TAB_ID)
        self.LoadPanel()

    def LoadPanel(self):
        if self.isInitialized:
            self.UpdateScroll()
            return
        self.topPanel = Container(name='topPanel', parent=self, align=uiconst.TOTOP, height=20, padding=(0, 6, 0, 6))
        self.profilaNameLabel = EveLabelLarge(text='', parent=self.topPanel, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, top=2)
        self.scroll = Scroll(parent=self, id='MyStructuresScroll')
        self.scroll.multiSelect = False
        self.scroll.GetTabStops = self.GetTabStops
        self.UpdateScroll()
        self.isInitialized = True

    def GetTabStops(self, headertabs, idx = None):
        return TabFinder().GetTabStops(self.scroll.sr.nodes, headertabs, MoonminingEntry, idx=idx)

    def UpdateScroll(self):
        if self.structureBrowserController.GetSelectedTab() != self.TAB_ID:
            return
        self.SetLabelProfileName()
        scrollList = self.GetScrollList()
        self.scroll.LoadContent(contentList=scrollList, headers=MoonminingEntry.GetHeaders(), noContentHint=GetByLabel('UI/Structures/Browser/NoExtractionsFound'))

    def SetLabelProfileName(self):
        currentProfileID = self.structureBrowserController.GetSelectedProfileID()
        c = self.allStructuresProfileController.GetSlimProfileController(currentProfileID)
        self.profilaNameLabel.text = c.GetProfileName() if c else ''

    def GetScrollList(self):
        extractions = sm.GetService('scheduling').GetExtractionsForCorp()
        scrollList = []
        toPrime = {x.structureID for x in extractions}
        toPrime.update({x.solarSystemID for x in extractions})
        cfg.evelocations.Prime(toPrime)
        for eachExtraction in extractions:
            structureController = self.myStructureControllersByID.get(eachExtraction.structureID, None)
            if structureController is None:
                log.LogWarn('missing structure controller for structure %s' % eachExtraction.structureID)
                continue
            if self.IsFilteredOut(structureController):
                continue
            timerText, timeUntil = self.FmtTimeAndTimeUntil(eachExtraction.chunkAvailableTime)
            node = Bunch(numJumps=structureController.GetNumJumps(), structureName=structureController.GetName(), timerText=timerText, timeUntil=timeUntil, secText=structureController.GetSecurityWithColor(), secValue=structureController.GetSecurity(), structureID=eachExtraction.structureID, structureTypeID=structureController.GetTypeID(), chunkAvailableTime=eachExtraction.chunkAvailableTime, moonID=eachExtraction.moonID, decoClass=MoonminingEntry, GetSortValue=MoonminingEntry.GetSortValue)
            node.columnSortValues = MoonminingEntry.GetColumnSortValues(node)
            scrollList.append(node)

        return scrollList

    def IsFilteredOut(self, structureController):
        currentProfileID = self.structureBrowserController.GetSelectedProfileID()
        if currentProfileID != browserUIConst.ALL_PROFILES and currentProfileID != structureController.GetProfileID():
            return True
        return False

    def FmtTimeAndTimeUntil(self, timestamp):
        now = gametime.GetWallclockTimeNow()
        weekday = GetWeekdayTextForTimestamp(timestamp)
        timeText = '%s<br>%s' % (weekday, FmtDate(timestamp))
        diff = max(0, timestamp - now)
        timeUntil = FormatTimeIntervalShortWritten(diff)
        return (timeText, timeUntil)

    def Close(self):
        with EatSignalChangingErrors(errorMsg='MoonminingEventsCont'):
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)


HEIGHT = 48
LABEL_PARAMS = (EVE_MEDIUM_FONTSIZE, 0, 0)

class MoonminingEntry(BaseListEntryCustomColumns):

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.BuildUI()

    def BuildUI(self):
        self.jumpColumnLabel = self.AddCenteredTextColumn()
        self.securityColumn = self.AddCenteredTextColumn()
        self.nameColumn = self.AddColumnContainer()
        self.timerText = self.AddCenteredTextColumn()
        self.countdownText = self.AddCenteredTextColumn()
        self.LoadUI()

    def AddCenteredTextColumn(self, text = None):
        column = self.AddColumnContainer()
        return Label(parent=column, text=text, align=uiconst.CENTER)

    def LoadUI(self):
        self.PopulateLabels()
        self.PopulateNameColumn()

    def PopulateLabels(self):
        node = self.sr.node
        self.jumpColumnLabel.text = node.numJumps
        self.securityColumn.text = node.secText
        self.timerText.text = node.timerText
        self.countdownText.text = node.timeUntil

    def PopulateNameColumn(self):
        node = self.sr.node
        self.nameColumn.Flush()
        name = node.structureName
        size = HEIGHT - 4
        ItemIcon(parent=self.nameColumn, align=uiconst.CENTERLEFT, typeID=node.structureTypeID, width=size, height=size, state=uiconst.UI_DISABLED)
        label = Label(parent=self.nameColumn, text=name, align=uiconst.CENTERLEFT, left=HEIGHT, state=uiconst.UI_NORMAL)
        label.GetMenu = None
        label.DelegateEventsNotImplemented(self)

    def GetMenu(self):
        node = self.sr.node
        itemID = node.structureID
        typeID = node.structureTypeID
        return GetMenuService().GetMenuFromItemIDTypeID(itemID=itemID, typeID=typeID)

    @staticmethod
    def GetHeaders():
        return (GetByLabel('UI/Common/Jumps'),
         GetByLabel('UI/Common/Security'),
         GetByLabel('UI/Common/Name'),
         'Time',
         'Time Until')

    @staticmethod
    def GetDynamicHeight(node, width):
        return HEIGHT

    @staticmethod
    def GetColWidths(node, idx = None):
        widths = []
        getAllWidths = idx is None
        if getAllWidths or idx == 0:
            jumpText = unicode(node.numJumps)
            w = FindColumnWidth(jumpText)
            widths.append(w)
        if getAllWidths or idx == 1:
            securityText = unicode(node.secText)
            w = FindColumnWidth(securityText)
            widths.append(w)
        if getAllWidths or idx == 3:
            nameToUse = max(StripTags(node.structureName, ignoredTags=('br',)).split('<br>'), key=len)
            w = FindColumnWidth(nameToUse)
            widths.append(w + HEIGHT - 4)
        if getAllWidths or idx == 4:
            textToUse = max(StripTags(node.timerText, ignoredTags=('br',)).split('<br>'), key=len)
            w = FindColumnWidth(textToUse)
            widths.append(w)
        if getAllWidths or idx == 5:
            w = FindColumnWidth(node.timeUntil)
            widths.append(w)
        return widths

    @staticmethod
    def GetColumnSortValues(node):
        return (node.numJumps,
         node.secValue,
         StripTags(node.structureName).lower(),
         node.chunkAvailableTime,
         -node.chunkAvailableTime)

    @staticmethod
    def GetSortValue(node, by, sortDirection, idx):
        return (node.columnSortValues[idx],) + tuple(node.columnSortValues)


def FindColumnWidth(text):
    stringsData = (text,) + LABEL_PARAMS
    tabStops = uicore.font.MeasureTabstops([stringsData])
    return tabStops[0]


def GetWeekdayTextForTimestamp(timestamp):
    year, month, wd, day, hour, min, sec, ms = blue.os.GetTimeParts(timestamp)
    return DAY_NAME_TEXT[wd]
