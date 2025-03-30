#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localizationcache\cache.py
import math
import os
import fsdlite
from fsd import GetBranchRoot, AbsJoin, GetFullName, idGenerator
branch_root = GetBranchRoot()
_localization_root = GetFullName(AbsJoin(branch_root, 'eve', 'staticData', 'localization'))
_root = GetFullName(AbsJoin(_localization_root, 'data', 'messages'))
_root_projects = GetFullName(AbsJoin(_localization_root, 'data', 'projects'))
_cache = GetFullName(AbsJoin(branch_root, 'packages', 'localizationcache', 'cached', 'localization.static'))

class MessageGroup(dict):

    def __setstate__(self, values):
        for key, value in values.iteritems():
            try:
                self[int(key)] = value
            except ValueError:
                self[str(key)] = value

    def __getstate__(self):
        return dict(self)


def Storage(customCoerce = None):
    global _cache
    global _root
    try:
        return Storage.storage
    except AttributeError:
        if os.path.exists(os.path.dirname(_cache)):
            cache = _cache
        else:
            cache = None
        Storage.storage = fsdlite.Storage(_root, cache, mapping=[('$', MessageGroup)], monitor=True, coerce=customCoerce)
        return Storage.storage


def SetRoot(path):
    global _root
    _root = path
    if hasattr(Storage, 'storage'):
        del Storage.storage


def SetCache(path):
    global _cache
    _cache = path
    if hasattr(Storage, 'storage'):
        del Storage.storage


def ResetCache():
    Storage().cache.clear()


def ResetStorage():
    try:
        del Storage.storage
    except AttributeError:
        pass


def GetMessage(path, messageID, raises = False, languageID = None):
    if not messageID:
        return
    group = LoadGroup(path)
    try:
        if languageID is None or languageID in ('en', 'en-us'):
            return group[messageID]['baseText']['text']
        return group[messageID]['internationalText'][languageID]['text']
    except KeyError:
        if not raises:
            return '{}:{}'.format(path, messageID)
        raise


def GetMessageIDByLabel(path, label):
    if not label or not path:
        return None
    group = LoadGroup(path)
    for message_id, message in group.iteritems():
        if message.get('label') == label:
            return message_id


def GetMessageWithDefault(path, messageID, default = None, languageID = None):
    try:
        return GetMessage(path, messageID, raises=True, languageID=languageID)
    except KeyError:
        return default


def GetAllMessageTexts(path, messageID):
    if not messageID:
        return None
    group = LoadGroup(path)
    allTexts = {}
    allTexts['en'] = group[messageID]['baseText']['text']
    for languageID, text in group[messageID]['internationalText'].iteritems():
        allTexts[languageID] = text['text']

    return allTexts


def GetVersion(path, messageID):
    group = LoadGroup(path)
    return group[messageID]['baseText']['version']


def UpdateMessage(path, messageID, text):
    group = LoadGroup(path)
    if UpdateMessageInGroup(group, messageID, text):
        SaveGroup(path, group)


def UpdateMessageInGroup(group, messageID, text):
    if text != group[messageID]['baseText']['text']:
        group[messageID]['baseText']['text'] = text.replace('\t', '')
        group[messageID]['baseText']['version'] += 1
        return True
    return False


def CreateMessage(path, text, context = '', messageID = None, label = None):
    messageID = messageID or CreateMessageID()
    group = LoadGroup(path)
    AddNewMessageToGroup(group, messageID, text, context, label)
    SaveGroup(path, group)
    return messageID


def CreateMessageID():
    return idGenerator.get_counter(idGenerator.MESSAGE_ID)


def AddNewMessageToGroup(group, messageID, text, context = None, label = None):
    group[messageID] = {'baseText': {'language': 'en-us',
                  'version': 1,
                  'text': text.replace('\t', '')},
     'context': context,
     'label': label,
     'internationalText': {}}


