#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\qa\skin_states_table.py
import carbonui.const as uiconst
from cosmetics.client.ships.ship_skin_signals import on_skin_state_set
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.entries.generic import Generic
from carbon.common.script.sys.serviceConst import ROLE_GML

class SkinStatesTableWindow(Window):
    __guid__ = 'SkinStatesTableWindow'
    default_width = 600
    default_height = 600
    default_windowID = 'skinStatesTableWindow'
    default_minSize = [default_width, default_height]

    def __init__(self, *args):
        super(SkinStatesTableWindow, self).__init__(*args)
        self.SetCaption('Ship Skin States')
        self._rebuilding = False
        self.scroll = Scroll(name='scroll', parent=self.sr.maincontainer, align=uiconst.TOALL)
        self.populate()
        on_skin_state_set.connect(self._on_skin_state_set)

    def _OnClose(self, *args, **kw):
        on_skin_state_set.disconnect(self._on_skin_state_set)
        super(SkinStatesTableWindow, self)._OnClose(*args, **kw)

    def populate(self):
        self._rebuilding = True
        cached_states = sm.GetService('cosmeticsSvc')._skin_state_controller._cache
        entries = []
        for ship_id, skin_state in cached_states.iteritems():
            data = [ str(x) or '' for x in [skin_state.character_id,
             skin_state.ship_instance_id,
             skin_state.skin_type,
             skin_state.skin_data] ]
            entries.append(GetFromClass(SkinStateCacheEntry, {'label': '<t>'.join(data),
             'skin_state': skin_state}))

        self.scroll.Load(contentList=entries, headers=self._get_headers())
        self._rebuilding = False

    def _get_headers(self):
        return ['char id',
         'ship id',
         'skin type',
         'skin data']

    def _on_skin_state_set(self, ship_id, skin_state):
        if not self._rebuilding:
            self.scroll.Clear()
            self.populate()


class SkinStateCacheEntry(Generic):
    __guid__ = 'listentry.SkinStateCacheEntry'
    __nonpersistvars__ = []

    def GetMenu(self):
        if session and session.role & ROLE_GML:
            menu = [['Flush', self._flush]]
            return menu

    def _flush(self):
        pass
