#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\characterSheetWindow.py
import telemetry
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import eveui
import inventorycommon.const as invconst
import uthread
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.services.setting import UserSettingBool
from carbonui.uianimations import animations
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from carbonui.control.window import Window
from eve.client.script.ui.shared.neocom.charsheet import PANEL_PLEX, PANEL_SKILLS_HISTORY, PANEL_CHARACTER, PANEL_INTERACTIONS, PANEL_HISTORY, GetPanelName, GetPanelDescription, PANEL_JUMPCLONES, PANEL_ATTRIBUTES, PANEL_SECURITYSTATUS, PANEL_STANDINGS, PANEL_IMPLANTSBOOTERS, PANEL_DECORATIONS, PANEL_HOME_STATION, PANEL_EXPERTSYSTEMS, PANEL_PERSONALIZATION
from eve.client.script.ui.shared.neocom.charsheet.characterPanel import CharacterPanel
from eve.client.script.ui.shared.neocom.charsheet.historyPanel import HistoryPanel
from eve.client.script.ui.shared.neocom.charsheet.interactionsPanel import InteractionsPanel
from eve.client.script.ui.shared.neocom.charsheet.personalizationPanel import PersonalizationPanel
from eve.client.script.ui.shared.neocom.charsheet.plexPanel import PLEXPanel
from eve.client.script.ui.shared.portraitWindow.portraitWindow import PortraitWindow
from eveservices.menu import GetMenuService
from menu import MenuLabel
charsheet_expanded_setting = UserSettingBool('charsheetExpanded', True)
PARENT_PANELS = {PANEL_SKILLS_HISTORY: PANEL_HISTORY,
 PANEL_JUMPCLONES: PANEL_CHARACTER,
 PANEL_ATTRIBUTES: PANEL_CHARACTER,
 PANEL_IMPLANTSBOOTERS: PANEL_CHARACTER,
 PANEL_SECURITYSTATUS: PANEL_INTERACTIONS,
 PANEL_STANDINGS: PANEL_INTERACTIONS,
 PANEL_DECORATIONS: PANEL_CHARACTER,
 PANEL_HOME_STATION: PANEL_CHARACTER,
 PANEL_EXPERTSYSTEMS: PANEL_CHARACTER}
TAB_UNIQUE_NAMES = {PANEL_CHARACTER: pConst.UNIQUE_NAME_CHARSHEET_CHARACTER_TAB,
 PANEL_INTERACTIONS: pConst.UNIQUE_NAME_CHARSHEET_INTERACTION_TAB,
 PANEL_PLEX: pConst.UNIQUE_NAME_PILOT_SERVICES_TAB,
 PANEL_PERSONALIZATION: pConst.UNIQUE_NAME_PERSONALIZATION_TAB}
LEFT_SIDE_WIDTH_EXPANDED = 340
LEFT_SIDE_WIDTH_COLLAPSED = 394
MINSIZE_STACKED = (580, 600)

class CharacterSheetTabNavigationWindowHeader(TabNavigationWindowHeader):

    def __init__(self, **kwargs):
        super(CharacterSheetTabNavigationWindowHeader, self).__init__(**kwargs)

    def mount(self, window):
        super(CharacterSheetTabNavigationWindowHeader, self).mount(window)
        self._update_element_visibility(window)
        window.on_stacked_changed.connect(self._on_stacked_changed)
        charsheet_expanded_setting.on_change.connect(self._on_charsheet_expanded_setting_changed)

    def unmount(self, window):
        super(CharacterSheetTabNavigationWindowHeader, self).unmount(window)
        charsheet_expanded_setting.on_change.disconnect(self._on_charsheet_expanded_setting_changed)

    @staticmethod
    def _get_icon_visible(window):
        return not (window.collapsed or window.compact) and (charsheet_expanded_setting.is_enabled() or window.stacked)

    def _on_stacked_changed(self, window):
        self._update_element_visibility(window)

    def _on_charsheet_expanded_setting_changed(self, value):
        self._update_element_visibility()

    def _update_element_visibility(self, window = None):
        if window is None:
            window = self.window
            if not window:
                return
        self._update_caption_icon_display(window)
        display = charsheet_expanded_setting.is_enabled() or window.stacked
        self._line.display = display
        self.tab_group.display = display


