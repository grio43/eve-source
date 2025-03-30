#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\colonyTemplateWindow.py
import base64
import json
import logging
import os
import blue
import eveformat
import eveicon
import evetypes
import locks
import uthread2
from bannedwords.client import bannedwords
from carbonui import uiconst, TextColor, Align, TextDetail, PickState, TextHeader, IdealSize, TextBody
from carbonui.button.menu import MenuButtonIcon, MenuButton
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.dragdrop.dragdata import BaseDragData
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.services.setting import UserSettingString
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.inflight.overview.overviewScrollEntry import get_distance_in_kilometers
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.planet import planetConst
import eve.client.script.ui.shared.planet.planetUtil as planetUtil
from eve.client.script.ui.shared.planet.colonyTemplate import ColonyTemplate
from eve.client.script.ui.shared.planet.colonyTemplateFilters import SETTING_KEY_CMD_CNTR, SETTING_KEY_EXTRACT_TYPE, SETTING_KEY_PROCESSED, SETTING_KEY_REFINED, SETTING_KEY_SPECIALIZED, SETTING_KEY_ADVANCED, SETTING_KEY_PLANET_TYPE, GetValidTemplates, CMD_CTR_LELVES
from eve.client.script.ui.shared.planet.colonyTemplateLoading import PreviewLoad
from eve.client.script.ui.shared.planet.pinContainers.storageIcon import StorageIcon
from eve.client.script.ui.shared.planet.planetCommon import GetTierByTypeID
from eve.client.script.ui.shared.planet.templateSavingUtil import ConfirmExportWnd, GetDefaultStoragePath, SaveToLocalFile
from eve.client.script.ui.shared.planet.planetConst import *
from eve.common.script.util.planetCommon import RADIUS_DRILLAREAMIN, RADIUS_DRILLAREAMAX
from eveplanet.client.templates.templateConst import *
import inventorycommon.const as invConst
from localization import GetByLabel
COMMENT_MAX_WIDTH = 60
DEFAULT_DRILL_RADIUS = (RADIUS_DRILLAREAMIN + RADIUS_DRILLAREAMAX) / 2.0

