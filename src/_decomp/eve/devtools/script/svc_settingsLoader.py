#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\svc_settingsLoader.py
import carbon.client.script.sys.appUtils as appUtils
import carbonui.const as uiconst
import yaml
import os
from carbon.common.script.sys.service import Service
from eve.client.script.ui.control.fileDialog import FileDialog
import raffles.common.const
from utillib import KeyVal
from eveexceptions import UserError

class PrettySafeLoader(yaml.SafeLoader):

    def construct_python_tuple(self, node):
        return tuple(self.construct_sequence(node))

    def construct_python_utillib_KeyVal(self, node):
        return KeyVal(self.construct_mapping(node))

    def construct_python_unicode(self, node):
        return self.construct_scalar(node)

    def construct_python_long(self, node):
        return long(self.construct_yaml_int(node))

    def construct_python_BlueprintType(self, node):
        return raffles.common.const.BlueprintType(int(self.construct_scalar(node.value[0])))


PrettySafeLoader.add_constructor(u'tag:yaml.org,2002:python/tuple', PrettySafeLoader.construct_python_tuple)
PrettySafeLoader.add_constructor(u'tag:yaml.org,2002:python/object:util.KeyVal', PrettySafeLoader.construct_python_utillib_KeyVal)
PrettySafeLoader.add_constructor(u'tag:yaml.org,2002:python/object:utillib.KeyVal', PrettySafeLoader.construct_python_utillib_KeyVal)
PrettySafeLoader.add_constructor(u'tag:yaml.org,2002:python/unicode', PrettySafeLoader.construct_python_unicode)
PrettySafeLoader.add_constructor(u'tag:yaml.org,2002:python/long', PrettySafeLoader.construct_python_long)
PrettySafeLoader.add_constructor(u'tag:yaml.org,2002:python/object/apply:raffles.common.const.BlueprintType', PrettySafeLoader.construct_python_BlueprintType)

class SettingsLoaderSvc(Service):
    __guid__ = 'svc.settingsLoader'

    def Run(self, *args):
        self.exportActive = False

    def Load(self):
        ret = eve.Message('CustomWarning', {'header': 'Load Settings',
         'warning': 'Note that you have to restart after loading new settings'}, uiconst.OKCANCEL)
        if ret == uiconst.ID_CANCEL:
            return
        path = settings.public.ui.Get('LoadSettingsPath', None)
        selection = FileDialog.SelectFiles(path=path, fileExtensions=['yaml'], multiSelect=False)
        if selection is None or len(selection.files) < 1 or selection.files[0] == '':
            return
        fileName = selection.files[0]
        folder = os.path.dirname(fileName)
        save = eve.Message('CustomQuestion', {'header': 'Save Current Settings?',
         'question': 'Do you want to save your current settings?'}, uiconst.YESNO)
        if save == uiconst.ID_YES:
            self.SaveCurrentSettings(folder)
        self.LoadSettings(fileName)
        settings.public.ui.Set('LoadSettingsPath', folder)
        appUtils.Reboot('Settings loaded')

    def Export(self):
        path = settings.public.ui.Get('LoadSettingsPath', None)
        selection = FileDialog.SelectFolders(path=path, multiSelect=False)
        if selection is None or len(selection.folders) < 1 or selection.folders[0] == '':
            return
        folder = selection.folders[0]
        self.SaveCurrentSettings(folder)
        settings.public.ui.Set('LoadSettingsPath', folder)

    def SaveCurrentSettings(self, folder):
        allSettings = {}
        for settingsType in ('public', 'user', 'char'):
            allSettings[settingsType] = getattr(settings, settingsType).datastore

        data = yaml.dump(allSettings)
        charName = cfg.eveowners.Get(session.charid).name
        maxIndex = -1
        for file in os.listdir(folder):
            if file.startswith(charName) and file.endswith('.yaml'):
                indexChar = file[len(charName)]
                try:
                    index = int(indexChar)
                    maxIndex = max(maxIndex, index)
                except ValueError:
                    maxIndex = 0

        if maxIndex > -1:
            append = str(maxIndex + 1)
        else:
            append = ''
        backupFile = os.path.join(folder, charName + append + '.yaml')
        with open(backupFile, 'w') as f:
            f.write(data)
        eve.Message('CustomInfo', {'info': 'Current settings saved as ' + backupFile})

    def LoadSettings(self, fileName):
        with open(fileName, 'r') as f:
            try:
                data = yaml.load(f, Loader=PrettySafeLoader)
            except Exception as e:
                self.LogException('Failed loading settings')
                msg = 'The settings file could not be read correctly and the import was aborted. The likely cause are settings with unsupported objects. Consider deleting the involved settings. <br>Reason: %s' % str(e)
                raise UserError('CustomError', {'error': msg})

            settings.public.datastore = data['public']
            settings.user.datastore = data['user']
            settings.char.datastore = data['char']
            settings.public.FlagDirty()
            settings.user.FlagDirty()
            settings.char.FlagDirty()
        sm.GetService('settings').SaveSettings(async=False)
