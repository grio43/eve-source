#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\export.py
import codecs
import operator
import os
import sys
import yaml
from xml.dom.minidom import getDOMImplementation, parse
import blue
import evetypes
import localization
import utillib
from carbon.common.script.util.commonutils import StripTags
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.stringManip import SanitizeFilename
import overviewPresets.overviewSettingsConst as osConst
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.checkbox import CheckboxEntry
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from eve.client.script.ui.control import eveLabel, eveScroll
from eve.client.script.ui.control.draggableShareContainer import DraggableShareContainer
from eveexceptions import UserError
from inventorycommon.util import IsShipFittable, IsSubsystemFlag, IsSubsystemFlagVisible
from overviewPresets import overviewSettingsConst
from overviewPresets.overviewPresetUtil import GetDeterministicListFromDict, GetDictFromList, ReplaceInnerListsWithDicts
from overviewPresets.overviewSettingsConst import SETTING_BRACKETS_SHOWNONE, SETTING_BRACKETS_SHOWSPECIALS, SETTING_BRACKETS_SHOWALL, TAB_SETTING_IDS, MAX_SHARED_PRESETS
from textImporting import StripImportantSymbol
INVALID_FLAG_STRING = 'invalid flag'

class ImportBaseWindow(Window):
    __guid__ = 'form.ImportBaseWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetMinSize([450, 250])
        self.minWidth = 225
        self.scrollWidth = 0
        dirpath = attributes.get('dirpath', None)
        if dirpath:
            self.dirpath = dirpath
        else:
            self.dirpath = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'Overview')
        self.ConstructLayout()

    def ConstructLayout(self, *args):
        self.sr.fileContainer = Container(name='fileContainer', align=uiconst.TOLEFT, parent=self.sr.main, padTop=const.defaultPadding, width=256)
        self.sr.profilesContainer = Container(name='profilesContainer', align=uiconst.TOALL, parent=self.sr.main, pos=(0, 0, 0, 0))
        self.sr.fileHeader = eveLabel.CaptionLabel(text=localization.GetByLabel('UI/Common/Files/FileName'), parent=self.sr.fileContainer, left=const.defaultPadding, align=uiconst.TOTOP, fontsize=14)
        fileScrollCont = Container(name='fileScrollCont', parent=self.sr.fileContainer, align=uiconst.TOALL)
        self.sr.fileScroll = eveScroll.Scroll(name='fileScroll', parent=fileScrollCont, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.refreshFileListBtn = ButtonGroup(btns=[[localization.GetByLabel('UI/Commands/Refresh'),
          self.RefreshFileList,
          (),
          None]], parent=self.sr.fileContainer, idx=0)
        profilesTopCont = Container(name='fileTopCont', parent=self.sr.profilesContainer, align=uiconst.TOTOP, height=40)
        profilesScrollCont = Container(name='fileScrollCont', parent=self.sr.profilesContainer, align=uiconst.TOALL)
        self.sr.profilesHeader = eveLabel.CaptionLabel(text=localization.GetByLabel('UI/Common/PleaseSelect'), parent=profilesTopCont, align=uiconst.TOPLEFT, left=4)
        self.sr.profilesHeader.fontsize = 14
        self.checkAllCB = Checkbox(text=localization.GetByLabel('UI/Shared/CheckAllOn'), parent=profilesTopCont, align=uiconst.TOBOTTOM, height=16, padLeft=const.defaultPadding, callback=self.CheckAll, checked=True)
        self.sr.profilesScroll = eveScroll.Scroll(name='profilesScroll', parent=profilesScrollCont, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.importProfilesBtnGroup = ButtonGroup(parent=self.sr.profilesContainer, idx=0, state=uiconst.UI_NORMAL)
        self.sr.importProfilesBtn = self.sr.importProfilesBtnGroup.AddButton(localization.GetByLabel('UI/Commands/Import'), self.Import)
        self.ChangeImportButtonDisplayState(display=False)
        self.RefreshFileList()

    def RefreshFileList(self, *args):
        fileList = self.GetFilesByExt('.xml')
        contentList = []
        for fileName in fileList:
            contentList.append(GetFromClass(Generic, {'label': fileName,
             'OnClick': self.OnFileSelected}))

        self.sr.fileScroll.Load(contentList=contentList)

    def GetFilesByExt(self, ext):
        fileList = []
        if os.path.exists(self.dirpath):
            for file in os.listdir(self.dirpath):
                if file.endswith(ext):
                    fileList.append(file[:-len(ext)])

        return fileList

    def OnChange(self, *args):
        self.ChangeImportButtonState()

    def ChangeImportButtonState(self):
        anySelected = self.IsAnyEntrySelected()
        self.ChangeImportButtonDisplayState(display=bool(anySelected))

    def ChangeImportButtonDisplayState(self, display):
        self.sr.importProfilesBtnGroup.display = display

    def IsAnyEntrySelected(self):
        for entry in self.sr.profilesScroll.GetNodes():
            if entry.checked:
                return True

        return False

    def Import(self, *args):
        raise NotImplementedError('')

    def OnFileSelected(self, entry):
        raise NotImplementedError('')

    def CheckAll(self, *args):
        for entry in self.sr.profilesScroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = self.checkAllCB.checked
                if entry.panel:
                    entry.panel.Load(entry)

        self.ChangeImportButtonState()


class ExportBaseWindow(Window):
    __guid__ = 'form.ExportBaseWindow'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        dirpath = attributes.get('dirpath', None)
        if dirpath:
            self.dirpath = dirpath
        else:
            self.dirpath = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'Overview')
        self.SetMinSize([370, 270])
        self.ConstructLayout()

    def ConstructLayout(self, *args):
        self.ConstructTopCont()
        left = const.defaultPadding
        self.sr.buttonContainer = Container(name='buttonContainer', align=uiconst.TOBOTTOM, parent=self.sr.main)
        self.sr.filenameLabel = eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Common/Files/FileName'), parent=self.sr.buttonContainer, top=const.defaultPadding, left=left, state=uiconst.UI_NORMAL)
        left += self.sr.filenameLabel.width + const.defaultPadding
        self.sr.filename = SingleLineEditText(name='filename', parent=self.sr.buttonContainer, pos=(left,
         const.defaultPadding,
         150,
         0), align=uiconst.TOPLEFT)
        self.sr.filename.SetMaxLength(32)
        left += self.sr.filename.width + const.defaultPadding
        self.sr.exportBtn = Button(parent=self.sr.buttonContainer, label=localization.GetByLabel('UI/Commands/Export'), func=self.Export, btn_default=1, idx=0, pos=(left,
         const.defaultPadding,
         0,
         0))
        self.sr.buttonContainer.height = self.sr.filename.height + 10
        self.sr.scrolllistcontainer = Container(name='scrolllistcontainer', align=uiconst.TOALL, parent=self.sr.main, pos=(0, 0, 0, 0))
        self.sr.scroll = eveScroll.Scroll(name='scroll', parent=self.sr.scrolllistcontainer, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.ConstructScrollList()

    def ConstructTopCont(self):
        self.topCont = Container(name='topCont', align=uiconst.TOTOP, height=14, parent=self.sr.main)
        self.checkAllCB = Checkbox(text=localization.GetByLabel('UI/Shared/CheckAllOn'), parent=self.topCont, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         0,
         100,
         0), callback=self.CheckAll, checked=True)

    def CheckAll(self, *args):
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = self.checkAllCB.checked
                if entry.panel:
                    entry.panel.Load(entry)

        self.ChangeExportButtonState()

    def OnSelectionChanged(self, c, *args):
        self.ChangeExportButtonState()

    def ChangeExportButtonState(self):
        anySelected = self.IsAnyEntrySelected()
        if anySelected:
            self.sr.exportBtn.state = uiconst.UI_NORMAL
        else:
            self.sr.exportBtn.state = uiconst.UI_HIDDEN

    def IsAnyEntrySelected(self):
        for entry in self.sr.scroll.GetNodes():
            if entry.checked:
                return True

        return False


class ExportFittingsWindow(ExportBaseWindow):
    __guid__ = 'form.ExportFittingsWindow'
    default_windowID = 'ExportFittingsWindow'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fitting.png'

    def ApplyAttributes(self, attributes):
        self.selectedOwnerID = attributes.ownerID
        self.fittingSvc = sm.StartService('fittingSvc')
        dirpath = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'Overview')
        attributes.dirpath = dirpath
        ExportBaseWindow.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/Fitting/ExportFittings'))

    def ConstructLayout(self, *args):
        ExportBaseWindow.ConstructLayout(self, *args)
        options = [(localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/PersonalFittings'), session.charid), (localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/CorporationFittings'), session.corpid)]
        if session.allianceid:
            options.append((localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/AllianceFittings'), session.allianceid))
        if self.selectedOwnerID in [ x[1] for x in options ]:
            selected = self.selectedOwnerID
        else:
            selected = session.charid
        self.ownerCombo = Combo(label=None, parent=self.topCont, options=options, name='exportFitting_ownerCombo', select=selected, callback=self.ChangeOwnerFilter, align=uiconst.TOTOP, padding=4)
        self.checkAllCB.SetAlign(uiconst.BOTTOMLEFT)
        self.topCont.height = self.ownerCombo.height + self.checkAllCB.height + 5

    def ChangeOwnerFilter(self, cb, key, value, *args):
        self.selectedOwnerID = value
        self.ConstructScrollList()

    def ConstructScrollList(self):
        fittings = self.fittingSvc.GetAllFittings()
        scrolllist = []
        fittingList = []
        for fittingID, fitting in fittings.iteritems():
            if fitting.ownerID == self.selectedOwnerID:
                fittingList.append((fitting.name, fitting))

        fittingList.sort()
        for fittingName, fitting in fittingList:
            scrolllist.append(GetFromClass(CheckboxEntry, {'label': fittingName,
             'checked': True,
             'cfgname': 'groups',
             'retval': True,
             'report': False,
             'OnChange': self.OnSelectionChanged,
             'fitting': fitting}))

        self.sr.scroll.Load(contentList=scrolllist)

    def Export(self, *args):
        if self.sr.filename.GetValue().strip() == '':
            raise UserError('NameInvalid')
        impl = getDOMImplementation()
        newdoc = impl.createDocument(None, 'fittings', None)
        try:
            docEl = newdoc.documentElement
            export = {}
            for entry in self.sr.scroll.GetNodes():
                if not entry.checked:
                    continue
                profile = newdoc.createElement('fitting')
                docEl.appendChild(profile)
                profile.attributes['name'] = entry.fitting.name
                element = newdoc.createElement('description')
                element.attributes['value'] = entry.fitting.Get('description')
                profile.appendChild(element)
                element = newdoc.createElement('shipType')
                shipType = evetypes.GetName(entry.fitting.Get('shipTypeID'))
                element.attributes['value'] = shipType
                profile.appendChild(element)
                for typeID, flag, qty in entry.fitting.fitData:
                    typeName = evetypes.GetName(typeID)
                    hardWareElement = newdoc.createElement('hardware')
                    hardWareElement.attributes['type'] = typeName
                    slot = self.GetSlotFromFlag(flag)
                    if slot is None:
                        slot = INVALID_FLAG_STRING
                    hardWareElement.attributes['slot'] = slot
                    if flag in (const.flagDroneBay, const.flagCargo, const.flagFighterBay):
                        hardWareElement.attributes['qty'] = str(qty)
                    profile.appendChild(hardWareElement)

            filename = self.sr.filename.GetValue()
            illegalFileNameChars = ['?',
             '*',
             ':',
             ';',
             '~',
             '\\',
             '/',
             '"',
             '|']
            for char in illegalFileNameChars:
                if char in filename:
                    eve.Message('IllegalFilename')
                    return

            self.dirpath = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'fittings')
            filepath = os.path.join(self.dirpath, self.sr.filename.GetValue() + '.xml')
            if not os.path.exists(self.dirpath):
                os.makedirs(self.dirpath)
            if os.path.exists(filepath):
                if eve.Message('FileExists', {}, uiconst.YESNO) == uiconst.ID_NO:
                    return
            outfile = codecs.open(filepath, 'w', 'utf-8')
            newdoc.writexml(outfile, indent='\t', addindent='\t', newl='\n')
            self.CloseByUser()
            eve.Message('FittingExportDone', {'filename': filepath})
        finally:
            newdoc.unlink()

    def GetSlotFromFlag(self, flag):
        if flag in const.hiSlotFlags:
            return 'hi slot ' + str(flag - const.flagHiSlot0)
        if flag in const.medSlotFlags:
            return 'med slot ' + str(flag - const.flagMedSlot0)
        if flag in const.loSlotFlags:
            return 'low slot ' + str(flag - const.flagLoSlot0)
        if flag in const.rigSlotFlags:
            return 'rig slot ' + str(flag - const.flagRigSlot0)
        if IsSubsystemFlagVisible(flag):
            return 'subsystem slot ' + str(flag - const.flagSubSystemSlot0)
        if flag == const.flagCargo:
            return 'cargo'
        if flag == const.flagDroneBay:
            return 'drone bay'
        if flag == const.flagFighterBay:
            return 'fighter bay'
        if flag in const.serviceSlotFlags:
            return 'service slot ' + str(flag - const.flagServiceSlot0)


class ImportFittingsWindow(ImportBaseWindow):
    __guid__ = 'form.ImportFittingsWindow'
    default_windowID = 'ImportFittingsWindow'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fitting.png'

    def ApplyAttributes(self, attributes):
        dirpath = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'Fittings')
        attributes.dirpath = dirpath
        ImportBaseWindow.ApplyAttributes(self, attributes)
        self.sr.importProfilesBtn.LoadTooltipPanel = self.LoadImportTooltip
        self.SetCaption(localization.GetByLabel('UI/Fitting/ImportFittings'))
        self.fittingSvc = sm.StartService('fittingSvc')

    def LoadImportTooltip(self, tooltipPanel, *args):
        hasCorpRoles = bool(session.corprole & const.corpRoleFittingManager)
        if not hasCorpRoles:
            return
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.columns = 1
        tooltipPanel.margin = (12, 12, 12, 12)
        tooltipPanel.cellPadding = 0
        tooltipPanel.cellSpacing = 10
        saveAllianceBtn = None
        if session.allianceid and sm.GetService('alliance').GetAlliance(session.allianceid).executorCorpID == session.corpid:
            saveAllianceBtn = Button(parent=tooltipPanel, label=localization.GetByLabel('UI/Fitting/FittingWindow/SaveForAlliance'), func=self.ImportForOwner, args=(session.allianceid,), align=uiconst.CENTER)
        importCorpBtn = Button(parent=tooltipPanel, label=localization.GetByLabel('UI/Fitting/FittingWindow/SaveForCorp'), func=self.ImportForOwner, args=(session.corpid,), align=uiconst.CENTER)
        importPersonalBtn = Button(parent=tooltipPanel, label=localization.GetByLabel('UI/Fitting/FittingWindow/SaveForCharacter', charID=session.charid), func=self.ImportForOwner, args=(session.charid,), align=uiconst.CENTER)
        maxWidth = max(importCorpBtn.width, importPersonalBtn.width)
        if saveAllianceBtn:
            maxWidth = max(maxWidth, saveAllianceBtn.width)
        importCorpBtn.width = importPersonalBtn.width = maxWidth
        if saveAllianceBtn:
            saveAllianceBtn.width = maxWidth

    def OnFileSelected(self, entry):
        filepath = os.path.join(self.dirpath, entry.sr.node.label + '.xml')
        self.sr.selectedFileName = entry.sr.node.label
        profileCheckboxes = []
        try:
            doc = parse(filepath)
            try:
                profiles = doc.documentElement.getElementsByTagName('fitting')
                for x in profiles:
                    profileCheckboxes.append(GetFromClass(CheckboxEntry, {'label': x.attributes['name'].value,
                     'checked': True,
                     'cfgname': 'profiles',
                     'retval': True,
                     'OnChange': self.OnChange}))

                self.ChangeImportButtonDisplayState(display=True)
            finally:
                doc.unlink()

        except Exception as e:
            raise
            profileCheckboxes = [GetFromClass(Generic, {'label': localization.GetByLabel('UI/Common/Files/FileNotValid')})]
            self.ChangeImportButtonDisplayState(display=False)

        self.sr.profilesScroll.Load(contentList=profileCheckboxes)
        self.OnChange()

    def Import(self, *args):
        return self.ImportForOwner()

    def ImportForOwner(self, ownerID = None):
        filepath = os.path.join(self.dirpath, self.sr.selectedFileName + '.xml')
        godma = sm.GetService('godma')
        doc = parse(filepath)
        try:
            fittings = doc.documentElement.getElementsByTagName('fitting')
            fittingsDict = {}
            borkedTypeNames = set()
            borkedFlags = set()
            obsoleteModules = set()
            for checkbox in self.sr.profilesScroll.GetNodes():
                if not checkbox.checked:
                    continue
                fittingName = checkbox.label
                kv = utillib.KeyVal()
                for fitting in fittings:
                    if fitting.attributes['name'].value != fittingName:
                        continue
                    descriptionElements = fitting.getElementsByTagName('description')
                    if descriptionElements > 0:
                        description = descriptionElements[0].attributes['value'].value
                    else:
                        description = ''
                    shipTypeName = fitting.getElementsByTagName('shipType')[0].attributes['value'].value
                    try:
                        cleanShipTypeName = StripTags(shipTypeName)
                        cleanShipTypeName = StripImportantSymbol(cleanShipTypeName)
                        importFittingUtil = sm.GetService('fittingSvc').GetImportFittingUtil()
                        shipTypeID = importFittingUtil.GetTypeIDFromName(cleanShipTypeName.lower())
                    except evetypes.TypeNotFoundException:
                        sys.exc_clear()
                        borkedTypeNames.add(shipTypeName)
                        continue

                    shipTypeID = int(shipTypeID)
                    fitData = {}
                    for hardwareElement in fitting.getElementsByTagName('hardware'):
                        typeName = hardwareElement.attributes['type'].value
                        try:
                            cleanTypeName = StripTags(typeName)
                            cleanTypeName = StripImportantSymbol(cleanTypeName)
                            typeID = evetypes.GetTypeIDByName(cleanTypeName)
                        except evetypes.TypeNotFoundException:
                            borkedTypeNames.add(typeName)
                            sys.exc_clear()
                            continue

                        slot = hardwareElement.attributes['slot'].value
                        flag = self.GetFlagFromSlot(slot)
                        if flag is None:
                            borkedFlags.add(typeName)
                            continue
                        if IsShipFittable(evetypes.GetCategoryID(typeID)) and flag != const.flagCargo:
                            qty = 1
                        elif IsModuleObsolete(typeID):
                            obsoleteModules.add(typeName)
                            continue
                        else:
                            qty = hardwareElement.attributes['qty'].value
                            qty = int(qty)
                        fitData[typeID, flag] = (typeID, flag, qty)

                    kv.name = fittingName
                    kv.description = description
                    kv.shipTypeID = shipTypeID
                    kv.fitData = fitData.values()
                    kv.ownerID = None
                    kv.fittingID = fittingName
                    fittingsDict[fittingName] = kv

            text = ''
            if len(borkedTypeNames) > 0:
                text += '<b>%s</b><br>' % localization.GetByLabel('UI/Fitting/MalformedXML')
                for typeName in borkedTypeNames:
                    text += typeName + '<br>'

            if len(borkedFlags) > 0:
                if len(text) > 0:
                    text += '<br><br>'
                text += '<b>%s</b><br>' % localization.GetByLabel('UI/Fitting/MalformedFlagInformation')
                for typeName in borkedFlags:
                    text += typeName + '<br>'

            if len(obsoleteModules) > 0:
                if len(text) > 0:
                    text += '<br><br>'
                text += '<b>%s</b><br>' % localization.GetByLabel('UI/Fitting/ObsoleteModules')
                for typeName in obsoleteModules:
                    text += typeName + '<br>'

            if len(text) > 0:
                eve.Message('CustomInfo', {'info': text})
            fittingOwner = ownerID or session.charid
            self.fittingSvc.PersistManyFittings(fittingOwner, fittingsDict.values())
            self.CloseByUser()
        finally:
            doc.unlink()

    def GetFlagFromSlot(self, slot):
        if slot == INVALID_FLAG_STRING:
            return None
        if slot == 'drone bay':
            return const.flagDroneBay
        if slot == 'fighter bay':
            return const.flagFighterBay
        if slot == 'cargo':
            return const.flagCargo
        offset = int(slot[-1])
        if slot.startswith('hi slot'):
            return const.flagHiSlot0 + offset
        if slot.startswith('med slot'):
            return const.flagMedSlot0 + offset
        if slot.startswith('low slot'):
            return const.flagLoSlot0 + offset
        if slot.startswith('rig slot'):
            return const.flagRigSlot0 + offset
        if slot.startswith('subsystem slot'):
            return const.flagSubSystemSlot0 + offset
        if slot.startswith('service slot'):
            return const.flagServiceSlot0 + offset


