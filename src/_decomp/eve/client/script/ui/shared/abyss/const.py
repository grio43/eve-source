#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\abyss\const.py
import inventorycommon.const as invconst
from abyss.common import TIER_0_DEMO
from abyss.common import TIER_1, TIER_2, TIER_3, TIER_4, TIER_5, TIER_0, TIER_6
TIER_DESCRIPTION_BY_TIER = {TIER_0: 'UI/Abyss/tranquilDescription',
 TIER_0_DEMO: 'UI/Abyss/tranquilDescription',
 TIER_1: 'UI/Abyss/CalmDescription',
 TIER_2: 'UI/Abyss/AgitatedDescription',
 TIER_3: 'UI/Abyss/FierceDescription',
 TIER_4: 'UI/Abyss/RagingDescription',
 TIER_5: 'UI/Abyss/ChaoticDescription',
 TIER_6: 'UI/Abyss/cataclysmicDescription'}
WEATHER_DESCRIPTION_BY_TYPE = {invconst.typeCausticAbyss: 'UI/Abyss/ExoticParticleStormDescription',
 invconst.typeDarkAbyss: 'UI/Abyss/DarkMatterFieldDescription',
 invconst.typeInfernalAbyss: 'UI/Abyss/PlasmaFirestormDescription',
 invconst.typeElectricAbyss: 'UI/Abyss/ElectricalStormDescription',
 invconst.typeXenonAbyss: 'UI/Abyss/GammaRayAfterglowDescription'}
