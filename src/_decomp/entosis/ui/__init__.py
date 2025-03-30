#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\entosis\ui\__init__.py


def IsSameCaptureTeam(allianceID, teamID):
    if teamID is None or allianceID is None:
        return False
    if teamID > 0 and teamID == allianceID:
        return True
    if teamID < 0 and -teamID != allianceID:
        return True
    return False