class ImportOverviewWindow(ImportBaseWindow):
    __guid__ = 'form.ImportOverviewWindow'
    default_windowID = 'ImportOverviewWindow'

    def ApplyAttributes(self, attributes):
        dirpath = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'Overview')
        self.presetsSelected = set()
        ImportBaseWindow.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/Overview/ImportOverviewSettings'))
        self.sr.fileScroll.multiSelect = False
        self.fileType = ''
        self.yamlSettingsDict = {}

    def RefreshFileList(self, *args):
        legacyPresets = self.GetLegacyPresets()
        fileList = self.GetFilesByExt('.yaml')
        contentList = []
        for fileName in fileList:
            contentList.append(GetFromClass(Generic, {'label': fileName,
             'OnClick': self.OnFileSelected,
             'ext': 'yaml'}))

        contentList += legacyPresets
        self.sr.fileScroll.Load(contentList=contentList)

    def GetLegacyPresets(self):
        filelist = self.GetFilesByExt('.xml')
        if not filelist:
            return []
        return [GetFromClass(ListGroup, {'GetSubContent': self.GetOldPresetSubContent,
          'label': localization.GetByLabel('UI/Overview/OldOverviewSettings'),
          'id': ('importOverview', 'oldPresets'),
          'groupItems': filelist,
          'showlen': 1,
          'sublevel': 0,
          'showicon': 'hide',
          'state': 'locked'})]

    def GetOldPresetSubContent(self, nodedata):
        fileList = []
        for fileName in nodedata.groupItems:
            fileList.append(GetFromClass(Generic, {'label': fileName,
             'OnClick': self.OnFileSelected,
             'sublevel': 1,
             'ext': 'xml'}))

        return fileList

    def OnFileSelected(self, entry):
        if entry.sr.node.ext == 'xml':
            self.ShowXmlSettings(entry)
        else:
            self.yamlSettingsDict = {}
            self.ShowYamlSettings(entry)

    def ShowXmlSettings(self, entry):
        self.fileType = 'xml'
        filepath = os.path.join(self.dirpath, entry.sr.node.label + '.xml')
        self.sr.selectedFileName = entry.sr.node.label
        profileCheckboxes = []
        try:
            doc = parse(filepath)
            try:
                profiles = doc.documentElement.getElementsByTagName('profile')
                for x in profiles:
                    profileCheckboxes.append(GetFromClass(CheckboxEntry, {'label': x.attributes['name'].value,
                     'checked': True,
                     'cfgname': 'profiles',
                     'retval': True,
                     'OnChange': self.OnChange}))

                if len(doc.documentElement.getElementsByTagName('globalSettings')):
                    profileCheckboxes.append(GetFromClass(CheckboxEntry, {'label': localization.GetByLabel('UI/Overview/GlobalOverviewSettings'),
                     'checked': True,
                     'cfgname': 'profiles',
                     'retval': True,
                     'OnChange': self.OnChange}))
                self.ChangeImportButtonDisplayState(display=True)
            finally:
                doc.unlink()

        except Exception as e:
            profileCheckboxes = [GetFromClass(Generic, {'label': localization.GetByLabel('UI/Common/Files/FileNotValid')})]
            self.ChangeImportButtonDisplayState(display=False)

        self.sr.profilesScroll.Load(contentList=profileCheckboxes)
        self.ChangeImportButtonState()

    def ShowYamlSettings(self, entry):
        self.fileType = 'yaml'
        filepath = os.path.join(self.dirpath, entry.sr.node.label + '.yaml')
        filestream = open(filepath)
        settingDict = yaml.safe_load(filestream)
        self.yamlSettingsDict = settingDict
        self.ConstructScrollList(initPresetsSelected=True)

    def ConstructScrollList(self, initPresetsSelected = False):
        if self.fileType != 'yaml':
            return
        allChecked = True
        settingDict = self.yamlSettingsDict
        tabPresets = GetDictFromList(settingDict.get('presets', []))
        tabPresets = ReplaceInnerListsWithDicts(tabPresets)
        tabSetup = sm.GetService('overviewPresetSvc').GetTabSetupToLoad(settingDict)
        presetsInUseDict = sm.GetService('overviewPresetSvc').GetPresetsInUseFromTabSettings(tabSetup, tabPresets)
        if initPresetsSelected:
            self.InitPresetsSelected(presetsInUseDict)
        checked = 'generalSettings' in self.presetsSelected
        scrolllist = [GetGeneralOverviewSettingsEntry(onChangeFunc=self.OnChange, checked=checked)]
        allChecked = allChecked and checked
        checked = 'overviewProfile' in self.presetsSelected
        profileEntry = GetOverviewProfileEntry(onChangeFunc=self.OnChange, checked=checked)
        scrolllist.append(profileEntry)
        allChecked = allChecked and checked
        presetsInUseList = []
        for eachPresetName in presetsInUseDict:
            lowerDisplayName = eachPresetName.lower()
            presetsInUseList.append((lowerDisplayName, eachPresetName))

        presetsInUseList = [ x[1] for x in localization.util.Sort(presetsInUseList, key=operator.itemgetter(0)) ]
        for eachPresetName in presetsInUseList:
            checked = eachPresetName in self.presetsSelected
            entry = GetTabPresetEntry(eachPresetName, onChangeFunc=self.OnChange, checked=checked)
            scrolllist.append(entry)
            allChecked = allChecked and checked

        restOfPresets = []
        for eachPresetName in tabPresets:
            if eachPresetName in presetsInUseList:
                continue
            lowerDisplayName = eachPresetName.lower()
            restOfPresets.append((lowerDisplayName, eachPresetName))

        if restOfPresets:
            restOfPresets = [ x[1] for x in localization.util.Sort(restOfPresets, key=operator.itemgetter(0)) ]
            posttext, allSubPresetsChecked = GetPresetPostText(restOfPresets, self.presetsSelected)
            allChecked = allChecked and allSubPresetsChecked
            scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetPresetSubContent,
             'label': localization.GetByLabel('UI/Overview/OtherTabPresets'),
             'id': ('importOverview', 'restOfPresets'),
             'groupItems': restOfPresets,
             'showlen': 0,
             'sublevel': 0,
             'showicon': 'hide',
             'state': 'locked',
             'posttext': posttext}))
        self.sr.profilesScroll.Load(contentList=scrolllist)
        self.ChangeImportButtonState()
        self.checkAllCB.SetChecked(allChecked, report=False)

    def InitPresetsSelected(self, presetsInUseDict):
        self.presetsSelected = set(['generalSettings', 'overviewProfile'])
        for eachPresetName in presetsInUseDict:
            self.presetsSelected.add(eachPresetName)

    def OnChange(self, c, *args):
        OnOverviewCheckboxChange(c, self.presetsSelected)
        if self.fileType == 'yaml':
            self.ConstructScrollList()
        ImportBaseWindow.OnChange(self, c)

    def CheckAll(self, *args):
        if self.fileType == 'xml':
            return ImportBaseWindow.CheckAll(self)
        if self.fileType == 'yaml':
            checkAll = self.checkAllCB.checked
            ModifyPresetSelectedDict(checkAll, self.sr.profilesScroll, self.presetsSelected)
            self.ConstructScrollList()
        self.ChangeImportButtonState()

    def IsAnyEntrySelected(self):
        if self.fileType == 'xml':
            return ImportBaseWindow.IsAnyEntrySelected(self)
        else:
            return bool(self.presetsSelected)

    def GetPresetSubContent(self, nodedata):
        scrolllist = []
        for eachPresetName in nodedata.groupItems:
            checked = eachPresetName in self.presetsSelected
            entry = GetTabPresetEntry(eachPresetName, onChangeFunc=self.OnChange, checked=checked)
            scrolllist.append(entry)

        return scrolllist

    def AddProfilesToSettings(self, profileName, profiles):
        for profile in profiles:
            groups = []
            filteredStates = []
            if profile.attributes['name'].value != profileName:
                continue
            for groupElement in profile.getElementsByTagName('groups')[0].getElementsByTagName('group'):
                groups.append(int(groupElement.attributes['id'].value))

            for el in profile.getElementsByTagName('filteredStates')[0].getElementsByTagName('state'):
                filteredStates.append(int(el.attributes['state'].value))

            profileValues = {overviewSettingsConst.PRESET_SETTINGS_GROUPS: groups,
             overviewSettingsConst.PRESET_SETTINGS_FILTERED_STATES: filteredStates}
            return (profileName, profileValues)

        return (None, None)

    def ImportGlobalSettings(self, doc, miscSettings):
        settingsElement = doc.documentElement.getElementsByTagName('globalSettings')[0]
        for setting in [osConst.SETTING_NAME_SMALL_TAGS,
         osConst.SETTING_NAME_APPLY_STRUCTURE,
         osConst.SETTING_NAME_APPLY_OTHER_OBJ,
         osConst.SETTING_HIDE_CORP_TICKER,
         osConst.SETTING_BROADCAST_TO_TOP]:
            elements = settingsElement.getElementsByTagName(setting)
            if not elements:
                continue
            element = elements[0]
            value = bool(element.attributes['value'])
            miscSettings[setting] = value

        overviewColumns = []
        columnsElement = settingsElement.getElementsByTagName('columns')[0]
        for columnElement in columnsElement.getElementsByTagName('column'):
            overviewColumns.append(columnElement.attributes['id'].value)

        shipLabels = []
        if len(settingsElement.getElementsByTagName('shipLabels')):
            shipLabelsElement = settingsElement.getElementsByTagName('shipLabels')[0]
            shipLabelElements = shipLabelsElement.getElementsByTagName('label')
            for sle in shipLabelElements:
                d = {}
                for shipLabelPartElement in sle.getElementsByTagName('part'):
                    n = shipLabelPartElement.attributes['name'].value
                    v = shipLabelPartElement.attributes['value'].value
                    if n == 'state':
                        v = int(v)
                    if v == 'None':
                        v = None
                    d[n] = v

                shipLabels.append(d)

        stateService = sm.StartService('stateSvc')
        if hasattr(stateService, 'shipLabels'):
            delattr(stateService, 'shipLabels')
        return (overviewColumns, shipLabels)

    def GetTabData(self, selectedProfiles, tabElement):
        overviewProfileName = tabElement.attributes['overview'].value
        bracketProfileName = tabElement.attributes['bracket'].value
        tabdata = {}
        if overviewProfileName in selectedProfiles and bracketProfileName in selectedProfiles:
            for attributeName in TAB_SETTING_IDS:
                attribute = tabElement.getAttribute(attributeName)
                if attribute:
                    if attribute in (SETTING_BRACKETS_SHOWNONE, SETTING_BRACKETS_SHOWSPECIALS, SETTING_BRACKETS_SHOWALL):
                        attribute = bool(attribute)
                    tabdata[attributeName] = attribute

        return tabdata

    def Import(self, *args):
        if self.fileType == 'xml':
            return self.ImportXml()
        else:
            return self.ImportYaml()

    def ImportXml(self, *args):
        dirpath = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'Overview')
        filepath = os.path.join(dirpath, self.sr.selectedFileName + '.xml')
        doc = parse(filepath)
        try:
            profiles = doc.documentElement.getElementsByTagName('profile')
            ov = settings.user.overview.Get(osConst.SETTING_PROFILE_PRESETS, {})
            miscSettings = {}
            selectedProfiles = []
            shipLabels = None
            overviewColumns = None
            closeWindow = True
            profileUpdateDict = {}
            for checkbox in self.sr.profilesScroll.GetNodes():
                if not checkbox.checked:
                    continue
                profileName = checkbox.label
                if profileName in ov and eve.Message('OverviewProfileExists', {'name': profileName}, uiconst.YESNO) != uiconst.ID_YES:
                    closeWindow = False
                    continue
                if profileName == localization.GetByLabel('UI/Overview/GlobalOverviewSettings'):
                    overviewColumns, shipLabels = self.ImportGlobalSettings(doc, miscSettings)
                    continue
                selectedProfiles.append(profileName)
                profileName, profileValues = self.AddProfilesToSettings(profileName, profiles)
                if profileValues:
                    profileUpdateDict[profileName] = profileValues

            overviewPresetSvc = sm.GetService('overviewPresetSvc')
            overviewPresetSvc.UpdateAllPresets(profileUpdateDict)
            tabsChanged = False
            tabsData = {}
            tabIndex = 0
            for tabElement in doc.documentElement.getElementsByTagName('tab'):
                if tabIndex >= 5:
                    eve.Message('TooManyTabsImported')
                    break
                dataForTab = self.GetTabData(selectedProfiles, tabElement)
                if dataForTab:
                    tabsData[tabIndex] = dataForTab
                    tabIndex += 1
                    tabsChanged = True

            if overviewColumns:
                settings.user.overview.Set(osConst.SETTING_COLUMNS, overviewColumns)
            if shipLabels:
                settings.user.overview.Set(osConst.SETTINGS_SHIP_LABELS, shipLabels)
            for k, v in miscSettings.items():
                settings.user.overview.Set(k, v)

            overviewPresetSvc.LoadPresetsFromUserSettings()
            if tabsChanged:
                overviewPresetSvc.ImportOverviewSettings(tabsData)
            if tabsChanged:
                sm.ScatterEvent('OnOverviewPresetsChanged')
            else:
                sm.ScatterEvent('OnFullOverviewReload')
            if closeWindow:
                self.CloseByUser()
        finally:
            doc.unlink()

    def ImportYaml(self):
        tabPresetNamesToImport = []
        tabsChanged = False
        for checkboxConfig in self.presetsSelected:
            if checkboxConfig == 'generalSettings':
                sm.GetService('overviewPresetSvc').LoadGeneralSettings(self.yamlSettingsDict)
            elif checkboxConfig == 'overviewProfile':
                tabSetup = sm.GetService('overviewPresetSvc').GetTabSetupToLoad(self.yamlSettingsDict)
                sm.GetService('overviewPresetSvc').PersistSettingsByTabID(tabSetup)
                tabsChanged = True
            else:
                tabPresetNamesToImport.append(checkboxConfig)

        presetsDict = GetDictFromList(self.yamlSettingsDict.get('presets', []))
        presetsDict = ReplaceInnerListsWithDicts(presetsDict)
        myPresets = {presetName:presetValue for presetName, presetValue in presetsDict.iteritems() if presetName in tabPresetNamesToImport}
        sm.GetService('overviewPresetSvc').UpdateAllPresets(myPresets)
        if tabsChanged:
            sm.GetService('overviewPresetSvc').ImportOverviewSettings(tabSetup)
        sm.ScatterEvent('OnReloadingOverviewProfile')
        self.CloseByUser()


