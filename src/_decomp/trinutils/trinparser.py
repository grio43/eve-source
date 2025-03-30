#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinutils\trinparser.py
import blue
import trinity
import yamlext

def DictToTrinityParser(trinityrecipe, persistedAttributesOnly = True):
    dr = blue.DictReader()
    dr.persistedAttributesOnly = persistedAttributesOnly
    result = dr.CreateObject(trinityrecipe)
    blue.resMan.Wait()
    return result


def TrinityToDict(blueobj):
    asStr = blue.resMan.SaveObjectToYamlString(blueobj)
    return yamlext.loads(asStr)
