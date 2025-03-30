#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipfitting\multiFitMenu.py
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.util.sortUtil import SortListOfTuples
from localization import GetByLabel
from menu import MenuList

def GetMultiFitMenu(item, typeID):
    fittingSvc = sm.GetService('fittingSvc')
    fitStackFunc = sm.GetService('menu').FitStack
    personalFittingsList = []
    corpFittingsList = []
    allianceFittingsList = []
    for ownerID, ownerFittingList in ((session.charid, personalFittingsList), (session.corpid, corpFittingsList), (session.allianceid, allianceFittingsList)):
        if not ownerID:
            continue
        fittings = fittingSvc.GetFittingsForType(ownerID, typeID)
        for fittingID, fit in fittings:
            ownerFittingList.append((fit.name, fitStackFunc, [item, fit]))

        ownerFittingList.sort(key=lambda x: x[0].lower())

    totalNumFittings = len(personalFittingsList) + len(corpFittingsList) + len(allianceFittingsList)
    numOwners = bool(personalFittingsList) + bool(corpFittingsList) + bool(allianceFittingsList)
    if numOwners < 2 or totalNumFittings < 15:
        menuEntries = MenuList()
        for fittingList in (personalFittingsList, corpFittingsList, allianceFittingsList):
            if not fittingList:
                continue
            if menuEntries:
                menuEntries.append(None)
            menuEntries += fittingList

        if menuEntries:
            return menuEntries
    else:
        menuData = MenuData()
        for menuName, fList in (('UI/Fitting/FittingWindow/FittingManagement/Personal', personalFittingsList), ('UI/Fitting/FittingWindow/FittingManagement/Corporation', corpFittingsList), ('UI/Fitting/FittingWindow/FittingManagement/Alliance', allianceFittingsList)):
            if fList:
                menuData.AddEntry(GetByLabel(menuName), subMenuData=fList)

        if menuData:
            return menuData
    m = MenuData()
    m.AddEntry(GetByLabel('UI/Fitting/FittingWindow/FittingManagement/NoFittingsFound'), isEnabled=False)
    return m
