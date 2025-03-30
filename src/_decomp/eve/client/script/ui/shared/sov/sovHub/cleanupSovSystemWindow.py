#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\cleanupSovSystemWindow.py
import localization
from eve.common.script.sys import idCheckers
import gametime
import uthread2
import carbonui
from carbonui.control.window import Window
from carbonui.window.control.action import CloseWindowAction
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.scroll import Scroll
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.entries.checkbox import CheckboxEntry
from eve.client.script.ui.control.message import ShowQuickMessage

def open_sov_system_cleanup():
    CleanupSovSystemWindow.CloseIfOpen()
    if not sm.GetService('sov').CanCleanUpSystem():
        ShowQuickMessage(localization.GetByLabel('UI/Sovereignty/SovHub/SystemCleanup/NotAllowedMessage'))
        return
    if not bool(sm.GetService('sov').GetStructuresAvailableToCleanUp()):
        ShowQuickMessage(localization.GetByLabel('UI/Sovereignty/SovHub/SystemCleanup/NoStructuresMessage'))
        return
    window = CleanupSovSystemWindow.Open()
    window.ShowDialog(modal=True, closeWhenClicked=True)


class CleanupSovSystemWindow(Window):
    default_name = 'CleanupSovSystemWindow'
    default_windowID = 'cleanup_sov_system'
    default_captionLabelPath = 'UI/Sovereignty/SovHub/SystemCleanup/WindowTitle'
    default_width = 600
    default_height = 300
    default_isStackable = False
    default_isCollapseable = False
    default_isCompact = True
    __notifyevents__ = ['OnSessionChanged']

    def OnSessionChanged(self, isRemote, session, change):
        if 'locationid' in change:
            self.Close()

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        self.SetSize(self.default_width, self.default_height)
        skyhook_entries = self._get_entries()
        carbonui.TextBody(parent=self.content, align=carbonui.Align.TOTOP, text=localization.GetByLabel('UI/Sovereignty/SovHub/SystemCleanup/WindowBody', numSkyhooks=len(skyhook_entries)))
        self._time_remaining_label = carbonui.TextBody(parent=self.content, align=carbonui.Align.TOTOP)
        button_container = ContainerAutoSize(parent=self.content, align=carbonui.Align.TOBOTTOM)
        self._button = Button(parent=button_container, align=carbonui.Align.CENTERRIGHT, label=localization.GetByLabel('UI/Sovereignty/SovHub/SystemCleanup/ConfirmButton'), func=self._destroy_selected)
        self._button.enabled = bool(skyhook_entries)
        self._scroll = Scroll(parent=self.content, align=carbonui.Align.TOALL, id='sov_system_cleanup', padBottom=8, padTop=8)
        self._scroll.GetEffectiveColumnOffset = lambda *args: 24
        self._select_all_checkbox = Checkbox(parent=self._scroll, align=carbonui.Align.TOPLEFT, checked=bool(skyhook_entries), left=4, callback=self._select_all, idx=0, top=-1)
        self._scroll.LoadContent(contentList=skyhook_entries, headers=(localization.GetByLabel('UI/Common/Name'), localization.GetByLabel('UI/Common/Corporation'), localization.GetByLabel('UI/Common/Alliance')))
        uthread2.start_tasklet(self._time_remaining_thread)

    def _get_entries(self):
        result = []
        for item in sm.GetService('sov').GetStructuresAvailableToCleanUp():
            data = {'label': '%s<t>%s<t>%s' % (localization.GetByLabel('UI/OrbitalSkyhook/SkyhookWnd/SlimSkyhookName', typeID=item.typeID, planetID=item.planetID), cfg.eveowners.Get(item.ownerID).name, cfg.eveowners.Get(item.allianceID).name if item.allianceID else ''),
             'checked': True,
             'OnChange': self._selection_changed,
             'item_id': item.itemID,
             'disabled': False}
            entry = GetFromClass(CheckboxEntry, data)
            result.append(entry)

        return result

    def _selection_changed(self, *args, **kwargs):
        self._update_button_state()
        self._select_all_checkbox.SetChecked(all((entry.checked for entry in self._scroll.GetNodes())), False)

    def _update_button_state(self):
        self._button.enabled = not self._button.busy and any((entry.checked and not entry.disabled for entry in self._scroll.GetNodes()))

    def _select_all(self, checkbox, *args, **kwargs):
        checked = checkbox.checked
        for entry in self._scroll.GetNodes():
            if not entry or entry.disabled:
                continue
            entry.checked = checked
            if entry.panel:
                entry.panel.sr.checkbox.SetChecked(checked, 0)

        self._update_button_state()

    def _destroy_selected(self, *args, **kwargs):
        self._button.disabled = True
        self._button.busy = True
        if not sm.GetService('sov').CanCleanUpSystem():
            ShowQuickMessage(localization.GetByLabel('UI/Sovereignty/SovHub/SystemCleanup/NotAllowedMessage'))
            self.Close()
            return
        skyhook_ids = set((entry.item_id for entry in self._scroll.GetNodes() if entry.checked))
        destroyed_ids = sm.GetService('sov').CleanUpSystem(skyhook_ids)
        if destroyed_ids is None:
            ShowQuickMessage(localization.GetByLabel('UI/Sovereignty/SovHub/SystemCleanup/FailedMessage'))
            self.Close()
            return
        for entry in self._scroll.GetNodes():
            if entry.item_id not in destroyed_ids:
                continue
            entry.checked = True
            entry.disabled = True
            if entry.panel:
                entry.panel.sr.checkbox.SetChecked(True, 0)
                entry.panel.sr.checkbox.disabled = True
                entry.panel.sr.label.SetTextColor(carbonui.TextColor.DANGER)

        self._button.busy = False
        self._update_button_state()

    def _time_remaining_thread(self):
        hub_info = sm.GetService('sov').GetInfrastructureHubInfo(session.solarsystemid2)
        end_time = hub_info.claimTime + gametime.HOUR
        while not self.destroyed:
            self._time_remaining_label.text = localization.GetByLabel('UI/Sovereignty/SovHub/SystemCleanup/TimeRemaining', timeRemaining=max(0, gametime.GetTimeDiff(gametime.GetWallclockTime(), end_time)))
            uthread2.sleep(0.5)

    def _get_window_actions(self):
        return [CloseWindowAction(self)]
