#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\Alliances\sovHubs\sovHubEntry.py
from collections import OrderedDict
import carbonui
import eveicon
import uthread
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import const as uiconst, TextColor
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.shared.neocom.Alliances.sovHubs.sovHubEntryController import UNDEFINED
from eve.client.script.ui.shared.sov.threadedLoader import ThreadedLoader
from eveexceptions import ExceptionEater
from eveservices.menu import GetMenuService
from eveui import animation
from localization import GetByLabel
from menu import MenuLabel
from sovereignty.client.quasarCallWrapper import DATA_NOT_AVAILABLE

class ColumnInfo(object):

    def __init__(self, labelPath, hintPath = None, defaultWidth = None, valueStorageAttribute = None):
        self._labelPath = labelPath
        self._hintPath = hintPath
        self._defaultWidth = defaultWidth
        self._valueStorageAttribute = valueStorageAttribute

    @property
    def columnText(self):
        if self._labelPath:
            return GetByLabel(self._labelPath)
        return ''

    @property
    def defaultWidth(self):
        if self._defaultWidth:
            return self._defaultWidth

    @property
    def hintText(self):
        if self._hintPath:
            return GetByLabel(self._hintPath)

    @property
    def valueStorageAttribute(self):
        return self._valueStorageAttribute


class SovHubEntry(BaseListEntryCustomColumns):
    default_name = 'SovHubEntry'
    isDragObject = True
    dblclick = 0
    default_height = 30
    default_bgColor = eveColor.WHITE[:3] + (0.1,)
    headerInfo = d = OrderedDict()
    d['sovHubName'] = ColumnInfo('UI/Sovereignty/HubPage/ColumnSovHub', None, 100)
    d['jumps'] = ColumnInfo('UI/Common/Jumps', None, 40)
    d['region'] = ColumnInfo('UI/Common/LocationTypes/Region', None, 80)
    d['upgrade'] = ColumnInfo('UI/Sovereignty/HubPage/ColumnUpgrades', None, 60, 'upgradeSortValue')
    d['power'] = ColumnInfo('UI/Sovereignty/HubPage/ColumnPower', None, 100, 'powerSortValue')
    d['workforce'] = ColumnInfo('UI/Sovereignty/HubPage/ColumnWorkforce', None, 120, 'workforceSortValue')
    d['transit'] = ColumnInfo('UI/Sovereignty/SovHub/HubWnd/WorceforceMode', None, 70, 'worceforceMode')
    d['lavaFuel'] = ColumnInfo('UI/Sovereignty/HubPage/ColumnLavaFuel', None, 80, 'lavaText')
    d['iceFuel'] = ColumnInfo('UI/Sovereignty/HubPage/ColumnIceFuel', None, 80, 'iceText')
    d['vulnStatus'] = ColumnInfo('UI/Generic/Status', None, 100)
    d['vulnHour'] = ColumnInfo('UI/Sovereignty/HubPage/ColumnVulnerabilityHour', None, 200)

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.entryController = self.node.entryController
        self.threadedLoader = ThreadedLoader('SovHubEntry')
        self.expander = GlowSprite(parent=self, pos=(4, 0, 16, 16), name='expander', state=uiconst.UI_DISABLED, texturePath=eveicon.caret_right, align=uiconst.CENTERLEFT)
        self.expander.OnClick = self.Toggle
        self.AddStructureName()
        self.AddJumps()
        self.AddRegion()
        self.AddUpgrades()
        self.AddPower()
        self.AddWorkforce()
        self.AddWorkforceTransit()
        self.AddLavaFuel()
        self.AddIceFuel()
        self.AddStatus()
        self.AddVulnerabilityHour()

    def AddStructureName(self):
        cont = self.AddColumnContainer()
        Sprite(parent=cont, align=carbonui.Align.CENTERLEFT, pos=(24, 0, 16, 16), texturePath=self.entryController.GetTexturePath(), color=eveColor.TUNGSTEN_GREY)
        text = self.entryController.GetSolarSystemName()
        Label(parent=cont, text=text, align=uiconst.CENTERLEFT, left=45)

    def AddJumps(self):
        jumps = self.entryController.GetJumpText()
        col = self.AddLoadingLabelCont(jumps)
        col.label.left = 0
        col.label.SetAlign(carbonui.Align.CENTERRIGHT)

    def AddRegion(self):
        regionName = self.entryController.GetRegionName()
        self.AddLoadingLabelCont(regionName)

    def AddUpgrades(self):
        self.upgradesLabelCont = self.AddLoadingLabelCont('')

    def AddPower(self):
        self.powerLabelCont = self.AddLoadingLabelCont('')

    def AddWorkforce(self):
        self.workforceLabelCont = self.AddLoadingLabelCont('')

    def AddWorkforceTransit(self):
        self.workforceTransit = self.AddLoadingLabelCont('')
        self.workforceTransitSprite = Sprite(parent=self.workforceTransit, pos=(0, 0, 16, 16), align=carbonui.Align.CENTER, color=eveColor.TUNGSTEN_GREY)

    def AddIceFuel(self):
        self.iceFuelLabelCont = self.AddLoadingLabelCont('')

    def AddLavaFuel(self):
        self.lavaFuelLabelCont = self.AddLoadingLabelCont('')

    def AddStatus(self):
        text = self.entryController.GetVulnerabilityStateText()
        self.AddLoadingLabelCont(text)

    def AddVulnerabilityHour(self):
        text = self.entryController.GetVulnerabilityTime()
        col = self.AddLoadingLabelCont(text)
        self.vulnerabilityHourLabel = col.label
        self.vulnerability_thread = AutoTimer(500, self.UpdateVulnerabilityTimer)

    def Load(self, node):
        super(SovHubEntry, self).Load(node)
        self.sr.id = node.id
        isOpen = uicore.registry.GetListGroupOpenState(self.sr.id, False)
        self.ShowOpenState(isOpen)
        self.threadedLoader.StartLoading(self.LoadInfo, self)

    def LoadInfo(self):
        uthread2.StartTasklet(self.ShowDelayedLoading_thread, 0.5, [self.upgradesLabelCont,
         self.powerLabelCont,
         self.workforceLabelCont,
         self.iceFuelLabelCont,
         self.lavaFuelLabelCont])
        results = uthread.parallel([(self.entryController.GetUpgradesTextShort, ()),
         (self.entryController.GetPowerColumnText, ()),
         (self.entryController.GetWorkforceColumnText, ()),
         (self.entryController.GetIceText, ()),
         (self.entryController.GetLavaText, ()),
         (self.entryController.GetTransitMode, ())])
        upgradeText, powerText, workforceText, iceFuelText, lavelFuelText, transit = results
        if self.destroyed:
            return
        self.upgradesLabelCont.text = upgradeText
        self.powerLabelCont.text = powerText
        self.workforceLabelCont.text = workforceText
        self.iceFuelLabelCont.text = iceFuelText
        self.lavaFuelLabelCont.text = lavelFuelText
        if transit == DATA_NOT_AVAILABLE:
            self.workforceTransit.text = self.entryController.GetNotAvailableText()
        else:
            texturePath, hintText, info = transit
            self.workforceTransitSprite.SetTexturePath(texturePath)
            self.workforceTransitSprite.hint = hintText

    def ShowDelayedLoading_thread(self, delaySec, labelConts):
        for eachLabelCont in labelConts:
            eachLabelCont.SetPendingLoadingAnimation()

        uthread2.Sleep(delaySec)
        if self.destroyed:
            return
        for eachLabelCont in labelConts:
            if eachLabelCont.loadingAnimationPending:
                eachLabelCont.SetLoadingState(True)

    @classmethod
    def GetHeaders(cls):
        return [ x.columnText for x in cls.headerInfo.itervalues() ]

    @staticmethod
    def GetDefaultColumnWidth(*args):
        return {x.columnText:x.defaultWidth for x in SovHubEntry.headerInfo.itervalues() if x.defaultWidth}

    @staticmethod
    def GetSortValue(node, by, direction, idx):
        entryController = node.entryController
        structureName = entryController.GetSolarSystemName()
        if idx is None:
            return structureName
        headerKey = SovHubEntry.headerInfo.keys()[idx]
        headerValue = SovHubEntry.headerInfo[headerKey]
        valueStorageAttribute = headerValue.valueStorageAttribute
        if valueStorageAttribute:
            storage = entryController.valueStorage
            val = getattr(storage, valueStorageAttribute, UNDEFINED)
            if val in (UNDEFINED, DATA_NOT_AVAILABLE):
                if direction:
                    val = -99999999999999999999L
                else:
                    val = 'zzzzzzzzzzzzzzzzzzzzzzzz'
            return (val, structureName)
        if headerKey == 'sovHubName':
            return structureName
        if headerKey == 'jumps':
            return (entryController.GetNumJumps(), structureName)
        if headerKey == 'region':
            return (entryController.GetRegionName(), structureName)
        if headerKey == 'vulnStatus':
            return (entryController.GetVulnerabilityStateText(), structureName)
        if headerKey == 'vulnStatus':
            return (entryController.GetVulnerabilityTime()(), structureName)
        return structureName

    def GetMenu(self):
        typeID = self.entryController.typeID
        itemID = self.entryController.itemID
        m = GetMenuService().GetMenuFromItemIDTypeID(itemID, typeID, includeMarketDetails=False)
        if self.entryController.solarSystemID != session.solarsystemid2:
            m.append(MenuEntryData(MenuLabel('UI/Menusvc/OpenSovHubConfigWindow'), func=lambda *args: self.entryController.OpenSovHubWindow(), texturePath=eveicon.settings))
        m.append(MenuEntryData(MenuLabel('UI/Common/Location'), subMenuData=GetMenuService().CelestialMenu(self.entryController.solarSystemID), texturePath=eveicon.location))
        return m

    def OnClick(self, *args, **kwargs):
        self.Toggle()

    def Toggle(self, *args):
        node = self.sr.node
        if not node or node.get('toggling', 0):
            return
        node.toggling = 1
        w = node.panel
        if not w:
            node.toggling = 0
            return
        node.open = not node.open
        if node.open:
            PlaySound(uiconst.SOUND_EXPAND)
            node.scroll.CollapseAll()
        else:
            PlaySound(uiconst.SOUND_COLLAPSE)
        self.ShowOpenState(node.open)
        uicore.registry.SetListGroupOpenState(node.id, node.open)
        node.scroll.PrepareSubContent(node)
        if node.get('onToggle', None):
            node.onToggle()
        node.toggling = 0

    def ShowOpenState(self, open_):
        if self.expander:
            if open_:
                self.expander.SetTexturePath(eveicon.caret_down)
            else:
                self.expander.SetTexturePath(eveicon.caret_right)

    def AddLoadingLabelCont(self, text):
        column = LoadingLabelCont(parent=self, text=text)
        self.columns.append(column)
        return column

    def UpdateVulnerabilityTimer(self):
        if self.destroyed:
            self.vulnerability_thread = None
            return
        self.vulnerabilityHourLabel.text = self.entryController.GetVulnerabilityTime()

    def Close(self):
        with ExceptionEater('Closing SovHubEntry'):
            self.entryController = None
        super(SovHubEntry, self).Close()


