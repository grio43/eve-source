#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uihighlighting\uniqueNameChains.py
import logging
import neocom2.btnIDs as btnIDs
import uihighlighting.uniqueNameConst as pConst
from skills.skillplan.skillPlanService import GetSkillPlanSvc
logger = logging.getLogger(__name__)
fittingBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.FITTING_ID)
contractsBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.CONTRACTS_ID)
charactersheetBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.CHARACTER_SHEET_ID)
fleetBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.FLEET_ID)
inventoryBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.INVENTORY_ID)
corpBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.CORP_ID)
industryBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.INDUSTRY_ID)
marketBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.MARKET_ID)
addressbookBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.ADDRESSBOOK_ID)
skillsBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.SKILLS_ID)
locationsBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.LOCATIONS_ID)
mapBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.MAP_BETA_ID)
acpBtnPointer = pConst.GetUniqueNeocomPointerName(btnIDs.AIR_CAREER_PROGRAM_ID)
helpWndPointer = pConst.GetUniqueNeocomPointerName(btnIDs.HELP_ID)
locationsPointer = pConst.GetUniqueNeocomPointerName(btnIDs.LOCATIONS_ID)
skinrPointer = pConst.GetUniqueNeocomPointerName(btnIDs.SHIP_SKINR)
walletPointer = pConst.GetUniqueNeocomPointerName(btnIDs.WALLET_ID)
opportunityPointer = pConst.GetUniqueNeocomPointerName(btnIDs.JOB_BOARD_ID)
skillPlanPre = None
preByUniqueName = {pConst.UNIQUE_NAME_FITTING_EQUIPMENT: fittingBtnPointer,
 pConst.UNIQUE_NAME_FITTING_PERSONALIZATION: fittingBtnPointer,
 pConst.UNIQUE_NAME_FITTING_BROWSER: pConst.UNIQUE_NAME_FITTING_EQUIPMENT,
 pConst.UNIQUE_NAME_CURRENT_FIT: pConst.UNIQUE_NAME_FITTING_EQUIPMENT,
 pConst.UNIQUE_NAME_GROUP_WEAPONS: pConst.UNIQUE_NAME_FITTING_EQUIPMENT,
 pConst.UNIQUE_NAME_SIMULATE_SHIP: pConst.UNIQUE_NAME_FITTING_EQUIPMENT,
 pConst.UNIQUE_NAME_FITING_STATS: pConst.UNIQUE_NAME_FITTING_EQUIPMENT,
 pConst.UNIQUE_NAME_FITTING_INVENTORY: pConst.UNIQUE_NAME_FITTING_EQUIPMENT,
 pConst.UNIQUE_NAME_FITTING_SKIN_BROWSER: pConst.UNIQUE_NAME_FITTING_PERSONALIZATION,
 pConst.UNIQUE_NAME_AVAILABLE_CONTRACTS_TAB: contractsBtnPointer,
 pConst.UNIQUE_NAME_EXPAND_CHARSHEET: charactersheetBtnPointer,
 pConst.UNIQUE_NAME_PROBE_SCANNER: pConst.UNIQUE_NAME_SCANNER_BTN,
 pConst.UNIQUE_NAME_FILTER_SCAN_RESULTS: pConst.UNIQUE_NAME_PROBE_SCANNER,
 pConst.UNIQUE_NAME_PROBE_FORMATIONS: pConst.UNIQUE_NAME_PROBE_SCANNER,
 pConst.UNIQUE_NAME_PROBE_SIZE_MODIFIER: pConst.UNIQUE_NAME_PROBE_SCANNER,
 pConst.UNIQUE_NAME_RECOVER_PROBES: pConst.UNIQUE_NAME_PROBE_SCANNER,
 pConst.UNIQUE_NAME_PROBE_REFRESH: pConst.UNIQUE_NAME_SCANNER_BTN,
 pConst.UNIQUE_NAME_DIRECTIONAL_SCANNER: pConst.UNIQUE_NAME_SCANNER_BTN,
 pConst.UNIQUE_NAME_FLEET_FINDER_TAB: fleetBtnPointer,
 pConst.UNIQUE_NAME_FLEET_HISTORY_TAB: fleetBtnPointer,
 pConst.UNIQUE_NAME_FLEET_SETTINGS: fleetBtnPointer,
 pConst.UNIQUE_NAME_FLEET_MY_FLEET_TAB: fleetBtnPointer,
 pConst.UNIQUE_NAME_FLEET_ACTIVE_RECLONERS_TAB: fleetBtnPointer,
 pConst.UNIQUE_NAME_FLEET_SHOW_BROADCASTS: fleetBtnPointer,
 pConst.UNIQUE_NAME_FLEET_FINDER_SETTINGS: pConst.UNIQUE_NAME_FLEET_FINDER_TAB,
 pConst.UNIQUE_NAME_FLEET_HISTORY_FILTER: pConst.UNIQUE_NAME_FLEET_HISTORY_TAB,
 pConst.UNIQUE_NAME_BROADCAST_ARMOR: pConst.UNIQUE_NAME_FLEET_SHOW_BROADCASTS,
 pConst.UNIQUE_NAME_BROADCAST_SHIELD: pConst.UNIQUE_NAME_FLEET_SHOW_BROADCASTS,
 pConst.UNIQUE_NAME_FLEET_BROADCAST_ICONS: pConst.UNIQUE_NAME_FLEET_SHOW_BROADCASTS,
 pConst.UNIQUE_NAME_INVENTORY_VIEW: inventoryBtnPointer,
 pConst.UNIQUE_NAME_INVENTORY_STACK_ALL: inventoryBtnPointer,
 pConst.UNIQUE_NAME_CORP_CORPORATION_TAB: corpBtnPointer,
 pConst.UNIQUE_NAME_CORP_ADMIN_TAB: corpBtnPointer,
 pConst.UNIQUE_NAME_CORP_ALLIANCES_TAB: corpBtnPointer,
 pConst.UNIQUE_NAME_CORP_HOME_TAB: pConst.UNIQUE_NAME_CORP_CORPORATION_TAB,
 pConst.UNIQUE_NAME_CORP_ASSETS_TAB: pConst.UNIQUE_NAME_CORP_ADMIN_TAB,
 pConst.UNIQUE_NAME_INDUSTRY_COPY_BTN: industryBtnPointer,
 pConst.UNIQUE_NAME_INDUSTRY_FACILITIES_TAB: industryBtnPointer,
 pConst.UNIQUE_NAME_INDUSTRY_INVENTION_BTN: industryBtnPointer,
 pConst.UNIQUE_NAME_INDUSTRY_JOBS_TAB: industryBtnPointer,
 pConst.UNIQUE_NAME_INDUSTRY_MANUF_BTN: industryBtnPointer,
 pConst.UNIQUE_NAME_INDUSTRY_ME_BTN: industryBtnPointer,
 pConst.UNIQUE_NAME_INDUSTRY_TE_BTN: industryBtnPointer,
 pConst.UNIQUE_NAME_INDUSTRY_BP_BTN: industryBtnPointer,
 pConst.UNIQUE_NAME_INDUSTRY_RESEARCH_TAB: industryBtnPointer,
 pConst.UNIQUE_NAME_MARKET_BROWSE_SETTINGS: marketBtnPointer,
 pConst.UNIQUE_NAME_MARKET_DETAILS: marketBtnPointer,
 pConst.UNIQUE_NAME_SKILLQUEUE: skillsBtnPointer,
 pConst.UNIQUE_NAME_APPLY_SP_BTN: skillsBtnPointer,
 pConst.UNIQUE_NAME_START_TRAINING_BTN: skillsBtnPointer,
 pConst.UNIQUE_NAME_SKILL_PLANS_TAB: skillsBtnPointer,
 pConst.UNIQUE_NAME_SKILL_PLANS_CERTIFIED_TAB: pConst.UNIQUE_NAME_SKILL_PLANS_TAB,
 pConst.UNIQUE_NAME_SKILL_PLANS_PERSONAL_TAB: pConst.UNIQUE_NAME_SKILL_PLANS_TAB,
 pConst.UNIQUE_NAME_SKILL_PLANS_CORP_TAB: pConst.UNIQUE_NAME_SKILL_PLANS_TAB,
 pConst.UNIQUE_NAME_ROUTE_SHORTER: pConst.UNIQUE_NAME_AUTOPILOT_SETTINGS,
 pConst.UNIQUE_NAME_ROUTE_SAFER: pConst.UNIQUE_NAME_AUTOPILOT_SETTINGS,
 pConst.UNIQUE_NAME_ROUTE_INCLUDE_JUMP_GATES: pConst.UNIQUE_NAME_AUTOPILOT_SETTINGS,
 pConst.UNIQUE_NAME_CHARSHEET_CHARACTER_TAB: pConst.UNIQUE_NAME_EXPAND_CHARSHEET,
 pConst.UNIQUE_NAME_PILOT_SERVICES_TAB: pConst.UNIQUE_NAME_EXPAND_CHARSHEET,
 pConst.UNIQUE_NAME_CHARSHEET_INTERACTION_TAB: pConst.UNIQUE_NAME_EXPAND_CHARSHEET,
 pConst.UNIQUE_NAME_PERSONALIZATION_TAB: pConst.UNIQUE_NAME_EXPAND_CHARSHEET,
 pConst.UNIQUE_NAME_SKINS_TAB: pConst.UNIQUE_NAME_PERSONALIZATION_TAB,
 pConst.UNIQUE_NAME_EMBLEMS_TAB: pConst.UNIQUE_NAME_PERSONALIZATION_TAB,
 pConst.UNIQUE_NAME_FITTING_HARDWARE: pConst.UNIQUE_NAME_FITTING_BROWSER,
 pConst.UNIQUE_NAME_FITS_IN_FITTING_WND: pConst.UNIQUE_NAME_FITTING_BROWSER,
 pConst.UNIQUE_NAME_FITTING_CAP: pConst.UNIQUE_NAME_FITING_STATS,
 pConst.UNIQUE_NAME_FITTING_DEFENSE: pConst.UNIQUE_NAME_FITING_STATS,
 pConst.UNIQUE_NAME_FITTING_DRONES: pConst.UNIQUE_NAME_FITING_STATS,
 pConst.UNIQUE_NAME_FITTING_NAVIGATION: pConst.UNIQUE_NAME_FITING_STATS,
 pConst.UNIQUE_NAME_FITTING_OFFENSE: pConst.UNIQUE_NAME_FITING_STATS,
 pConst.UNIQUE_NAME_FITTING_TARGETING: pConst.UNIQUE_NAME_FITING_STATS,
 pConst.UNIQUE_NAME_SHOW_BUY_ALL_BTN: pConst.UNIQUE_NAME_FITING_STATS,
 pConst.UNIQUE_NAME_AUGMENTATIONS_TAB: pConst.UNIQUE_NAME_CHARSHEET_CHARACTER_TAB,
 pConst.UNIQUE_NAME_JUMP_CLONES_TAB: pConst.UNIQUE_NAME_CHARSHEET_CHARACTER_TAB,
 pConst.UNIQUE_NAME_CHARSHEET_HOME_TAB: pConst.UNIQUE_NAME_CHARSHEET_CHARACTER_TAB,
 pConst.UNIQUE_NAME_EXPERT_SYSTEMS_TAB: pConst.UNIQUE_NAME_CHARSHEET_CHARACTER_TAB,
 pConst.UNIQUE_NAME_COMMUNITY_FIT_FILTER: pConst.UNIQUE_NAME_FITS_IN_FITTING_WND,
 pConst.UNIQUE_NAME_CORP_FIT_FILTER: pConst.UNIQUE_NAME_FITS_IN_FITTING_WND,
 pConst.UNIQUE_NAME_ALLIANCE_FIT_FILTER: pConst.UNIQUE_NAME_FITS_IN_FITTING_WND,
 pConst.UNIQUE_NAME_SHOW_CONTRACT_OPTIONS: pConst.UNIQUE_NAME_AVAILABLE_CONTRACTS_TAB,
 pConst.UNIQUE_NAME_CONTRACT_AVAILABILITY_SETTINGS: pConst.UNIQUE_NAME_SHOW_CONTRACT_OPTIONS,
 pConst.UNIQUE_NAME_MY_APPLICATIONS: pConst.UNIQUE_NAME_CORP_CORPORATION_TAB,
 pConst.UNIQUE_NAME_CORP_BULLETIN_TAB: pConst.UNIQUE_NAME_CORP_CORPORATION_TAB,
 pConst.UNIQUE_NAME_CORP_PROJECTS: pConst.UNIQUE_NAME_CORP_CORPORATION_TAB,
 pConst.UNIQUE_NAME_FIND_NEW_CORP: pConst.UNIQUE_NAME_CORP_CORPORATION_TAB,
 pConst.UNIQUE_NAME_CHAR_STANDINGS_TAB: pConst.UNIQUE_NAME_CHARSHEET_INTERACTION_TAB,
 pConst.UNIQUE_NAME_SECURITY_STATUS_TAB: pConst.UNIQUE_NAME_CHARSHEET_INTERACTION_TAB,
 pConst.UNIQUE_NAME_COMBAT_LOG_TAB: pConst.UNIQUE_NAME_CHARSHEET_INTERACTION_TAB,
 pConst.UNIQUE_NAME_SHOW_KILL_RIGHTS_TAB: pConst.UNIQUE_NAME_CHARSHEET_INTERACTION_TAB,
 pConst.UNIQUE_NAME_SHOW_KILLS_LOSSES: pConst.UNIQUE_NAME_COMBAT_LOG_TAB,
 pConst.UNIQUE_NAME_MARKET_DATA: pConst.UNIQUE_NAME_MARKET_DETAILS,
 pConst.UNIQUE_NAME_MARKET_FIND_IN_BROWSER: pConst.UNIQUE_NAME_MARKET_DETAILS,
 pConst.UNIQUE_NAME_MARKET_PRICE_HISTORY: pConst.UNIQUE_NAME_MARKET_DETAILS,
 pConst.UNIQUE_NAME_MARKET_SELLER_LIST: pConst.UNIQUE_NAME_MARKET_DATA,
 pConst.UNIQUE_NAME_MARKET_BUYER_LIST: pConst.UNIQUE_NAME_MARKET_DATA,
 pConst.UNIQUE_NAME_MARKET_BUYERS_JUMP_COL: pConst.UNIQUE_NAME_MARKET_BUYER_LIST,
 pConst.UNIQUE_NAME_MARKET_BUYERS_QTY_COL: pConst.UNIQUE_NAME_MARKET_BUYER_LIST,
 pConst.UNIQUE_NAME_MARKET_BUYERS_PRICE_COL: pConst.UNIQUE_NAME_MARKET_BUYER_LIST,
 pConst.UNIQUE_NAME_MARKET_SELLERS_JUMP_COL: pConst.UNIQUE_NAME_MARKET_SELLER_LIST,
 pConst.UNIQUE_NAME_MARKET_SELLERS_QTY_COL: pConst.UNIQUE_NAME_MARKET_SELLER_LIST,
 pConst.UNIQUE_NAME_MARKET_SELLERS_PRICE_COL: pConst.UNIQUE_NAME_MARKET_SELLER_LIST,
 pConst.UNIQUE_NAME_CREATE_CHANNEL_BTN: pConst.UNIQUE_NAME_CHANNEL_WND,
 pConst.UNIQUE_NAME_SENSOR_OVERLAY_SETTING: pConst.UNIQUE_NAME_HUD_SETTINGS,
 pConst.UNIQUE_NAME_SENSOR_OVERLAY: pConst.UNIQUE_NAME_SENSOR_OVERLAY_SETTING,
 pConst.UNIQUE_NAME_REPROCESS_BUTTON: pConst.GetUniqueStationServiceName('reprocessingPlant'),
 pConst.UNIQUE_NAME_MAP_COLOR_SETTINGS: mapBtnPointer,
 pConst.UNIQUE_NAME_ACP_CLAIM_ALL_BUTTON: pConst.UNIQUE_NAME_ACP_REWARDS_CONTAINER,
 pConst.UNIQUE_NAME_ACP_REWARDS_CONTAINER: acpBtnPointer,
 pConst.UNIQUE_NAME_HELP_CENTER_BTN: helpWndPointer,
 pConst.UNIQUE_NAME_BOOKMARKS_TAB: locationsPointer,
 pConst.UNIQUE_NAME_SKINR_COLLECTION: skinrPointer,
 pConst.UNIQUE_NAME_SKINR_PARAGON_HUB: skinrPointer,
 pConst.UNIQUE_NAME_SKINR_STUDIO: skinrPointer,
 pConst.UNIQUE_NAME_CORP_CHAT_SETTINGS: pConst.UNIQUE_NAME_CORP_CHAT,
 pConst.UNIQUE_NAME_CORP_CHAT_RELOAD_MOTD: pConst.UNIQUE_NAME_CORP_CHAT_SETTINGS,
 pConst.UNIQUE_NAME_FLEET_CHAT_SETTINGS: pConst.UNIQUE_NAME_FLEET_CHAT,
 pConst.UNIQUE_NAME_FLEET_CHAT_RELOAD_MOTD: pConst.UNIQUE_NAME_FLEET_CHAT_SETTINGS,
 pConst.UNIQUE_NAME_MY_WALLET_TAB: walletPointer,
 pConst.UNIQUE_NAME_WALLET_MARKET_TRANSACTIONS: pConst.UNIQUE_NAME_MY_WALLET_TAB,
 pConst.UNIQUE_NAME_WALLET_TRANSACTIONS_TAB: pConst.UNIQUE_NAME_MY_WALLET_TAB,
 pConst.UNIQUE_NAME_OPPORTUNITY_BROWSER: opportunityPointer,
 pConst.UNIQUE_NAME_ACTIVE_OPPORTUNITIES: opportunityPointer,
 pConst.UNIQUE_NAME_OPPORTUNITY_REWARDS: opportunityPointer,
 pConst.UNIQUE_NAME_OPPORTUNITY_FILTERS: opportunityPointer}

