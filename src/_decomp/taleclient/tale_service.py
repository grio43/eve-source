#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\taleclient\tale_service.py
from collections import OrderedDict
from carbon.common.script.sys.service import Service
from talecommon.const import templateClass
from taleclient.active_tale import ActiveTale
from caching import Memoize
from signals import Signal
on_active_tale_added = Signal(signalName='on_active_tale_added')
on_active_tale_updated = Signal(signalName='on_active_tale_updated')
on_active_tale_removed = Signal(signalName='on_active_tale_removed')

class TaleService(Service):
    __guid__ = 'svc.tale'
    __displayname__ = 'Tale Client Service'
    __notifyevents__ = ['OnTaleData',
     'OnTaleRemove',
     'OnInfluenceUpdate',
     'OnSessionChanged']
    __startupdependencies__ = []

    def __init__(self):
        super(TaleService, self).__init__()
        self._active_tales = OrderedDict()

    def OnTaleData(self, solarSystemID, data):
        if solarSystemID != session.solarsystemid2:
            return
        for tale in data.itervalues():
            self._add_active_tale(tale)

    def OnTaleRemove(self, taleID, templateClassID, templateID):
        self._remove_active_tale(taleID)

    def OnInfluenceUpdate(self, taleID, newInfluenceData):
        if taleID in self._active_tales:
            self._active_tales[taleID].influence = newInfluenceData.influence
            on_active_tale_updated(taleID)

    def OnSessionChanged(self, isremote, sess, change):
        if 'solarsystemid2' in change or 'charid' in change:
            self._remove_irrelevant_tales()

    def get_active_tale(self, tale_id):
        return self._active_tales.get(tale_id, None)

    def get_active_tales(self, template_class_id):
        return [ tale for tale in self._active_tales.itervalues() if tale.template_class_id == template_class_id ]

    def get_active_world_event_tales(self):
        return self.get_active_tales(templateClass.worldEvents)

    @Memoize(15)
    def get_global_world_event_tales(self):
        return sm.RemoteSvc('taleMgr').GetGlobalWorldEventTales()

    def _add_active_tale(self, tale):
        if getattr(tale, 'objectiveChainID', None) is None:
            return
        if tale.taleID not in self._active_tales:
            self._active_tales[tale.taleID] = ActiveTale(tale)
            on_active_tale_added(tale.taleID)
            sm.GetService('infoPanel').UpdateWorldEventsPanel()
        else:
            self._active_tales[tale.taleID].update(tale)
            on_active_tale_updated(tale.tale_id)

    def _remove_active_tale(self, tale_id):
        if tale_id not in self._active_tales:
            return
        tale = self._active_tales.pop(tale_id, None)
        if tale:
            tale.close()
            on_active_tale_removed(tale.tale_id)
            sm.GetService('infoPanel').UpdateWorldEventsPanel()

    def _remove_irrelevant_tales(self):
        for tale_id in self._active_tales.keys():
            if self._active_tales[tale_id].solar_system_id != session.solarsystemid2:
                tale = self._active_tales.pop(tale_id, None)
                if tale:
                    tale.close()
                    on_active_tale_removed(tale.tale_id)

        sm.GetService('infoPanel').UpdateWorldEventsPanel()
