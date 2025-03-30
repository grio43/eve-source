#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\skillRequirements.py
from collections import defaultdict
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import TextHeader
from carbonui.util.sortUtil import SortListOfTuples
from dogma.items.characterDogmaItem import CharacterDogmaItem
from dogma.items.shipDogmaItem import ShipDogmaItem
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveHeaderMedium
import evetypes
import carbonui.const as uiconst
from eve.client.script.ui.shared.fittingScreen.skillRequirementsUtil import GetAllSkillsAndLevels, _GetSkillTypeIDAndLevelRequired
from eve.client.script.ui.shared.industry.submitButton import PrimaryButton
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1, COLOR_SKILL_2
from eve.client.script.ui.shared.tooltip.itemObject import ItemObject
from eve.client.script.ui.shared.tooltip.skill_requirement import RequiredSkillRow, AddSkillActionForList, AddTrainingTime
from inventorycommon.const import categoryBlueprint
from localization import GetByLabel
import blue

def GetSkillTooltip(tooltipPanel, fittingController, fitName = None):
    tooltipPanel.state = uiconst.UI_NORMAL
    tooltipPanel.columns = 2
    tooltipPanel.margin = (12, 8, 12, 12)
    tooltipPanel.state = uiconst.UI_NORMAL
    dogmaLocation = fittingController.GetDogmaLocation()
    shipAndFitTypeIDs = _GetAllTypesForShipAndFit(dogmaLocation)
    shipAndFitTypeIDsMissingSomeReq = GetMissingSkillsForTypeIDs(shipAndFitTypeIDs)
    shipAndFitHighestLevelByTypeID, _ = GetMissingSkills_HighestLevelByTypeID(shipAndFitTypeIDsMissingSomeReq)
    cargoholdTypeIDs = _GetAllTypesForCargoHold(dogmaLocation)
    cargoholdTypeIDsMissingSomeReq = GetMissingSkillsForTypeIDs(cargoholdTypeIDs)
    cargoholdTypeIDsMissingSomeReq -= shipAndFitTypeIDsMissingSomeReq
    cargoholdHighestLevelByTypeID, _ = GetMissingSkills_HighestLevelByTypeID(cargoholdTypeIDsMissingSomeReq)
    for typeID, lvl in cargoholdHighestLevelByTypeID.items():
        lvlForFit = shipAndFitHighestLevelByTypeID.get(typeID, 0)
        if lvlForFit >= lvl:
            cargoholdHighestLevelByTypeID.pop(typeID)

    shipText = None
    holdText = GetByLabel('UI/Fitting/FittingWindow/Warnings/CargoHold')
    if shipAndFitTypeIDsMissingSomeReq and cargoholdTypeIDsMissingSomeReq:
        shipText = GetByLabel('UI/Fitting/FittingWindow/Warnings/ShipAndFit')
    if shipAndFitTypeIDs:
        AddMissingSkillRequirements(tooltipPanel, shipAndFitHighestLevelByTypeID, True, shipText)
    if cargoholdTypeIDsMissingSomeReq:
        AddMissingSkillRequirements(tooltipPanel, cargoholdHighestLevelByTypeID, False, holdText)
    allSkillLevelsByID = []
    for key in set(shipAndFitHighestLevelByTypeID.keys()) | set(cargoholdHighestLevelByTypeID.keys()):
        valA = shipAndFitHighestLevelByTypeID.get(key, 0)
        valB = cargoholdHighestLevelByTypeID.get(key, 0)
        allSkillLevelsByID.append((key, max(valA, valB)))

    skillSvc = sm.GetService('skills')
    allSkillLevelsByID = skillSvc.GetSkillsMissingToUseAllSkillsFromListRecursiveAsList(allSkillLevelsByID)
    allSkillLevelsByIDDict = dict(allSkillLevelsByID)
    missingSkills = skillSvc.GetMissingSkillBooksFromList(allSkillLevelsByID)
    totalTime = long(skillSvc.GetSkillTrainingTimeLeftForTypesAndLevels(allSkillLevelsByIDDict, includeBoosters=False))
    if totalTime <= 0:
        return
    isOmegaRestricted = False
    for typeID, level in allSkillLevelsByID:
        if not isOmegaRestricted:
            isOmegaRestricted = ItemObject(typeID).NeedsOmegaUpgrade()

    isOmega = sm.GetService('cloneGradeSvc').IsOmega()
    AddTrainingTime(tooltipPanel, isOmega=isOmega, isOmegaRestricted=isOmegaRestricted, trainingTime=totalTime, activityText=GetByLabel('Tooltips/SkillPlanner/ActivityFlyFittedShip'))
    if fitName:
        skillPlanName = GetByLabel('Tooltips/SkillPlanner/SkillPlanNameStringWithType', typeName=fitName)
    else:
        skillPlanName = GetByLabel('UI/SkillPlan/DefaultCreateFitSkillPlanName')
    AddSkillActionForList(tooltipPanel, allSkillLevelsByID, missingSkills, minWidth=300, skillPlanName=skillPlanName)


