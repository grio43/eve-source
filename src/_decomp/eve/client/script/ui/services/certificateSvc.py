#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\certificateSvc.py
from collections import defaultdict
import localization
import log
from carbon.common.script.sys.service import Service
from skills.certificates.certificateConst import CERTIFICATE_GRADES_LABELS

class Certificate(object):

    def __init__(self, certificateID, groupID, nameID, descriptionID, skillTypes, recommendedFor):
        self.skillSvc = sm.GetService('skills')
        self.certificateID = certificateID
        self.groupID = groupID
        self.nameID = nameID
        self.descriptionID = descriptionID
        self._SetupSkills(skillTypes)
        self.recommendedFor = recommendedFor
        self.currentLevel = None

    def __str__(self):
        return 'Certificate: %s (%d)' % (self.GetName(), self.certificateID)

    def _SetupSkills(self, skillTypes):
        skills = {}
        for skillTypeID, level in skillTypes.iteritems():
            skills[skillTypeID] = {}
            skills[skillTypeID][1] = level.basic
            skills[skillTypeID][2] = level.standard
            skills[skillTypeID][3] = level.improved
            skills[skillTypeID][4] = level.advanced
            skills[skillTypeID][5] = level.elite

        self.skills = skills

    def GetName(self):
        return localization.GetByMessageID(self.nameID)

    def GetDescription(self):
        return localization.GetByMessageID(self.descriptionID)

    def GetLabel(self, level):
        return localization.GetByLabel('UI/InfoWindow/CertificateNameWithProgress', certificateName=self.GetName(), skillsTrained=self.CountCompletedSkills(level), skillsTotal=self.CountSkills(level))

    def GetSkills(self):
        return self.skills

    def SkillsByTypeAndLevel(self, level):
        return [ (typeID, levelData[level]) for typeID, levelData in self.skills.iteritems() if levelData[level] > 0 ]

    def GetLevel(self):
        if self.currentLevel is None:
            self.currentLevel = 0
            for i in xrange(5, 0, -1):
                for typeID in self.skills.iterkeys():
                    charLevel = self.skillSvc.MySkillLevel(typeID)
                    reqLevel = self.skills[typeID][i]
                    if reqLevel > 0 and charLevel < reqLevel:
                        break
                else:
                    self.currentLevel = i
                    break

        return self.currentLevel

    def HasAllSkills(self, level):
        for typeID, levels in self.skills.iteritems():
            if levels[level] > 0 and not self.skillSvc.HasSkill(typeID):
                return False

        return True

    def CountCompletedSkills(self, level):
        count = 0
        for typeID, levels in self.skills.iteritems():
            if levels[level] > 0 and self.skillSvc.MySkillLevel(typeID) >= levels[level]:
                count += 1

        return count

    def CountSkills(self, level):
        count = 0
        for typeID, levels in self.skills.iteritems():
            if levels[level] > 0:
                count += 1

        return count

    def ClearCache(self):
        self.currentLevel = None


class Certificates(Service):
    __notifyevents__ = ['OnSkillsChanged', 'OnSessionReset']
    __guid__ = 'svc.certificates'
    __servicename__ = 'certificates'
    __displayname__ = 'Certificate Service'
    __startupdependencies__ = ['settings', 'godma']

    def __init__(self):
        super(Certificates, self).__init__()
        self.certificates = {}
        try:
            for key, value in cfg.certificates['certificates'].iteritems():
                if hasattr(value, 'recommendedFor'):
                    recommendedFor = value.recommendedFor
                else:
                    recommendedFor = []
                self.certificates[key] = Certificate(key, value.groupID, value.nameID, value.descriptionID, value.skillTypes, recommendedFor)

        except KeyError:
            log.LogException()

    def OnSessionReset(self):
        self.OnSkillsChanged()

    def OnSkillsChanged(self, *args):
        for certificate in self.certificates.itervalues():
            certificate.ClearCache()

    def GetCertificate(self, certificateID):
        return self.certificates[certificateID]

    def GetAllCertificatesByCategoryID(self):
        return self._GroupByCategoryID(self.certificates.values())

    def GetMyCertificates(self):
        myCertificates = {}
        for certificateID, certificate in self.certificates.iteritems():
            if certificate.GetLevel() > 0:
                myCertificates[certificateID] = certificate

        return myCertificates

    def GetMyCertificatesByCategoryID(self):
        certs = self.GetMyCertificates().values()
        return self._GroupByCategoryID(certs)

    def _GroupByCategoryID(self, certificates):
        ret = defaultdict(list)
        for cert in certificates:
            ret[cert.groupID].append(cert)

        return ret

    def GetCertificatesByGroupID(self, groupID):
        return [ cert for cert in self.certificates.values() if cert.groupID == groupID ]

    def GetCurrCharMasteryLevel(self, shipTypeID):
        for i in xrange(5, 0, -1):
            certificates = self.GetCertificatesForShipByMasteryLevel(shipTypeID, i)
            levels = set()
            for certificate in certificates:
                levels.add(certificate.GetLevel())

            for level in levels:
                if level < i:
                    break
                else:
                    return i

        return 0

    def GetMasteryIconForLevel(self, masteryLevel):
        if masteryLevel == 0:
            return 'res:/UI/Texture/Classes/Mastery/masterySmall0.png'
        if masteryLevel == 1:
            return 'res:/UI/Texture/Classes/Mastery/masterySmall1.png'
        if masteryLevel == 2:
            return 'res:/UI/Texture/Classes/Mastery/masterySmall2.png'
        if masteryLevel == 3:
            return 'res:/UI/Texture/Classes/Mastery/masterySmall3.png'
        if masteryLevel == 4:
            return 'res:/UI/Texture/Classes/Mastery/masterySmall4.png'
        if masteryLevel == 5:
            return 'res:/UI/Texture/Classes/Mastery/masterySmall5.png'

    def GetCertificatesForShipByMasteryLevel(self, typeID, masteryLevel):
        if typeID in cfg.certificates['masteries'] and masteryLevel > 0:
            certificates = cfg.certificates['masteries'][typeID][masteryLevel - 1]
            return [ self.certificates[certificateID] for certificateID in certificates ]
        return []

    def GetSkillsRequiredForMasteryLevel(self, typeID, masteryLevel):
        skills = {}
        for certificate in self.GetCertificatesForShipByMasteryLevel(typeID, masteryLevel):
            for skillID, level in certificate.SkillsByTypeAndLevel(masteryLevel):
                skills[skillID] = max(skills.get(skillID, 0), level)

        return skills

    def GetShipTrainingTimeForMasteryLevel(self, typeID, masteryLevel):
        skills = self.GetSkillsRequiredForMasteryLevel(typeID, masteryLevel)
        return sm.GetService('skills').GetTrainingTimeForSkills(skills)

    def GetCertificateTrainingTimeForMasteryLevel(self, certificateID, masteryLevel):
        certificate = self.certificates[certificateID]
        skills = {}
        for skillID, level in certificate.SkillsByTypeAndLevel(masteryLevel):
            skills[skillID] = max(skills.get(skillID, 0), level)

        return sm.GetService('skills').GetTrainingTimeForSkills(skills)

    def GetCertificateRecommendationsFromCertificateID(self, certificateID):
        return self.certificates[certificateID].recommendedFor

    def GetCertificateLabel(self, certificateID):
        certificate = self.certificates[certificateID]
        levelPath = CERTIFICATE_GRADES_LABELS.get(certificate.GetLevel())
        level = localization.GetByLabel(levelPath)
        return (certificate.GetName(), level, certificate.GetDescription())
