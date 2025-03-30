#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\filters\filtersByID.py
from eve.client.script.ui.shared.mapView.filters.mapFilterActualColor import MapFilterActualColor
from eve.client.script.ui.shared.mapView.filters.mapFilterAnomalies import MapFilterAnomalies
from eve.client.script.ui.shared.mapView.filters.mapFilterAsteroidBelts import MapFilterAsteroidBelts
from eve.client.script.ui.shared.mapView.filters.mapFilterIceBelts import MapFilterIceBelts
from eve.client.script.ui.shared.mapView.filters.mapFilterSettledByCorp import MapFilterSettledByCorp
from eve.client.script.ui.shared.mapView.filters.mapFilterSignatures import MapFilterSignatures
from eve.client.script.ui.shared.mapView.filters.mapFilterEDENCOMFortress import MapFilterEDENCOMFortress
from eve.client.script.ui.shared.mapView.filters.mapFilterEDENCOMMinorVictories import MapFilterEDENCOMMinorVictories
from eve.client.script.ui.shared.mapView.filters.mapFilterTriglavianMinorVictories import MapFilterTriglavianMinorVictories
from eve.client.script.ui.shared.maps import mapcommon
_filtersByID = {mapcommon.STARMODE_SETTLED_SYSTEMS_BY_CORP: MapFilterSettledByCorp,
 mapcommon.STARMODE_ICEBELTS: MapFilterIceBelts,
 mapcommon.STARMODE_ASTEROIDBELTS: MapFilterAsteroidBelts,
 mapcommon.STARMODE_SIGNATURES: MapFilterSignatures,
 mapcommon.STARMODE_ANOMALIES: MapFilterAnomalies,
 mapcommon.STARMODE_REAL: MapFilterActualColor,
 mapcommon.STARMODE_EDENCOM_FORTRESS: MapFilterEDENCOMFortress,
 mapcommon.STARMODE_EDENCOM_MINOR_VICTORIES: MapFilterEDENCOMMinorVictories,
 mapcommon.STARMODE_TRIGLAVIAN_MINOR_VICTORIES: MapFilterTriglavianMinorVictories}

def GetFilterByID(filterID):
    return _filtersByID.get(filterID, None)
