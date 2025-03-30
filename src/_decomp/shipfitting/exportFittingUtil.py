#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\exportFittingUtil.py
import inventorycommon.const as invconst
from eveprefs import boot
from textImporting import GetNameFunc, CleanText
EXTRA_ITEM_TEMPLATE = '%s x%s'
EMPTY_TEMPLATE_STRING = '[Empty %s slot]'
SHIP_AND_FITTINGNAME_TEMPLATE = '[%s, %s]'
LINEBREAK = '\r\n'
NUM_SLOTS = 8
emptySlotDict = {invconst.flagLoSlot0: EMPTY_TEMPLATE_STRING % 'Low',
 invconst.flagMedSlot0: EMPTY_TEMPLATE_STRING % 'Med',
 invconst.flagHiSlot0: EMPTY_TEMPLATE_STRING % 'High',
 invconst.flagRigSlot0: EMPTY_TEMPLATE_STRING % 'Rig',
 invconst.flagServiceSlot0: EMPTY_TEMPLATE_STRING % 'Service'}

def GetFittingEFTString(fitting, isLocalized = False):
    fitData = fitting.fitData
    cargoItems = [ x for x in fitData if x[1] == invconst.flagCargo ]
    droneItems = [ x for x in fitData if x[1] == invconst.flagDroneBay ]
    fighterItems = [ x for x in fitData if x[1] == invconst.flagFighterBay ]
    fitDataFlagDict = {x[1]:x for x in fitData}
    slotTuples = [(NUM_SLOTS, invconst.flagLoSlot0),
     (NUM_SLOTS, invconst.flagMedSlot0),
     (NUM_SLOTS, invconst.flagHiSlot0),
     (NUM_SLOTS, invconst.flagRigSlot0),
     (invconst.numVisibleSubsystems, invconst.flagSubSystemSlot0),
     (NUM_SLOTS, invconst.flagServiceSlot0)]
    nameFunc = GetNameFunc(isLocalized)
    shipName = nameFunc(fitting.shipTypeID)
    shipName = CleanText(shipName)
    mysStringList = [SHIP_AND_FITTINGNAME_TEMPLATE % (shipName, fitting.name)]
    for numSlots, firstSlot in slotTuples:
        tempStringList = []
        emptyString = emptySlotDict.get(firstSlot, '')
        for i in xrange(numSlots):
            currentSlotIdx = firstSlot + i
            moduleInfo = fitDataFlagDict.get(currentSlotIdx, None)
            if moduleInfo:
                mysStringList += tempStringList
                tempStringList = []
                typeID = moduleInfo[0]
                typeName = nameFunc(typeID)
                typeName = CleanText(typeName)
                mysStringList.append(typeName)
            else:
                tempStringList.append(emptyString)

        mysStringList.append('')

    for location in (droneItems, cargoItems, fighterItems):
        for eachItem in location:
            typeID = eachItem[0]
            typeName = nameFunc(typeID)
            typeName = CleanText(typeName)
            lineText = EXTRA_ITEM_TEMPLATE % (typeName, eachItem[2])
            mysStringList.append(lineText)

        mysStringList.append('')

    fittingString = LINEBREAK.join(mysStringList)
    return fittingString


def AreModulesTranslated(playerSession):
    try:
        region = boot.region
    except AttributeError:
        region = 'ccp'

    if region == 'optic':
        return False
    return playerSession.languageID in ('KO', 'FR', 'JP')
