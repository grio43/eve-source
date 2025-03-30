#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\paperDoll\paperDollCommonFunctions.py
import logging
import re
import yaml
import blue
import log
import stackless
import telemetry
logger = logging.getLogger(__name__)

def WaitForAll(iterable, condition):
    while any(map(condition, iterable)):
        Yield(frameNice=False)

    BeFrameNice()


def Yield(frameNice = True, ms = 15):
    try:
        if not stackless.current.is_main:
            blue.synchro.Yield()
            if frameNice:
                return BeFrameNice(ms)
        else:
            return False
    except:
        raise


def BeFrameNice(ms = 15):
    try:
        if not stackless.current.is_main:
            if ms < 1.0:
                ms = 1.0
            while blue.os.GetWallclockTimeNow() - blue.os.GetWallclockTime() > ms * 10000:
                blue.synchro.Yield()
                ms *= 1.02

            return True
        return False
    except:
        raise


def AddToDictList(d, key, item):
    l = d.get(key, [])
    l.append(item)
    d[key] = l


def GetFromDictList(d, key):
    l = d.get(key, [])
    if type(l) != list:
        return []
    return l


@telemetry.ZONE_FUNCTION
def NastyYamlLoad(yamlStr):
    yamlStr = _replace_nasty_paper_doll_references(yamlStr)
    instance = None
    try:
        blue.statistics.EnterZone('yaml.load')
        instance = yaml.load(yamlStr, Loader=yaml.CLoader)
    except Exception:
        log.LogError('PaperDoll: Yaml parsing failed for data', yamlStr)
    finally:
        blue.statistics.LeaveZone()

    return instance


def _replace_nasty_paper_doll_references(yaml_text):
    global _nasty_paper_doll_reference_pattern
    if _nasty_paper_doll_reference_pattern is None:
        _nasty_paper_doll_reference_pattern = re.compile('!!python/object:paperDoll\\.(\\w+)')
    replacement_template = '!!python/object:{}'
    return _nasty_paper_doll_reference_pattern.sub(lambda match: replacement_template.format(_get_nice_paper_doll_reference(match.group(1))), yaml_text)


_nasty_paper_doll_reference_pattern = None

def _get_nice_paper_doll_reference(nasty_name):
    return _nasty_paper_doll_class_map[nasty_name]


_nasty_paper_doll_class_map = {'AvatarPartMetaData': 'eve.common.script.paperDoll.yamlPreloader.AvatarPartMetaData',
 'ProjectedDecal': 'eve.client.script.paperDoll.projectedDecals.ProjectedDecal'}
