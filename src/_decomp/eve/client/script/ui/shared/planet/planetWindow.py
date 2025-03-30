#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetWindow.py
import blue
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.neocom.journal import PlanetaryInteractionLaunchEntry
from eve.client.script.ui.shared.planet.planetsWindow.coloniesPanel import ColoniesPanel
from eve.common.lib import appConst as const
from localization import GetByLabel
from localization.formatters.timeIntervalFormatters import FormatTimeIntervalShortWritten

class PlanetWindow(Window):
    __guid__ = 'form.PlanetWindow'
    __notifyevents__ = ['OnPILaunchesChange']
    default_width = 500
    default_height = 500
    default_minSize = (300, 400)
    default_windowID = 'planetWindow'
    default_analyticID = 'pi_planet_window'
    default_captionLabelPath = 'UI/InfoWindow/TabNames/PlanetaryProduction'
    default_descriptionLabelPath = 'UI/ScienceAndIndustry/PlanetaryColoniesDesc'
    default_caption = GetByLabel('UI/InfoWindow/TabNames/PlanetaryProduction')
    default_iconNum = 'res:/UI/Texture/WindowIcons/planets.png'
    default_isCompactable = True

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.ReconstructWindow()

    def ReconstructWindow(self):
        self.sr.main.Flush()
        coloniesPanel = ColoniesPanel(parent=self.sr.main, isCompact=self.IsCompact())
        launches = self.GetLaunches()
        if launches:
            launchesPanel = LaunchesPanel(parent=self.sr.main)
            TabGroup(name='myTabGroup', parent=self.sr.main, groupID='MyTabGroupID', idx=0, tabs=((GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Colonies'),
              coloniesPanel,
              self,
              'colonies'), (GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Launches'),
              launchesPanel,
              self,
              'launchesPanel')))
        else:
            coloniesPanel.LoadPlanetScroll()

    def GetLaunches(self, reload = False):
        return sm.GetService('planetUI').GetLaunches(force=reload)

    def OnPILaunchesChange(self):
        self.GetLaunches(reload=True)
        self.ReconstructWindow()

    def OnCompactModeEnabled(self):
        super(PlanetWindow, self).OnCompactModeEnabled()
        self.ReconstructWindow()

    def OnCompactModeDisabled(self):
        super(PlanetWindow, self).OnCompactModeDisabled()
        self.ReconstructWindow()


class LaunchesPanel(Container):
    default_name = 'LaunchesPanel'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.scroll = Scroll(parent=self)
        self.scroll.sr.id = 'launchesScroll'

    def OnTabSelect(self):
        self.UpdateScroll()

    def UpdateScroll(self, reload = 0):
        launchsRowSet = sm.GetService('planetUI').GetLaunches(force=reload)
        scrolllist = []
        for launch in launchsRowSet:
            label = '<t>'.join(['    ',
             cfg.evelocations.Get(launch.solarSystemID).name,
             cfg.evelocations.Get(launch.planetID).name,
             FmtDate(launch.launchTime)])
            expired = not blue.os.GetWallclockTime() - launch.launchTime < const.piLaunchOrbitDecayTime
            scrolllist.append(GetFromClass(PlanetaryInteractionLaunchEntry, {'id': launch.launchID,
             'label': label,
             'callback': None,
             'selected': 0,
             'expired': expired,
             'rec': launch}))

        self.scroll.Load(contentList=scrolllist, headers=[GetByLabel('UI/Journal/JournalWindow/PI/HeaderReentry'),
         GetByLabel('UI/Journal/JournalWindow/PI/HeaderSolarSystem'),
         GetByLabel('UI/Journal/JournalWindow/PI/HeaderPlanet'),
         GetByLabel('UI/Journal/JournalWindow/PI/HeaderLaunchTime')], noContentHint=GetByLabel('UI/Journal/JournalWindow/PI/NoActiveLaunches'))
        self.AutoUpdateLaunchDecayTimes()
        self.sr.launchtimer = AutoTimer(1000, self.AutoUpdateLaunchDecayTimes)

    def AutoUpdateLaunchDecayTimes(self):
        if self.destroyed:
            self.sr.launchtimer = None
            return
        for entry in self.scroll.GetNodes():
            text = entry.label
            if not entry.rec:
                continue
            expiryNumeric = blue.os.GetWallclockTime() - entry.rec.launchTime
            if expiryNumeric < const.piLaunchOrbitDecayTime:
                expiryLabel = '<color=0xFFFFFF00>' + FormatTimeIntervalShortWritten(const.piLaunchOrbitDecayTime - expiryNumeric) + '</color>'
            else:
                expiryLabel = '<color=0xffeb3700>' + GetByLabel('UI/Journal/JournalWindow/PI/BurnedUp') + '</color>'
                entry.expired = True
            entry.label = expiryLabel + text[text.find('<t>'):]
            if entry.panel:
                entry.panel.Load(entry)
