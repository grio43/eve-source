#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\imageserver\generate_package.py
import sys
import argparse
import time
import os
import subprocess
import logging
searchPaths = []
if os.getenv('TEAMCITY_VERSION', False):
    pkgspath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if pkgspath not in sys.path:
        sys.path.append(pkgspath)
    mainlinepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    if mainlinepath not in sys.path:
        sys.path.append(mainlinepath)
    searchPaths = [('root', mainlinepath), ('app', 'root:/eve/client'), ('bin', 'app:bin')]
import evetypes
from iconrendering2.setup import SetupStandaloneEnvironment
from utils import WriteMapping

def ParseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outputFolder', default=None, help='Output folder for the generated icons. If none is specified, a temp folder will be used.')
    parser.add_argument('--typeIDs', default='all', nargs='+', help='TypeIDs to generate icons for.')
    parser.add_argument('--inputAlliancesFolder', default=None, help='Input folder for the player alliance logos.')
    parser.add_argument('--viewOutput', default=False, action='store_true', help='Indicates whether the output folder(s) will be automatically opened in the explorer.')
    return parser.parse_args()


def main():
    logger, resourceMapper, sofFactory = SetupStandaloneEnvironment(True, True, True, logLevel=logging.INFO, blueSearchPaths=searchPaths)
    try:
        start = time.clock()
        from generate.process_types import GenerateVariationsForTypeIDs
        from generate.process_corps import GenerateCorpAndFactionIcons
        from generate.process_alliances import GeneratePlayerAllianceIcons
        from generate.process_characters import GenerateCharacterIcons
        arguments = ParseArguments()
        if arguments.viewOutput:
            subprocess.Popen('explorer %s' % arguments.outputFolder.replace('/', '\\'))
        if isinstance(arguments.typeIDs, str) and arguments.typeIDs.lower() == 'all':
            typeIDs = evetypes.GetAllTypeIDs()
        else:
            typeIDs = [ int(t) for t in arguments.typeIDs ]
        logger.info('Generating icons for %s typeIDs...' % len(typeIDs))
        typeMapping, typeMappingZH, errorList = GenerateVariationsForTypeIDs(arguments.outputFolder, typeIDs, resourceMapper, sofFactory, logger)
        typeMappingFile = WriteMapping(typeMapping, arguments.outputFolder, 'typeIDMapping')
        typeMappingFileZH = WriteMapping(typeMappingZH, arguments.outputFolder, 'typeIDMapping.zh')
        for e in errorList:
            logger.error(e)

        logger.info('Generating icons for NPC corps and factions...')
        npcMapping, npcMappingZH, errorList = GenerateCorpAndFactionIcons(arguments.outputFolder)
        npcMappingFile = WriteMapping(npcMapping, arguments.outputFolder, 'corpsFactionsMapping')
        npcMappingFileZH = WriteMapping(npcMappingZH, arguments.outputFolder, 'corpsFactionsMapping.zh')
        for e in errorList:
            logger.error(e)

        logger.info('Generating icons for player alliances...')
        alliancesMapping, alliancesMappingZH, errorList = GeneratePlayerAllianceIcons(arguments.inputAlliancesFolder, arguments.outputFolder)
        alliancesMappingFile = WriteMapping(alliancesMapping, arguments.outputFolder, 'alliancesMapping')
        alliancesMappingFileZH = WriteMapping(alliancesMappingZH, arguments.outputFolder, 'alliancesMapping.zh')
        for e in errorList:
            logger.error(e)

        logger.info('Generating icons for characters...')
        charactersMapping, charactersMappingZH, errorList = GenerateCharacterIcons(arguments.outputFolder)
        charactersMappingFile = WriteMapping(charactersMapping, arguments.outputFolder, 'charactersMapping')
        charactersMappingFileZH = WriteMapping(charactersMappingZH, arguments.outputFolder, 'charactersMapping.zh')
        for e in errorList:
            logger.error(e)

        logger.info('Compiling package mapping...')
        globalMapping = {}
        globalMapping['en'] = [ os.path.basename(x) for x in [typeMappingFile,
         npcMappingFile,
         alliancesMappingFile,
         charactersMappingFile] ]
        globalMapping['zh'] = [ os.path.basename(x) for x in [typeMappingFileZH,
         npcMappingFileZH,
         alliancesMappingFileZH,
         charactersMappingFileZH] ]
        WriteMapping(globalMapping, arguments.outputFolder, 'imageserver_package')
        end = time.clock()
        elapsed = end - start
        logger.info('All done. Total time : %.3f seconds' % elapsed)
    except IOError as e:
        logger.error('%s %s' % (e.filename, e.strerror))
    except evetypes.TypeNotFoundException as e:
        logger.error('TypeID not found: %s' % e.message)
    except Exception as e:
        logger.error(e.message)


if __name__ == '__main__':
    import blue
    t = blue.pyos.CreateTasklet(main, (), {})
    while t.alive:
        blue.os.Pump()
