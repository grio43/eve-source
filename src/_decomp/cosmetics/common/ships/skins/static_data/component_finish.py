#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\static_data\component_finish.py
from itertoolsext.Enum import SortedEnum

@SortedEnum

class ComponentFinish(object):
    MATTE = 'Matte'
    SATIN = 'Satin'
    GLOSS = 'Gloss'


def get_finish_from_fsd(fsd_finish):
    if fsd_finish == 'Satin':
        return ComponentFinish.SATIN
    if fsd_finish == 'Gloss':
        return ComponentFinish.GLOSS
    if fsd_finish == 'Matte':
        return ComponentFinish.MATTE