def GetMissingSkillsForTypeIDs(allTypeIDs):
    skillsSvc = sm.GetService('skills')
    missingReq = set()
    for eachTypeID in allTypeIDs:
        if not skillsSvc.IsSkillRequirementMet(eachTypeID):
            missingReq.add(eachTypeID)

    return missingReq


def GetAllTypeIDsMissingSkillsForShipAndContent(dogmaLocation):
    allTypeIDs = _GetAllTypesForShipAndFit(dogmaLocation)
    allTypeIDs.update(_GetAllTypesForCargoHold(dogmaLocation))
    return allTypeIDs


def _GetAllTypesForShipAndFit(dogmaLocation):
    allTypeIDs = set()
    ship = dogmaLocation.GetShipItem()
    if ship is None:
        return allTypeIDs
    allTypeIDs.add(ship.typeID)
    fittedItems = dogmaLocation.GetFittedItemsToShip()
    for eachItem in fittedItems.itervalues():
        if isinstance(eachItem, (CharacterDogmaItem, ShipDogmaItem)):
            continue
        allTypeIDs.add(eachItem.typeID)

    for flagID in [const.flagDroneBay, const.flagFighterBay] + const.fighterTubeFlags:
        allTypeIDs.update(_GetTypesInFlag(dogmaLocation, flagID))

    return allTypeIDs


def _GetAllTypesForCargoHold(dogmaLocation):
    return _GetTypesInFlag(dogmaLocation, const.flagCargo)


def _GetTypesInFlag(dogmaLocation, flagID):
    holdItems = dogmaLocation.GetHoldItems(flagID)
    typesInHold = {x.typeID for x in holdItems.itervalues()}
    return typesInHold


def AddMissingSkillRequirements(tooltipPanel, highestLevelByTypeID, addHeaderLabel = True, text = None):
    if not highestLevelByTypeID:
        return
    skillsSvc = sm.GetService('skills')
    tooltipPanel.AddSpacer(width=250, colSpan=tooltipPanel.columns)
    tooltipPanel.FillRow()
    if addHeaderLabel:
        headerText = GetByLabel('UI/Skills/RequiredSkills')
        headerLabel = TextHeader(text=headerText)
        tooltipPanel.AddCell(headerLabel, colSpan=tooltipPanel.columns, cellPadding=(0, 4, 0, 0))
    tooltipPanel.FillRow()
    if text:
        headerLabel = EveHeaderMedium(text=text, color=COLOR_SKILL_1)
        topPadding = 8 if addHeaderLabel else 20
        tooltipPanel.AddCell(headerLabel, colSpan=tooltipPanel.columns, cellPadding=(0,
         topPadding,
         0,
         0))
    skillList = []
    for skillTypeID, skillLevel in highestLevelByTypeID.iteritems():
        name = evetypes.GetName(skillTypeID)
        skillList.append((name, (skillTypeID, skillLevel)))

    skillList = SortListOfTuples(skillList)
    for skillID, level in skillList:
        tooltipPanel.AddRow(rowClass=RequiredSkillRow, typeID=skillID, level=level, cellPadding=(0, 4, 0, 0), colSpan=tooltipPanel.columns)


