#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\filterContProvider.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.ui.filters.agentFinderFiltersCont import AgentFinderFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.filters.agentsFiltersCont import AgentsFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.filters.asteroidBeltFiltersCont import AsteroidBeltFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.filters.baseFiltersCont import BaseFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.filters.essFiltersCont import ESSFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.filters.factionalWarfareAgentsFiltersCont import FactionalWarfareAgentsFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.filters.factionalWarfareSystemFiltersCont import FactionalWarfareSystemFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.filters.homefrontSitesFiltersCont import HomefrontSitesFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.filters.pirateInsurgenceSystemFilterCont import PirateInsurgenceSystemFilterCont
from eve.client.script.ui.shared.agencyNew.ui.filters.planetaryProductionSystemFiltersCont import PlanetaryProductionSystemFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.filters.colonyResourcesAgencyFiltersCont import ColonyResourceAgencyFiltersCont

def GetFilterCls(contentType):
    if contentType in agencyConst.MISSION_AGENT_CONTENT_TYPES:
        return AgentsFiltersCont
    if contentType == agencyConst.CONTENTTYPE_AGENTS:
        return AgentFinderFiltersCont
    if contentType == agencyConst.CONTENTTYPE_ASTEROIDBELTS:
        return AsteroidBeltFiltersCont
    if contentType == agencyConst.CONTENTTYPE_FACTIONALWARFAREAGENTS:
        return FactionalWarfareAgentsFiltersCont
    if contentType == agencyConst.CONTENTTYPE_FACTIONALWARFARESYSTEM:
        return FactionalWarfareSystemFiltersCont
    if contentType == agencyConst.CONTENTTYPE_PLANETARYPRODUCTION:
        return PlanetaryProductionSystemFiltersCont
    if contentType == agencyConst.CONTENTTYPE_ESS:
        return ESSFiltersCont
    if contentType == agencyConst.CONTENTTYPE_HOMEFRONT_SITES:
        return HomefrontSitesFiltersCont
    if contentType == agencyConst.CONTENTTYPE_PIRATEINSURGENCESYSTEM:
        return PirateInsurgenceSystemFilterCont
    if contentType == agencyConst.CONTENTTYPE_COLONYRESOURCESAGENCY:
        return ColonyResourceAgencyFiltersCont
    if contentType in (agencyConst.CONTENTTYPE_INCURSIONS,
     agencyConst.CONTENTTYPE_SIGNATURES,
     agencyConst.CONTENTTYPE_SITES,
     agencyConst.CONTENTTYPE_OREANOMALY,
     agencyConst.CONTENTTYPE_ICEBELTS,
     agencyConst.CONTENTTYPE_PIRATE_STRONGHOLD):
        return BaseFiltersCont
