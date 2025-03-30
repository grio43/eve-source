#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\structures\const.py
from platformtools.compatibility.dependencies.itertoolsext import Enum
from inventorycommon import const as invconst
FLAG_PAINTWORK_SKINR_KILLSWITCH = 'heraldry-disable-structure-paintworks-and-skinr'
FLAG_PAINTWORK_SKINR_KILLSWITCH_DEFAULT = False
PAINT_ELIGIBLE_STRUCTURE_TYPE_IDS = [invconst.typeCitadelAstrahus,
 invconst.typeCitadelFortizar,
 invconst.typeCitadelKeepstar,
 invconst.typeEngineeringComplexRaitaru,
 invconst.typeEngineeringComplexAzbel,
 invconst.typeEngineeringComplexSotiyo,
 invconst.typeRefineryAthanor,
 invconst.typeRefineryTatara,
 invconst.typeUpwellCynosuralBeacon,
 invconst.typeUpwellCynosuralSystemJammer,
 invconst.typeUpwellSmallStargate]

@Enum

class StructurePaintSlot(object):
    PRIMARY = 'primary'
    SECONDARY = 'secondary'
    DETAILING = 'detailing'


SLOT_ORDER = [StructurePaintSlot.PRIMARY, StructurePaintSlot.SECONDARY, StructurePaintSlot.DETAILING]
