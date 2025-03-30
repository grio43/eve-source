#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\colonyResourcesAgencyPlanetContentPiece.py
import log
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
import eveicon

class ColonyResourcesAgencyPlanetContentPiece(BaseContentPiece):

    def __init__(self, planetColonyResourcesValues, hasVulnerableSkyhook, expiry, *args, **kwargs):
        super(ColonyResourcesAgencyPlanetContentPiece, self).__init__(*args, **kwargs)
        self.planetColonyResourcesValues = planetColonyResourcesValues
        self.planetName = kwargs.get('planetName')
        self.isBlacklisted = self.itemID in cfg.planetBlacklist
        self.hasVulnerableSkyhook = hasVulnerableSkyhook
        self.expiry = expiry

    def GetName(self):
        return self.planetName
