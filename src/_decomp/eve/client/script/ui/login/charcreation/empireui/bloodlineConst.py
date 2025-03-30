#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation\empireui\bloodlineConst.py
from carbon.common.lib.const import genderFemale, genderMale
from eve.common.lib.appConst import bloodlineAmarr, bloodlineNiKunni, bloodlineKhanid
from eve.common.lib.appConst import bloodlineAchura, bloodlineCivire, bloodlineDeteis
from eve.common.lib.appConst import bloodlineGallente, bloodlineIntaki, bloodlineJinMei
from eve.common.lib.appConst import bloodlineBrutor, bloodlineSebiestor, bloodlineVherokior
IMAGES_PATH = 'res:/UI/Texture/classes/EmpireSelection/BloodlineImages/%s.png'
VIDEO_PATH = 'res:/video/empireselection/bloodlines/%s.webm'

class BloodlineResType(object):
    SELECTED = 1
    NOT_SELECTED = 2


BLOODLINE_RES = {BloodlineResType.SELECTED: {bloodlineAmarr: {genderFemale: 'Amarr_Amarr_FS',
                                              genderMale: 'Amarr_Amarr_MS'},
                             bloodlineNiKunni: {genderFemale: 'Amarr_NiKunni_FS',
                                                genderMale: 'Amarr_NiKunni_MS'},
                             bloodlineKhanid: {genderFemale: 'Amarr_Khanid_FS',
                                               genderMale: 'Amarr_Khanid_MS'},
                             bloodlineAchura: {genderFemale: 'Caldari_Achura_FS',
                                               genderMale: 'Caldari_Achura_MS'},
                             bloodlineCivire: {genderFemale: 'Caldari_Civire_FS',
                                               genderMale: 'Caldari_Civire_MS'},
                             bloodlineDeteis: {genderFemale: 'Caldari_Deteis_FS',
                                               genderMale: 'Caldari_Deteis_MS'},
                             bloodlineGallente: {genderFemale: 'Gallente_Gallente_FS',
                                                 genderMale: 'Gallente_Gallente_MS'},
                             bloodlineIntaki: {genderFemale: 'Gallente_Intaki_FS',
                                               genderMale: 'Gallente_Intaki_MS'},
                             bloodlineJinMei: {genderFemale: 'Gallente_JinMei_FS',
                                               genderMale: 'Gallente_JinMei_MS'},
                             bloodlineBrutor: {genderFemale: 'Minmatar_Brutor_FS',
                                               genderMale: 'Minmatar_Brutor_MS'},
                             bloodlineSebiestor: {genderFemale: 'Minmatar_Sebiestor_FS',
                                                  genderMale: 'Minmatar_Sebiestor_MS'},
                             bloodlineVherokior: {genderFemale: 'Minmatar_Vherokior_FS',
                                                  genderMale: 'Minmatar_Vherokior_MS'}},
 BloodlineResType.NOT_SELECTED: {bloodlineAmarr: {genderFemale: 'Amarr_Amarr_FD',
                                                  genderMale: 'Amarr_Amarr_MD'},
                                 bloodlineNiKunni: {genderFemale: 'Amarr_NiKunni_FD',
                                                    genderMale: 'Amarr_NiKunni_MD'},
                                 bloodlineKhanid: {genderFemale: 'Amarr_Khanid_FD',
                                                   genderMale: 'Amarr_Khanid_MD'},
                                 bloodlineAchura: {genderFemale: 'Caldari_Achura_FD',
                                                   genderMale: 'Caldari_Achura_MD'},
                                 bloodlineCivire: {genderFemale: 'Caldari_Civire_FD',
                                                   genderMale: 'Caldari_Civire_MD'},
                                 bloodlineDeteis: {genderFemale: 'Caldari_Deteis_FD',
                                                   genderMale: 'Caldari_Deteis_MD'},
                                 bloodlineGallente: {genderFemale: 'Gallente_Gallente_FD',
                                                     genderMale: 'Gallente_Gallente_MD'},
                                 bloodlineIntaki: {genderFemale: 'Gallente_Intaki_FD',
                                                   genderMale: 'Gallente_Intaki_MD'},
                                 bloodlineJinMei: {genderFemale: 'Gallente_JinMei_FD',
                                                   genderMale: 'Gallente_JinMei_MD'},
                                 bloodlineBrutor: {genderFemale: 'Minmatar_Brutor_FD',
                                                   genderMale: 'Minmatar_Brutor_MD'},
                                 bloodlineSebiestor: {genderFemale: 'Minmatar_Sebiestor_FD',
                                                      genderMale: 'Minmatar_Sebiestor_MD'},
                                 bloodlineVherokior: {genderFemale: 'Minmatar_Vherokior_FD',
                                                      genderMale: 'Minmatar_Vherokior_MD'}}}

def GetImage(type, bloodlineID, gender):
    return IMAGES_PATH % BLOODLINE_RES[type][bloodlineID][gender]


def GetVideo(type, bloodlineID, gender):
    return VIDEO_PATH % BLOODLINE_RES[type][bloodlineID][gender]


PLATFORM_PATH = 'res:/UI/Texture/classes/EmpireSelection/shadowBlob.png'
PLATFORM_VERTICAL_OFFSET = 5
PLATFORM_HORIZONTAL_OFFSET_DEFAULT = {genderFemale: 0,
 genderMale: 25}
PLATFORM_HORIZONTAL_OFFSETS = {(bloodlineJinMei, genderMale): 20,
 (bloodlineNiKunni, genderMale): 5,
 (bloodlineGallente, genderMale): 15,
 (bloodlineIntaki, genderMale): 15,
 (bloodlineSebiestor, genderMale): 15}

def GetPlatformHorizontalOffset(bloodlineID, genderID):
    if (bloodlineID, genderID) in PLATFORM_HORIZONTAL_OFFSETS:
        return PLATFORM_HORIZONTAL_OFFSETS[bloodlineID, genderID]
    return PLATFORM_HORIZONTAL_OFFSET_DEFAULT[genderID]