def CopyAllSkills(typeIDs):
    allSkillsAndLevels = GetAllSkillsAndLevels(typeIDs)
    textList = []
    for eachSkillTypeID, skillLvl in allSkillsAndLevels:
        name = evetypes.GetName(eachSkillTypeID)
        textList.append('%s %d' % (name, skillLvl))

    text = '\r\n'.join(textList)
    blue.pyos.SetClipboardData(text)


def AddSkillAction(tooltipPanel, typeIDs):
    allMissingSkillbooks = GetMissingSkillbooksForTypeIDs(typeIDs)
    areSomeTypesMissingSkillNotInQueue = bool(GetTypesWithMissingSkills(typeIDs))
    skillTypesAndLvlsToUse, _ = GetMissingSkills_HighestLevelByTypeID(typeIDs)
    if allMissingSkillbooks:
        AddBuyAndTrainForRequiredSkillbooksMissingRow(tooltipPanel, list(allMissingSkillbooks), skillTypesAndLvlsToUse, tooltipPanel.columns)
    if areSomeTypesMissingSkillNotInQueue:
        if _ShouldAddTrainNowBtn(skillTypesAndLvlsToUse.keys()):
            AddTrainNowRow(tooltipPanel, skillTypesAndLvlsToUse)
    if session.role & ROLE_GML == ROLE_GML:
        skillsAndLevels, _ = GetMissingSkills_HighestLevelByTypeID(typeIDs)
        if skillsAndLevels:
            btn = Button(label='Give Skills', func=sm.GetService('info').DoGiveSkills, args=(skillsAndLevels, None), idx=0)
            tooltipPanel.AddCell(cellObject=btn, colSpan=tooltipPanel.columns)


def _ShouldAddTrainNowBtn(skillTypesToUse):
    for eachTypeID in skillTypesToUse:
        if ItemObject(eachTypeID).CanTrainNow():
            return True

    return False


def AddTrainNowRow(tooltipPanel, skillTypesAndLvlsToUse):
    tooltipPanel.AddCell(cellPadding=(0, 12, 0, 0), colSpan=tooltipPanel.columns)
    trainNowButton = TrainNowButtonManyTypes(align=uiconst.CENTER, fixedheight=30, fixedwidth=120, skillTypesAndLvlsToUse=skillTypesAndLvlsToUse)
    tooltipPanel.AddCell(trainNowButton, colSpan=tooltipPanel.columns)


def AddBuyAndTrainForRequiredSkillbooksMissingRow(grid, missing, skillTypesAndLvlsToUse, colSpan):
    grid.AddCell(cellPadding=(0, 12, 0, 0), colSpan=colSpan)
    grid.FillRow()
    available = [ x for x in missing if evetypes.IsSkillAvailableForPurchase(x) ]
    numUnavailable = len(missing) - len(available)
    text = GetByLabel('UI/SkillQueue/RequiredSkillBooksMissingWithNum', numBooks=len(missing))
    if available and numUnavailable:
        text += '<br>%s' % GetByLabel('UI/SkillQueue/AvailableAndUnavailableSkillbooks', numAvailable=len(available), numUnavailable=numUnavailable)
    label = EveLabelMedium(align=uiconst.CENTERLEFT, text=text, color=COLOR_SKILL_1)
    grid.AddCell(label, colSpan=colSpan - 1)
    btn = Button(align=uiconst.CENTERRIGHT, label=GetByLabel('UI/Skills/BuyAndTrain'), fixedheight=24, func=BuyAndTrain, args=(available, skillTypesAndLvlsToUse))
    if not available and numUnavailable:
        btn.Disable()
        if numUnavailable == 1:
            btn.hint = GetByLabel('UI/Skills/ErrorRareSkill')
        else:
            btn.hint = GetByLabel('UI/Skills/ErrorRareSkills')
    grid.AddCell(btn, cellPadding=(10, 0, 0, 0))


