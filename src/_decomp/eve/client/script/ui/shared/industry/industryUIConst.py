#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\industryUIConst.py
from carbonui.util.color import Color
import industry
import inventorycommon.const as const
import localization
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
ACTIVITY_NAMES = {industry.MANUFACTURING: 'UI/Industry/ActivityManufacturing',
 industry.COPYING: 'UI/Industry/ActivityCopying',
 industry.RESEARCH_MATERIAL: 'UI/Industry/ActivityMaterialEfficiencyResearch',
 industry.RESEARCH_TIME: 'UI/Industry/ActivityTimeEfficiencyResearch',
 industry.INVENTION: 'UI/Industry/ActivityInvention',
 industry.REACTION: 'UI/Industry/ActivityReaction'}
ACTIVITY_HINTS = {industry.MANUFACTURING: 'UI/Industry/ActivityHintManufacturing',
 industry.COPYING: 'UI/Industry/ActivityHintCopying',
 industry.RESEARCH_MATERIAL: 'UI/Industry/ActivityHintMaterialEfficiencyResearch',
 industry.RESEARCH_TIME: 'UI/Industry/ActivityHintTimeEfficiencyResearch',
 industry.INVENTION: 'UI/Industry/ActivityHintInvention',
 industry.REACTION: 'UI/Industry/ActivityHintReaction'}
ACTIVITY_ICONS_SMALL = {industry.MANUFACTURING: 'res:/UI/Texture/classes/Industry/manufacturing.png',
 industry.COPYING: 'res:/UI/Texture/classes/Industry/copying.png',
 industry.RESEARCH_MATERIAL: 'res:/UI/Texture/classes/Industry/researchMaterial.png',
 industry.RESEARCH_TIME: 'res:/UI/Texture/classes/Industry/researchTime.png',
 industry.INVENTION: 'res:/UI/Texture/classes/Industry/invention.png',
 industry.REACTION: 'res:/UI/Texture/classes/Industry/reaction.png'}
ACTIVITY_ICONS_LARGE = {industry.MANUFACTURING: 'res:/UI/Texture/classes/Industry/activity/manufacturing.png',
 industry.COPYING: 'res:/UI/Texture/classes/Industry/activity/copying.png',
 industry.RESEARCH_MATERIAL: 'res:/UI/Texture/classes/Industry/activity/researchMaterial.png',
 industry.RESEARCH_TIME: 'res:/UI/Texture/classes/Industry/activity/researchTime.png',
 industry.INVENTION: 'res:/UI/Texture/classes/Industry/activity/invention.png',
 industry.REACTION: 'res:/UI/Texture/classes/Industry/activity/reaction.png'}
ACTIVITY_AUDIOEVENTS = {industry.MANUFACTURING: 'ind_activityManufacturing',
 industry.COPYING: 'ind_activityCopying',
 industry.RESEARCH_MATERIAL: 'ind_activityMEResearch',
 industry.RESEARCH_TIME: 'ind_activityTEResearch',
 industry.INVENTION: 'ind_activityInvention',
 industry.REACTION: 'ind_activityReactions'}
ACTIVITY_HELP_POINTERS = {industry.MANUFACTURING: pConst.UNIQUE_NAME_INDUSTRY_MANUF_BTN,
 industry.COPYING: pConst.UNIQUE_NAME_INDUSTRY_COPY_BTN,
 industry.RESEARCH_MATERIAL: pConst.UNIQUE_NAME_INDUSTRY_ME_BTN,
 industry.RESEARCH_TIME: pConst.UNIQUE_NAME_INDUSTRY_TE_BTN,
 industry.INVENTION: pConst.UNIQUE_NAME_INDUSTRY_INVENTION_BTN,
 industry.REACTION: None}
TYPE_MANUFACTURING = 1
TYPE_SCIENCE = 2
TYPE_REACTION = 3

def GetActivityType(activityID):
    if activityID == industry.MANUFACTURING:
        return TYPE_MANUFACTURING
    elif activityID == industry.REACTION:
        return TYPE_REACTION
    else:
        return TYPE_SCIENCE


def GetStatusIconAndColor(status):
    if status == industry.STATUS_INSTALLED:
        return ('res:/UI/Texture/Classes/industry/status/installed.png', Color.WHITE)
    elif status == industry.STATUS_PAUSED:
        return ('res:/UI/Texture/Classes/industry/status/halted.png', Color.WHITE)
    elif status == industry.STATUS_READY:
        return ('res:/UI/Texture/Classes/industry/status/ready.png', Color.WHITE)
    elif status == industry.STATUS_CANCELLED:
        return ('res:/UI/Texture/Classes/industry/status/halted.png', COLOR_NOTREADY)
    else:
        return ('res:/UI/Texture/Classes/industry/status/delivered.png', Color.WHITE)


