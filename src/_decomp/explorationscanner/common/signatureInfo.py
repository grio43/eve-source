#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\explorationscanner\common\signatureInfo.py
from explorationscanner.common.siteInfo import SiteInfo

class SignatureInfo(SiteInfo):

    def __init__(self, position, targetID, difficulty, deviation):
        super(SignatureInfo, self).__init__(position=position, targetID=targetID, difficulty=difficulty, dungeonID=None, archetypeID=None)
        self.deviation = deviation
