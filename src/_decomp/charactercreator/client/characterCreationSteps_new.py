#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\charactercreator\client\characterCreationSteps_new.py
import charactercreator.const as ccConst
STEPS_BY_MODE = {ccConst.MODE_FULL_BLOODLINECHANGE: [ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP, ccConst.NAMINGSTEP],
 ccConst.MODE_FULL_RECUSTOMIZATION: [ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP],
 ccConst.MODE_LIMITED_RECUSTOMIZATION: [ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP],
 ccConst.MODE_FULLINITIAL_CUSTOMIZATION: [ccConst.EMPIRESTEP,
                                          ccConst.DOLLSTEP,
                                          ccConst.CUSTOMIZATIONSTEP,
                                          ccConst.NAMINGSTEP]}
STEP_ORDER_LIST_NEW = [ccConst.EMPIRESTEP,
 ccConst.DOLLSTEP,
 ccConst.CUSTOMIZATIONSTEP,
 ccConst.PORTRAITSTEP,
 ccConst.NAMINGSTEP]

def GetStepOrder(step):
    try:
        return STEP_ORDER_LIST_NEW.index(step)
    except ValueError:
        return -1


def GetStepsUpToAndIncluding(lastStep):
    s = set()
    if lastStep not in STEP_ORDER_LIST_NEW:
        return s
    for step in STEP_ORDER_LIST_NEW:
        s.add(step)
        if step == lastStep:
            return s


class Mode(object):

    def __init__(self, modeID, canChangeBaseAppearance = False, canChangeName = False, canChangeGender = False, canChangeBloodline = False, willExitToStation = True, askPortraitInfo = False, isInitialCreation = False, limited = False, useOldPortraitData = False):
        self.modeID = modeID
        self.canChangeName = canChangeName
        self.canChangeGender = canChangeGender
        self.canChangeBaseAppearance = canChangeBaseAppearance
        self.canChangeBloodline = canChangeBloodline
        self.willExitToStation = willExitToStation
        self.askForPortraitConfirmation = askPortraitInfo
        self.isInitialCreation = isInitialCreation
        self.limitedHelpText = limited
        self.useOldPortraitData = useOldPortraitData
        self.steps = {}

    def GetValue(self):
        return ccConst.MODE_FULL_BLOODLINECHANGE

    def GetSteps(self):
        return STEPS_BY_MODE[self.modeID]

    def CanChangeBaseAppearance(self):
        return self.canChangeBaseAppearance

    def CanChangeGender(self):
        return self.canChangeGender

    def CanChangeName(self):
        return self.canChangeName

    def CanChangeBloodLine(self):
        return self.canChangeBloodline

    def AskForPortraitConfirmation(self):
        return self.askForPortraitConfirmation

    def ExitToStation(self):
        return self.willExitToStation

    def IsInitialCreation(self):
        return self.isInitialCreation

    def IsLimited(self):
        return self.limitedHelpText

    def GetOldPortraitData(self):
        return self.useOldPortraitData


class ModeStorage(object):

    def __init__(self):
        self.modes = {}
        fullInitialCustomization = Mode(modeID=ccConst.MODE_FULLINITIAL_CUSTOMIZATION, canChangeBaseAppearance=True, canChangeBloodline=True, canChangeName=True, canChangeGender=True, willExitToStation=False)
        fullBloodlineChange = Mode(modeID=ccConst.MODE_FULL_BLOODLINECHANGE, canChangeBloodline=True, canChangeGender=False, canChangeBaseAppearance=False)
        fullRecustomization = Mode(modeID=ccConst.MODE_FULL_RECUSTOMIZATION, canChangeBaseAppearance=True, askPortraitInfo=True, useOldPortraitData=True)
        limitedRecustomization = Mode(modeID=ccConst.MODE_LIMITED_RECUSTOMIZATION, canChangeBaseAppearance=False, askPortraitInfo=True, limited=1, useOldPortraitData=True, willExitToStation=True)
        self.modes[ccConst.MODE_FULLINITIAL_CUSTOMIZATION] = fullInitialCustomization
        self.modes[ccConst.MODE_FULL_BLOODLINECHANGE] = fullBloodlineChange
        self.modes[ccConst.MODE_FULL_RECUSTOMIZATION] = fullRecustomization
        self.modes[ccConst.MODE_LIMITED_RECUSTOMIZATION] = limitedRecustomization

    def GetModeFor(self, modeID):
        return self.modes[modeID]