class ImportLegacyFittingsWindow(ExportBaseWindow):
    __guid__ = 'form.ImportLegacyFittingsWindow'
    default_windowID = 'ImportLegacyFittingsWindow'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fitting.png'

    def OnSelectionChanged(self, c, *args):
        checkedCount = 0
        for entry in self.sr.scroll.GetNodes():
            if entry.checked:
                checkedCount += 1

        text = localization.GetByLabel('UI/Fitting/MovingCount', count=checkedCount, total=self.totalLocalFittings)
        if self.fittingCount > 0:
            text += ' (' + localization.GetByLabel('UI/Fitting/CurrentlySaved', count=self.fittingCount) + ')'
        self.sr.countSelectedTextLabel.text = text
        if not self.okBtn.disabled and self.fittingCount + checkedCount > const.maxCharFittings:
            self.okBtn.Disable()
        elif self.okBtn.disabled and self.fittingCount + checkedCount <= const.maxCharFittings:
            self.okBtn.Enable()

    def ApplyAttributes(self, attributes):
        self.fittingSvc = sm.StartService('fittingSvc')
        self.fittingCount = len(self.fittingSvc.GetFittingMgr(session.charid).GetFittings(session.charid))
        Window.ApplyAttributes(self, attributes)
        self.SetMinSize([370, 270])
        self.SetCaption(localization.GetByLabel('UI/Fitting/MoveToServer'))
        self.ConstructLayout()

    def ConstructLayout(self, *args):
        self.countSelectedText = ''
        self.sr.textContainer = Container(name='textContainer', align=uiconst.TOTOP, parent=self.sr.main, height=65, padding=const.defaultPadding)
        self.sr.textLabel = eveLabel.EveLabelMedium(text=localization.GetByLabel('UI/Fitting/LegacyImport', maxFittings=const.maxCharFittings), align=uiconst.TOTOP, parent=self.sr.textContainer)
        self.sr.textContainer2 = Container(name='textContainer', align=uiconst.TOTOP, parent=self.sr.main, height=15, padding=const.defaultPadding)
        self.sr.countSelectedTextLabel = eveLabel.EveLabelMedium(text=self.countSelectedText, align=uiconst.TOALL, parent=self.sr.textContainer2)
        self.sr.buttonContainer = Container(name='buttonContainer', align=uiconst.TOBOTTOM, parent=self.sr.main)
        btns = [[localization.GetByLabel('UI/Generic/Cancel'),
          self.CloseByUser,
          None,
          81], [localization.GetByLabel('UI/Generic/OK'),
          self.Import,
          None,
          81]]
        self.buttonGroup = ButtonGroup(btns=btns, parent=self.sr.buttonContainer)
        self.okBtn = self.buttonGroup.children[0].children[1]
        self.sr.buttonContainer.height = 23
        self.sr.scrolllistcontainer = Container(name='scrolllistcontainer', align=uiconst.TOALL, parent=self.sr.main, pos=(0, 0, 0, 0))
        self.sr.scroll = eveScroll.Scroll(name='scroll', parent=self.sr.scrolllistcontainer, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.ConstructScrollList()

    def ConstructScrollList(self):
        fittings = self.fittingSvc.GetLegacyClientFittings()
        scrolllist = []
        fittingList = []
        for fittingID, fitting in fittings.iteritems():
            fittingList.append((fitting.name, fitting))

        fittingList.sort()
        self.emptyFittings = []
        for fittingName, fitting in fittingList:
            if len(fitting.fitData) == 0:
                self.emptyFittings.append(fitting)
                continue
            typeFlag = set()
            for typeID, flag, qty in fitting.fitData[:]:
                if (typeID, flag) in typeFlag:
                    fitting.fitData.remove((typeID, flag, qty))
                else:
                    typeFlag.add((typeID, flag))

            scrolllist.append(GetFromClass(CheckboxEntry, {'label': fittingName,
             'checked': False,
             'OnChange': self.OnSelectionChanged,
             'cfgname': 'groups',
             'retval': True,
             'report': False,
             'fitting': fitting}))

        self.sr.scroll.Load(contentList=scrolllist)
        self.totalLocalFittings = len(fittingList)
        self.OnSelectionChanged(None)

    def Import(self, *args):
        impl = getDOMImplementation()
        newdoc = impl.createDocument(None, 'fittings', None)
        try:
            docEl = newdoc.documentElement
            fittings = []
            saveSomeToFile = False
            for entry in self.sr.scroll.GetNodes():
                if entry.checked:
                    fittings.append(entry.fitting)
                else:
                    saveSomeToFile = True
                    profile = newdoc.createElement('fitting')
                    docEl.appendChild(profile)
                    profile.attributes['name'] = entry.fitting.name
                    element = newdoc.createElement('description')
                    element.attributes['value'] = entry.fitting.Get('description')
                    profile.appendChild(element)
                    element = newdoc.createElement('shipType')
                    try:
                        shipType = evetypes.GetName(entry.fitting.Get('shipTypeID'))
                    except KeyError:
                        shipType = 'unknown type'

                    element.attributes['value'] = shipType
                    profile.appendChild(element)
                    for typeID, flag, qty in entry.fitting.fitData:
                        try:
                            typeName = evetypes.GetName(typeID)
                        except KeyError:
                            typeName = 'unknown type'

                        hardWareElement = newdoc.createElement('hardware')
                        hardWareElement.attributes['type'] = typeName
                        slot = self.GetSlotFromFlag(flag)
                        if slot is None:
                            slot = 'unknown slot'
                        hardWareElement.attributes['slot'] = slot
                        if flag == const.flagDroneBay:
                            hardWareElement.attributes['qty'] = str(qty)
                        profile.appendChild(hardWareElement)

            for emptyFitting in self.emptyFittings:
                saveSomeToFile = True
                profile = newdoc.createElement('fitting')
                docEl.appendChild(profile)
                profile.attributes['name'] = entry.fitting.name
                element = newdoc.createElement('description')
                element.attributes['value'] = entry.fitting.Get('description')
                profile.appendChild(element)
                element = newdoc.createElement('shipType')
                try:
                    shipType = evetypes.GetName(entry.fitting.Get('shipTypeID'))
                except KeyError:
                    shipType = 'unknown type'

                element.attributes['value'] = shipType
                profile.appendChild(element)

            if len(fittings) > 0:
                self.fittingSvc.PersistManyFittings(session.charid, fittings)
            if saveSomeToFile:
                self.dirpath = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'fittings')
                filename = cfg.eveowners.Get(session.charid).ownerName
                filename = filename.replace(' ', '')
                filename = SanitizeFilename(filename)
                dirpath = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'fittings')
                filename = os.path.join(dirpath, filename)
                extraEnding = ''
                while os.path.exists(filename + str(extraEnding) + '.xml'):
                    if not isinstance(extraEnding, int):
                        extraEnding = 1
                    extraEnding += 1

                filename += str(extraEnding) + '.xml'
                if not os.path.exists(self.dirpath):
                    os.makedirs(self.dirpath)
                outfile = codecs.open(filename, 'w', 'utf-8')
                newdoc.writexml(outfile, indent='\t', addindent='\t', newl='\n')
                eve.Message('LegacyFittingExportDone', {'filename': filename})
            self.fittingSvc.DeleteLegacyClientFittings()
            self.CloseByUser()
        finally:
            newdoc.unlink()

    def GetSlotFromFlag(self, flag):
        if const.flagHiSlot0 <= flag <= const.flagHiSlot7:
            return 'hi slot ' + str(flag - const.flagHiSlot0)
        if const.flagMedSlot0 <= flag <= const.flagMedSlot7:
            return 'med slot ' + str(flag - const.flagMedSlot0)
        if const.flagLoSlot0 <= flag <= const.flagLoSlot7:
            return 'low slot ' + str(flag - const.flagLoSlot0)
        if const.flagRigSlot0 <= flag <= const.flagRigSlot7:
            return 'rig slot ' + str(flag - const.flagRigSlot0)
        if IsSubsystemFlag(flag):
            return 'subsystem slot ' + str(flag - const.flagSubSystemSlot0)
        if flag == const.flagDroneBay:
            return 'drone bay'
        if flag in const.serviceSlotFlags:
            return 'service slot ' + str(flag - const.flagServiceSlot0)


