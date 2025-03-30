#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\settingsYamlLoader.py
import yaml

class UnicodeConvertingYamlLoader(yaml.CSafeLoader):
    pass


def StringToUnicodeConstructor(loader, node):
    s = loader.construct_scalar(node)
    return unicode(s)


UnicodeConvertingYamlLoader.add_constructor(u'tag:yaml.org,2002:str', StringToUnicodeConstructor)