class LoadingLabelCont(Container):
    default_align = carbonui.Align.TOLEFT
    default_clipChildren = True
    normalOpacity = TextColor.NORMAL[3]

    def ApplyAttributes(self, attributes):
        super(LoadingLabelCont, self).ApplyAttributes(attributes)
        text = attributes.text
        innerCont = Container(parent=self, left=uiconst.LABELTABMARGIN, width=uiconst.LABELTABMARGIN, clipChildren=True)
        self._loadingAnimationPending = False
        self.loadingWheel = LoadingWheel(parent=innerCont, align=carbonui.Align.CENTER, pos=(0, 0, 16, 16), opacity=0.0, color=eveColor.TUNGSTEN_GREY)
        self.label = carbonui.TextBody(parent=innerCont, text=text, align=uiconst.CENTERLEFT, left=uiconst.LABELTABMARGIN, autoFadeSides=6)

    def SetText(self, text):
        self.label.text = text
        self.SetLoadingState(False)

    def SetPendingLoadingAnimation(self):
        if self._loadingAnimationPending:
            return
        self._loadingAnimationPending = True

    def SetLoadingState(self, isLoading, animate = True):
        self._loadingAnimationPending = False
        if animate:
            if isLoading:
                animation.fade_in(self.loadingWheel)
                animation.fade_out(self.label, duration=0.1)
            else:
                animation.fade_out(self.loadingWheel, duration=0.1)
                animation.fade_in(self.label, end_value=self.normalOpacity)
        elif isLoading:
            self.loadingWheel.opacity = 1.0
            self.label.opacity = 0.0
        else:
            self.loadingWheel.opacity = 0.0
            self.label.opacity = self.normalOpacity

    @property
    def loadingAnimationPending(self):
        return self._loadingAnimationPending

    @property
    def text(self):
        return self.label.text

    @text.setter
    def text(self, value):
        self.SetText(value)
