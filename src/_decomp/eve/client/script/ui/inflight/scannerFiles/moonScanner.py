#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\moonScanner.py
import carbonui.const as uiconst
import evetypes
import gametime
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from carbonui.button.group import ButtonGroup
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.inflight.moonscan import MoonScanView
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.common.lib import appConst as const
import inventorycommon.const as invConst
from eveservices.menu import GetMenuService
from localization import GetByLabel
from localization.formatters import FormatGenericList
from signals.signalUtil import ChangeSignalConnect
from utillib import KeyVal
from fsdBuiltData.common.iconIDs import GetIconFile
import blue
import mathext
LINEBREAK = '\r\n'
GAUGE_COLOR = (0.1, 0.37, 0.55, 1.0)

class MoonScanner(Window):
    __notifyevents__ = ['OnSessionChanged']
    default_windowID = 'MoonScanner'
    default_width = 360
    default_height = 420
    default_minSize = (360, 420)
    default_captionLabelPath = 'UI/Inflight/Scanner/MoonAnalysis'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.moonScanSvc = sm.GetService('moonScan')
        self.scope = uiconst.SCOPE_INFLIGHT
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=32, clipChildren=True)
        self.AddCopyBtn()
        self.ConstructHeader()
        self.BuildProbeCont()
        self.sr.moonscanner = MoonScanView(name='moonparent', parent=self.sr.main, align=uiconst.TOALL, pos=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.moonscanner.Startup()
        self.LoadWnd(attributes.moonID)
        self.UpdateInfo()
        self.ChangeSignalConnection()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.moonScanSvc.moonProbeTracker.on_probes_changed, self.OnProbesChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnProbesChanged(self):
        self.UpdateInfo()

    def UpdateInfo(self):
        self.LoadProbeIcon()
        self.LoadProbeScroll()
        self.UpdateProbeInfoText()

    def AddCopyBtn(self):
        self.btnGroup = ButtonGroup(parent=self.sr.main, idx=0)
        text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ExportToClipboard')
        self.btnGroup.AddButton(GetByLabel('UI/Generic/Close'), self.CloseByUser, ())
        self.btnGroup.AddButton(text, self.CopyToClipboard, ())

    def BuildProbeCont(self):
        self.probeCont = DragResizeCont(name='probeCont', parent=self.sr.main, align=uiconst.TOTOP_PROP, minSize=0.15, maxSize=0.7, defaultSize=0.45, padding=4, settingsID='moonminingDivider')
        self.scroll = Scroll(parent=self.probeCont)
        self.scroll.sr.id = 'moonsprobeScroll'
        self.scroll.GetStrengir = self.GetScrollStrengir
        self.scroll.sr.minColumnWidth = {GetByLabel('UI/Inflight/Scanner/ProbeTimeLeftHeader'): 90}

    def GetScrollStrengir(self, node, fontsize, letterspace, shift, idx = None):
        shift = MoonProbeItemEntry.GetShift(node)
        return Scroll.GetStrengir(self.scroll, node, fontsize, letterspace, shift, idx)

    def ConstructHeader(self):
        self.headerContainer = Container(name='HeaderContainer', parent=self.topParent, align=uiconst.TOTOP, height=32)
        PanelUnderlay(name='HeaderUnderlay', bgParent=self.headerContainer)
        self.probeInfoContainer = ContainerAutoSize(name='probeInfoContainer', parent=self.headerContainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, left=4)
        self.probeSprite = Sprite(name='ProbeSprite', parent=self.probeInfoContainer, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, pos=(1, 0, 32, 32))
        self.probeSpriteFrame = Sprite(name='probeSpriteFrame', texturePath='res:/UI/Texture/classes/ProbeScanner/probeFrame.png', parent=self.probeInfoContainer, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, width=32, height=32)
        self.probesLaunchedLabel = EveLabelMedium(name='ProbesLaunchedLabel', parent=self.probeInfoContainer, align=uiconst.CENTERLEFT, left=36)
        infoIcon = ButtonIcon(name='infoIcon', parent=self.headerContainer, texturePath='res:/UI/Texture/Icons/generic/more_info_16.png', align=uiconst.BOTTOMRIGHT, pos=(6, 4, 16, 16), state=uiconst.UI_NORMAL)
        infoIcon.hint = GetByLabel('UI/Inflight/Scanner/MoonScanHint')

    def LoadWnd(self, moonID = None):
        scans = self.moonScanSvc.GetScans()
        self.sr.moonscanner.SetEntries(scans, moonID=moonID)
        self.LoadProbeScroll()

    def ClearMoons(self):
        self.sr.moonscanner.Clear()

    def UpdateProbeInfoText(self):
        probeData = self.moonScanSvc.GetProbeData()
        numProbes = len(probeData)
        if numProbes:
            text = 'X %s' % numProbes
        elif not self.moonScanSvc.HasOnlineProbeLauncher():
            text = GetByLabel('UI/Inflight/Scanner/NoLauncherFitted')
        elif self.moonScanSvc.GetChargesInProbeLauncher():
            text = GetByLabel('UI/Inflight/Scanner/NoProbesLaunched')
        else:
            text = GetByLabel('UI/Inflight/Scanner/NoProbesInLauncher')
        self.probesLaunchedLabel.SetText(text)
        color = Label.default_color if numProbes else Color.ORANGE
        self.probesLaunchedLabel.SetRGBA(*color)
        self.probeSpriteFrame.SetRGBA(*color)

    def LoadProbeIcon(self):
        typeID = self.moonScanSvc.GetActiveProbeTypeID()
        if not typeID:
            self.probeSprite.opacity = 0.3
            self.probeInfoContainer.tooltipPanelClassInfo = MoonProbeTooltip(typeID, 0)
            typeID = invConst.typeSurveyProbeLauncher
        else:
            numProbes = self.moonScanSvc.moonProbeTracker.GetNumProbes()
            self.probeSprite.opacity = 1.0
            self.probeInfoContainer.tooltipPanelClassInfo = MoonProbeTooltip(typeID, numProbes)
        iconID = evetypes.GetIconID(typeID)
        texturePath = GetIconFile(iconID)
        self.probeSprite.texturePath = texturePath

    def LoadProbeScroll(self):
        probesInScroll = {node.itemID for node in self.scroll.GetNodes()}
        scrolllist = []
        for eachProbe in self.moonScanSvc.GetProbeData().itervalues():
            moonID = self.moonScanSvc.GetMoonForProbe(eachProbe.probeID)
            moonName = MoonProbeItemEntry.GetMoonName(moonID)
            probeName = GetByLabel('UI/Inflight/Scanner/ProbeLabel', probeIndex=eachProbe.probeNumber)
            data = KeyVal()
            data.typeID = eachProbe.typeID
            data.moonID = moonID
            data.expiry = eachProbe.expiry
            data.delay = eachProbe.delay
            data.probeName = probeName
            data.destinationText = moonName
            data.getIcon = True
            data.label = MoonProbeItemEntry.GetProbeText(data)
            data.Set('sort_%s' % GetByLabel('UI/Inflight/Scanner/ProbeTimeLeftHeader'), eachProbe.expiry)
            data.Set('sort_%s' % GetByLabel('UI/Inflight/Scanner/Probe'), eachProbe.probeNumber)
            data.isNewEntry = eachProbe.probeID not in probesInScroll
            entry = GetFromClass(MoonProbeItemEntry, data)
            scrolllist.append(entry)

        headers = [GetByLabel('UI/Inflight/Scanner/Probe'), GetByLabel('UI/Inflight/Scanner/ProbeTimeLeftHeader'), GetByLabel('UI/Inflight/Scanner/ProbeDestination')]
        self.scroll.LoadContent(contentList=scrolllist, headers=headers, noContentHint=GetByLabel('UI/Inflight/Scanner/NoProbesInSpace'))

    def Close(self, *args, **kwargs):
        with EatSignalChangingErrors(errorMsg='Container'):
            self.ChangeSignalConnection(connect=False)
        Window.Close(self, *args, **kwargs)

    def CopyToClipboard(self):
        allScans = self.moonScanSvc.GetScans()
        allScansSorted = SortListOfTuples([ (celestialID, (celestialID, products)) for celestialID, products in allScans.iteritems() ])
        headerList = [GetByLabel('UI/Common/Groups/Moon'),
         GetByLabel('UI/Inflight/Scanner/MoonProduct'),
         GetByLabel('UI/Common/Quantity'),
         GetByLabel('UI/Ledger/OreTypeID'),
         GetByLabel('UI/Ledger/SolarSystemID'),
         GetByLabel('UI/Moonmining/PlanetID'),
         GetByLabel('UI/Moonmining/MoonID')]
        lineList = ['\t'.join(headerList)]
        for eachCelestialID, products in allScansSorted:
            try:
                celestialInfo = cfg.evelocations.Get(eachCelestialID)
                celestialName = celestialInfo.name
                lineList.append(celestialName)
                moonInfo = cfg.mapSolarSystemContentCache.moons[eachCelestialID]
                planetID = moonInfo.orbitID
                sortedProducts = SortListOfTuples([ (evetypes.GetName(typeID), (evetypes.GetName(typeID), typeID, qty)) for typeID, qty in products.iteritems() ])
                for typeName, typeID, qty in sortedProducts:
                    stringList = ['',
                     typeName,
                     unicode(float(qty)),
                     unicode(typeID),
                     unicode(celestialInfo.solarSystemID),
                     unicode(planetID),
                     unicode(eachCelestialID)]
                    line = '\t'.join(stringList)
                    lineList.append(line)

            except StandardError as e:
                self.moonScanSvc.LogException(e)
                continue

        text = LINEBREAK.join(lineList)
        blue.pyos.SetClipboardData(text)


class MoonProbeItemEntry(BaseListEntryCustomColumns):
    default_name = 'MoonProbeItemEntry'
    updateLabelTimer = None
    default_height = 29

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.sr.infoicon = InfoIcon(left=2, parent=self, idx=0, align=uiconst.CENTERRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo
        probeNameCont = self.AddColumnContainer()
        self.icon = ItemIcon(parent=probeNameCont, pos=(1, 2, 24, 24), align=uiconst.TOPLEFT, idx=0)
        self.probeLabel = Label(parent=probeNameCont, text='', align=uiconst.CENTERLEFT, left=28)
        timeCont = self.AddColumnContainer()
        self.gauge = Gauge(parent=timeCont, name='timeGauge', value=0.0, color=GAUGE_COLOR, gaugeHeight=16, align=uiconst.TOALL, pos=(5, 5, 5, 0), state=uiconst.UI_DISABLED, gradientBrightnessFactor=1.5)
        self.destinationLabel = self.AddColumnText(text='')
        self.destinationLabel.state = uiconst.UI_NORMAL

    def Load(self, node):
        self.sr.node = node
        self.itemID = node.itemID
        self.typeID = node.typeID
        isNew = node.isNewEntry
        node.isNewEntry = False
        self.icon.SetTypeID(self.typeID)
        self.probeLabel.text = node.probeName
        self.destinationLabel.text = node.destinationText
        self.UpdateTime(isNew=isNew)
        self.updateLabelTimer = AutoTimer(1000, self.UpdateTime)

    def UpdateTime(self, isNew = False):
        if self.destroyed:
            self.updateLabelTimer = None
            return
        node = self.sr.node
        timeLeftText, timeLeft = self.GetProbTimeLeft(node)
        if node.moonID == -1:
            node.moonID = sm.GetService('moonScan').GetMoonForProbe(node.itemID)
            if node.moonID != -1:
                node.destinationText = self.GetMoonName(node.moonID)
                self.destinationLabel.text = node.destinationText
        totalDelay = node.delay
        percentage = round(1.0 - mathext.clamp(max(0, timeLeft) / float(totalDelay * const.MSEC), 0.0, 1.0), 2)
        self.gauge.SetValue(percentage, animate=isNew)
        self.gauge.SetValueText(timeLeftText)

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(self.itemID, self.typeID, includeMarketDetails=True)

    @classmethod
    def GetProbTimeLeft(cls, node):
        timeLeft = node.expiry - gametime.GetSimTime()
        timeLeft = max(0, timeLeft)
        timeLeftText = FmtDate(timeLeft, 'ns')
        return (timeLeftText, timeLeft)

    def ShowInfo(self):
        sm.GetService('info').ShowInfo(self.typeID)

    @classmethod
    def GetProbeText(cls, node):
        timeLeft = node.expiry - gametime.GetWallclockTime()
        timeLeft = max(0, timeLeft)
        timeLeftText = FmtDate(timeLeft, 'ns')
        text = '%s<t><right>%s</right><t>%s' % (node.probeName, timeLeftText, node.destinationText)
        return text

    @classmethod
    def GetMoonName(cls, moonID):
        if moonID > 0:
            return GetShowInfoLink(invConst.typeMoon, cfg.evelocations.Get(moonID).name, moonID)
        else:
            return GetByLabel('UI/Inflight/Scanner/ProbeDestinationUnknown')

    @staticmethod
    def GetShift(node):
        return 28


class MoonProbeTooltip(TooltipBaseWrapper):

    def __init__(self, probeTypeID, numProbes):
        super(MoonProbeTooltip, self).__init__()
        self.probeTypeID = probeTypeID
        self.numProbes = numProbes

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        if not self.probeTypeID:
            text = GetNoProbesTooltipText()
        else:
            text = GetByLabel('UI/Inflight/Scanner/NumSurveyProbesInSpace', numProbes=self.numProbes)
        self.tooltipPanel.AddLabelMedium(text=text, state=uiconst.UI_NORMAL, wrapWidth=200)
        return self.tooltipPanel


def GetNoProbesTooltipText():
    typeLinks = []
    for eachTypeID in evetypes.GetTypeIDsByGroup(invConst.groupSurveyProbe):
        if not evetypes.IsPublished(eachTypeID):
            continue
        typeName = evetypes.GetName(eachTypeID)
        link = GetShowInfoLink(eachTypeID, typeName)
        typeLinks.append((typeName, link))

    typeLinks = SortListOfTuples(typeLinks)
    typeText = FormatGenericList(typeLinks)
    groupName = evetypes.GetGroupNameByGroup(invConst.groupSurveyProbe)
    probeLauncherLink = GetShowInfoLink(invConst.typeSurveyProbeLauncher, evetypes.GetName(invConst.typeSurveyProbeLauncher))
    return GetByLabel('UI/Inflight/Scanner/NoSurveyProbesTooltip', groupName=groupName, listOfLinksToTypes=typeText, probeLauncherLink=probeLauncherLink)
