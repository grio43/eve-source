#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\charactercreator\client\empireSelectionData.py
from charactercreator.client.empireSelectionTechnology import TechnologyData
from fsd.schemas.binaryLoader import LoadFSDDataForCFGOrFail
EMPIRES_DATA_PATH = 'res:/staticdata/empireSelection.static'
EMPIRES_TECHNOLOGY_PATH = 'res:/staticdata/empireTechnologies.static'
_empiresData = None
_technologyData = None

def GetTechnologyData():
    global _technologyData
    if _technologyData is None:
        technologyStaticData = LoadFSDDataForCFGOrFail(EMPIRES_TECHNOLOGY_PATH)
        _technologyData = TechnologyData(technologyStaticData)
    return _technologyData


def _GetEmpireData(raceID):
    global _empiresData
    if _empiresData is None:
        _empiresData = LoadFSDDataForCFGOrFail(EMPIRES_DATA_PATH)
    empireData = _empiresData.get(raceID, None)
    if empireData is None:
        raise ValueError('No empire data found with raceID {raceID}'.format(raceID=raceID))
    return empireData


def GetEmpireQuote(raceID):
    empireData = _GetEmpireData(raceID)
    return empireData.quote


def GetBloodlinesInfo(raceID):
    empireData = _GetEmpireData(raceID)
    return empireData.bloodlines


def GetEmpireButtonLogo(raceID):
    empireData = _GetEmpireData(raceID)
    return empireData.logoPath


def GetEmpireLogo(raceID):
    empireData = _GetEmpireData(raceID)
    return empireData.namedLogoPath


def GetEmpireSeal(raceID):
    empireData = _GetEmpireData(raceID)
    return empireData.sealPath


def GetEmpireColor(raceID):
    empireData = _GetEmpireData(raceID)
    return empireData.empireColor