class ColonyTemplateWindow(Window):
    default_height = IdealSize.SIZE_480
    default_width = IdealSize.SIZE_480
    default_minSize = (350, IdealSize.SIZE_240)
    default_caption = GetByLabel('UI/PI/PITemplates')
    default_windowID = u'ColonyTemplateWindow'
    default_analyticID = 'pi_template_window'
    __notifyevents__ = ['OnPITemplatesUpdated', 'OnTemplateDeleted']

    def ApplyAttributes(self, attributes):
        super(ColonyTemplateWindow, self).ApplyAttributes(attributes)
        self.clipChildren = True
        self._loadingTemplates = False
        self._blockTemplateLoading = False
        self._templateLoadingPending = False
        self.planetEditModeContainer = attributes.get('target')
        self.ConstructUI()
        self.AsyncLoadTemplatesFromLocal()
        sm.RegisterNotify(self)

    def ConstructUI(self):
        self.ConstructTextFilter()
        bottomRightCont = Container(name='bottomRightcont', parent=self.content, align=uiconst.TOBOTTOM, height=24, clipChildren=True)
        self.numTemplatesLabel = TextBody(name='numTemplatesLabel', parent=bottomRightCont, align=uiconst.CENTERLEFT, color=TextColor.SECONDARY, bold=True)
        self.scroll = ScrollContainer(parent=self.content, align=uiconst.TOALL, top=16)

    def ConstructTextFilter(self):
        self.textFilterSetting = UserSettingString('PI_template_text_filter', '')
        filterCont = ContainerAutoSize(name='filterCont', parent=self.content, align=Align.TOTOP, alignMode=Align.TOTOP)
        mb = MenuButton(parent=filterCont, hint=GetByLabel('UI/Fitting/FittingWindow/ImportAndExport'), texturePath=eveicon.export, get_menu_func=self._get_import_export_menu)
        mbi = MenuButtonIcon(parent=filterCont, align=uiconst.CENTERLEFT, left=mb.left + mb.width + 8, widht=24, height=24, texturePath=eveicon.filter, iconSize=16, get_menu_func=self._GetMenuMoreOptions)
        self.filterEdit = QuickFilterEdit(name='searchField', parent=filterCont, hintText=GetByLabel('UI/Inventory/Filter'), maxLength=64, align=uiconst.TOTOP, OnClearFilter=self.OnFilterEditCleared, padLeft=mbi.left + mbi.width + 8, setvalue=self.textFilterSetting.get())
        self.filterEdit.ReloadFunction = self.OnFilterEdit

    def OnFilterEdit(self):
        self.RecordTextFieldChanges()

    def OnFilterEditCleared(self):
        self._RecordTextFieldChanges()

    @uthread2.debounce(0.5)
    def RecordTextFieldChanges(self):
        self._RecordTextFieldChanges()

    def _RecordTextFieldChanges(self):
        filterText = self.filterEdit.GetValue().strip().lower()
        self.textFilterSetting.set(filterText)
        self.AsyncLoadTemplatesFromLocal()

    def OnPITemplatesUpdated(self):
        self.AsyncLoadTemplatesFromLocal()

    def AsyncLoadTemplatesFromLocalForFilters(self, *args):
        if self._blockTemplateLoading:
            return
        if self._loadingTemplates:
            self._templateLoadingPending = True
            return
        uthread2.start_tasklet(self.InvokeLoadTemplatesFromLocal)

    def AsyncLoadTemplatesFromLocal(self, *args):
        if self._loadingTemplates:
            self._templateLoadingPending = True
            return
        uthread2.start_tasklet(self.InvokeLoadTemplatesFromLocal)

    def InvokeLoadTemplatesFromLocal(self):
        if self.destroyed:
            return
        if self._loadingTemplates:
            self._templateLoadingPending = True
            return
        self._templateLoadingPending = False
        self._loadingTemplates = True
        try:
            self.scroll.Flush()
            templatesToLoad, numTotalTemplates = self._GetValidTemplatesAndTotalNum()
            self.UpdateFilteredText(len(templatesToLoad), numTotalTemplates)
            timeOffsetValue = 0.1
            for i, temp in enumerate(templatesToLoad):
                try:
                    templateEntry = ColonyTemplateEntry(parent=self.scroll, colonyTemplate=temp, height=135, align=uiconst.TOTOP, target=self.planetEditModeContainer, fileName=temp.filename)
                except:
                    logging.error(u'File {0} cannot be interpreted'.format(temp.filename))
                    continue

                uicore.animations.FadeTo(templateEntry, 0, 1.0, duration=0.65, timeOffset=i * timeOffsetValue)

        finally:
            self._loadingTemplates = False
            if self._templateLoadingPending:
                self.AsyncLoadTemplatesFromLocal()

    def _GetValidTemplatesAndTotalNum(self):
        allTemplates = self._LoadFromLocal()
        currentPlanet = sm.GetService('planetUI').GetCurrentPlanet()
        currentPlanetRadius = currentPlanet.GetPlanetRadius() / 1000 if currentPlanet else None
        filterText = self.filterEdit.GetValue().strip().lower()
        validTemplates = GetValidTemplates(allTemplates, currentPlanetRadius, filterText)
        return (validTemplates, len(allTemplates))

    def UpdateFilteredText(self, numValidTemplates, numTotalTemplates):
        numFilteredout = max(0, numTotalTemplates - numValidTemplates)
        if numValidTemplates < 1:
            if self.planetEditModeContainer:
                if numFilteredout:
                    notFoundText = GetByLabel('UI/PI/NoTemplatesFoundWithFilter', numFilteredOut=numFilteredout)
                else:
                    notFoundText = GetByLabel('UI/PI/NoTemplatesFoundInPiView')
            else:
                notFoundText = GetByLabel('UI/PI/NoTemplatesFound')
            self.scroll.ShowNoContentHint(notFoundText)
        if numFilteredout > 0:
            filtered_text = GetByLabel('UI/Inventory/NumFiltered', numFiltered=numFilteredout)
        else:
            filtered_text = ''
        text = GetByLabel('UI/PI/NumTemplates', numTemplates=numValidTemplates, numFilteredTxt=filtered_text)
        if numFilteredout > 0:
            text = eveformat.color(text, eveColor.SUCCESS_GREEN)
        self.numTemplatesLabel.text = text

    def OnTemplateDeleted(self):
        templatesToLoad, numTotalTemplates = self._GetValidTemplatesAndTotalNum()
        self.UpdateFilteredText(len(templatesToLoad), numTotalTemplates)

    def _GetMenuMoreOptions(self, *args):
        menu = MenuData()
        cmdCenterLV = self.CreateListOfSelectionsOfMenuData(CMD_CTR_LELVES, SETTING_KEY_CMD_CNTR)
        planetTypesToShow = self.CreateListOfSelectionsOfMenuData(PlanetTypes.itervalues(), SETTING_KEY_PLANET_TYPE, True)
        extractTypesToShow = self.CreateListOfSelectionsOfMenuData(ExtractionTypes.itervalues(), SETTING_KEY_EXTRACT_TYPE, True)
        processedTypesToShow = self.CreateListOfSelectionsOfMenuData(ProcessedTypes.itervalues(), SETTING_KEY_PROCESSED, True)
        refinedTypesToShow = self.CreateListOfSelectionsOfMenuData(RefinedTypes.itervalues(), SETTING_KEY_REFINED, True)
        specializedTypesToShow = self.CreateListOfSelectionsOfMenuData(SpecializedTypes.itervalues(), SETTING_KEY_SPECIALIZED, True)
        advancedTypesToShow = self.CreateListOfSelectionsOfMenuData(AdvancedTypes.itervalues(), SETTING_KEY_ADVANCED, True)
        menu.AddEntry(text=GetByLabel('UI/PI/CmdCtrLV'), subMenuData=cmdCenterLV)
        menu.AddEntry(text=GetByLabel('UI/PI/PlanetTypes'), subMenuData=planetTypesToShow)
        menu.AddEntry(text=evetypes.GetCategoryNameByCategory(invConst.categoryPlanetaryResources), subMenuData=extractTypesToShow)
        menu.AddSeparator()
        menu.AddEntry(text=localization.GetByMessageID(evetypes.GetGroupNameIDByGroup(invConst.groupBasicCommodities)), subMenuData=processedTypesToShow)
        menu.AddEntry(text=localization.GetByMessageID(evetypes.GetGroupNameIDByGroup(invConst.groupRefinedCommodities)), subMenuData=refinedTypesToShow)
        menu.AddEntry(text=localization.GetByMessageID(evetypes.GetGroupNameIDByGroup(invConst.groupSpecializedCommodities)), subMenuData=specializedTypesToShow)
        menu.AddEntry(text=localization.GetByMessageID(evetypes.GetGroupNameIDByGroup(invConst.groupAdvancedCommodities)), subMenuData=advancedTypesToShow)
        menu.AddSeparator()
        currentPlanet = sm.GetService('planetUI').GetCurrentPlanet()
        if currentPlanet:
            menu.AddCheckbox(text=GetByLabel('UI/PI/HideInapprop'), setting=SettingsHideInappropriateRadius)
            SettingsHideInappropriateRadius.on_change.connect(self.AsyncLoadTemplatesFromLocal)
        menu.AddEntry(text=GetByLabel('UI/Commands/Refresh'), func=self.InvokeLoadTemplatesFromLocal)
        return menu

    def CreateListOfSelectionsOfMenuData(self, iterable, settingString, isInputTypeID = False):
        menuDataInstance = MenuData()
        checkBoxes = []
        sortedValues = sorted(iterable, key=lambda x: (localization.GetByMessageID(evetypes.GetNameID(x)) if isInputTypeID else unicode(x)))
        for value in sortedValues:
            settingBool = UserSettingBool(settings_key=settingString.format(str(value)), default_value=False)
            settingBool.on_change.connect(self.AsyncLoadTemplatesFromLocalForFilters)
            label = localization.GetByMessageID(evetypes.GetNameID(value)) if isInputTypeID else unicode(value)
            newChkBox = menuDataInstance.AddCheckbox(text=label, setting=settingBool)
            checkBoxes.append(newChkBox)

        def DoAll(action):
            self._blockTemplateLoading = True
            for ckbox in checkBoxes:
                ckbox.setting.set(action)

            self._blockTemplateLoading = False
            self.AsyncLoadTemplatesFromLocal()

        menuDataInstance.AddEntry(text=GetByLabel('UI/Common/DeselectAll'), func=lambda : DoAll(False))
        menuDataInstance.AddEntry(text=GetByLabel('UI/Common/SelectAll'), func=lambda : DoAll(True))
        return menuDataInstance

    def LoadFromClipboard(self, *args):
        warnResult = uicore.Message('CustomWarning', {'header': GetByLabel('UI/Generic/Warning'),
         'warning': GetByLabel('UI/PI/LoadWarning')}, buttons=uiconst.OKCANCEL)
        if warnResult != uiconst.ID_OK:
            return
        newJSON = blue.clipboard.GetClipboardUnicode()
        if newJSON is None:
            return
        if len(newJSON) > 65536:
            warnResult = uicore.Message('CustomWarning', {'header': GetByLabel('UI/Generic/Warning'),
             'warning': GetByLabel('UI/PI/TemplateTooLong')}, buttons=uiconst.OKCANCEL)
            if warnResult != uiconst.ID_OK:
                return
        try:
            newTemplate = ColonyTemplate(unicode(newJSON), None)
            PreviewLoad(newTemplate)
        except UserError as e:
            raise
        except Exception as e:
            logging.exception('PI Templates: Error while saving file')
            uicore.Message('CustomError', {'error': GetByLabel('UI/PI/ErrorLoadingFromClipboard')})

    def SaveFromClipboard(self, *args):
        newJSON = blue.clipboard.GetClipboardUnicode()
        SaveToLocalFile(newJSON, encoding='unicode-escape')

    def SaveFromLink(self, url):
        newJSON = url
        warnResult = uicore.Message('CustomWarning', {'header': GetByLabel('UI/Generic/Warning'),
         'warning': GetByLabel('UI/PI/LoadWarning')}, buttons=uiconst.OKCANCEL)
        if warnResult != uiconst.ID_OK:
            return
        if len(newJSON) > 65536:
            warnResult = uicore.Message('CustomWarning', {'header': GetByLabel('UI/Generic/Warning'),
             'warning': GetByLabel('UI/PI/TemplateTooLong')}, buttons=uiconst.OKCANCEL)
            if warnResult != uiconst.ID_OK:
                return
        SaveToLocalFile(newJSON)

    def _LoadFromLocal(self):
        files = []
        defaultStoragePath = GetDefaultStoragePath()
        if not os.path.exists(defaultStoragePath):
            try:
                os.makedirs(defaultStoragePath)
                files = os.listdir(defaultStoragePath)
            except:
                ShowQuickMessage(GetByLabel('UI/PI/FailedOnCreatingDirectory', path=defaultStoragePath))

        try:
            files = os.listdir(defaultStoragePath)
        except:
            try:
                os.makedirs(defaultStoragePath)
                files = os.listdir(defaultStoragePath)
            except:
                ShowQuickMessage(GetByLabel('UI/PI/FailedOnCreatingDirectory', path=defaultStoragePath))

        templates = []
        for singleTemp in files:
            try:
                with open(os.path.join(defaultStoragePath, singleTemp)) as tempStream:
                    templates.append(ColonyTemplate(tempStream.read(), singleTemp))
            except StandardError as e:
                pass

        templates = sorted(templates, key=lambda x: x.description.lower())
        return templates

    def _get_import_export_menu(self):
        m = MenuData()
        if self.planetEditModeContainer is not None:
            m.AddEntry(text=GetByLabel('UI/PI/LoadFromClipboard'), func=self.LoadFromClipboard)
        m.AddEntry(text=GetByLabel('UI/PI/SaveFromClipboard'), func=self.SaveFromClipboard)
        m.AddSeparator()
        if self.planetEditModeContainer and self.planetEditModeContainer.IsCommandCenterPresent():
            m.AddEntry(text=GetByLabel('UI/PI/ExportToClipboard'), func=lambda *args: self.planetEditModeContainer.CopyTemplateToClipboard())
            m.AddEntry(text=GetByLabel('UI/PI/ExportToFileLong'), func=lambda *args: self.planetEditModeContainer.SaveTemplateToFile())
        return m


