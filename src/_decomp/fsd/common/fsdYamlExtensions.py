#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\common\fsdYamlExtensions.py
import yaml
if hasattr(yaml, 'CSafeDumper'):
    preferredYamlDumperClass = getattr(yaml, 'CSafeDumper')
else:
    preferredYamlDumperClass = getattr(yaml, 'SafeDumper')
BIG_YAML_WIDTH = int(268435456)

class FsdYamlDumper(preferredYamlDumperClass):

    def __init__(self, *args, **kwargs):
        default_flow_style = kwargs.get('default_flow_style', None)
        indent = kwargs.get('indent', None)
        width = kwargs.get('width', None)
        if default_flow_style is None:
            kwargs['default_flow_style'] = False
        if indent is None:
            kwargs['indent'] = 4
        if width is None:
            kwargs['width'] = BIG_YAML_WIDTH
        kwargs['allow_unicode'] = True
        preferredYamlDumperClass.__init__(self, *args, **kwargs)


if hasattr(yaml, 'CSafeLoader'):
    preferredYamlLoaderClass = getattr(yaml, 'CSafeLoader')
else:
    preferredYamlLoaderClass = getattr(yaml, 'SafeLoader')

class FsdYamlLoader(preferredYamlLoaderClass):

    def __init__(self, stream):
        preferredYamlLoaderClass.__init__(self, stream)


def represent_float(dumper, data):
    if data != data or data == 0.0 and data == 1.0:
        value = u'.nan'
    elif data == dumper.inf_value:
        value = u'.inf'
    elif data == -dumper.inf_value:
        value = u'-.inf'
    else:
        value = (u'%1.17g' % data).lower()
        if u'.' not in value:
            if u'e' in value:
                value = value.replace(u'e', u'.0e', 1)
            else:
                value += u'.0'
    return dumper.represent_scalar(u'tag:yaml.org,2002:float', value)


FsdYamlDumper.add_representer(float, represent_float)