class ExportOverviewWindow(ExportBaseWindow):
    __guid__ = 'form.ExportOverviewWindow'
    default_windowID = 'ExportOverviewWindow'
    __notifyevents__ = ['OnOverviewPresetSaved']
    EXPORT_EVERYTHING = False

    def ApplyAttributes(self, attributes):
        self.overviewPresetSvc = sm.StartService('overviewPresetSvc')
        dirpath = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'Overview')
        attributes.dirpath = dirpath
        self.InitPresetsSelected()
        ExportBaseWindow.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/Commands/ExportOverviewSettings'))

    def ConstructTopCont(self):
        self.topCont = ContainerAutoSize(name='topCont', align=uiconst.TOTOP, padLeft=4, parent=self.sr.main)
        currentText = self.overviewPresetSvc.GetOverviewName()
        defaultText = localization.GetByLabel('UI/Overview/DefaultOverviewName', charID=session.charid)
        configName = 'overviewProfileNameInExport'
        getDragDataFunc = self.GetShareData
        shareContainer = DraggableShareContainer(parent=self.topCont, currentText=currentText, defaultText=defaultText, configName=configName, getDragDataFunc=getDragDataFunc, hintText=localization.GetByLabel('UI/Overview/SharableOverviewIconExportHint'), align=uiconst.TOTOP, padTop=4)
        self.topCont.height = shareContainer.sharedNameLabel.height + 10
        self.checkAllCB = Checkbox(text=localization.GetByLabel('UI/Shared/CheckAllOn'), parent=self.topCont, align=uiconst.TOTOP, callback=self.CheckAll, checked=True, padTop=6, padLeft=4)

    def GetShareData(self, text):
        selected = self.presetsSelected.copy()
        for x in ('generalSettings', 'overviewProfile'):
            if x in selected:
                selected.remove(x)

        if len(selected) > MAX_SHARED_PRESETS:
            eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Overview/TryingToShareTooManyPresets')})
            return []
        return self.overviewPresetSvc.GetShareData(text=text, presetsToUse=selected)

    def InitPresetsSelected(self):
        self.presetsSelected = set(['generalSettings', 'overviewProfile'])
        presetsInUse = self.overviewPresetSvc.GetPresetsInUse()
        for eachPresetName in presetsInUse:
            lowerDisplayName = eachPresetName.lower()
            self.presetsSelected.add(eachPresetName)

    def ConstructScrollList(self):
        allChecked = True
        scrolllist = []
        checked = 'generalSettings' in self.presetsSelected
        generalSettingsEntry = GetGeneralOverviewSettingsEntry(onChangeFunc=self.OnSelectionChanged, checked=checked)
        scrolllist.append(generalSettingsEntry)
        allChecked = allChecked and checked
        checked = 'overviewProfile' in self.presetsSelected
        profileEntry = GetOverviewProfileEntry(onChangeFunc=self.OnSelectionChanged, checked=checked)
        scrolllist.append(profileEntry)
        allChecked = allChecked and checked
        presetsInUse = self.overviewPresetSvc.GetPresetsInUse()
        presetsInUseList = []
        for eachPresetName in presetsInUse:
            lowerDisplayName = eachPresetName.lower()
            presetsInUseList.append((lowerDisplayName, eachPresetName))

        presetsInUseList = [ x[1] for x in localization.util.Sort(presetsInUseList, key=operator.itemgetter(0)) ]
        for eachPresetName in presetsInUseList:
            checked = eachPresetName in self.presetsSelected
            entry = GetTabPresetEntry(eachPresetName, onChangeFunc=self.OnSelectionChanged, checked=checked)
            scrolllist.append(entry)
            allChecked = allChecked and checked

        allPresets = self.overviewPresetSvc.GetAllPresets()
        restOfPresets = []
        defaultProfileNames = self.overviewPresetSvc.GetDefaultOverviewPresetNames()
        for eachPresetName in allPresets:
            if not self.EXPORT_EVERYTHING:
                if eachPresetName in presetsInUse or eachPresetName in defaultProfileNames:
                    continue
            lowerDisplayName = eachPresetName.lower()
            restOfPresets.append((lowerDisplayName, eachPresetName))

        if restOfPresets:
            restOfPresets = [ x[1] for x in localization.util.Sort(restOfPresets, key=operator.itemgetter(0)) ]
            posttext, allSubPresetsChecked = GetPresetPostText(restOfPresets, self.presetsSelected)
            allChecked = allChecked and allSubPresetsChecked
            scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetPresetSubContent,
             'label': localization.GetByLabel('UI/Overview/OtherTabPresets'),
             'id': ('exportOverview', 'restOfPresets'),
             'groupItems': restOfPresets,
             'showlen': 0,
             'sublevel': 0,
             'showicon': 'hide',
             'state': 'locked',
             'posttext': posttext}))
        self.sr.scroll.Load(contentList=scrolllist)
        self.checkAllCB.SetChecked(allChecked, report=False)

    def GetPresetSubContent(self, nodedata):
        scrolllist = []
        for eachPresetName in nodedata.groupItems:
            checked = eachPresetName in self.presetsSelected
            entry = GetTabPresetEntry(eachPresetName, onChangeFunc=self.OnSelectionChanged, checked=checked)
            scrolllist.append(entry)

        return scrolllist

    def Export(self, *args):
        if self.sr.filename.GetValue().strip() == '':
            raise UserError('NameInvalid')
        exportData = {}
        presetList = []
        allPresets = self.overviewPresetSvc.GetAllPresets()
        defaultProfileNames = self.overviewPresetSvc.GetDefaultOverviewPresetNames()
        for checkboxConfig in self.presetsSelected:
            if checkboxConfig == 'generalSettings':
                generalSettings = self.GetGeneralSettings()
                exportData.update(generalSettings)
            elif checkboxConfig == 'overviewProfile':
                overviewProfile = self.GetOverviewProfile()
                exportData['tabSetup'] = overviewProfile
            else:
                presetName = checkboxConfig
                if presetName in allPresets and (self.EXPORT_EVERYTHING or presetName not in defaultProfileNames):
                    presetAsDict = allPresets[presetName]
                    presetAsList = GetDeterministicListFromDict(presetAsDict)
                    presetList.append((presetName, presetAsList))

        if presetList:
            exportData['presets'] = presetList
        dirpath = os.path.join(blue.sysinfo.GetUserDocumentsDirectory(), 'EVE', 'Overview')
        filepath = os.path.join(dirpath, self.sr.filename.GetValue().strip() + '.yaml')
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        if os.path.exists(filepath):
            if eve.Message('FileExists', {}, uiconst.YESNO) != uiconst.ID_YES:
                return
        with open(filepath, 'w') as yamlFile:
            yaml.safe_dump(exportData, yamlFile, default_flow_style=False, allow_unicode=True)
        self.CloseByUser()
        eve.Message('OverviewExportDone', {'filename': filepath})

    def GetGeneralSettings(self):
        return self.overviewPresetSvc.GetGeneralSettings()

    def GetOverviewProfile(self):
        return self.overviewPresetSvc.GetTabSettingsForSaving()

    def OnSelectionChanged(self, c, *args):
        OnOverviewCheckboxChange(c, self.presetsSelected)
        self.ConstructScrollList()
        ExportBaseWindow.OnSelectionChanged(self, c)

    def CheckAll(self, *args):
        checkAll = self.checkAllCB.checked
        ModifyPresetSelectedDict(checkAll, self.sr.scroll, self.presetsSelected)
        self.ConstructScrollList()
        self.ChangeExportButtonState()

    def IsAnyEntrySelected(self):
        return bool(self.presetsSelected)

    def OnOverviewPresetSaved(self, *args):
        self.ConstructScrollList()