VIEWMODE_ICONLIST = 1
VIEWMODE_LIST = 2
COLOR_ME = (0.0, 0.1, 0.2, 1.0)
COLOR_PE = (0.0, 0.2, 0.0, 1.0)
COLOR_FRAME = (0.4, 0.4, 0.4, 1.0)
COLOR_READY = (0.2, 0.447, 0.714, 1.0)
COLOR_NOTREADY = (1.0, 0.275, 0.0, 1.0)
COLOR_MANUFACTURING = (1.0, 0.6, 0.0, 1.0)
COLOR_REACTION = (0.07, 0.9, 0.79, 1.0)
COLOR_SCIENCE = COLOR_READY
COLOR_RED = (0.3, 0.0, 0.0, 1.0)
COLOR_SYSTEMCOSTINDEX = (1.0, 0.051, 0.0, 1.0)
OPACITY_LINES = 0.3
OPACITY_SEGMENTINCOMPLETE = 0.1
RADIUS_CONNECTOR_SMALL = 15
RADIUS_CONNECTOR_LARGE = 18
RADIUS_CENTERCIRCLE_OUTER = 200.0
RADIUS_CENTERCIRCLE_INNER = 143.0
GROUP_MINERAL = 1
GROUP_MATERIAL = 2
GROUP_PI = 3
GROUP_SALVAGE = 4
GROUP_REACTION = 5
GROUP_COMPONENT = 6
GROUP_DECRYPTOR = 8
GROUP_DATAINTERFACE = 9
GROUP_DATACORE = 10
GROUP_ITEM = 11
GROUP_SELECTABLEITEM = 12
GROUP_OPTIONALITEM = 13
CATEGORYIDS_BY_INDUSTRYGROUPIDS = {GROUP_PI: (const.categoryPlanetaryCommodities, const.categoryPlanetaryResources),
 GROUP_DECRYPTOR: (const.categoryDecryptors,)}
INDISTRYGROUPS_BY_CATEGORYID = {}
for indGroupID, categoryIDs in CATEGORYIDS_BY_INDUSTRYGROUPIDS.iteritems():
    for categoryID in categoryIDs:
        INDISTRYGROUPS_BY_CATEGORYID[categoryID] = indGroupID

GROUPIDS_BY_INDUSTRYGROUPIDS = {GROUP_MINERAL: (const.groupMineral, const.groupIceProduct),
 GROUP_MATERIAL: (const.groupMaterialsAndCompounds, const.groupArtifactsAndPrototypes, const.groupRougeDroneComponents),
 GROUP_SALVAGE: (const.groupSalvagedMaterials, const.groupAncientSalvage),
 GROUP_REACTION: (const.groupMoonMaterials,
                  const.groupIntermediateMaterials,
                  const.groupComposite,
                  const.groupBiochemicalMaterial,
                  const.groupHybridPolymers),
 GROUP_COMPONENT: (const.groupConstructionComponents,
                   const.groupAdvancedCapitalConstructionComponents,
                   const.groupCapitalConstructionComponents,
                   const.groupHybridTechComponents,
                   const.groupFuelBlock,
                   const.groupStationComponents),
 GROUP_DATAINTERFACE: (const.groupDataInterfaces,),
 GROUP_DATACORE: (const.groupDatacores,)}
INDISTRYGROUPS_BY_GROUPID = {}
for indGroupID, groupIDs in GROUPIDS_BY_INDUSTRYGROUPIDS.iteritems():
    for groupID in groupIDs:
        INDISTRYGROUPS_BY_GROUPID[groupID] = indGroupID

TYPEIDS_BY_INDUSTRYGROUPIDS = {GROUP_ITEM: (const.typeRDbHybridTechnology,)}
INDISTRYGROUPS_BY_TYPEID = {}
for indGroupID, typeIDs in TYPEIDS_BY_INDUSTRYGROUPIDS.iteritems():
    for typeID in typeIDs:
        INDISTRYGROUPS_BY_TYPEID[typeID] = indGroupID

def GetIndustryGroupID(typeID, groupID, categoryID):
    if typeID in INDISTRYGROUPS_BY_TYPEID:
        return INDISTRYGROUPS_BY_TYPEID[typeID]
    elif groupID in INDISTRYGROUPS_BY_GROUPID:
        return INDISTRYGROUPS_BY_GROUPID[groupID]
    elif categoryID in INDISTRYGROUPS_BY_CATEGORYID:
        return INDISTRYGROUPS_BY_CATEGORYID[categoryID]
    else:
        return GROUP_ITEM


