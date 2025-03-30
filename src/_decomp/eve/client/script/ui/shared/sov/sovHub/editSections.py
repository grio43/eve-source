#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\editSections.py
import carbonui
import eveicon
from carbonui import const as uiconst
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.tooltips import TooltipPersistentPanel
from eve.client.script.ui.shared.bookmarks.bookmarkContainerWindow import DropCombo
from eve.client.script.ui.shared.messagebox import MessageBox
from localization import GetByLabel
from sovereignty.client.quasarCallWrapper import DATA_NOT_AVAILABLE
from sovereignty.workforce.client.data_types import WorkforceConfiguration, WorkforceImportConfiguration, WorkforceExportConfiguration
import sovereignty.workforce.workforceConst as workforceConst

class BaseSectionCont(ContainerAutoSize):
    sectionTexturePath = eveicon.workforce
    sectionNameLabelPath = ''
    default_canEdit = True

    def ApplyAttributes(self, attributes):
        self.descLabel = None
        self.editLabel = None
        super(BaseSectionCont, self).ApplyAttributes(attributes)
        self.canEdit = attributes.Get('canEdit', self.default_canEdit)
        self.ConstructUI()

    def ConstructUI(self):
        self.header = carbonui.TextDetail(parent=self, text=GetByLabel(self.sectionNameLabelPath), color=carbonui.TextColor.SECONDARY, align=carbonui.Align.TOTOP)
        self.stateCont = ContainerAutoSize(name='stateCont', parent=self, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP)
        self.stateSprite = Sprite(parent=self.stateCont, align=carbonui.Align.CENTERLEFT, pos=(0, 0, 16, 16), texturePath=self.sectionTexturePath, color=eveColor.TUNGSTEN_GREY)
        self.labelCont = ContainerAutoSize(name='labelCont', parent=self.stateCont, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.TOTOP, padLeft=20)
        self.stateLabel = carbonui.TextHeader(name='stateLabel', parent=self.labelCont, text=' ', align=carbonui.Align.TOTOP)
        if self.canEdit:
            self.editLabel = carbonui.TextBody(parent=self.labelCont, text=GetByLabel('UI/Sovereignty/SovHub/HubWnd/SectionEdit'), color=eveColor.CRYO_BLUE, align=carbonui.Align.BOTTOMRIGHT, top=2, pickState=carbonui.PickState.ON)
            self.stateLabel.padRight = self.editLabel.width
            self.editLabel.OnClick = self.OnEditClicked

    def LoadSection(self):
        pass

    def OnEditClicked(self, *args):
        pass

    def GetDesriptionText(self):
        return ''


