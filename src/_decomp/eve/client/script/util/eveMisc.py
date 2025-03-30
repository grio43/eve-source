#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\util\eveMisc.py
import sys
import uthread
from carbonui import uiconst
from eve.common.lib import appConst as const
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import UserError

def LaunchFromShip(items, whoseBehalfID = None, ignoreWarning = False, maxQty = None):
    oldItems = []
    drones = False
    for item in items:
        if getattr(item, 'categoryID', 0) == const.categoryDrone:
            drones = True
        qty = getattr(item, 'quantity', 0)
        if qty < 0:
            oldItems.insert(0, (item.itemID, 1))
        elif qty > 0:
            if maxQty is not None:
                qty = min(qty, maxQty)
            oldItems.append((item.itemID, qty))

    try:
        if drones:
            ret = sm.StartService('gameui').GetShipAccess().LaunchDrones(oldItems, whoseBehalfID, ignoreWarning)
        else:
            ret = sm.StartService('gameui').GetShipAccess().Drop(oldItems, whoseBehalfID, ignoreWarning)
    except UserError as e:
        if e.msg in ('LaunchCPWarning', 'LaunchUpgradePlatformWarning'):
            reply = eve.Message(e.msg, e.dict, uiconst.YESNO)
            if reply == uiconst.ID_YES:
                LaunchFromShip(items, whoseBehalfID, ignoreWarning=True)
            sys.exc_clear()
            return
        raise e

    newIDs = {}
    errorByLabel = {}
    for itemID, seq in ret.iteritems():
        newIDs[itemID] = []
        for each in seq:
            if type(each) is tuple:
                errorByLabel[each[0]] = each
            else:
                newIDs[itemID].append(each)

    sm.ScatterEvent('OnItemLaunch', newIDs)

    def raise_(e):
        raise e

    for error in errorByLabel.itervalues():
        uthread.new(raise_, UserError(*error))


def CSPAChargedActionForMany(message, obj, function, *args):
    try:
        func = getattr(obj, function)
        return func(*args)
    except UserError as e:
        if e.msg == 'ContactCostNotApprovedForMany':
            listOfMessage = e.dict['costNotApprovedFor']
            totalCost = 0
            totalApprovedCost = 0
            listingOutPlayers = []
            for each in listOfMessage:
                totalCost += each['totalCost']
                totalApprovedCost += each['approvedCost']
                charID = each['charID']
                listingOutPlayers.append('%s : %s' % (cfg.eveowners.Get(charID).name, FmtISK(each['totalCost'])))

            namelist = '<br>'.join(listingOutPlayers)
            if eve.Message(message, {'amountISK': FmtISK(totalCost),
             'namelist': namelist}, uiconst.YESNO) != uiconst.ID_YES:
                return None
            kwArgs = {'approvedCost': totalCost}
            return apply(getattr(obj, function), args, kwArgs)
        raise


def CSPAChargedAction(message, obj, function, *args):
    try:
        return apply(getattr(obj, function), args)
    except UserError as e:
        if e.msg == 'ContactCostNotApproved':
            info = e.args[1]
            if eve.Message(message, {'amount': info['totalCost'],
             'amountISK': info['totalCostISK']}, uiconst.YESNO) != uiconst.ID_YES:
                return None
            kwArgs = {'approvedCost': info['totalCost']}
            return apply(getattr(obj, function), args, kwArgs)
        raise


def GetRemoveServiceConfirmationQuestion(serviceTypeID):
    confirmQuestionsByModuleID = {const.typeStandupMarketHub: 'AskRemoveMarketStructureService',
     const.typeStandupCloningCenter: 'AskRemoveCloneStructureService',
     const.typeStandupManufacturingPlant: 'AskRemoveIndustryStructureService',
     const.typeStandupCapitalShipYard: 'AskRemoveIndustryStructureService',
     const.typeStandupSuperCapitalShipYard: 'AskRemoveIndustryStructureService',
     const.typeStandupResearchLab: 'AskRemoveIndustryStructureService',
     const.typeStandupHyasyodaResearchLab: 'AskRemoveIndustryStructureService',
     const.typeStandupInventionLab: 'AskRemoveIndustryStructureService'}
    questionPath = confirmQuestionsByModuleID.get(serviceTypeID, 'AskRemoveStructureService')
    params = _GetExtraParams(serviceTypeID)
    return (questionPath, params)


def GetOfflineServiceConfirmationQuestion(serviceTypeID):
    confirmQuestionsByModuleID = {const.typeStandupMarketHub: 'AskOfflineMarketStructureService',
     const.typeStandupCloningCenter: 'AskOfflineCloneStructureService',
     const.typeStandupManufacturingPlant: 'AskOfflineIndustryStructureService',
     const.typeStandupCapitalShipYard: 'AskOfflineIndustryStructureService',
     const.typeStandupSuperCapitalShipYard: 'AskOfflineIndustryStructureService',
     const.typeStandupResearchLab: 'AskOfflineIndustryStructureService',
     const.typeStandupHyasyodaResearchLab: 'AskOfflineIndustryStructureService',
     const.typeStandupInventionLab: 'AskOfflineIndustryStructureService'}
    questionPath = confirmQuestionsByModuleID.get(serviceTypeID, 'AskOfflineStructureService')
    params = _GetExtraParams(serviceTypeID)
    return (questionPath, params)


def _GetExtraParams(serviceTypeID):
    params = {}
    if serviceTypeID == const.typeStandupCloningCenter:
        numClones = sm.GetService('clonejump').GetNumClonesInPilotsStructure()
        if numClones is not None:
            params['numClones'] = numClones
    return params
