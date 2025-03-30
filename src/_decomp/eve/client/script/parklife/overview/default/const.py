#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\default\const.py
from eve.client.script.parklife.overview.default.data.jotunn_default import JOTUNN_DEFAULT
from eve.client.script.parklife.overview.default.data.old_default import OLD_DEFAULT

class OverviewType(object):
    FSD = 1
    YAML = 2


OVERVIEWS = [('old_default', OverviewType.FSD, False), ('jotunn_default', OverviewType.YAML, True)]
DEFAULT = 'jotunn_default'
YAML_OVERVIEWS = {'old_default': {'yaml': OLD_DEFAULT,
                 'default_preset': 'default',
                 'preset_name_ids': {'defaultpvp': 59570,
                                     'defaultmining': 59571,
                                     'defaultwarpto': 59572,
                                     'defaultloot': 59573,
                                     'defaultall': 59574,
                                     'defaultdrones': 59575,
                                     'default': 59576},
                 'tab_name_ids': {0: 59576,
                                  1: 59571,
                                  2: 59572}},
 'jotunn_default': {'yaml': JOTUNN_DEFAULT,
                    'default_preset': 'DefaultPreset_639452',
                    'preset_name_ids': {},
                    'tab_name_ids': {0: 59576,
                                     1: 639384,
                                     2: 59571,
                                     3: 59572,
                                     4: 59574}}}