def GetGeneralOverviewSettingsEntry(onChangeFunc, checked = True):
    return GetFromClass(CheckboxEntry, {'label': localization.GetByLabel('UI/Overview/GeneralOverviewSettings'),
     'checked': checked,
     'cfgname': 'generalSettings',
     'retval': checked,
     'OnChange': onChangeFunc})


def GetOverviewProfileEntry(onChangeFunc, checked = True):
    return GetFromClass(CheckboxEntry, {'label': localization.GetByLabel('UI/Overview/OverviewProfile'),
     'checked': checked,
     'cfgname': 'overviewProfile',
     'retval': checked,
     'OnChange': onChangeFunc,
     'hint': localization.GetByLabel('UI/Overview/OverviewProfileHint')})


def GetTabPresetEntry(eachProfileName, onChangeFunc, checked = True):
    return GetFromClass(CheckboxEntry, {'label': localization.GetByLabel('UI/Overview/TabPresetName', presetName=eachProfileName),
     'checked': checked,
     'cfgname': eachProfileName,
     'presetName': eachProfileName,
     'retval': checked,
     'sublevel': 1,
     'OnChange': onChangeFunc})


def ModifyPresetSelectedDict(checkAll, scroll, presetSelectedDict):
    if checkAll:
        for entry in scroll.GetNodes():
            guid = entry.__guid__
            if guid == 'listentry.Checkbox':
                presetSelectedDict.add(entry.cfgname)
            elif guid == 'listentry.Group':
                for each in entry.groupItems:
                    presetSelectedDict.add(each)

    else:
        presetSelectedDict.clear()


def OnOverviewCheckboxChange(c, presetSelectedDict):
    if c.checked:
        presetSelectedDict.add(c.GetSettingsKey())
    elif c.GetSettingsKey() in presetSelectedDict:
        presetSelectedDict.remove(c.GetSettingsKey())


def GetPresetPostText(presetsList, presetSelectedDict):
    checkedPresets = [ p for p in presetsList if p in presetSelectedDict ]
    allChecked = len(checkedPresets) == len(presetsList)
    return ('[%s/%s]' % (len(checkedPresets), len(presetsList)), allChecked)


def IsModuleObsolete(typeID):
    return bool(sm.GetService('clientDogmaStaticSvc').GetTypeAttribute(typeID, const.attributeModuleIsObsolete))