def GetTypesWithMissingSkills(typeIDs):
    typesWithMissingSkills = set()
    for eachTypeID in typeIDs:
        isMet = sm.GetService('skills').IsSkillRequirementMetIncludingSkillQueue(eachTypeID)
        if not isMet:
            typesWithMissingSkills.add(eachTypeID)

    return typesWithMissingSkills


def GetMissingSkillbooksForTypeIDs(typeIDs):
    allMissingSkillbooks = set()
    for eachTypeID in typeIDs:
        itemObject = ItemObject(eachTypeID)
        missingSkillbooks = itemObject.GetMissingSkillBooks()
        allMissingSkillbooks.update(missingSkillbooks)

    return allMissingSkillbooks


def GetMissingSkills_HighestLevelByTypeID(typeIDs):
    skillsSvc = sm.GetService('skills')
    highestLevelByTypeID = defaultdict(int)
    missingSkillsForTypeID = defaultdict(set)
    for eachTypeID in typeIDs:
        if not evetypes.Exists(eachTypeID) or evetypes.GetCategoryID(eachTypeID) == categoryBlueprint:
            continue
        allMissing = skillsSvc.GetSkillsMissingToUseItemRecursive(eachTypeID)
        for skillTypeID, skillLevel in allMissing.iteritems():
            highestLevelByTypeID[skillTypeID] = int(max(skillLevel, highestLevelByTypeID[skillTypeID]))
            missingSkillsForTypeID[eachTypeID].add(skillTypeID)

    return (highestLevelByTypeID, missingSkillsForTypeID)


def GetSkillTypeIDAndLevelRequired(typeID):
    ret = []
    _GetSkillTypeIDAndLevelRequired(typeID, ret)
    return ret


class TrainNowButtonManyTypes(PrimaryButton):
    default_name = 'TrainNowButton'

    def ApplyAttributes(self, attributes):
        super(TrainNowButtonManyTypes, self).ApplyAttributes(attributes)
        self.skillTypesAndLvlsToUse = attributes.skillTypesAndLvlsToUse
        self._isFinished = False
        self.UpdateState()

    def IsActive(self):
        return not self._isFinished

    def ClickFunc(self, *args):
        self.Disable()
        try:
            for eachTypeID, eachLvl in self.skillTypesAndLvlsToUse.iteritems():
                sm.GetService('skillqueue').AddSkillAndRequirementsToQueue(eachTypeID, eachLvl)

            self._isFinished = True
        except Exception:
            self.Enable()

        self.UpdateState()

    def GetColor(self):
        if self._isFinished:
            return (1.0, 1.0, 1.0, 0.3)
        else:
            return COLOR_SKILL_2

    def GetText(self):
        if self._isFinished:
            return GetByLabel('UI/SkillQueue/SkillQueueUpdated')
        else:
            return GetByLabel('UI/SkillQueue/AddToQueue')

    def GetTranslation(self):
        return 0.1667

    def Update_Size_(self):
        PrimaryButton.Update_Size_(self)
        self.width = max(self.fixedwidth, self.sr.label.width + 20)


def BuyAndTrain(availableForPurchase, skillTypesAndLvlsToUse):
    skillSvc = sm.GetService('skills')
    boughtSkills = skillSvc.PurchaseSkills(availableForPurchase)
    if not boughtSkills:
        return
    skillSvc.WaitUntilSkillsAreAvailable(availableForPurchase)
    skillqueueSvc = sm.GetService('skillqueue')
    for eachTypeID, eachLvl in skillTypesAndLvlsToUse.iteritems():
        skillqueueSvc.AddSkillAndRequirementsToQueue(eachTypeID, eachLvl)
