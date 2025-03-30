#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\petitionWindow.py
import localization
import uthread
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.util import searchUtil
from eve.client.script.ui.util.form import FormWnd
from eve.common.lib import appConst
from eve.common.script.search.const import ResultType
from eveservices.xmppchat import GetChatService
from evepetitions.data import get_property_description_id, get_property_input_info, get_property_input_type, get_property_name, get_property_required_int

class PetitionWindow(Window):
    __guid__ = 'form.PetitionWindow'
    billingCategories = {}
    default_windowID = 'petitionwindow'
    default_iconNum = 'res:/ui/Texture/WindowIcons/help.png'
    default_captionLabelPath = 'UI/Neocom/Petition/CreateNew'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.mainCont = ContainerAutoSize(name='mainCont', align=uiconst.TOTOP, parent=self.sr.main, callback=self.UpdateMinHeight)
        self.formWindow = FormWnd(name='form', align=uiconst.TOTOP, parent=self.mainCont)
        self.mainText = eveLabel.EveLabelMedium(name='mainText', parent=self.mainCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=8)
        self.mainCont.SetSizeAutomatically()
        _, height = self.GetWindowSizeForContentSize(height=self.mainCont.height)
        self.SetMinSize((350, height))
        self.CategoryScreen()

    def ConstructTopParent(self):
        topParent = Container(name='topParent', parent=self.mainCont, align=uiconst.TOTOP, height=62, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=topParent, state=uiconst.UI_DISABLED, pos=(0, -3, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.sr.mainCaption = eveLabel.CaptionLabel(text=localization.GetByLabel('UI/Neocom/Petition/CreateNew'), parent=topParent, align=uiconst.RELATIVE, left=64, top=16)

    def CategoryScreen(self):
        self.formWindow.Flush()
        self.mainText.SetText('')
        format = [{'type': 'push',
          'frame': 0}]
        self.GetFromSelect = 0
        self.OocCharacterID = None
        if not session.charid:
            if self.OocCharacterID == None:
                chars = sm.RemoteSvc('charUnboundMgr').GetCharacterInfo()
                first = 1
                self.GetFromSelect = 1
                format.append({'type': 'text',
                 'text': localization.GetByLabel('UI/CharacterSelection/SelectCharacter'),
                 'frame': 0})
                for char in chars:
                    format.append({'type': 'checkbox',
                     'required': 1,
                     'group': 'OocCharacter',
                     'height': 16,
                     'setvalue': first,
                     'key': char.characterID,
                     'label': '',
                     'text': char.characterName,
                     'frame': 0})
                    first = 0

                format.append({'type': 'push',
                 'frame': 0})
                format.append({'type': 'push',
                 'frame': 0})
        self.superCategories, self.childCategories, self.descriptions = self.GetCategories()
        if len(self.superCategories) < 2 or len(self.childCategories) < 1:
            self.superCategories, self.childCategories, self.descriptions = self.GetCategories(forcedLanguage=localization.const.LOCALE_SHORT_ENGLISH)
        format.append({'type': 'combo',
         'required': 1,
         'frame': 0,
         'key': 'superCategoryID',
         'label': localization.GetByLabel('UI/Inventory/ItemGroup'),
         'options': self.superCategories,
         'callback': self.SuperCategorySelection})
        format.append({'type': 'push',
         'frame': 0})
        format.append({'type': 'combo',
         'required': 1,
         'frame': 0,
         'key': 'subCategory',
         'label': localization.GetByLabel('UI/Common/Category'),
         'options': [[localization.GetByLabel('UI/Neocom/Petition/SelectGroup'), None]],
         'callback': self.SubCategorySelection})
        format.append({'type': 'btnonly',
         'frame': 0,
         'uniSize': False,
         'buttons': [{'caption': localization.GetByLabel('UI/Help/OpenHelpCenter'),
                      'function': self.OpenHelpCenter}, {'caption': localization.GetByLabel('UI/Common/Buttons/Select'),
                      'function': self.ConfirmCategory}]})
        format.append({'type': 'push',
         'frame': 0})
        format.append({'type': 'push'})
        self.sr.formData = sm.GetService('form').GetForm(format, self.formWindow)
        Container(name='push', parent=self.formWindow, align=uiconst.TOLEFT, width=6)
        Container(name='push', parent=self.formWindow, align=uiconst.TORIGHT, width=6)
        category = self.sr.formData[0].sr.subCategory.GetValue()
        if category:
            text = self.descriptions[category][0]
        else:
            text = ''
        self.mainText.SetText(text)
        try:
            self.selectBtn = self.sr.formData[0].FindChild('%s_Btn' % localization.GetByLabel('UI/Common/Buttons/Select'))
            self.helpDeskBtn = self.sr.formData[0].FindChild('%s_Btn' % localization.GetByLabel('UI/Help/OpenHelpCenter'))
            self.helpDeskBtn.display = False
            self.helpDeskBtn.align = uiconst.TOPRIGHT
        except Exception:
            pass

    def OpenHelpCenter(self, *args):
        import webbrowser
        if eve.Message('HelpCenterOpenWarning', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
            webbrowser.open_new(sm.RemoteSvc('petitioner').GetZendeskJwtLink())
            self.Close()

    def SubCategorySelection(self, combo, header, value, *args):
        if value != None:
            if combo.name == 'subCategory':
                ops = self.descriptions[value[0]]
            self.mainText.SetText(ops)

    def UpdateMinHeight(self):
        _, mh = self.GetWindowSizeForContentSize(height=self.mainCont.height)
        self.SetMinSize((self.width, mh), refresh=True)

    def SuperCategorySelection(self, combo, header, value, *args):
        if combo.name == 'superCategoryID' and value is not None:
            try:
                if value == 29 and sm.RemoteSvc('petitioner').IsZendeskEnabled() and session.languageID.lower() == 'en':
                    self.mainText.SetText(localization.GetByLabel('UI/Help/MovedToHelpCenter'))
                    self.sr.formData[0].sr.subCategory.parent.display = False
                    self.selectBtn.display = False
                    self.helpDeskBtn.display = True
                else:
                    ops = self.childCategories[value]
                    hints = {}
                    for k, v in ops:
                        hints[k] = self.descriptions[v[0]]

                    self.sr.formData[0].sr.subCategory.LoadOptions(ops, hints=hints)
                    current = self.sr.formData[0].sr.subCategory.GetValue()
                    ops = self.descriptions[current[0]]
                    self.mainText.SetText(ops)
                    self.sr.formData[0].sr.subCategory.parent.display = True
                    self.selectBtn.display = True
                    self.helpDeskBtn.display = False
            except Exception:
                ops = self.childCategories[value]
                hints = {}
                for k, v in ops:
                    hints[k] = self.descriptions[v[0]]

                self.sr.formData[0].sr.subCategory.LoadOptions(ops, hints=hints)
                current = self.sr.formData[0].sr.subCategory.GetValue()
                ops = self.descriptions[current[0]]
                self.mainText.SetText(ops)

    def ConfirmCategory(self, *args):
        result = sm.GetService('form').ProcessForm(self.sr.formData[1], self.sr.formData[2])
        catCountry = sm.RemoteSvc('petitioner').GetUserCatalogCountry()
        if result:
            if self.billingCategories.has_key((result['subCategory'][0], catCountry)):
                url, messageLabel = self.billingCategories[result['subCategory'][0], catCountry]
                ret = sm.GetService('gameui').MessageBox(localization.GetByLabel(messageLabel), result['subCategory'][1], buttons=uiconst.YESNO)[0]
                if ret == uiconst.ID_YES:
                    uicore.cmd.OpenBrowser(url=url, newTab=True)
                    self.Close()
                    return
                else:
                    self.Close()
                    return
            self.category = result['subCategory']
            if self.GetFromSelect:
                self.OocCharacterID = result['OocCharacter']
            uthread.new(self.InputPetition)

    def InputPetition(self, *args):
        categoryID = self.category[0]
        categoryName = self.category[1]
        OocCharacterID = self.OocCharacterID
        can = sm.RemoteSvc('petitioner').MayPetition(categoryID, OocCharacterID)
        if can < 0:
            if can == -1:
                eve.Message('CannotPostPetition', {'text': localization.GetByLabel('UI/Neocom/Petition/CannotPostPetition1')})
                return
            if can == -2:
                eve.Message('CannotPostPetition', {'text': localization.GetByLabel('UI/Neocom/Petition/CannotPostPetition2')})
                return
            if can == -3:
                eve.Message('CannotPostPetition', {'text': localization.GetByLabel('UI/Neocom/Petition/CannotPostPetition3')})
                return
            if can == -4:
                eve.Message('CannotPostPetition', {'text': localization.GetByLabel('UI/Neocom/Petition/CannotPostPetition4')})
                return
            if can == -6:
                eve.Message('CannotPostPetition', {'text': localization.GetByLabel('UI/Neocom/Petition/CannotPostPetition6')})
                return
            if can == -7:
                eve.Message('CannotPostPetition', {'text': localization.GetByLabel('UI/Neocom/Petition/CannotPostPetition7')})
            return
        self.formWindow.Flush()
        self.mainText.SetText('')
        format = []
        format.append({'type': 'header',
         'text': categoryName,
         'frame': 0,
         'hideLine': True})
        format.append({'type': 'push',
         'frame': 0})
        self.properties = sm.RemoteSvc('petitioner').GetCategoryProperties(self.category[0])
        for propertyID in self.properties:
            required = get_property_required_int(propertyID)
            descriptionID = get_property_description_id(propertyID)
            inputType = get_property_input_type(propertyID)
            propertyName = get_property_name(propertyID)
            inputInfo = get_property_input_info(propertyID)
            format.append({'type': 'labeltext',
             'text': localization.GetByMessageID(descriptionID),
             'frame': 0})
            if inputType == 'DropDown':
                populationInfo = sm.RemoteSvc('petitioner').PropertyPopulationInfo(inputInfo, self.OocCharacterID)
                populationInfo = self.FormatForDropDown(populationInfo)
                format.append({'type': 'combo',
                 'required': required,
                 'frame': 0,
                 'key': propertyName,
                 'options': populationInfo})
            if inputType == 'Picker':
                format.append({'type': 'edit',
                 'key': propertyName,
                 'maxLength': 200,
                 'height': 28,
                 'required': required,
                 'frame': 0})
                format.append({'type': 'labeltext',
                 'frame': 0,
                 'text': localization.GetByLabel('UI/Neocom/Petition/Search')})
                format.append({'type': 'btnonly',
                 'frame': 0,
                 'buttons': [{'caption': localization.GetByLabel('UI/Neocom/Petition/Search'),
                              'function': self.PopulatePicker,
                              'args': propertyName}]})
            if inputType == 'EditBox':
                format.append({'type': 'edit',
                 'key': propertyName,
                 'setvalue': inputInfo,
                 'maxLength': 200,
                 'height': 28,
                 'required': required,
                 'frame': 0})
            format.append({'type': 'push',
             'frame': 0})

        format.append({'type': 'push',
         'frame': 0})
        format.append({'type': 'edit',
         'key': 'subject',
         'label': localization.GetByLabel('UI/Neocom/Petition/Subject'),
         'maxLength': 200,
         'required': 1,
         'frame': 0})
        format.append({'type': 'textedit',
         'key': 'petition',
         'label': localization.GetByLabel('UI/Neocom/Petition/Text'),
         'maxLength': 10000,
         'height': 300,
         'required': 1,
         'frame': 0})
        format.append({'type': 'btnonly',
         'frame': 0,
         'buttons': [{'caption': localization.GetByLabel('UI/Generic/Submit'),
                      'function': self.CreatePetition}, {'caption': localization.GetByLabel('UI/Commands/Back'),
                      'function': self.GoBack}]})
        format.append({'type': 'push',
         'frame': 0})
        self.mainText.SetText(self.descriptions[categoryID])
        self.sr.formData = sm.GetService('form').GetForm(format, self.formWindow)
        self.lockPetitioning = False

    def GoBack(self, *args):
        ret = eve.Message('AskAreYouSure', {'cons': localization.GetByLabel('UI/Neocom/Petition/LoseInfo')}, uiconst.YESNO, default=uiconst.ID_NO)
        if ret == uiconst.ID_YES:
            self.CategoryScreen()

    def PopulatePicker(self, *args):
        elementName = args[0]
        filterString = sm.GetService('form').ProcessForm(self.sr.formData[1], [])[elementName]
        if len(filterString) >= 1:
            if elementName == 'StarbaseLocation':
                resList = searchUtil.GetResultsList(filterString, [ResultType.solar_system])
                populationRecords = []
                for x in resList:
                    populationRecords.append((cfg.evelocations.Get(x).name, x))

            elif elementName == 'Agents':
                resList = searchUtil.GetResultsList(filterString, [ResultType.agent])
                populationRecords = []
                for x in resList:
                    populationRecords.append((cfg.eveowners.Get(x).name, x))

            else:
                populationRecords = sm.RemoteSvc('petitioner').GetClientPickerInfo(filterString, elementName)
                if len(populationRecords) >= 25:
                    eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Neocom/Petition/NarrowSearch')})
            picker = self.sr.formData[0].sr.Get(elementName)
            if len(populationRecords) > 0:
                picker.LoadCombo(elementName, populationRecords, None, None)
                picker.SetValue(str(populationRecords[0][1]))
                picker.SetText(populationRecords[0][0])
            else:
                picker.SetText(localization.GetByLabel('UI/Neocom/Petition/ReportInfoNotFound'))
        else:
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Neocom/Petition/PleaseType3Letters')})

    def FormatForDropDown(self, entryList):
        newList = []
        for entry in entryList:
            entryID, entryText = entry
            if isinstance(entryText, tuple):
                entryText = cfg.FormatConvert(*entryText)
            newList.append([entryText, entryID])

        return newList

    def CreatePetition(self, *args):
        if self.lockPetitioning:
            return
        self.lockPetitioning = True
        propertyList = []
        resultDict = sm.GetService('form').ProcessForm(self.sr.formData[1], self.sr.formData[2])
        combatLog = None
        chatLog = None
        categoryID = self.category[0]
        if resultDict:
            chatLog = GetChatService().GetChannelMessages()
            combatLog = sm.GetService('logger').GetLog()
            if chatLog:
                chatLog = chatLog[-appConst.petitionMaxChatLogSize:]
            if combatLog:
                combatLog = combatLog[-appConst.petitionMaxCombatLogSize:]
            for propertyID in self.properties:
                propertyName = get_property_name(propertyID)
                inputType = get_property_input_type(propertyID)
                if inputType == 'Picker':
                    value = self.sr.formData[0].sr.Get(propertyName).GetComboValue()
                    propertyList.append([propertyID, value])
                else:
                    propertyList.append([propertyID, resultDict[propertyName]])

            subject = resultDict['subject']
            petition = resultDict['petition']
            sm.RemoteSvc('petitioner').CreatePetition(subject, petition, categoryID, None, self.OocCharacterID, chatLog, combatLog, propertyList)
            sm.ScatterEvent('OnPetitionCreated')
            eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/Neocom/Petition/Created')})
            self.CloseByUser()
        else:
            self.lockPetitioning = False

    def GetCategories(self, forcedLanguage = None):
        parentCategoryDict, childCategoryDict, descriptionDict, self.billingCategories = sm.RemoteSvc('petitioner').GetCategoryHierarchicalInfo()
        parentCategories = [[localization.GetByLabel('UI/Neocom/Petition/SelectParentCategory'), None]]
        childCategoryRetDict = {}
        descriptions = []
        if forcedLanguage is not None:
            myLanguage = forcedLanguage
        else:
            myLanguage = localization.util.GetLanguageID()
        for parentID, catAndLanguage in parentCategoryDict.iteritems():
            cat, languageID = catAndLanguage
            if languageID != myLanguage:
                continue
            parentCategories.append((cat, parentID))

        for childGroupID, childGroupDict in childCategoryDict.iteritems():
            childCategories = []
            for childID, childnameAndLanguage in childGroupDict.iteritems():
                childName, languageID = childnameAndLanguage
                if languageID != myLanguage:
                    continue
                childCategories.append((childName, (childID, childName)))

            if len(childCategories) > 0:
                childCategoryRetDict[childGroupID] = childCategories

        return (parentCategories, childCategoryRetDict, descriptionDict)
