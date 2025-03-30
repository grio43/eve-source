#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\icon_cli.py
import argparse
import blue
import uthread2
import evetypes
import fsdBuiltData.common.graphicIDs as graphicIDs
import fsdBuiltData.common.iconIDs as iconIDs
from platformtools.compatibility.exposure import perforceutils
from iconrendering2.const import InputType, Language
from iconrendering2.icongenerator import IconGenerator, Options
from iconrendering2.setup import SetupStandaloneEnvironment

class InputTypeException(Exception):
    pass


class OutputFolderException(Exception):
    pass


def Setup():
    changelist = perforceutils.p4manager().get_or_create_changelist('Icon CLI')
    logger, resourceMapper, sofFactory = SetupStandaloneEnvironment()
    iconGenerator = IconGenerator(resourceMapper=resourceMapper, sofFactory=sofFactory, changelist=changelist, language=Language.AUTO_DETECT, options=Options.VIEW_OUTPUT | Options.CHECKOUT)
    return (logger, iconGenerator)


def _PrepAsset(asset):
    try:
        return int(asset)
    except Exception:
        return asset


def _DetermineInput(asset):
    if isinstance(asset, str):
        if asset.endswith('.red'):
            return InputType.RED_FILE
        return
    if graphicIDs.GetGraphic(asset) is not None:
        return InputType.GRAPHIC_ID
    if evetypes.Exists(asset):
        return InputType.TYPE_ID
    if iconIDs.GetIcon(asset) is not None:
        return InputType.ICON_ID


def _DetermineOutput(asset, inputType):
    iconFolder = None
    if inputType == InputType.GRAPHIC_ID:
        iconFolder = graphicIDs.GetIconFolder(asset)
    elif inputType == InputType.TYPE_ID:
        graphic = evetypes.GetGraphicID(asset)
        iconFolder = graphicIDs.GetIconFolder(graphic)
    if iconFolder is not None:
        return blue.paths.ResolvePath(iconFolder)


def GenerateIcons(asset, output, inputType):
    logger, iconGenerator = Setup()
    asset = _PrepAsset(asset)
    inputType = inputType or _DetermineInput(asset)
    if inputType is None:
        raise InputTypeException()
    output = output or _DetermineOutput(asset, inputType)
    if output is None:
        raise OutputFolderException()
    logger.info('Processing %s as a %s. Will save it to %s' % (asset, inputType, output))
    iconGenerator.Generate(inputType, asset, output)
    logger.info('Done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Icon generator')
    parser.add_argument('asset', help='path, iconId, graphicId or typeID')
    parser.add_argument('-output', default='', help="Usually can be inferred by the asset, but if it can't then specify it here")
    parser.add_argument('-inputType', default=None, choices=[ k[1] for k in InputType.GetEnumAsList() ], help="Usually can be inferred by the asset, but if it can't then specify it here")
    arguments = parser.parse_args()
    t = uthread2.StartTasklet(GenerateIcons, arguments.asset, arguments.output, arguments.inputType)
    while t.IsAlive():
        blue.os.Pump()
