#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentCards\contentCardProvider.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.ui.contentCards.agentContentCard import AgentContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.anomalySystemContentCard import AnomalySystemContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.asteroidBeltContentCard import AsteroidBeltContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.baseContentCard import BaseContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.careerAgentContentCard import CareerAgentContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.colonyResourcesAgencySystemContentCard import ColonyResourcesAgencySystemContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.epicArcContentCard import EpicArcContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.escalationsSystemContentCard import EscalationsSystemContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.essContentCard import ESSContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.factionWarfareSystemContentCard import FactionWarfareSystemContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.homefrontSitesContentCard import HomefrontSitesContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.iceBeltContentCard import IceBeltContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.incursionContentCard import IncursionContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.oreAnomalyContentCard import OreAnomalyContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.pirateInsurgencySystemCard import PirateInsurgencySystemCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.pirateStrongholdContentCard import PirateStrongholdContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.planetaryProductionSystemContentCard import PlanetaryProductionSystemContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.signatureSystemContentCard import SignatureSystemContentCard
from eve.client.script.ui.shared.agencyNew.ui.contentCards.storylineAgentContentCard import StorylineAgentContentCard
_contentCardClassByContentTypeID = {agencyConst.CONTENTTYPE_AGENTS: AgentContentCard,
 agencyConst.CONTENTTYPE_HERALDRYAGENTS: AgentContentCard,
 agencyConst.CONTENTTYPE_SECURITYAGENTS: AgentContentCard,
 agencyConst.CONTENTTYPE_DISTRIBUTIONAGENTS: AgentContentCard,
 agencyConst.CONTENTTYPE_MININGAGENTS: AgentContentCard,
 agencyConst.CONTENTTYPE_RESEARCHAGENTS: AgentContentCard,
 agencyConst.CONTENTTYPE_LOCATORAGENTS: AgentContentCard,
 agencyConst.CONTENTTYPE_STORYLINEAGENTS: StorylineAgentContentCard,
 agencyConst.CONTENTTYPE_CAREERAGENTS: CareerAgentContentCard,
 agencyConst.CONTENTTYPE_ASTEROIDBELTS: AsteroidBeltContentCard,
 agencyConst.CONTENTTYPE_EPICARCS: EpicArcContentCard,
 agencyConst.CONTENTTYPE_ICEBELTS: IceBeltContentCard,
 agencyConst.CONTENTTYPE_SIGNATURES: SignatureSystemContentCard,
 agencyConst.CONTENTTYPE_SITES: AnomalySystemContentCard,
 agencyConst.CONTENTTYPE_FACTIONALWARFAREAGENTS: AgentContentCard,
 agencyConst.CONTENTTYPE_FACTIONALWARFARESYSTEM: FactionWarfareSystemContentCard,
 agencyConst.CONTENTTYPE_PIRATE_STRONGHOLD: PirateStrongholdContentCard,
 agencyConst.CONTENTTYPE_INCURSIONS: IncursionContentCard,
 agencyConst.CONTENTTYPE_PLANETARYPRODUCTION: PlanetaryProductionSystemContentCard,
 agencyConst.CONTENTTYPE_ESCALATION: EscalationsSystemContentCard,
 agencyConst.CONTENTTYPE_OREANOMALY: OreAnomalyContentCard,
 agencyConst.CONTENTTYPE_ESS: ESSContentCard,
 agencyConst.CONTENTTYPE_HOMEFRONT_SITES: HomefrontSitesContentCard,
 agencyConst.CONTENTTYPE_PIRATEINSURGENCESYSTEM: PirateInsurgencySystemCard,
 agencyConst.CONTENTTYPE_COLONYRESOURCESAGENCY: ColonyResourcesAgencySystemContentCard}

def GetContentCardCls(contentType):
    return _contentCardClassByContentTypeID.get(contentType, BaseContentCard)