def DeleteMessage(path, messageID):
    group = LoadGroup(path)
    if RemoveMessageFromGroup(group, messageID):
        SaveGroup(path, group)


def RemoveMessageFromGroup(group, messageID):
    return group.pop(messageID, None) is not None


def LoadGroup(path):
    return Storage()[path + '/messages']


def GetGroupInfo(path = None):
    if path is not None:
        return Storage()[path + '/group']
    allGroups = [ path for path in Storage() if path.endswith('group') ]
    groupInfoByPath = {}
    for path in allGroups:
        groupInfoByPath[path[:-5]] = Storage()[path]

    return groupInfoByPath


def SaveGroup(path, data):
    storage = Storage()
    with storage:
        storage[path + '/messages'] = data


def DeleteGroup(path):
    storage = Storage()
    RemoveGroupFromProjects(path)
    with storage:
        del storage[path + '/messages']
        del storage[path + '/group']


def EnsureGroupDirectoryExists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def GetProjectStorage():
    try:
        storage = GetProjectStorage.storage
    except AttributeError:
        storage = GetProjectStorage.storage = fsdlite.Storage(data=_root_projects, cache=None, monitor=True, mapping=[('$', MessageGroup)])

    return storage


def AddGroupToProjects(parent_group_path, newGroupID):
    storage = GetProjectStorage()
    with storage:
        parent_group_id = GetGroupInfo(parent_group_path.strip('/'))['ID']
        for projectID, project in storage.iteritems():
            groups = project.get('groups', [])
            if parent_group_id in groups and newGroupID not in groups:
                groups.append(newGroupID)
                project['groups'] = groups
                storage[projectID] = project


def RemoveGroupFromProjects(group_path):
    storage = GetProjectStorage()
    with storage:
        group_id = GetGroupInfo(group_path.strip('/'))['ID']
        for projectID, project in storage.iteritems():
            groups = project.get('groups', [])
            if group_id in groups:
                groups.remove(group_id)
                project['groups'] = groups
                storage[projectID] = project


def AddGroup(path, parent_group_path = None):
    storage = Storage()
    with storage:
        path_list = [ x for x in path.split('/') ]
        if parent_group_path is None:
            parent_group_path = '/'.join(path_list[:-1])
        newGroupID = idGenerator.get_counter(idGenerator.MESSAGE_GROUP_ID)
        groupDict = {'ID': newGroupID,
         'groupName': str([ x for x in path_list if x ][-1]),
         'readOnly': False}
        EnsureGroupDirectoryExists(GetFullName(AbsJoin(_root, *path_list)))
        storage[path.strip('/') + '/group'] = groupDict
        storage[path.strip('/') + '/messages'] = {}
        AddGroupToProjects(parent_group_path, newGroupID)
    return {}


def Groups():
    return sorted([ path[:-6] for path in Storage() if path.endswith('group') ])


def Messages(path):
    try:
        return Storage()[path + '/messages']
    except:
        return {}


def BatchUpdate(message_container):
    try:
        group = LoadGroup(message_container.path)
    except KeyError:
        if message_container.parent_group_path is not None:
            group = AddGroup(message_container.path, message_container.parent_group_path)
        else:
            raise

    has_changes = False
    for message_id, message in message_container.changes.iteritems():
        if message.text is None:
            if RemoveMessageFromGroup(group, message_id):
                has_changes = True
        elif message_id in group:
            if UpdateMessageInGroup(group, message_id, message.text):
                has_changes = True
        else:
            AddNewMessageToGroup(group, message_id, message.text)
            has_changes = True

    if has_changes:
        if not group and all((message.delete_group_if_empty for message in message_container.changes.itervalues())):
            DeleteGroup(message_container.path)
        else:
            SaveGroup(message_container.path, group)


def GetGroupPath(path, buckets, messageID):
    if buckets:
        return path + '/' + str(messageID % buckets).zfill(int(math.log10(buckets)))
    return path
