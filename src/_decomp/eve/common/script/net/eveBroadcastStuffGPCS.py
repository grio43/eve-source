#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\net\eveBroadcastStuffGPCS.py
from carbon.common.script.net import machoNetAddress, machoNetPacket
from carbon.common.script.net.BroadcastStuffGPCS import CoreBroadcastStuff
from carbon.common.script.sys import basesession

class BroadcastStuff(CoreBroadcastStuff):
    __guid__ = 'gpcs.BroadcastStuff'

    def SinglecastByRegionID(self, regionid, method, *args):
        callTimer = basesession.CallTimer('SinglecastByRegionID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='regionid', narrowcast=[regionid]), payload=(1, args)))
        finally:
            callTimer.Done()

    def NarrowcastBySolarSystemIDs(self, solarsystemids, method, *args):
        if not solarsystemids:
            return
        callTimer = basesession.CallTimer('NarrowcastBySolarSystemIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='solarsystemid', narrowcast=solarsystemids), payload=(1, args)))
        finally:
            callTimer.Done()

    def SinglecastBySolarSystemID(self, solarsystemid, method, *args):
        callTimer = basesession.CallTimer('SinglecastBySolarSystemID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='solarsystemid', narrowcast=[solarsystemid]), payload=(1, args)))
        finally:
            callTimer.Done()

    def NarrowcastBySolarSystemID2s(self, solarsystemid2s, method, *args):
        if not solarsystemid2s:
            return
        callTimer = basesession.CallTimer('NarrowcastBySolarSystemID2s::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='solarsystemid2', narrowcast=solarsystemid2s), payload=(1, args)))
        finally:
            callTimer.Done()

    def SinglecastBySolarSystemID2(self, solarsystemid2, method, *args):
        callTimer = basesession.CallTimer('SinglecastBySolarSystemID2::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='solarsystemid2', narrowcast=[solarsystemid2]), payload=(1, args)))
        finally:
            callTimer.Done()

    def NarrowcastByCorporationIDs(self, corpids, method, *args):
        if not corpids:
            return
        callTimer = basesession.CallTimer('NarrowcastByCorporationIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='corpid', narrowcast=corpids), payload=(1, args)))
        finally:
            callTimer.Done()

    def SinglecastByCorporationID(self, corpid, method, *args):
        callTimer = basesession.CallTimer('SinglecastByCorporationID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='corpid', narrowcast=[corpid]), payload=(1, args)))
        finally:
            callTimer.Done()

    def NarrowcastByAllianceIDs(self, allianceids, method, *args):
        if not allianceids:
            return
        callTimer = basesession.CallTimer('NarrowcastByAllianceIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='allianceid', narrowcast=allianceids), payload=(1, args)))
        finally:
            callTimer.Done()

    def SinglecastByAllianceID(self, allianceid, method, *args):
        callTimer = basesession.CallTimer('SinglecastByAllianceID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='allianceid', narrowcast=[allianceid]), payload=(1, args)))
        finally:
            callTimer.Done()

    def NarrowcastByFleetIDs(self, fleetids, method, *args):
        if not fleetids:
            return
        callTimer = basesession.CallTimer('NarrowcastByFleetIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='fleetid', narrowcast=fleetids), payload=(1, args)))
        finally:
            callTimer.Done()

    def SinglecastByFleetID(self, fleetid, method, *args):
        callTimer = basesession.CallTimer('SinglecastByFleetID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='fleetid', narrowcast=[fleetid]), payload=(1, args)))
        finally:
            callTimer.Done()

    def NarrowcastByShipIDs(self, shipids, method, *args):
        if not shipids:
            return
        callTimer = basesession.CallTimer('NarrowcastByShipIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='shipid', narrowcast=shipids), payload=(1, args)))
        finally:
            callTimer.Done()

    def SinglecastByShipID(self, shipid, method, *args):
        callTimer = basesession.CallTimer('SinglecastByShipID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='shipid', narrowcast=[shipid]), payload=(1, args)))
        finally:
            callTimer.Done()

    def NarrowcastByStationIDs(self, stationids, method, *args):
        if not stationids:
            return
        callTimer = basesession.CallTimer('NarrowcastByStationIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='stationid', narrowcast=stationids), payload=(1, args)))
        finally:
            callTimer.Done()

    def SinglecastByStationID(self, stationid, method, *args):
        callTimer = basesession.CallTimer('SinglecastByStationID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='stationid', narrowcast=[stationid]), payload=(1, args)))
        finally:
            callTimer.Done()

    def NarrowcastByStructureIDs(self, structureids, method, *args):
        if not structureids:
            return
        callTimer = basesession.CallTimer('NarrowcastByStructureIDs::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='structureid', narrowcast=structureids), payload=(1, args)))
        finally:
            callTimer.Done()

    def SinglecastByStructureID(self, structureid, method, *args):
        callTimer = basesession.CallTimer('SinglecastByStructureID::%s (Broadcast\\Client)' % method)
        try:
            self.ForwardNotifyDown(machoNetPacket.Notification(destination=machoNetAddress.MachoAddress(broadcastID=method, idtype='structureid', narrowcast=[structureid]), payload=(1, args)))
        finally:
            callTimer.Done()
