#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetbroadcast.py
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import evefleet.client
import localization
from carbonui import ButtonVariant, Density, uiconst
from carbonui.button.const import HEIGHT_COMPACT
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.colorPanel import ColorPanel
from eve.client.script.ui.control.entries.checkbox import CheckboxEntry
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.fleet import fleetbroadcastexports as fleetbr, fleetBroadcastConst
from evefleet import BROADCAST_SHOW_OWN
from eve.common.script.sys.idCheckers import IsUniverseCelestial
from eveservices.menu import GetMenuService
from utillib import KeyVal
comboOptions = ((localization.GetByLabel('UI/Common/All'), 'all'),
 (localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastHistory'), 'broadcasthistory'),
 (localization.GetByLabel('UI/Fleet/FleetBroadcast/MemberHistory'), 'memberhistory'),
 (localization.GetByLabel('UI/Fleet/FleetBroadcast/LootHistory'), 'loothistory'))

class BroadcastHistoryPanel(Container):
    __notifyevents__ = ['OnFleetBroadcast_Local',
     'OnFleetLootEvent_Local',
     'OnFleetBroadcastFilterChange',
     'OnFleetJoin_Local',
     'OnFleetLeave_Local',
     'OnFleetMemberChanged_Local']

    def PostStartup(self):
        sm.RegisterNotify(self)
        self.sr.broadcastHistory = []
        self.broadcastMenuItems = []
        header = self
        header.baseHeight = header.height
        self.panelHistory = Container(name='panelHistory', parent=self)
        historyType = settings.user.ui.Get('fleetHistoryFilter', 'broadcasthistory')
        topCont = Container(parent=self.panelHistory, align=uiconst.TOTOP, height=HEIGHT_COMPACT)
        self.combo = Combo(parent=topCont, options=comboOptions, name='filter', select=historyType, callback=self.LoadHistory, width=145, align=uiconst.TOPLEFT, uniqueUiName=pConst.UNIQUE_NAME_FLEET_HISTORY_FILTER, density=Density.COMPACT)
        self.clearBtn = Button(parent=topCont, label=localization.GetByLabel('UI/Accessories/Calculator/Clear'), func=self.OnClear, align=uiconst.TOPRIGHT, density=Density.COMPACT, variant=ButtonVariant.GHOST)
        self.scrollHistory = Scroll(name='allHistoryScroll', parent=self.panelHistory, align=uiconst.TOALL, padTop=4)

    def ClearHistory(self, args):
        fleetSvc = sm.GetService('fleet')
        if args == 'broadcasthistory':
            fleetSvc.broadcastHistory = []
        elif args == 'loothistory':
            fleetSvc.lootHistory = []
        elif args == 'memberhistory':
            fleetSvc.memberHistory = []
        elif args == 'all':
            fleetSvc.broadcastHistory = []
            fleetSvc.lootHistory = []
            fleetSvc.memberHistory = []
        self.LoadHistory(self.combo, '', args)

    def LoadPanel(self):
        if not self.sr.Get('inited', 0):
            self.PostStartup()
            setattr(self.sr, 'inited', 1)
        self.LoadHistory(self.combo, '', self.combo.selectedValue)

    def LoadHistory(self, combo, label, value, *args):
        sp = self.scrollHistory.GetScrollProportion()
        self.scrollHistory.multiSelect = 1
        self.scrollHistory.OnChar = self.OnScrollHistoryChar
        if value == 'broadcasthistory':
            scrolllist, hint = self.LoadBroadcastHistory()
            self.scrollHistory.multiSelect = 0
            self.scrollHistory.OnChar = self.OnScrollBroadcastChar
        elif value == 'loothistory':
            scrolllist, hint = self.LoadLootHistory()
        elif value == 'memberhistory':
            scrolllist, hint = self.LoadMemberHistory()
        else:
            scrolllist, hint = self.LoadAllHistory()
        settings.user.ui.Set('fleetHistoryFilter', value)
        self.scrollHistory.Load(contentList=scrolllist, scrollTo=sp, headers=[], noContentHint=hint)

    def LoadAllHistory(self):
        allHistory = []
        broadcastHistory, hint = self.LoadBroadcastHistory()
        memberHistory, hint = self.LoadMemberHistory()
        lootHistory, hint = self.LoadLootHistory()
        allHistory.extend(broadcastHistory)
        allHistory.extend(memberHistory)
        allHistory.extend(lootHistory)
        allHistory.sort(key=lambda x: x.time, reverse=True)
        hint = localization.GetByLabel('UI/Fleet/FleetBroadcast/NoEventsYet')
        return (allHistory, hint)

    def LoadBroadcastHistory(self):
        scrolllist = []
        broadcastHistory = sm.GetService('fleet').GetBroadcastHistory()
        for kv in broadcastHistory:
            data = self.GetBroadcastListEntry(kv)
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/DateWords/Time'), kv.time)
            data.time = kv.time
            data.OnClick = self.OnBroadcastClick
            scrolllist.append(GetFromClass(BroadcastEntry, data))

        hint = localization.GetByLabel('UI/Fleet/FleetBroadcast/NoEventsYet')
        return (scrolllist, hint)

    def OnBroadcastClick(self, entry):
        data = entry.sr.node.data
        itemID = data.itemID
        if data.itemID == session.shipid or session.shipid is None or data.itemID is None or IsUniverseCelestial(data.itemID):
            return
        GetMenuService().TacticalItemClicked(itemID)

    def LoadLootHistory(self):
        scrolllist = []
        lootHistory = sm.GetService('fleet').GetLootHistory()
        for kv in lootHistory:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastEventLoot', time=kv.time, charID=kv.charID, item=kv.typeID, itemQuantity=kv.quantity)
            data = KeyVal(charID=kv.charID, label=label, GetMenu=self.GetLootMenu, data=kv)
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/DateWords/Time'), kv.time)
            data.time = kv.time
            scrolllist.append(GetFromClass(Generic, data))

        hint = localization.GetByLabel('UI/Fleet/FleetBroadcast/NoEventsYet')
        return (scrolllist, hint)

    def LoadMemberHistory(self):
        scrolllist = []
        memberHistory = sm.GetService('fleet').GetMemberHistory()
        for kv in memberHistory:
            label = localization.GetByLabel('UI/Fleet/FleetBroadcast/Event', time=kv.time, eventLabel=kv.event)
            data = KeyVal(charID=kv.charID, label=label, GetMenu=self.GetMemberMenu, data=kv)
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/DateWords/Time'), kv.time)
            data.time = kv.time
            scrolllist.append(GetFromClass(Generic, data))

        hint = localization.GetByLabel('UI/Fleet/FleetBroadcast/NoEventsYet')
        return (scrolllist, hint)

    def OpenSettings(self):
        BroadcastSettings.Open()

    def OnClear(self, *args):
        selectedValue = self.combo.selectedValue
        self.ClearHistory(selectedValue)

    def OnScrollHistoryChar(self, *args):
        Scroll.OnChar(self, *args)

    def OnScrollBroadcastChar(self, *args):
        return False

    def GetBroadcastListEntry(self, data):
        label = localization.GetByLabel('UI/Fleet/FleetBroadcast/Event', time=data.time, eventLabel=data.broadcastLabel)
        colorcoded = settings.user.ui.Get(fleetBroadcastConst.BROADCAST_COLOR_SETTING % data.name, None)
        data2 = KeyVal(charID=data.charID, label=label, GetMenu=self.GetBroadcastMenu, data=data, colorcoded=colorcoded)
        return data2

    def OnFleetLootEvent_Local(self):
        selectedValue = self.combo.selectedValue
        if selectedValue in ('loothistory', 'all'):
            self.LoadHistory(self.combo, '', selectedValue)

    def OnFleetJoin_Local(self, rec):
        selectedValue = self.combo.selectedValue
        if selectedValue in ('memberhistory', 'all'):
            self.LoadHistory(self.combo, '', selectedValue)

    def OnFleetLeave_Local(self, rec):
        selectedValue = self.combo.selectedValue
        if selectedValue in ('memberhistory', 'all'):
            self.LoadHistory(self.combo, '', selectedValue)

    def OnFleetMemberChanged_Local(self, *args):
        selectedValue = self.combo.selectedValue
        if selectedValue in ('memberhistory', 'all'):
            self.LoadHistory(self.combo, '', selectedValue)

    def GetBroadcastMenu(self, entry):
        m = []
        data = entry.sr.node.data
        func = getattr(fleetbr, 'GetMenu_%s' % data.name, None)
        if func:
            args = (data.charID, data.solarSystemID, data.itemID)
            if getattr(data, 'typeID', None):
                args += (data.typeID,)
            m = func(*args)
            m += [None]
        m += fleetbr.GetMenu_Member(data.charID)
        m += [None]
        m += fleetbr.GetMenu_Ignore(data.name)
        return m

    def GetLootMenu(self, entry):
        m = []
        data = entry.sr.node.data
        m += GetMenuService().GetMenuFromItemIDTypeID(None, data.typeID, includeMarketDetails=True)
        m += [None]
        m += fleetbr.GetMenu_Member(data.charID)
        return m

    def GetMemberMenu(self, entry):
        m = []
        data = entry.sr.node.data
        m += fleetbr.GetMenu_Member(data.charID)
        return m

    def OnFleetBroadcast_Local(self, broadcast):
        self.RefreshBroadcastHistory()

    def OnFleetBroadcastFilterChange(self):
        self.RefreshBroadcastHistory()

    def RefreshBroadcastHistory(self):
        selectedValue = self.combo.selectedValue
        if selectedValue in ('broadcasthistory', 'all'):
            self.LoadHistory(self.combo, '', selectedValue)


def CopyFunctions(class_, locals_):
    for name, fn in class_.__dict__.iteritems():
        if type(fn) is type(CopyFunctions):
            if name in locals_:
                raise RuntimeError, 'What are you trying to do here?'
            locals_[name] = fn


class BroadcastSettings(Window):
    __guid__ = 'form.BroadcastSettings'
    default_windowID = 'broadcastsettings'
    default_captionLabelPath = 'UI/Fleet/FleetBroadcast/BroadcastSettings'
    default_width = 480
    default_height = 380
    default_minSize = (300, 200)

    def ApplyAttributes(self, attributes):
        self.shareContainer = None
        Window.ApplyAttributes(self, attributes)
        self.sr.main.left = self.sr.main.width = self.sr.main.top = self.sr.main.height = uiconst.defaultPadding
        eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Fleet/FleetBroadcast/BroadcastSettingsHelp'), parent=self.sr.main, align=uiconst.TOTOP, padding=(20, 0, 6, 0), state=uiconst.UI_NORMAL)
        Container(name='push', parent=self.sr.main, align=uiconst.TOTOP, height=6)
        shareParent = Container(name='shareParent', parent=self.sr.main, align=uiconst.TOBOTTOM, height=36, padTop=4)
        self.sr.scrollBroadcasts = Scroll(name='scrollBroadcasts', parent=self.sr.main)
        self.sr.scrollBroadcasts.multiSelect = 0
        self.LoadFilters()
        from eve.client.script.ui.control.draggableShareContainer import DraggableShareContainer
        defaultText = localization.GetByLabel('UI/Fleet/FleetBroadcast/SharedBroadcastSettings', charID=session.charid)
        currentText = settings.char.ui.Get('sharedBroadcastDragCont_name', '')
        currentText = currentText.strip() or defaultText
        self.shareContainer = DraggableShareContainer(parent=shareParent, currentText=currentText, defaultText=defaultText, align=uiconst.BOTTOMRIGHT, configName='sharedBroadcastDragCont', getDragDataFunc=self.OnFilterDragged, hintText=localization.GetByLabel('UI/Fleet/FleetBroadcast/ShareBroadcastSettingsHint'), maxLength=60)

    def OnFilterDragged(self, text, *args):
        text = text or localization.GetByLabel('UI/Fleet/FleetBroadcast/SharedBroadcastSettings', charID=session.charid)
        broadcastSettings = self.GetDataForSharing()
        data = {'broadcastSettings': broadcastSettings}
        sharedSettingKeyVal = KeyVal(__guid__='fakeentry.BroadcastSharing', data=data, label=text)
        return [sharedSettingKeyVal]

    def GetDataForSharing(self):
        nameToFlag = {y:x for x, y in fleetBroadcastConst.flagToName.iteritems()}
        data = []
        for name in fleetBroadcastConst.broadcastNames.iterkeys():
            isChecked = bool(settings.user.ui.Get(fleetBroadcastConst.LISTEN_BROADCAST_SETTING % name, True))
            colorcoded = settings.user.ui.Get(fleetBroadcastConst.BROADCAST_COLOR_SETTING % name, None)
            if name == BROADCAST_SHOW_OWN:
                flag = BROADCAST_SHOW_OWN
            else:
                flag = nameToFlag.get(name)
            data.append((flag, isChecked, colorcoded))

        return data

    def LoadFilters(self):
        scrolllist = []
        for name, labelName in fleetBroadcastConst.broadcastNames.iteritems():
            data = KeyVal()
            if name == 'Event':
                rngName = ''
            else:
                rng = fleetbr.GetBroadcastWhere(name)
                rngName = fleetbr.GetBroadcastWhereName(rng)
            if name == BROADCAST_SHOW_OWN:
                data.showColorPicker = False
                checkedDefault = False
            else:
                data.showColorPicker = True
                checkedDefault = True
                data.hint = '%s:<br>%s' % (localization.GetByLabel('UI/Fleet/FleetBroadcast/RecipientRange'), rngName)
            data.label = localization.GetByLabel(labelName)
            data.props = None
            data.checked = bool(settings.user.ui.Get(fleetBroadcastConst.LISTEN_BROADCAST_SETTING % name, checkedDefault))
            data.cfgname = name
            data.retval = None
            data.colorcoded = settings.user.ui.Get(fleetBroadcastConst.BROADCAST_COLOR_SETTING % name, None)
            data.OnChange = self.Filter_OnCheckBoxChange
            scrolllist.append(GetFromClass(BroadcastSettingsEntry, data))

        self.sr.scrollBroadcasts.sr.id = 'scrollBroadcasts'
        self.sr.scrollBroadcasts.Load(contentList=scrolllist)

    def Filter_OnCheckBoxChange(self, cb, *args):
        sm.GetService('fleet').SetListenBroadcast(cb.GetSettingsKey(), cb.checked)

    def _OnResize(self, *args, **kw):
        if self.shareContainer is None:
            return
        self.shareContainer.SetMaxWidth(self.width - 2 * self.shareContainer.left - 10)


class BroadcastSettingsEntry(CheckboxEntry):
    colorList = [(1.0, 0.7, 0.0),
     (1.0, 0.35, 0.0),
     (0.75, 0.0, 0.0),
     (0.1, 0.6, 0.1),
     (0.0, 0.63, 0.57),
     (0.2, 0.5, 1.0),
     (0.0, 0.15, 0.6),
     (0.0, 0.0, 0.0),
     (0.7, 0.7, 0.7)]

    def Startup(self, *args):
        CheckboxEntry.Startup(self, *args)
        self.colorPicker = evefleet.client.FleetColorPickerCont(parent=self, idx=0, callback=self.SetBroadcastTypeColor)

    def Load(self, node):
        CheckboxEntry.Load(self, node)
        if node.showColorPicker:
            self.colorPicker.display = True
            self.colorPicker.SetCurrentFill(self.sr.node.colorcoded)
        else:
            self.colorPicker.display = False

    def GetColorTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def GetTooltipDelay(self):
        return 50

    def SetBroadcastTypeColor(self, color, colorPicker, *args):
        settings.user.ui.Set(fleetBroadcastConst.BROADCAST_COLOR_SETTING % self.sr.node.cfgname, color)
        self.sr.node.colorcoded = color
        sm.ScatterEvent('OnFleetBroadcastFilterChange')

    def _OnResize(self):
        w, h = self.GetAbsoluteSize()
        availableWidth = w - self.sr.label.left - self.colorPicker.colorCont.width - 10
        textwidth = self.sr.label.textwidth
        if textwidth > availableWidth:
            fadeEnd = availableWidth
            self.sr.label.SetRightAlphaFade(fadeEnd, maxFadeWidth=20)
        else:
            self.sr.label.SetRightAlphaFade(0, maxFadeWidth=0)


class BroadcastEntry(Generic):

    def Startup(self, *args):
        Generic.Startup(self, *args)
        self.colorcodedFill = Fill(bgParent=self, color=(0, 0, 0, 0))

    def Load(self, node):
        Generic.Load(self, node)
        if node.colorcoded:
            fillColor = node.colorcoded + (0.25,)
            self.colorcodedFill.SetRGBA(*fillColor)