class TransitCont(BaseSectionCont):
    default_name = 'transitCont'
    sectionNameLabelPath = 'UI/Sovereignty/SovHub/HubWnd/SectionWorkforceTransport'
    sectionTexturePath = eveicon.workforce

    def ApplyAttributes(self, attributes):
        self.workforceController = attributes.workforceController
        super(TransitCont, self).ApplyAttributes(attributes)
        if hasattr(self.workforceController, 'on_workforce_changed'):
            self.workforceController.on_workforce_changed.connect(self.OnWorkforceChanged)

    def ConstructUI(self):
        super(TransitCont, self).ConstructUI()
        self.descLabel = carbonui.TextBody(parent=self, text='', color=carbonui.TextColor.SECONDARY, align=carbonui.Align.TOTOP, pickState=carbonui.PickState.ON)
        cont = ContainerAutoSize(parent=self, align=carbonui.Align.TOTOP)
        self.systemFlowCont = FlowContainer(name='systemFlowCont', parent=cont, align=uiconst.TOTOP)

    def LoadSection(self):
        text, valid, texturePath = self.workforceController.GetWorkforceTextsAndTexturePath()
        if text == DATA_NOT_AVAILABLE or not valid:
            text = GetByLabel('UI/Sovereignty/HubPage/NotAvailable', color=eveColor.GUNMETAL_HEX)
            if self.editLabel:
                self.editLabel.Hide()
        elif self.editLabel:
            self.editLabel.Show()
        self.stateSprite.SetTexturePath(texturePath)
        self.stateLabel.text = text
        descText = self.workforceController.GetWorkforceTransportDesc()
        self.descLabel.text = descText
        importedSystems = self.workforceController.GetWorkforceImportSystems()
        self.systemFlowCont.Flush()
        if importedSystems:
            self._LoadImportedSystems(importedSystems)

    def _LoadImportedSystems(self, importedSystems):
        for systemLink, amount in importedSystems:
            cont = ContainerAutoSize(parent=self.systemFlowCont)
            textLeft = 0
            if not amount:
                sprite = Sprite(parent=cont, align=carbonui.Align.CENTERLEFT, texturePath='res:/UI/Texture/classes/agency/iconExclamation.png', pos=(0, 0, 16, 16))
                if amount is None:
                    sprite.hint = GetByLabel('UI/Sovereignty/SovHub/HubWnd/SourceSystemNotConnected')
                else:
                    sprite.hint = GetByLabel('UI/Sovereignty/SovHub/HubWnd/SourceSystemNotSendingWorkforce')
                textLeft = 20
                text = systemLink
            else:
                text = '%s (%s)' % (systemLink, amount)
            carbonui.TextBody(parent=cont, text=text, left=textLeft, pickState=carbonui.PickState.ON, align=carbonui.Align.CENTERLEFT, padRight=10)

    def OnWorkforceChanged(self, *args):
        self.KillTooltip()
        self.LoadSection()

    def OnEditClicked(self, *args):
        uicore.uilib.tooltipHandler.LoadPersistentTooltip(owner=self.editLabel, customTooltipClass=EditSectionTooltip, loadArguments=(EditTransitCont, self.workforceController), parent=uicore.layer.utilmenu)

    def KillTooltip(self):
        existingTooltip = uicore.uilib.tooltipHandler.GetPersistentTooltipByOwner(self.editLabel)
        if existingTooltip and not existingTooltip.destroyed:
            existingTooltip.Close()


class AclSectionCont(BaseSectionCont):
    sectionTexturePath = 'res:/UI/Texture/WindowIcons/accessGroups.png'
    sectionNameLabelPath = 'UI/Sovereignty/SovHub/HubWnd/SectionACL'
    headerHintPath = 'UI/Sovereignty/SovHub/HubWnd/SectionACLDesc'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        self.editAclCont = None
        self.aclCombo = None
        self.controller = attributes.controller
        super(AclSectionCont, self).ApplyAttributes(attributes)
        if hasattr(self.controller, 'on_acl_changed'):
            self.controller.on_acl_changed.connect(self.OnAclChanged)
        if hasattr(self.controller, 'on_acl_setting_failed'):
            self.controller.on_acl_setting_failed.connect(self.OnAclSettingFailed)

    def ConstructUI(self):
        super(AclSectionCont, self).ConstructUI()
        self.header.pickState = carbonui.PickState.ON
        self.header.hint = GetByLabel(self.headerHintPath)
        if self.canEdit:
            self.editAclCont = Container(name='editAclCont', parent=self.stateCont, height=HEIGHT_NORMAL, align=carbonui.Align.TOTOP)
            bntCont = ContainerAutoSize(name='bntCont', parent=self.editAclCont, align=carbonui.Align.TORIGHT)
            comboCont = Container(name='comboCont', parent=self.editAclCont)
            btn = Button(name='applyBtn', parent=bntCont, align=uiconst.CENTER, label=GetByLabel('UI/Sovereignty/SovHub/HubWnd/SectionEditApply'), func=self.ApplyAcl)
            self.aclCombo = DropCombo(parent=comboCont, name='aclCombo', align=carbonui.Align.TOALL, options=self.controller.accessGroupOptions, select=self.controller.fuelACL, dropped=self.OnDroppedGroup, emptyTooltip=GetByLabel('UI/OrbitalSkyhook/ConfigWnd/TakeAccessComboHint'), left=20, padRight=8)
            self.editAclCont.display = False

    def OnDroppedGroup(self, newGroupID):
        for groupName, groupID in self.controller.accessGroupOptions:
            if groupID == newGroupID:
                self.aclCombo.SetValue(newGroupID)
                return

        self.controller.AddGroup(newGroupID)
        self.aclCombo.entries = self.controller.accessGroupOptions
        self.aclCombo.SetValue(newGroupID)

    def ApplyAcl(self, *args):
        newVal = self.aclCombo.GetValue()
        self.controller.SetFuelACL(newVal)
        self.editAclCont.display = False
        self.labelCont.display = True

    def LoadSection(self):
        text = self.controller.GetAclName()
        self.stateLabel.text = text

    def GetContentClass(self):
        return EditTransitCont

    def OnAclChanged(self, *args):
        self.LoadSection()

    def OnAclSettingFailed(self):
        self.editAclCont.display = False
        self.labelCont.display = True

    def OnEditClicked(self, *args):
        self.editAclCont.display = True
        self.labelCont.display = False


