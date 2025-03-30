#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\ccUtil.py
import charactercreator.const as ccConst
import telemetry
import trinity
from eve.common.script.paperDoll.paperDollDefinitions import GENDER
from eve.common.script.paperDoll.yamlPreloader import LoadYamlFileNicely

@telemetry.ZONE_FUNCTION
def GenderIDToPaperDollGender(genderID):
    if genderID == ccConst.GENDERID_FEMALE:
        return GENDER.FEMALE
    if genderID == ccConst.GENDERID_MALE:
        return GENDER.MALE
    raise RuntimeError('GenderIDToPaperDollGender: Invalid genderID!')


@telemetry.ZONE_FUNCTION
def PaperDollGenderToGenderID(gender):
    if gender == GENDER.MALE:
        return ccConst.GENDERID_MALE
    if gender == GENDER.FEMALE:
        return ccConst.GENDERID_FEMALE
    raise RuntimeError('PaperDollGenderToGenderID: Invalid gender!')


@telemetry.ZONE_FUNCTION
def SetupLighting(scene, lightScene, lightColorScene, lightIntensity = 0.5):
    intensityMultiplier = 0.75 + lightIntensity / 2.0
    if scene is not None:
        lightList = []
        for l in scene.lights:
            lightList.append(l)

        for l in lightList:
            scene.RemoveLightSource(l)

        for index in range(len(lightScene.lights)):
            light = lightScene.lights[index]
            for l in lightColorScene.lights:
                if l.name == light.name:
                    light.color = l.color

            light.color = (light.color[0] * intensityMultiplier,
             light.color[1] * intensityMultiplier,
             light.color[2] * intensityMultiplier,
             1.0)
            scene.AddLightSource(light)


@telemetry.ZONE_FUNCTION
def LoadFromYaml(path):
    return LoadYamlFileNicely(path)


def HasUserDefinedWeight(category):
    return ccConst.COLORMAPPING.get(category, (0, 0))[0]


def HasUserDefinedSpecularity(category):
    return ccConst.COLORMAPPING.get(category, (0, 0))[1]


def CreateCategoryFolderIfNeeded(outputroot, folderName):
    import os
    folderName = os.path.normpath(folderName)
    if os.path.isdir(outputroot + folderName):
        return
    os.mkdir(outputroot + folderName)


def IsFactionSelectionDisabled(factionID):
    disabledFactionIDs = sm.GetService('machoNet').GetGlobalConfig().get('disabled_faction_ids', '')
    if not disabledFactionIDs:
        return False
    return factionID in [ int(disabledFactionID) for disabledFactionID in disabledFactionIDs.split(',') ]


def IsSchoolDisabled(schoolID):
    disabledSchoolIDs = sm.GetService('machoNet').GetGlobalConfig().get('disabled_school_ids', '')
    if not disabledSchoolIDs:
        return False
    return schoolID in [ int(disabledSchoolID) for disabledSchoolID in disabledSchoolIDs.split(',') ]
