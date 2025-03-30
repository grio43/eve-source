#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\propertyHandlers\locationPropertyHandler.py
import logging
import eveLocalization
from eve.common.script.sys.idCheckers import IsCelestial, IsConstellation, IsRegion, IsSolarSystem, IsStation
from eveprefs import boot
from localization import const as locconst
from localization.logger import LogInfo, LogWarn
from localization.propertyHandlers.basePropertyHandler import BasePropertyHandler
log = logging.getLogger(__name__)

class LocationPropertyHandler(BasePropertyHandler):
    PROPERTIES = {locconst.CODE_UNIVERSAL: ('name', 'rawName')}

    def _GetName(self, locationID, languageID, *args, **kwargs):
        try:
            return cfg.evelocations.Get(locationID).locationName
        except KeyError:
            msg = '[no location: %d]' % locationID
            log.warning(msg, exc_info=1)
            return msg

    def _GetRawName(self, locationID, languageID, *args, **kwargs):
        try:
            return cfg.evelocations.Get(locationID).GetRawName(languageID)
        except KeyError:
            msg = '[no location: %d]' % locationID
            log.warning(msg, exc_info=1)
            return msg

    if boot.role != 'client':
        _GetName = _GetRawName

    def Linkify(self, locationID, linkText):
        if IsRegion(locationID):
            locationTypeID = const.typeRegion
        elif IsConstellation(locationID):
            locationTypeID = const.typeConstellation
        elif IsSolarSystem(locationID):
            locationTypeID = const.typeSolarSystem
        else:
            if IsCelestial(locationID):
                warnText = "LOCALIZATION ERROR: 'linkify' argument used for a location of type celestial."
                warnText += " This is not supported. Please use the 'linkinfo' tag with arguments instead. locID:"
                LogWarn(warnText, locationID)
                return linkText
            if IsStation(locationID):
                try:
                    if locationID in cfg.oldStations:
                        locationTypeID = cfg.oldStations.Get(locationID).stationTypeID
                    else:
                        locationTypeID = cfg.stations.Get(locationID).stationTypeID
                except KeyError:
                    return '[no station: %d]' % locationID

            else:
                structure = sm.GetService('structureDirectory').GetStructureInfo(locationID)
                if structure is not None:
                    locationTypeID = structure.typeID
                else:
                    LogInfo("LOCALIZATION LINK: The 'linkify' argument was used for a location whose type can not be identified.", locationID)
                    return linkText
        return '<a href=showinfo:%d//%d>%s</a>' % (locationTypeID, locationID, linkText)


eveLocalization.RegisterPropertyHandler(eveLocalization.VARIABLE_TYPE.LOCATION, LocationPropertyHandler())