class ColonyTemplateEntry(ContainerAutoSize):
    isDragObject = True
    default_state = uiconst.UI_NORMAL
    default_bgColor = (0, 0, 0, 0.6)
    default_clipChildren = True
    default_padding = (0, 0, 0, 8)
    default_minHeight = 60
    default_alignMode = Align.TOTOP

    def ApplyAttributes(self, attributes):
        super(type(self), self).ApplyAttributes(attributes)
        self.colonyTemplate = attributes.get('colonyTemplate')
        self.fileName = attributes.get('fileName')
        self.storagePath = GetDefaultStoragePath()
        self.planetEditModeContainer = attributes.get('target')
        self.ConstructFrameAndBackground()
        self.innerCont = ContainerAutoSize(name='innerCont', parent=self, padding=16, align=Align.TOTOP)
        self.ConstructFirstRow()
        self.ConstructComment()
        self.ConstructSecondRow()

    def ConstructFrameAndBackground(self):
        texturePath = planetUtil.backgroundTexturePath.get(self.colonyTemplate.originalPlanetType)
        bgPlanetSprite = Sprite(parent=self, texturePath=texturePath, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, opacity=0.2, pos=(0, 0, 1138, 411))

    def AddLoadBtn(self, cont):
        btnCont = ContainerAutoSize(parent=cont, align=Align.TORIGHT)
        if self.planetEditModeContainer:
            plnet = sm.GetService('planetUI').GetCurrentPlanet()
            if plnet is not None and self.colonyTemplate.restricted and plnet.planetTypeID not in [PlanetTypes.BARREN, PlanetTypes.TEMPERATE]:
                btn = Button(parent=btnCont, label=GetByLabel('UI/Generic/NotAvailableShort'), enabled=False, align=Align.BOTTOMRIGHT)
            else:
                btn = Button(parent=btnCont, label=GetByLabel('UI/Generic/Load'), func=self.PreviewLoad, align=Align.BOTTOMRIGHT)
            cont.minHeight = max(cont.minHeight, btn.height)

    def DeleteTemplate(self, *args):
        fileName = self.fileName
        fullpath = u'{0}'.format(os.path.join(self.storagePath, fileName))
        templateName = self.colonyTemplate.description
        result = eve.Message('DeletePITemplate', {'templateName': templateName}, modal=True, buttons=uiconst.YESNO)
        if result != uiconst.ID_YES:
            return
        try:
            os.remove(fullpath)
            self.Disable()
            sm.ScatterEvent('OnTemplateDeleted')
            animations.FadeOut(self, duration=0.5, sleep=True)
            self.Close()
        except Exception as e:
            raise

    def CopyTemplate(self, *args):
        self.CopyToClipboard()

    def ConstructComment(self):
        cont = ContainerAutoSize(name='commentCont', parent=self.innerCont, align=Align.TOTOP, alignMode=Align.TOTOP, top=16)
        btnCont = Container(parent=cont, align=Align.TORIGHT, width=50)
        ButtonIcon(parent=btnCont, texturePath=eveicon.trashcan, pos=(0, 0, 16, 16), align=uiconst.TOPRIGHT, func=self.DeleteTemplate, hint=GetByLabel('UI/Common/Buttons/Delete'))
        ButtonIcon(parent=btnCont, texturePath=eveicon.copy, pos=(32, 0, 16, 16), align=uiconst.TOPRIGHT, func=self.CopyTemplate, hint=GetByLabel('UI/PI/CopyPlainText'))
        comment = self.colonyTemplate.description
        commentLabel = TextHeader(name='commentLabel', parent=cont, text=comment if len(comment) < COMMENT_MAX_WIDTH else u'{0}...'.format(comment[:COMMENT_MAX_WIDTH]), align=Align.TOTOP, state=uiconst.UI_NORMAL, bold=True)
        commentLabel.hint = comment
        commentLabel.isDragObject = True
        commentLabel.Draggable_blockDrag = False
        commentLabel.GetDragData = self.GetDragData
        commentLabel.PrepareDrag = self.PrepareDrag
        commentLabel.GetMenu = self.GetMenu

    def ConstructSecondRow(self):
        cont = ContainerAutoSize(name='secondRow', parent=self.innerCont, align=Align.TOTOP, height=30, alignMode=Align.TOTOP, top=16)
        self.AddLoadBtn(cont)
        if len(self.colonyTemplate.extractTypes) > 0:
            additionalText = ''
            textColor = TextColor.SECONDARY
            if self.planetEditModeContainer is not None:
                plnet = sm.GetService('planetUI').GetCurrentPlanet()
                if plnet is not None and self.colonyTemplate.originalPlanetType != plnet.planetTypeID:
                    textColor = Color.YELLOW
                    additionalText = GetByLabel('UI/PI/MightNotSuitable')
            exctItemAmount = self._GetAllProducts(self.colonyTemplate.extractSourceCount)
            text = TextDetail(parent=cont, text=GetByLabel('UI/PI/Common/Extraction'), align=Align.TOTOP, color=textColor, pickState=PickState.ON)
            text.hint = additionalText
            iconCont = FlowContainer(parent=cont, align=Align.TOTOP, top=4, contentSpacing=(8, 8))
            sortedExtractTypes = sorted(exctItemAmount.keys(), key=lambda x: (GetTierByTypeID(x), evetypes.GetName(x)))
            for typeID in sortedExtractTypes:
                c = Container(parent=iconCont, align=uiconst.TOPLEFT, color=(0, 0, 0, 1.4), pos=(0, 0, 32, 32))
                icon = StorageIcon(parent=c, align=uiconst.TOPLEFT, width=self.height, typeID=typeID, pos=(0, 0, 32, 32))
                Fill(parent=c, color=(0, 0, 0, 0.2))

        if len(self.colonyTemplate.productTypes) > 0:
            top = 8 if self.colonyTemplate.extractTypes else 0
            text = TextDetail(parent=cont, text=GetByLabel('UI/PI/Common/Production'), align=Align.TOTOP, color=TextColor.SECONDARY, top=top)
            pdItemAmount = self._GetAllProducts(self.colonyTemplate.productSourceCount)
            iconCont = FlowContainer(parent=cont, align=Align.TOTOP, top=4, contentSpacing=(8, 8))
            sortedProducts = sorted(pdItemAmount.keys(), key=lambda x: (GetTierByTypeID(x), evetypes.GetName(x)))
            for typeID in sortedProducts:
                c = Container(parent=iconCont, align=uiconst.TOPLEFT, color=(0, 0, 0, 1.4), pos=(0, 0, 32, 32))
                icon = StorageIcon(parent=c, align=uiconst.TOPLEFT, width=self.height, typeID=typeID, pos=(0, 0, 32, 32))
                Fill(parent=c, color=(0, 0, 0, 0.2))

    def ConstructFirstRow(self):
        labelOffset = 2
        grid = LayoutGrid(name='firstRow', parent=self.innerCont, align=Align.TOTOP, columns=4, cellSpacing=(30, 0))
        planetCont = ContainerAutoSize(name='planetCont', parent=grid, align=Align.CENTERLEFT, pickState=PickState.ON, hint=GetByLabel('UI/PI/PlanetTypes'))
        planetIcon = Sprite(parent=planetCont, texturePath=eveicon.planet_management, pos=(0, 0, 16, 16), align=Align.CENTERLEFT, pickState=PickState.OFF, color=TextColor.SECONDARY)
        planetTypeName = TextDetail(parent=planetCont, text=GetByLabel(planetConst.PLANETTYPE_NAMES[self.colonyTemplate.originalPlanetType]), left=labelOffset + planetIcon.width, align=Align.CENTERLEFT, color=TextColor.SECONDARY)
        cmdCtrCont = ContainerAutoSize(name='cmdCtrCont', parent=grid, align=Align.CENTERLEFT, pickState=PickState.ON, hint=GetByLabel('UI/PI/CmdCtrLV'))
        cmdCtr = Sprite(parent=cmdCtrCont, texturePath='res:/UI/Texture/Planet/icons/commandCenter_16.png', pos=(0, 0, 16, 16), align=Align.CENTERLEFT, pickState=PickState.OFF, color=TextColor.SECONDARY)
        textColor = TextColor.SECONDARY if sm.GetService('skills').GetEffectiveLevel(appConst.typeCommandCenterUpgrade) >= self.colonyTemplate.commandCenterLV else TextColor.DANGER
        cmdCtllv = TextDetail(parent=cmdCtrCont, text=GetByLabel('UI/PI/CommandCenterLevel', level=self.colonyTemplate.commandCenterLV + 1), left=labelOffset + cmdCtr.width, color=textColor, align=Align.CENTERLEFT)
        radiusCont = ContainerAutoSize(name='radiusCont', parent=grid, align=Align.CENTERLEFT, pickState=PickState.ON, hint=GetByLabel('UI/PI/RadiusOfPlanet'))
        radiusIcon = Sprite(parent=radiusCont, texturePath='res:/UI/Texture/Planet/icons/radius.png', pos=(0, 0, 16, 16), align=Align.CENTERLEFT, pickState=PickState.OFF, color=TextColor.SECONDARY)
        radiusText = TextDetail(parent=radiusCont, text=get_distance_in_kilometers(self.colonyTemplate.radiusOfPlanet), left=labelOffset + radiusIcon.width, align=Align.CENTERLEFT, color=TextColor.SECONDARY)
        templatePinCont = ContainerAutoSize(name='templatePinCont', parent=grid, align=Align.CENTERLEFT, pickState=PickState.ON)
        templatePinIcon = Sprite(name='templatePinIcon', parent=templatePinCont, texturePath='res:/UI/Texture/Planet/icons/templatePins.png', pos=(0, 0, 16, 16), align=Align.CENTERLEFT, pickState=PickState.OFF, color=TextColor.SECONDARY)
        templateData = self.colonyTemplate.loadedTemplate
        templatePinCont.LoadTooltipPanel = self.LoadTemplatePinsTooltip
        numPins = len(templateData[TemplateDictKeys.PinData])
        TextDetail(parent=templatePinCont, text=numPins, left=templatePinIcon.width + labelOffset, align=Align.CENTERLEFT, color=TextColor.SECONDARY)
        if self.planetEditModeContainer is not None:
            plnet = sm.GetService('planetUI').GetCurrentPlanet()
            if plnet is not None:
                if self.colonyTemplate.radiusOfPlanet * 1000.0 < plnet.radius:
                    radiusText.SetTextColor(Color.YELLOW)
                    radiusCont.SetHint(GetByLabel('UI/PI/HintOversizedPlanet'))
                else:
                    radiusText.SetTextColor(TextColor.SECONDARY)
                    radiusCont.SetHint(GetByLabel('UI/PI/RadiusOfPlanet'))
                if self.colonyTemplate.originalPlanetType != plnet.planetTypeID:
                    planetTypeName.SetTextColor(Color.YELLOW)
                    planetCont.SetHint(GetByLabel('UI/PI/MightNotSuitable'))
                if self.colonyTemplate.restricted and plnet.planetTypeID not in [PlanetTypes.BARREN, PlanetTypes.TEMPERATE]:
                    planetTypeName.SetTextColor(Color.RED)
                    planetCont.SetHint(GetByLabel('UI/PI/NotSuitableDueToCruelEnv'))

    def DoReRender(self, a):
        from eve.client.script.ui.control.message import ShowQuickMessage
        ShowQuickMessage(GetByLabel('UI/PI/Loading'))
        uthread2.sleep(0.5)
        ShowQuickMessage(GetByLabel('UI/PI/LoadCompleted'))
        planetUI = sm.GetService('planetUI')
        planetUI.myPinManager.ReRender()
        sm.GetService('planetUI').FocusCameraOnCommandCenter()
        self.planetEditModeContainer.ResetBuildbuttons(falser=True)
        sm.ScatterEvent('OnEditModeChanged', True)

    def _GetAllProducts(self, products):
        ret = defaultdict(int)
        for typeID, amount in products.iteritems():
            ret[typeID] += amount

        return ret

    def PreviewLoad(self, *args):
        return PreviewLoad(self.colonyTemplate)

    def CopyToClipboard(self, *args):
        blue.clipboard.SetClipboardData(self.colonyTemplate.rawTemplate.decode('unicode-escape'))
        ShowQuickMessage(GetByLabel('UI/PI/Copied'), flashNewText=False)

    def UpdateDescription(self):
        templateCopy = self.colonyTemplate.loadedTemplate.copy()
        defaultNote = templateCopy[TemplateDictKeys.Comments]
        wnd = ConfirmExportWnd.Open(defaultNote=defaultNote, captionPath='UI/PI/RenameTemplate', okPath='UI/PI/SaveTemplate')
        wnd.SetParent(uicore.layer.planet)
        wnd.ShowDialog(modal=True)
        retval = wnd.result
        if retval is None:
            return
        note = retval.get('note', '')
        bannedwords.check_words_allowed(note)
        templateCopy[TemplateDictKeys.Comments] = note
        jsonText = json.dumps(obj=templateCopy, sort_keys=True).decode('unicode-escape')
        fileName = u'{0}'.format(os.path.join(GetDefaultStoragePath(), self.colonyTemplate.filename))
        SaveToLocalFile(jsonText, fileName, encoding='unicode-escape')

    def GetMenu(self):
        menuData = MenuData()
        menuData.AddEntry(GetByLabel('UI/PI/RenameTemplate'), lambda : self.UpdateDescription())
        return menuData

    def GetDragData(self):
        from utillib import KeyVal
        template = KeyVal()
        plnName = GetByLabel(planetConst.PLANETTYPE_NAMES[self.colonyTemplate.originalPlanetType])
        templateName = GetByLabel('UI/PI/TemplateOf', planetType=plnName)
        templateDragData = PITempateDragData(templateName, self.colonyTemplate.rawTemplate)
        return [templateDragData]

    @classmethod
    def PrepareDrag(cls, dragContainer, dragSource, *args):
        dragData = dragContainer.dragData[0]
        displayText = eveformat.truncate_text_ignoring_tags(dragData.templateName, 24, '...')
        label = Label(parent=dragContainer, text=u'{0}({1}+)'.format(displayText, len(dragData.rawTemplate)), align=uiconst.TOPLEFT, bold=True)
        Fill(parent=dragContainer, color=(0, 0, 0, 0.3), padding=(-10, -2, -10, -2))
        dragContainer.width = label.textwidth
        dragContainer.height = label.textheight
        return (2, label.textheight)

    def LoadTemplatePinsTooltip(self, tooltipPanel, *args):
        templateData = self.colonyTemplate.loadedTemplate
        pinsByType = defaultdict(int)
        normalPinsByGroupID = defaultdict(int)
        for pin in templateData[TemplateDictKeys.PinData]:
            pinType = pin[TemplatePinDataDictKeys.PinTypeID]
            if planetUtil.IsTypeHighTechProcessor(pinType):
                pinsByType[PIN_HIGH] += 1
            elif planetUtil.IsTypeAdvancedProcessor(pinType):
                pinsByType[PIN_ADV] += 1
            elif planetUtil.IsTypeBasicProcessor(pinType):
                pinsByType[PIN_BASIC] += 1
            else:
                groupID = evetypes.GetGroupID(pinType)
                normalPinsByGroupID[groupID] += 1

        if pinsByType or normalPinsByGroupID:
            tooltipPanel.LoadStandardSpacing()
            tooltipPanel.columns = 3
        else:
            return

        def AddPinEntry(texturePath, text, countText):
            Sprite(parent=tooltipPanel, align=uiconst.CENTERLEFT, pos=(0, 0, 22, 22), texturePath=texturePath, color=TextColor.SECONDARY)
            tooltipPanel.AddTextBodyLabel(text=text)
            tooltipPanel.AddTextBodyLabel(text=countText)

        if pinsByType:
            for identifier, labelPath in [(PIN_BASIC, 'UI/PI/BasicIndustryFacilities'),
             (PIN_ADV, 'UI/PI/AdvancedIndustryFacilities'),
             (PIN_HIGH, 'UI/PI/HighTechProdPlant'),
             ('other', 'UI/PI/OtherPins')]:
                if identifier in pinsByType:
                    texturePath = planetUtil.GetTexturePath(identifier)
                    countText = pinsByType[identifier]
                    text = GetByLabel(labelPath)
                    AddPinEntry(texturePath, text, countText)

        for groupID, pinCount in normalPinsByGroupID.iteritems():
            groupName = evetypes.GetGroupNameByGroup(groupID)
            texturePath = planetUtil.GetTexturePath(None, groupID)
            AddPinEntry(texturePath, groupName, pinCount)

        numLinks = len(templateData[TemplateDictKeys.LinkData])
        numRoutes = len(templateData[TemplateDictKeys.RouteData])
        if numLinks:
            AddPinEntry('res:/UI/Texture/Planet/icons/link.png', GetByLabel('UI/PI/Common/Links'), numLinks)
        if numRoutes:
            AddPinEntry('', GetByLabel('UI/PI/Common/Routes'), numRoutes)