class CharacterSheetWindow(Window):
    __guid__ = 'form.CharacterSheet'
    default_width = 1235
    default_height = 768
    default_minSize = (920, 600)
    default_maxSize = (1600, 900)
    default_left = '__center__'
    default_top = '__center__'
    default_windowID = 'charactersheet'
    default_captionLabelPath = 'UI/CharacterSheet/CharacterSheetWindow/CharacterSheetCaption'
    default_descriptionLabelPath = 'Tooltips/Neocom/CharacterSheet_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/charactersheet.png'
    default_scope = uiconst.SCOPE_INGAME
    default_isCollapseable = False
    leftCont = None

    def OnUIRefresh(self):
        pass

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        from eve.client.script.ui.shared.preview import PreviewCharacterWnd
        PreviewCharacterWnd.CloseIfOpen()
        panelID = attributes.panelID
        self.loading = False
        self.skillsPanel = None
        self.prevWidth = None
        self.animationInProgress = False
        super(CharacterSheetWindow, self).ApplyAttributes(attributes)
        self.ConstructBaseLayout()
        self.ConstructCharacterOverview()
        tabs = self.GetMainTabData()
        for tab_data in tabs:
            label, panel, _, tab_id, _, hint, _ = tab_data
            self.header.tab_group.AddTab(label=label, panel=panel, tabID=tab_id, hint=hint)
            tab = self.header.tab_group.GetTabByID(tab_id)
            unique_ui_name = TAB_UNIQUE_NAMES.get(tab_id, None)
            if unique_ui_name:
                tab.uniqueUiName = unique_ui_name

        if not panelID:
            panelID = self.GetDefaultPanelID()
        self._LoadPanel(panelID, autoExpand=False)
        self._UpdateCharacterSheetExpanded(charsheet_expanded_setting.is_enabled(), animate=False)
        charsheet_expanded_setting.on_change.connect(self._on_expanded_setting_changed)
        self.on_content_padding_changed.connect(self._on_content_padding_changed)
        self.on_header_height_changed.connect(self._on_header_height_changed)
        self.on_stacked_changed.connect(self._on_stacked_changed)

    @property
    def mainTabGroup(self):
        if self.header is not None:
            return self.header.tab_group

    def Prepare_Header_(self):
        self.header = CharacterSheetTabNavigationWindowHeader(on_tab_selected=self.OnMainTabGroup)

    def ConstructBaseLayout(self):
        border_left, _, border_right, border_bottom = self.GetWindowBorderSize()
        self.leftCont = Container(name='leftCont', parent=self.sr.main, align=uiconst.TOLEFT, alignMode=uiconst.TOPLEFT, padding=self._get_left_cont_padding(), width=LEFT_SIDE_WIDTH_EXPANDED, idx=0)
        self.mainCont = Container(name='mainCont', parent=self.sr.main, align=uiconst.TOALL)
        self.panelCont = Container(name='panelCont', parent=self.mainCont)
        self.characterPanel = CharacterPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.interactionsPanel = InteractionsPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.plexPanel = PLEXPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)
        self.personalizationPanel = PersonalizationPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN, emblemsErrorScreenPadding=self.content_padding)
        self.historyPanel = HistoryPanel(parent=self.panelCont, state=uiconst.UI_HIDDEN)

    def GetMainTabData(self):
        tabData = []
        panelsData = [(PANEL_CHARACTER, self.characterPanel, CharacterPanel),
         (PANEL_INTERACTIONS, self.interactionsPanel, InteractionsPanel),
         (PANEL_PLEX, self.plexPanel, PLEXPanel),
         (PANEL_PERSONALIZATION, self.personalizationPanel, PersonalizationPanel),
         (PANEL_HISTORY, self.historyPanel, HistoryPanel)]
        for panelID, panel, panelClass in panelsData:
            tabData.append((GetPanelName(panelID),
             panel,
             None,
             panelID,
             None,
             GetPanelDescription(panelID),
             None))

        return tabData

    def OnMainTabGroup(self, tabID, oldTabID):
        settings.char.ui.Set('charSheetSelectedPanel', tabID)

    def GetDefaultPanelID(self):
        return settings.char.ui.Get('charSheetSelectedPanel', PANEL_HOME_STATION)

    def ConstructCharacterOverview(self):
        from eve.client.script.ui.shared.neocom.charsheet.characterOverviewPanel.characterOverviewPanel import CharacterSheetCharacterOverviewPanel
        self.overviewPanel = CharacterSheetCharacterOverviewPanel(parent=self.leftCont, isCharsheetExpanded=charsheet_expanded_setting.is_enabled(), toggleFunc=self.ToggleCharacterSheetExpanded)

    def ToggleCharacterSheetExpanded(self, *args):
        self._UpdateCharacterSheetExpanded(not charsheet_expanded_setting.is_enabled())

    def _UpdateCharacterSheetExpanded(self, isExpanded, animate = True):
        if self.animationInProgress:
            return
        charsheet_expanded_setting.set(isExpanded)
        if animate:
            self.header.opacity = 0.0
            animations.FadeTo(self.header, self.header.opacity, 1.0, timeOffset=0.3, duration=0.3)
        if isExpanded:
            self._SetExpanded(animate)
            self.overviewPanel.SetExpanded(animate)
        else:
            self._SetNotExpanded(animate)
            self.overviewPanel.SetNotExpanded(animate)

    def _SetNotExpanded(self, animate):
        self.prevWidth = self.width
        if animate:
            self._AnimateCollapse()
        else:
            self.mainCont.opacity = 0.0
            self.mainCont.Hide()
            border_left, _, border_right, border_bottom = self.GetWindowBorderSize()
            self.width = LEFT_SIDE_WIDTH_COLLAPSED + border_left + border_right
            self._update_header_padding()
            self.SetFixedWidth(self.width)
            self.leftCont.width = LEFT_SIDE_WIDTH_COLLAPSED

    def _SetExpanded(self, animate):
        if self.prevWidth is None:
            self.prevWidth = self.width
        self.SetFixedWidth(None)
        if animate:
            self._AnimateExpand()
        else:
            self.mainCont.opacity = 1.0
            self.mainCont.Show()
            self._update_header_padding()
            self.width = self.prevWidth
            self.leftCont.width = LEFT_SIDE_WIDTH_EXPANDED

    def _GetSizeToRegister(self):
        w, h = super(CharacterSheetWindow, self)._GetSizeToRegister()
        if not charsheet_expanded_setting.is_enabled():
            w = None
        return (w, h)

    def _AnimateCollapse(self):
        self.animationInProgress = True
        border_left, _, border_right, border_bottom = self.GetWindowBorderSize()
        window_width = LEFT_SIDE_WIDTH_COLLAPSED + border_left + border_right
        animations.FadeTo(self.mainCont, startVal=self.mainCont.opacity, endVal=0.0, duration=0.3, timeOffset=0.1)
        eveui.animate(self, 'width', end_value=window_width, start_value=self.width, duration=0.3, on_complete=self._OnToggleAnimEnd)
        eveui.animate(self.leftCont, 'width', end_value=LEFT_SIDE_WIDTH_COLLAPSED, start_value=self.leftCont.width, duration=0.2)

    def _AnimateExpand(self):
        self.animationInProgress = True
        self.mainCont.Show()
        animations.FadeTo(self.mainCont, startVal=self.mainCont.opacity, endVal=1.0, duration=0.3, timeOffset=0.1)
        eveui.animate(self, 'width', end_value=self.prevWidth, start_value=self.width, duration=0.3, on_complete=self._OnToggleAnimEnd)
        eveui.animate(self.leftCont, 'width', end_value=LEFT_SIDE_WIDTH_EXPANDED, start_value=self.leftCont.width, duration=0.2)

    def _OnToggleAnimEnd(self):
        self.animationInProgress = False
        if charsheet_expanded_setting.is_enabled():
            self.SetFixedWidth(None)
            self._update_header_padding()
        else:
            self.SetFixedWidth(self.width)
            self.mainCont.Hide()

    def GetMinWidth(self):
        if charsheet_expanded_setting.is_enabled() or self.leftCont is None:
            return super(CharacterSheetWindow, self).GetMinWidth()
        else:
            return self.leftCont.width

    def _LoadPanel(self, panelID, autoExpand = True):
        if panelID in PARENT_PANELS:
            parentPanelID = PARENT_PANELS[panelID]
            tab = self.mainTabGroup.GetTabByID(parentPanelID)
            tab.sr.panel.LoadSubPanel(panelID)
            tab.SaveSelectedTabName()
            self.mainTabGroup.SelectByID(parentPanelID)
        else:
            self.mainTabGroup.SelectByID(panelID)
        if autoExpand and not charsheet_expanded_setting.is_enabled() and not self.InStack():
            self.ToggleCharacterSheetExpanded()

    def GetActivePanelID(self):
        return self.mainTabGroup.GetSelectedID()

    def GetActivePanelIDs(self):
        parentPanelID = self.GetActivePanelID()
        if parentPanelID in PARENT_PANELS.values():
            tab = self.mainTabGroup.GetTabByID(parentPanelID)
            subPanelID = tab.sr.panel.GetActivePanelID()
            return (parentPanelID, subPanelID)
        return (parentPanelID, None)

    def HideAllPanels(self):
        for panel in self.panelCont.children:
            panel.Hide()

    def OpenPortraitWnd(self, *args):
        PortraitWindow.CloseIfOpen()
        PortraitWindow.Open(charID=session.charid)

    @classmethod
    def _OpenPanel(cls, panelID):
        wnd = cls.GetIfOpen()
        if not wnd:
            wnd = cls.Open(panelID=panelID)
        wnd.Maximize()
        uthread.new(wnd._LoadPanel, panelID)

    @classmethod
    def OpenSkillHistory(cls):
        return cls._OpenPanel(PANEL_SKILLS_HISTORY)

    @classmethod
    def OpenJumpClones(cls):
        return cls._OpenPanel(PANEL_JUMPCLONES)

    @classmethod
    def ToggleOpenWithPanel(cls, panelID):
        wnd = cls.GetIfOpen()
        if wnd and panelID in wnd.GetActivePanelIDs():
            wnd.Close()
        else:
            cls._OpenPanel(panelID)

    @classmethod
    def OpenImplantsAndBoosters(cls):
        return cls._OpenPanel(PANEL_IMPLANTSBOOTERS)

    @classmethod
    def OpenSecurityStatus(cls):
        return cls._OpenPanel(PANEL_SECURITYSTATUS)

    @classmethod
    def OpenPLEX(cls):
        return cls._OpenPanel(PANEL_PLEX)

    @classmethod
    def OpenStandings(cls):
        cls._OpenPanel(PANEL_STANDINGS)

    @classmethod
    def OpenDecorations(cls):
        cls._OpenPanel(PANEL_DECORATIONS)

    @classmethod
    def OpenExpertSystems(cls, *args):
        cls._OpenPanel(PANEL_EXPERTSYSTEMS)

    @classmethod
    def OpenSkillHistoryHilightSkills(cls, skillIDs):
        cls.OpenSkillHistory()
        sm.ScatterEvent('OnHighlightSkillHistorySkills', skillIDs)

    @classmethod
    def OpenHomeStation(cls):
        cls._OpenPanel(PANEL_HOME_STATION)

    def DeselectAllNodes(self, wnd):
        for node in wnd.sr.scroll.GetNodes():
            wnd.sr.scroll._DeselectNode(node)

    def GetMenu(self, *args):
        m = Window.GetMenu(self, *args)
        m.append((MenuLabel('UI/Commands/ShowInfo'), GetMenuService().ShowInfo, (invconst.typeCharacter, session.charid)))
        return m

    def OnStackInsert(self, stack):
        self._SetExpanded(animate=False)
        self.overviewPanel.avatarHeaderPreview.DisableRender()
        self.leftCont.Hide()
        self.SetMinSize(MINSIZE_STACKED)
        super(CharacterSheetWindow, self).OnStackInsert(stack)

    def OnStackRemove(self, correctpos, dragging, grab):
        self.leftCont.Show()
        self.overviewPanel.avatarHeaderPreview.EnableRender()
        self.SetMinSize(self.default_minSize)
        self._UpdateCharacterSheetExpanded(isExpanded=True, animate=False)
        super(CharacterSheetWindow, self).OnStackRemove(correctpos, dragging, grab)

    def _GetMinWidth(self):
        if self.GetStackID():
            return MINSIZE_STACKED[0]
        else:
            return super(CharacterSheetWindow, self)._GetMinWidth()

    def Minimize(self, animate = True):
        self.overviewPanel.avatarHeaderPreview.DisableRender()
        super(CharacterSheetWindow, self).Minimize(animate)

    def Maximize(self, retainOrder = False, *args, **kwds):
        if not self._changing:
            super(CharacterSheetWindow, self).Maximize(retainOrder, *args, **kwds)
            if self.leftCont.display:
                self.overviewPanel.avatarHeaderPreview.EnableRender()
            else:
                self.overviewPanel.avatarHeaderPreview.DisableRender()

    def _on_expanded_setting_changed(self, value):
        self._update_left_cont_padding()

    def _on_content_padding_changed(self, window):
        self._update_left_cont_padding()

    def _on_header_height_changed(self, header):
        self._update_left_cont_padding()

    def _update_left_cont_padding(self):
        self.leftCont.padding = self._get_left_cont_padding()

    def _get_left_cont_padding(self):
        border_left, border_top, border_right, border_bottom = self.GetWindowBorderSize()
        pad_left, pad_top, pad_right, pad_bottom = self.content_padding
        header_height = self.header_height
        if charsheet_expanded_setting.is_enabled():
            final_pad_right = pad_right
        else:
            final_pad_right = -(border_right + pad_right)
        return (-(border_left + pad_left),
         -(border_top + pad_top + header_height),
         final_pad_right,
         -(border_bottom + pad_bottom))

    def _on_stacked_changed(self, window):
        self._update_header_padding()

    def _get_header_padding(self):
        if self.stacked:
            return (0, 0, 0, 0)
        expanded = charsheet_expanded_setting.is_enabled()
        if expanded:
            if self.leftCont:
                return (self.leftCont.width,
                 0,
                 0,
                 0)
            else:
                return (0, 0, 0, 0)
        else:
            return (0, 0, 0, 0)

    def _update_header_padding(self):
        self.header.padding = self._get_header_padding()