def FindChainForUniqueName(uniqueName):
    global skillPlanPre
    chain = [uniqueName]
    currentName = uniqueName
    if skillPlanPre is None:
        skillPlanPre = GetSkillPlanPre()
        preByUniqueName.update(skillPlanPre)
    while currentName:
        currentName = preByUniqueName.get(currentName, None)
        if currentName in chain:
            logger.error('Circular chain, currentName = %s, chain = %s' % (currentName, chain))
            return [uniqueName]
        if currentName:
            chain.append(currentName)

    return chain


def GetSkillPlanPre():
    allCertified = GetSkillPlanSvc().GetAllCertified()
    ret = {}
    for skillPlan in allCertified.itervalues():
        careerName = None
        factionName = None
        planName = None
        showBtnName = None
        trainBtnName = None
        if skillPlan.careerPathID:
            careerName = pConst.GetUniqueSkillPlanCareerName(skillPlan.careerPathID)
        if skillPlan.factionID and skillPlan.careerPathID:
            factionName = pConst.GetUniqueSkillPlanFactionName(skillPlan.careerPathID, skillPlan.factionID)
        planFullID = skillPlan.GetID()
        if planFullID:
            planID = planFullID.int
            planName = pConst.GetUniqueSkillPlanName(planID)
            showBtnName = pConst.GetUniqueSkillPlanBtn(planID, 0)
            trainBtnName = pConst.GetUniqueSkillPlanBtn(planID, 1)
        if careerName:
            ret[careerName] = pConst.UNIQUE_NAME_SKILL_PLANS_CERTIFIED_TAB
        if careerName and factionName:
            ret[factionName] = careerName
        elif careerName and planName:
            ret[planName] = careerName
        if factionName and planName:
            ret[planName] = factionName
        if planName and showBtnName:
            ret[showBtnName] = planName
        if planName and trainBtnName:
            ret[trainBtnName] = planName

    return ret


def _DebugPrintAllChains():
    chains = []
    for eachName in preByUniqueName.iterkeys():
        c = FindChainForUniqueName(eachName)
        c = [ x.replace(pConst.UNIQUE_UI_PREFIX, '') for x in c ]
        chains.append(c)

    chains.sort(key=lambda x: len(x))
    for eachChain in chains:
        print ' - ', eachChain


def _DebugPrintChain(uniqueName):
    c = FindChainForUniqueName(uniqueName)
    c = [ x.replace(pConst.UNIQUE_UI_PREFIX, '') for x in c ]
    print c
