#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\pointerTool\pointerChains.py
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupProvider import GetRootContentGroup
from uihighlighting.uniqueNameChains import FindChainForUniqueName

def FindChainForPointer(pointerName):
    if pointerName.startswith(pConst.AGENCY_TAB_PREFIX) or pointerName.startswith(pConst.AGENCY_CARD_PREFIX):
        contentGroupID = pointerName.replace(pConst.AGENCY_TAB_PREFIX, '').replace(pConst.AGENCY_CARD_PREFIX, '')
        pointerChain = FindAgencyChainForGroupID(int(contentGroupID))
        if pointerChain:
            pointers = [pConst.GetUniqueNeocomPointerName('agency'), pConst.GetUniqueAgencyTabName(pointerChain[0])]
            for x in pointerChain[1:]:
                pointers.append(pConst.GetUniqueAgencyCardName(x))

            return pointers
    chain = FindChainForUniqueName(pointerName)
    if len(chain) > 1:
        chain.reverse()
        return chain
    return []


def FindAgencyChainForGroupID(groupIdToFind):
    resultList = []

    def WasGroupFound(children):
        for child in children:
            if child.contentGroupID == groupIdToFind:
                resultList.insert(0, child.contentGroupID)
                return True
            if child.children:
                if WasGroupFound(child.children):
                    resultList.insert(0, child.contentGroupID)
                    return True

    WasGroupFound(GetRootContentGroup().children)
    return resultList
