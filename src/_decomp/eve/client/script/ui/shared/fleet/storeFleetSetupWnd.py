#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\storeFleetSetupWnd.py
import eveicon
import localization
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control import eveLabel
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from carbonui.button.group import ButtonGroup
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
import evefleet.fleetSetupConst as fsConst
from evefleet import MAX_MEMBERS_IN_FLEET
CONTENT_WIDTH = 360

class StoreFleetSetupWnd(Window):
    default_width = CONTENT_WIDTH
    default_height = 300
    default_windowID = 'StoreFleetSetupWnd'
    default_captionLabelPath = 'UI/Fleet/FleetWindow/StoreFleetSetup'

    def ApplyAttributes(self, attributes):
        super(StoreFleetSetupWnd, self).ApplyAttributes(attributes)
        self.maxFleetSizeCb = None
        self.defaultSquadCb = None
        self.currentFleetInfo = attributes.get('currentFleetInfo')
        self.funcValidator = self.CheckName
        self.ConstructLayout(self.currentFleetInfo.oldSetupName)

    def ConstructLayout(self, oldSetupName):
        self._main_cont = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, callback=self._on_main_cont_size_changed, only_use_callback_when_size_changes=True)
        if oldSetupName:
            label = localization.GetByLabel('UI/Fleet/FleetWindow/StoreFleetSetupTextWithLastLoaded', oldFleetSetupName=oldSetupName)
        else:
            label = localization.GetByLabel('UI/Fleet/FleetWindow/StoreFleetSetupText')
        eveLabel.EveLabelSmall(name='nameLabel', parent=self._main_cont, align=uiconst.TOTOP, text=label)
        self.newName = SingleLineEditText(name='namePopup', parent=self._main_cont, align=uiconst.TOTOP, maxLength=15, OnReturn=self.Confirm)
        uicore.registry.SetFocus(self.newName)
        hint = localization.GetByLabel('UI/Fleet/FleetWindow/CurrentMotdHint', motd=self.currentFleetInfo.currentMotd)
        self.motdCb = Checkbox(parent=self._main_cont, align=uiconst.TOTOP, top=16, text=localization.GetByLabel('UI/Fleet/FleetWindow/IncludeMotd'), settingsKey='motdCb', checked=False, hint=hint)
        hint = localization.GetByLabel('UI/Fleet/FleetWindow/CurrentFreeMoveHint', value=self.currentFleetInfo.currentOptions.isFreeMove)
        self.freeMoveCb = Checkbox(parent=self._main_cont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Fleet/FleetWindow/IncludeFreeMoveSetting'), settingsKey='freeMoveCb', checked=False, hint=hint)
        currentMaxSize = self.currentFleetInfo.currentMaxSize
        if currentMaxSize != MAX_MEMBERS_IN_FLEET:
            hint = localization.GetByLabel('UI/Fleet/FleetWindow/CurrentFleetMaxSize', value=currentMaxSize)
            self.maxFleetSizeCb = Checkbox(parent=self._main_cont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Fleet/FleetWindow/IncludeMaxSize'), settingsKey='maxFleetSizeCb', checked=False, hint=hint)
        if self.currentFleetInfo.currentDefaultSquadName:
            hint = localization.GetByLabel('UI/Fleet/FleetWindow/CurrentDefaultSquadHint', value=self.currentFleetInfo.currentDefaultSquadName)
            self.defaultSquadCb = Checkbox(parent=self._main_cont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Fleet/FleetWindow/IncludeDefaultSquad'), settingsKey='defaultSquadCb', checked=False, hint=hint)
        buttons = ButtonGroup(parent=self._main_cont, align=uiconst.TOTOP, top=16)
        buttons.AddButton(label=localization.GetByLabel('UI/Common/Buttons/OK'), func=self.Confirm, isDefault=True)
        buttons.AddButton(label=localization.GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel)

    def CheckName(self, name, *args):
        name = self.newName.GetValue()
        if not len(name) or len(name) and len(name.strip()) < 1:
            return localization.GetByLabel('UI/Common/PleaseTypeSomething')

    def Confirm(self, *args):
        newName = self.newName.GetValue()
        storeMotd = self.motdCb.GetValue()
        storeFreeMove = self.freeMoveCb.GetValue()
        storeMaxSize = self.maxFleetSizeCb.GetValue() if self.maxFleetSizeCb else False
        storeDefaultSquad = self.defaultSquadCb.GetValue() if self.defaultSquadCb else False
        error = self.funcValidator(newName)
        if error:
            eve.Message('CustomInfo', {'info': error})
        else:
            results = StoreFleetSetupResults()
            results.setupName = newName
            results.storeMotd = storeMotd
            results.storeFreeMove = storeFreeMove
            results.storeDefaultSquad = storeDefaultSquad
            results.storeMaxSize = storeMaxSize
            self.result = results
            self.SetModalResult(1)

    def Cancel(self, *args):
        self.result = None
        self.SetModalResult(0)

    def _on_main_cont_size_changed(self):
        content_height = self._main_cont.height
        width, height = self.GetWindowSizeForContentSize(width=CONTENT_WIDTH, height=content_height)
        self.SetFixedWidth(width)
        self.SetFixedHeight(height)


class StoredFleetSetupListWnd(Window):
    default_width = 360
    default_height = 300
    default_minSize = (default_width, default_height)
    default_windowID = 'StoredFleetSetupListWnd'
    __notifyevents__ = ['OnFleetSetupChanged']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.fleetSvc = attributes.fleetSvc
        self.SetCaption(localization.GetByLabel('UI/Fleet/FleetWindow/SetupsOverview'))
        self.scroll = ScrollContainer(parent=self.sr.main)
        self.LoadSetups()

    def LoadSetups(self):
        fleetSetups = self.fleetSvc.GetFleetSetups()
        orderedFleetSetups = [ (fleetSetupName, setup) for fleetSetupName, setup in fleetSetups.iteritems() ]
        orderedFleetSetups.sort()
        for fleetSetupName, setup in orderedFleetSetups:
            StoredFleetSetupEntry(parent=self.scroll, name=fleetSetupName, setupInfo=setup, settingConfigName=fleetSetupName, fleetSvc=self.fleetSvc)

    def OnFleetSetupChanged(self):
        self.scroll.Flush()
        self.LoadSetups()


class StoredFleetSetupEntry(Container):
    default_height = 30
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    disabledOpacity = 0.3

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fleetSvc = attributes.fleetSvc
        self.setupInfo = setupInfo = attributes.get('setupInfo', {})
        motd = setupInfo.get(fsConst.FS_MOTD, None)
        isFreeMove = setupInfo.get(fsConst.FS_IS_FREE_MOVE, None)
        settingName = setupInfo.get(fsConst.FS_NAME)
        self.settingConfigName = attributes.get('settingConfigName', settingName)
        nameLabel = eveLabel.EveLabelSmall(name='nameLabel', parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=settingName, padLeft=8)
        iconCont = ContainerAutoSize(parent=self, height=16, align=uiconst.CENTERRIGHT, width=54, padRight=8)
        ButtonIcon(parent=iconCont, texturePath=eveicon.refresh, width=16, padLeft=4, align=uiconst.TORIGHT, func=self.LoadSetup, hint=localization.GetByLabel('UI/Fleet/FleetWindow/LoadFleetSetup'))
        ButtonIcon(parent=iconCont, texturePath=eveicon.trashcan, width=16, padLeft=4, align=uiconst.TORIGHT, func=self.DeleteSetup, hint=localization.GetByLabel('UI/Common/Buttons/Delete'))
        if motd is not None:
            sprite = Sprite(parent=iconCont, width=16, padLeft=4, align=uiconst.TORIGHT, texturePath='res:/ui/texture/icons/6_64_7.png')
            sprite.hint = localization.GetByLabel('UI/Chat/ChannelMotd', motd=motd)
            if not motd:
                sprite.opacity = self.disabledOpacity
        if isFreeMove is not None:
            sprite = Sprite(parent=iconCont, width=16, padLeft=4, align=uiconst.TORIGHT, texturePath='res:/ui/texture/icons/44_32_32.png')
            if isFreeMove:
                sprite.hint = localization.GetByLabel('UI/Fleet/FleetWindow/FreeMoveOn')
            else:
                sprite.hint = localization.GetByLabel('UI/Fleet/FleetWindow/FreeMoveOff')
                sprite.opacity = self.disabledOpacity
        self.underlay = ListEntryUnderlay(bgParent=self)

    def DeleteSetup(self):
        self.fleetSvc.DeleteFleetSetup(setupName=self.settingConfigName)

    def LoadSetup(self):
        self.fleetSvc.LoadSetup(self.settingConfigName)

    def GetHint(self):
        return self.GetMouseOver(self.setupInfo)

    def GetMouseOver(self, setup):
        allWingsInfo = setup[fsConst.FS_WINGS_INFO]
        textList = []
        unnamedText = localization.GetByLabel('UI/Fleet/FleetWindow/UnnamedSquad')
        for wingInfo in allWingsInfo.itervalues():
            textList.append('* %s' % wingInfo[fsConst.FS_WING_NAME])
            textList += [ '  - %s' % (squadName or unnamedText) for squadName in wingInfo[fsConst.FS_SQUAD_NAMES] ]

        text = '<br>'.join(textList)
        return text

    def OnMouseEnter(self, *args):
        super(StoredFleetSetupEntry, self).OnMouseEnter(*args)
        self.underlay.hovered = True

    def OnMouseExit(self, *args):
        super(StoredFleetSetupEntry, self).OnMouseExit(*args)
        self.underlay.hovered = False


class StoreFleetSetupResults(object):

    def __init__(self):
        self.setupName = ''
        self.storeMotd = False
        self.storeFreeMove = False
        self.storeDefaultSquad = False
        self.storeMaxSize = False
