#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\voiceover\bake.py
import os
import sys
from P4 import P4Exception
import ccpp4
import logging
from eveaudio.eveaudiomanager import LANGUAGE_ID_TO_BANK
from eveaudio.const import AUDIO_SOURCES_P4_DEPOT_PATH
from eveaudio.const import GENERATED_SOUNDBANKS_PATH
from eveaudio.const import WWISE_PROJECT_PATH
from fsd import GetBranchRoot
from platformtools.compatibility.exposure.wwiseinterface import ActionTypes, ImportOperation, NameConflictModes, WwiseInterfaceError, WWiseInterface
VOICES_DEPOT_PATH = '{}/Voices'.format(AUDIO_SOURCES_P4_DEPOT_PATH)
logger = logging.getLogger('eveaudio.voiceover')
logger.level = logging.INFO
logger.addHandler(logging.StreamHandler(sys.stdout))

def _P4CreateEmptyChangelist(p4, description):
    emptyChangelist = p4.save_change({'Change': 'new',
     'Description': description})[0]
    clNumber = int(emptyChangelist.split()[1])
    logger.info('Changelist {} was created...'.format(clNumber))
    return clNumber


def _P4CheckoutFolder(p4, folderFilepath, clNumber):
    logger.info('Checking out {} in perforce...'.format(folderFilepath))
    p4.run_edit('-c', clNumber, '{}/...'.format(folderFilepath))


def _P4RevertUnchangedInFolder(p4, folderFilepath):
    logger.info('Reverting unchanged files in {}...'.format(folderFilepath))
    p4.run_revert('-a', '{}/...'.format(folderFilepath))


def _ValidateInputs(p4, folderPath, languageID):
    if not os.path.isdir(folderPath):
        raise ValueError('The folder path {} is not a valid directory! Please provide a valid path to the directory that contains the .wav files you want to import and try again'.format(folderPath))
    try:
        p4.run_where('{}/...'.format(VOICES_DEPOT_PATH))[0]['path']
    except P4Exception as e:
        if 'not in client view' in e.value:
            raise P4Exception('Baking voice overs is not available without adding {} to your perforce workspace! Please add it and try again.'.format(VOICES_DEPOT_PATH))
        else:
            raise P4Exception('Voiceover baking encountered an unexpected perforce error: {}'.format(e))

    try:
        LANGUAGE_ID_TO_BANK[languageID]
    except KeyError:
        raise ValueError('The given language ID {} is not one of {}! Please provide a valid language ID and try again.'.format(languageID, LANGUAGE_ID_TO_BANK.keys()))


def _CreateOrUpdateEvents(createdObjects, interface, eventsParent):
    allEvents = []
    existingEvents = interface.GetAllItemsOfType('Event').Wait().RaiseIfFailed().result
    for obj in createdObjects:
        createdEvents = []
        if obj['type'] == 'Sound':
            for key, value in ActionTypes.iteritems():
                eventName = '{}_{}'.format(obj['name'], key.lower())
                request = interface.CreateEvent(eventsParent, obj['id'], eventName, value, nameConflictMode=NameConflictModes.REPLACE).Wait().RaiseIfFailed()
                createdEvents.append(request.result)

            generatedEvents = []
            for event in createdEvents:
                status = 'created'
                if any((event['name'] == wwiseEvent.name for wwiseEvent in existingEvents)):
                    status = 'updated'
                generatedEvents.append({'eventName': event['name'],
                 'status': status})

            allEvents.append({'audioSource': '{}.wav'.format(obj['name']),
             'generatedEvents': generatedEvents})

    return allEvents


def _GenerateSoundbanks(interface, languages):
    logger.info('Generating soundbanks...')
    soundbanksToGenerate = ['Common', 'Voice']
    interface.GenerateSoundbanks(soundbanksToGenerate, languages).Wait().RaiseIfFailed()


def _PrepP4(p4, p4DirsToSubmit, p4DirsToKeepLocal):
    msg = 'SUBMIT THIS CL FOR OTHERS TO HEAR AUTO IMPORTED VO IN GAME, IT WILL KICK OFF SOUNDBANK GENERATION (AND PLEASE DELETE THIS LINE BEFORE SUBMITTING)\nAdd voiceovers to the Wwise project using automated voiceover baking'
    submitCL = _P4CreateEmptyChangelist(p4, msg)
    for filepath in p4DirsToSubmit:
        _P4CheckoutFolder(p4, filepath, submitCL)

    msg = 'DO NOT SUBMIT THIS CL, IT WILL BE AUTOMATICALLY GENERATED AS PART OF THE BUILD\nThis changelist contains the soundbanks you need to be able to hear your newly imported voiceovers.'
    localCL = _P4CreateEmptyChangelist(p4, msg)
    for filepath in p4DirsToKeepLocal:
        _P4CheckoutFolder(p4, filepath, localCL)

    return (submitCL, localCL)


def BakeVoiceovers(folderPath, languageID = 'en', soundsParent = '\\Actor-Mixer Hierarchy\\Voice\\Auto Imported Voices\\Auto Imported Voices', eventsParent = '\\Events\\VO\\Auto Imported VO', originalsSubFolder = 'Auto Imported'):
    interface = WWiseInterface()
    try:
        p4 = ccpp4.P4InitForPath(GetBranchRoot())
        _ValidateInputs(p4, folderPath, languageID)
        language = LANGUAGE_ID_TO_BANK[languageID]
        wavDirectory = p4.run_where('{}/{}/{}'.format(VOICES_DEPOT_PATH, language, originalsSubFolder))[0]['path']
        p4DirsToSubmit = [WWISE_PROJECT_PATH, wavDirectory]
        p4DirsToKeepLocal = [GENERATED_SOUNDBANKS_PATH]
        submitCL, localCL = _PrepP4(p4, p4DirsToSubmit, p4DirsToKeepLocal)
        createdEvents = []
        interface.StartWaapiServer()
        logger.info('Importing audio files into the Wwise project...')
        request = interface.ImportFilesFromFolder(ImportOperation.REPLACE_EXISTING, folderPath, soundsParent, importLanguage=language, originalsSubFolder=originalsSubFolder).Wait().RaiseIfFailed()
        createdObjects = request.result.get('objects', [])
        if len(createdObjects) > 0:
            logger.info('Creating Wwise events for the given audio files...')
            createdEvents = _CreateOrUpdateEvents(createdObjects, interface, eventsParent)
            request = interface.SaveWwiseProject().Wait().RaiseIfFailed()
            logger.info('Wwise project saved...')
            _GenerateSoundbanks(interface, languages=[language])
        return createdEvents
    except P4Exception as e:
        logger.exception(e.value)
    except ValueError as e:
        logger.exception(e.message)
    except Exception as e:
        msg = 'An unexpected error occurred while baking voiceovers: {}'.format(e)
        baseException = ''
        if hasattr(e, 'baseExceptions') and len(e.baseExceptions) > 0:
            baseException = e.baseExceptions[0][1]
        if type(baseException) == WwiseInterfaceError:
            msg = baseException.message
        logger.exception(msg)
    finally:
        interface.KillWaapiServer()
        for filename in os.listdir(wavDirectory):
            if filename.endswith('.wav'):
                p4.run_add('-c', submitCL, os.path.join(wavDirectory, filename))

        for filepath in p4DirsToSubmit + p4DirsToKeepLocal:
            _P4RevertUnchangedInFolder(p4, filepath)

        p4.run_change('-d', submitCL)
        p4.run_change('-d', localCL)