ICON_BY_INDUSTRYGROUP = {GROUP_MINERAL: 'res:/UI/Texture/classes/Industry/Groups/groupMineral.png',
 GROUP_MATERIAL: 'res:/UI/Texture/classes/Industry/Groups/groupRefinedMaterials.png',
 GROUP_PI: 'res:/UI/Texture/classes/Industry/Groups/groupPlantaryMaterials.png',
 GROUP_SALVAGE: 'res:/UI/Texture/classes/Industry/Groups/groupSalavageMaterials.png',
 GROUP_REACTION: 'res:/UI/Texture/classes/Industry/Groups/groupReactionMaterials.png',
 GROUP_COMPONENT: 'res:/UI/Texture/classes/Industry/Groups/groupComponents.png',
 GROUP_DECRYPTOR: 'res:/UI/Texture/classes/Industry/Groups/groupDecryptors.png',
 GROUP_DATAINTERFACE: 'res:/UI/Texture/classes/Industry/Groups/groupDataInterfaces.png',
 GROUP_DATACORE: 'res:/UI/Texture/classes/Industry/Groups/groupDatacores.png',
 GROUP_ITEM: 'res:/UI/Texture/classes/Industry/Groups/groupItems.png',
 GROUP_SELECTABLEITEM: 'res:/UI/Texture/classes/Industry/Groups/groupDataInterfaces.png',
 GROUP_OPTIONALITEM: 'res:/UI/Texture/classes/Industry/Groups/groupItems.png'}
LABEL_BY_INDUSTRYGROUP = {GROUP_MINERAL: 'UI/Industry/GroupMineral',
 GROUP_MATERIAL: 'UI/Industry/GroupMaterial',
 GROUP_PI: 'UI/Industry/GroupPI',
 GROUP_SALVAGE: 'UI/Industry/GroupSalvage',
 GROUP_REACTION: 'UI/Industry/GroupReaction',
 GROUP_COMPONENT: 'UI/Industry/GroupComponent',
 GROUP_DECRYPTOR: 'UI/Industry/GroupDecryptor',
 GROUP_DATAINTERFACE: 'UI/Industry/GroupDataInterface',
 GROUP_DATACORE: 'UI/Industry/GroupDatacore',
 GROUP_ITEM: 'UI/Industry/GroupItem',
 GROUP_SELECTABLEITEM: 'UI/Industry/GroupDataInterface',
 GROUP_OPTIONALITEM: 'UI/Industry/GroupOptionalItem'}
HINT_BY_INDUSTRYGROUP = {GROUP_MINERAL: 'UI/Industry/HintGroupMineral',
 GROUP_MATERIAL: 'UI/Industry/HintGroupMaterial',
 GROUP_PI: 'UI/Industry/HintGroupPI',
 GROUP_SALVAGE: 'UI/Industry/HintGroupSalvage',
 GROUP_REACTION: 'UI/Industry/HintGroupReaction',
 GROUP_COMPONENT: 'UI/Industry/HintGroupComponent',
 GROUP_DECRYPTOR: 'UI/Industry/HintGroupDecryptor',
 GROUP_DATAINTERFACE: 'UI/Industry/HintGroupDataInterface',
 GROUP_DATACORE: 'UI/Industry/HintGroupDatacore',
 GROUP_ITEM: 'UI/Industry/HintGroupItem',
 GROUP_SELECTABLEITEM: 'UI/Industry/HintGroupDataInterface',
 GROUP_OPTIONALITEM: 'UI/Industry/HintGroupItem'}

def GetJobColor(jobData):
    if jobData is None:
        return COLOR_FRAME
    return GetActivityColor(jobData.activityID)


def GetActivityColor(activityID):
    if activityID == industry.MANUFACTURING:
        return COLOR_MANUFACTURING
    elif activityID == industry.REACTION:
        return COLOR_REACTION
    else:
        return COLOR_SCIENCE


def GetControlRangeLabel(jumps):
    if jumps == -1:
        return localization.GetByLabel('UI/Industry/CurrentFacility')
    elif jumps == 0:
        return localization.GetByLabel('UI/Generic/CurrentSystem')
    elif jumps == 50:
        return localization.GetByLabel('UI/Contracts/ContractsWindow/CurrentRegion')
    else:
        return localization.GetByLabel('UI/Fleet/FleetRegistry/NumberOfJumps', numJumps=jumps)
