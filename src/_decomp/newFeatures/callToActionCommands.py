#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\newFeatures\callToActionCommands.py
import logging
import uthread2
from carbonui.uicore import uicore
from eve.client.script.ui.shared.systemMenu import systemMenuConst
logger = logging.getLogger(__file__)

def OpenSeason():
    uicore.cmd.OpenSeason()


def OpenCSMVoting():
    uicore.cmd.OpenCSMVoting()


def OpenEVEPortalLandingPage():
    uicore.cmd.OpenEVEPortalLandingPage()


def OpenEVEAcademyLandingPage():
    uicore.cmd.OpenEVEAcademyLandingPage()


def ToggleAurumStore():
    sm.GetService('vgsService').OpenStore()


def OpenPVPFilamentEventWindow():
    uicore.cmd.OpenPVPFilamentEventWindow()


def AgencyOpenCombatAnomalies():
    uicore.cmd.OpenCombatAnomaliesInAgency()


def AgencyOpenSeason():
    uicore.cmd.OpenSeason()


def OpenSkillWindow():
    uicore.cmd.OpenSkillsWindow()


def OpenCSMCandidateInfo():
    uicore.cmd.OpenCSMCandidateInfo()


def OpenUprisingPatchNotes():
    uicore.cmd.OpenUprisingPatchNotes()


def OpenOverviewFeaturePreviewPanel():
    systemMenu = uicore.layer.systemmenu
    if not systemMenu.isopen:
        sm.GetService('uipointerSvc').SuppressPointers()
        systemMenu.OpenView(tabID=systemMenuConst.PANELID_FEATUREPREVIEW, subTabID='beta_overview')


def OpenProjectDiscoveryWindow():
    uicore.cmd.OpenProjectDiscovery()