class PITempateDragData(BaseDragData):
    check_link_fits = True

    def __init__(self, templateName, rawTemplate):
        super(PITempateDragData, self).__init__()
        self.templateName = templateName
        self.displayText = templateName
        self.rawTemplate = rawTemplate

    def get_link(self):
        return self._template_link()

    def _template_link(self):
        url = format_pi_template_url(self.rawTemplate)
        text = u'{0}({1}+)'.format(self.templateName, len(url))
        import evelink.client
        return evelink.Link(url=url, text=text)


PIScheme = 'colonytemplate'

def register_link_handlers(registry):
    registry.register(PIScheme, _handle_link, hint=_get_link_hint)


def _handle_link(url):
    newJSON = _parse_url(url)
    ColonyTemplateWindow.Open().SaveFromLink(newJSON)


def _get_link_hint(url):
    newJSON = _parse_url(url)
    loaded = json.loads(newJSON)
    hint = u'{0}<br><br>{1}'.format(loaded[TemplateDictKeys.Comments], GetByLabel('UI/PI/ClickToSaveToLocal'))
    return hint


def _parse_url(url):
    url = unicode(url).replace(u'colonytemplate:', '')
    url = base64.b64decode(decompressFromUnicode(url))
    return url


def format_pi_template_url(content):
    return u'{0}:{1}'.format(PIScheme, compressToUnicode(base64.b64encode(content)))


def compressToUnicode(text):
    while len(text) % 2 != 0:
        text += '\x00'

    unicode_text = u''
    for i in range(0, len(text), 2):
        ord_val = (ord(text[i]) << 8) + ord(text[i + 1])
        unicode_text += unichr(ord_val)

    return unicode_text


def decompressFromUnicode(unicode_text):
    text = u''
    for ch in unicode_text:
        ord_val = ord(ch)
        text += chr(ord_val >> 8 & 255)
        text += chr(ord_val & 255)

    return text.rstrip('\x00')
