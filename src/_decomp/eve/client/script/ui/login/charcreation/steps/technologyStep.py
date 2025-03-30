#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\steps\technologyStep.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
import charactercreator.client.scalingUtils as ccScalingUtils
import charactercreator.const as ccConst
from eve.client.script.ui.login.charcreation.charCreation import BaseCharacterCreationStep
from eve.client.script.ui.login.charcreation.charCreationButtons import GetEmpireTabSizeLarge
from eve.client.script.ui.login.charcreation.technologiesView import EmpireTechnologiesView
from eve.client.script.ui.shared.colorThemes import DEFAULT_COLORTHEMEID, COLOR_THEME_ID_BY_RACE
from characterdata.races import CHARACTER_CREATION_RACE_IDS

def GetEmpireNavigationWidth():
    return 4 * GetEmpireTabSizeLarge()


def GetEmpireNavigationHeight():
    return GetEmpireTabSizeLarge()


class TechnologyStep(BaseCharacterCreationStep):
    __guid__ = 'uicls.TechnologyStep'
    stepID = ccConst.TECHNOLOGYSTEP

    def ApplyAttributes(self, attributes):
        self.raceID = None
        self.techCont = None
        shouldGoBackToStart = attributes.Get('shouldGoBackToStart', True)
        technologyViewsTracker = attributes.Get('technologyViewsTracker')
        BaseCharacterCreationStep.ApplyAttributes(self, attributes)
        info = self.GetInfo()
        self.techCont = Container(name='techCont', parent=self, align=uiconst.CENTER, width=ccScalingUtils.GetMainPanelWidth(), height=ccScalingUtils.GetMainPanelHeight(), state=uiconst.UI_PICKCHILDREN, padding=(0, 0, 0, 0))
        self.buttonCont = Container(parent=self.techCont, name='buttonContainer', align=uiconst.TOALL)
        self.raceID = info.raceID if info.raceID else self._GetFirstRace()
        self.techView = EmpireTechnologiesView(name='raceBtn', parent=self.buttonCont, align=uiconst.TOLEFT, width=ccScalingUtils.GetMainPanelWidth(), height=ccScalingUtils.GetMainPanelHeight(), raceID=info.raceID, stepContainer=self.parent, buttonContainer=uicore.layer.charactercreation.controller.empireNavigationButtonContainer, shouldGoBackToStart=shouldGoBackToStart, technologyViewsTracker=technologyViewsTracker)
        self.UpdateLayout()

    def _GetFirstRace(self):
        for raceID in CHARACTER_CREATION_RACE_IDS:
            return raceID

        return const.raceAmarr

    def UpdateLayout(self):
        if self.raceID:
            raceTheme = COLOR_THEME_ID_BY_RACE.get(self.raceID, DEFAULT_COLORTHEMEID)
            sm.GetService('uiColor').SetNoCharTheme(raceTheme)
        bannerWidth = ccScalingUtils.GetMainPanelWidth()
        bannerHeight = ccScalingUtils.GetMainPanelHeight()
        self.techView.UpdateLayout(bannerWidth, bannerHeight)
        self.techCont.width = ccScalingUtils.GetMainPanelWidth()
        self.techCont.height = ccScalingUtils.GetMainPanelHeight()

    def OnRaceSelected(self, raceID, *args):
        self.raceID = raceID
        uicore.layer.charactercreation.controller.SwitchStep(ccConst.TECHNOLOGYSTEP)

    def UpdateRaceInfo(self, raceID):
        self.raceID = raceID
        uicore.layer.charactercreation.controller.Approve()