class EditSectionTooltip(TooltipPersistentPanel):
    default_pointerDirection = carbonui.uiconst.POINT_LEFT_2
    default_columns = 1
    default_state = carbonui.uiconst.UI_NORMAL
    default_margin = 16
    isTopLevelWindow = True

    def __init__(self, **kwargs):
        super(EditSectionTooltip, self).__init__(**kwargs)
        self.contentCont = None
        self.pickState = uiconst.TR2_SPS_ON
        uicore.registry.SetFocus(self)
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self._on_global_mouse_down)

    def LoadTooltip(self, contentClass, workforceController, *args):
        self.contentCont = contentClass(parent=self, workforceController=workforceController)

    def _on_global_mouse_down(self, *args):
        mouseOver = uicore.uilib.mouseOver
        if mouseOver is self or mouseOver.IsUnder(self):
            return True
        if self.contentCont and self.contentCont.BelongsToWindow(mouseOver):
            return True
        messageBox = MessageBox.GetIfOpen()
        if mouseOver.IsUnder(messageBox) and messageBox.isModal:
            return True
        self.Close()
        return False


class EditTransitCont(ContainerAutoSize):
    default_align = carbonui.Align.TOPLEFT
    default_height = 150
    default_width = 230
    default_state = carbonui.uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(EditTransitCont, self).ApplyAttributes(attributes)
        self.workforceController = attributes.workforceController
        self.importCombos = []
        carbonui.TextBody(parent=self, text=GetByLabel('UI/Sovereignty/SovHub/HubWnd/SectionWorkforceTransportSettings'), align=carbonui.Align.TOTOP)
        modeCont, self.modeLabel, self.modeCombo = self.GetComboCont(self, 'modeCont', GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorceforceMode'), self.OnModeChanged)
        options = self.workforceController.GetModeComboOptions()
        self.modeCombo.LoadOptions(options)
        self.ConstructExport()
        self.ConstructImport()
        self.AdjustComobWidths()
        btnGroup = ButtonGroup(parent=self, align=carbonui.Align.TOTOP)
        self.applyBtn = Button(name='applyBtn', align=uiconst.CENTER, label=GetByLabel('UI/Sovereignty/SovHub/HubWnd/SectionEditApply'), func=self.ApplySettings, enabled=False, top=6)
        btnGroup.add_button(self.applyBtn)
        self.LoadEditWnd()

    def ConstructExport(self):
        self.exportCont = ContainerAutoSize(name='exportCont', parent=self, align=carbonui.Align.TOTOP, top=4)
        amountCont = ContainerAutoSize(name='amountCont', parent=self.exportCont, align=carbonui.Align.TOTOP, alignMode=carbonui.Align.CENTERLEFT)
        self.amountLabel = carbonui.TextBody(parent=amountCont, text=GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceTransitAmount'), align=carbonui.Align.CENTERLEFT)
        self.amountEdit = SingleLineEditInteger(parent=amountCont, align=carbonui.Align.CENTERLEFT, setvalue=0, left=100, width=140, OnChange=self.OnExportAmountChanged)
        receiverCont, self.receiverLabel, self.receiverCombo = self.GetComboCont(self.exportCont, 'receiverCont', GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceTransitReceiver'), self.OnSenderReceiverChanged)

    def ConstructImport(self):
        self.importCont = ContainerAutoSize(name='importCont', parent=self, align=carbonui.Align.TOTOP)
        textS1 = GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceTransitSenderNum', senderNum=1)
        s1Cont, self.s1Label, self.s1Combo = self.GetComboCont(self.importCont, 'sender1', textS1, callback=self.OnSenderChanged)
        textS2 = GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceTransitSenderNum', senderNum=2)
        s2Cont, self.s2Label, self.s2Combo = self.GetComboCont(self.importCont, 'sender2', textS2, callback=self.OnSenderChanged)
        textS3 = GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceTransitSenderNum', senderNum=3)
        s3Cont, self.s3Label, self.s3Combo = self.GetComboCont(self.importCont, 'sender3', textS3, callback=self.OnSenderChanged)
        self.importCombos = [self.s1Combo, self.s2Combo, self.s3Combo]

    def AdjustComobWidths(self):
        allLabels = [self.modeLabel,
         self.receiverLabel,
         self.s1Label,
         self.s2Label,
         self.s3Label,
         self.amountLabel,
         self.receiverLabel]
        allInput = [self.modeCombo,
         self.receiverCombo,
         self.s1Combo,
         self.s2Combo,
         self.s3Combo,
         self.amountEdit,
         self.receiverCombo]
        maxLabelWidth = max(60, max([ x.textwidth for x in allLabels ]) + 28)
        for inputElement in allInput:
            inputElement.left = maxLabelWidth

    def OnModeChanged(self, cb, key, value):
        self.LoadEditWnd(value)

    def OnSenderChanged(self, cb, key, value):
        self.UpdateBtnState()
        self.RefreshSenderOptions()

    def OnSenderReceiverChanged(self, cb, key, value):
        self.UpdateBtnState()

    def OnExportAmountChanged(self, *args):
        self.UpdateBtnState()

    def GetComboCont(self, parent, configName, text, callback = None):
        cont = ContainerAutoSize(name=configName, parent=parent, align=carbonui.Align.TOTOP, top=4)
        label = carbonui.TextBody(parent=cont, text=text, align=carbonui.Align.CENTERLEFT)
        combo = Combo(parent=cont, name='%sCombo' % configName, options=[], left=100, align=carbonui.Align.CENTERLEFT, adjustWidth=False, callback=callback)
        return (cont, label, combo)

    def BelongsToWindow(self, elementToCheck):
        for combo in [self.modeCombo,
         self.s1Combo,
         self.s2Combo,
         self.s3Combo,
         self.receiverCombo]:
            optionMenu = getattr(combo, 'optionMenu', None)
            if optionMenu:
                if elementToCheck.IsUnder(combo.optionMenu):
                    return True

        return False

    def LoadEditWnd(self, mode = None):
        if mode is None:
            mode = self.workforceController.GetCurrentMode()
        if mode == workforceConst.MODE_IMPORT:
            self.RefreshSenderOptions()
        elif mode == workforceConst.MODE_EXPORT:
            systemOptions = self.workforceController.GetSystemOptions(False)
            self.receiverCombo.LoadOptions(systemOptions)
        self.ReloadWnd(mode)

    def RefreshSenderOptions(self):
        networkableHubs = self.workforceController.GetNetworkableHubs()
        senderCombos = [self.s1Combo, self.s2Combo, self.s3Combo]
        for eachCombo in senderCombos:
            otherCombValues = filter(None, [ x.GetValue() for x in senderCombos if x != eachCombo ])
            options = self.workforceController.GetSystemOptionsFromNetworkableHubs(True, otherCombValues, networkableHubs)
            eachCombo.LoadOptions(options, eachCombo.GetValue())

    def UpdateBtnState(self):
        selectedMode = self.modeCombo.GetValue()
        currentConfig = self.workforceController.workforceConfiguration
        currentMode = currentConfig.get_mode()
        if currentMode == selectedMode and selectedMode in (workforceConst.MODE_IDLE, workforceConst.MODE_TRANSIT):
            self.applyBtn.enabled = False
            return
        if selectedMode == workforceConst.MODE_EXPORT:
            exportedAmount = self.amountEdit.GetValue()
            if not exportedAmount:
                self.applyBtn.enabled = False
                return
            exportConfig = currentConfig.export_configuration
            if exportConfig:
                destination = self.receiverCombo.GetValue()
                if exportedAmount == exportConfig.amount and destination == exportConfig.destination_system_id:
                    self.applyBtn.enabled = False
                    return
        if selectedMode == workforceConst.MODE_IMPORT:
            importConfig = currentConfig.import_configuration
            if importConfig:
                comboValues = [self.s1Combo.GetValue(), self.s2Combo.GetValue(), self.s3Combo.GetValue()]
                sources = set(filter(None, comboValues))
                if sources == importConfig.source_system_ids:
                    self.applyBtn.enabled = False
                    return
        self.applyBtn.enabled = True

    def ReloadWnd(self, mode):
        self.exportCont.Hide()
        self.importCont.Hide()
        self.modeCombo.SetValue(mode)
        config = self.workforceController.workforceConfiguration
        if mode == workforceConst.MODE_IDLE:
            pass
        elif mode == workforceConst.MODE_EXPORT:
            self.exportCont.Show()
            if config.export_configuration:
                self.amountEdit.SetValue(config.export_configuration.amount)
                destID = config.export_configuration.destination_system_id
                self.receiverCombo.SetValue(destID)
        elif mode == workforceConst.MODE_IMPORT:
            self.importCont.Show()
            if config.import_configuration:
                sourceSystemIDs = filter(None, config.import_configuration.source_system_ids)
                for combo, systemID in zip(self.importCombos, sourceSystemIDs):
                    combo.SetValue(systemID)

                self.RefreshSenderOptions()
        elif mode == workforceConst.MODE_TRANSIT:
            pass
        self.UpdateBtnState()

    def ApplySettings(self, *args):
        mode = self.modeCombo.GetValue()
        if mode == workforceConst.MODE_IDLE:
            newConfig = WorkforceConfiguration(self.workforceController.sovHubID, inactive=True)
        elif mode == workforceConst.MODE_TRANSIT:
            newConfig = WorkforceConfiguration(self.workforceController.sovHubID, transit=True)
        elif mode == workforceConst.MODE_IMPORT:
            importConfig = self._GetImportConfig()
            newConfig = WorkforceConfiguration(self.workforceController.sovHubID, import_configuration=importConfig)
        elif mode == workforceConst.MODE_EXPORT:
            exportConfig = self._GetExportConfig()
            newConfig = WorkforceConfiguration(self.workforceController.sovHubID, export_configuration=exportConfig)
        else:
            raise RuntimeError('Invalid mode = %s' % mode)
        if self.ChangeIsConfirmed(self.workforceController.workforceConfiguration, newConfig):
            self.workforceController.SetWorkforceConfiguration(newConfig)

    def _GetImportConfig(self):
        sourceIDs = set()
        for combo in [self.s1Combo, self.s2Combo, self.s3Combo]:
            val = combo.GetValue()
            if val:
                sourceIDs.add(val)

        importConfig = WorkforceImportConfiguration(self.workforceController.sovHubID, sourceIDs)
        return importConfig

    def _GetExportConfig(self):
        amount = self.amountEdit.GetValue()
        systemID = self.receiverCombo.GetValue()
        exportConfig = WorkforceExportConfiguration(self.workforceController.sovHubID, systemID, amount)
        return exportConfig

    def ChangeIsConfirmed(self, oldConfig, newConfig):
        oldMode = oldConfig.get_mode()
        newMode = newConfig.get_mode()
        infoText = confirmText = ''
        systemName = cfg.evelocations.Get(self.workforceController.solarSystemID).name
        if oldMode == workforceConst.MODE_TRANSIT:
            infoText = GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceChangeFromTransit', systemName=systemName)
        if oldMode == workforceConst.MODE_IMPORT:
            infoText = GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceChangeFromImport', systemName=systemName)
        if oldMode == workforceConst.MODE_EXPORT:
            infoText = GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceChangeFromExport', systemName=systemName)
        if oldMode == workforceConst.MODE_IDLE:
            infoText = GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceChangeFromInactive', systemName=systemName)
        if newMode == workforceConst.MODE_TRANSIT:
            confirmText = GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceChangeToTransit', systemName=systemName)
        if newMode == workforceConst.MODE_IMPORT:
            confirmText = GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceChangeToImport', systemName=systemName)
        if newMode == workforceConst.MODE_EXPORT:
            confirmText = GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceChangeToExport', systemName=systemName)
        if newMode == workforceConst.MODE_IDLE:
            confirmText = GetByLabel('UI/Sovereignty/SovHub/HubWnd/WorkforceChangeToInactive', systemName=systemName)
        if eve.Message('ConfirmWorkforceChanged', {'infoText': infoText,
         'confirmText': confirmText}, uiconst.YESNO) == uiconst.ID_YES:
            return True
        return False
