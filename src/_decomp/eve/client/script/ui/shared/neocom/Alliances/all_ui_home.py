#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\Alliances\all_ui_home.py
import sys
import carbonui
from carbon.common.script.util.format import FormatUrl
from carbonui import Align
from carbonui.control.scroll import Scroll
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.radioButton import RadioButton
from eve.client.script.ui.control.entries.label_text import LabelTextSides, LabelTextSidesMoreInfo, LabelTextTop
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
import blue
import uthread
from eve.client.script.ui.control import eveLabel
import log
import carbonui.const as uiconst
import localization
from carbonui.uicore import uicore
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.shared.neocom.corporation.corp_ui_bulletins import BulletinsOrder
from eve.common.lib.appConst import allianceNameMaxLenSR, allianceNameMaxLenTQ
from eveprefs import boot
from eveservices.menu import GetMenuService
from evewar.warPermitUtil import GetLabelPathForAllowWar
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from localization import GetByLabel
from menucheckers import SessionChecker
ICON_SIZE = 128

class FormAlliancesHome(Container):
    is_loaded = False
    scroll = None

    def Load(self, *args):
        if not self.is_loaded:
            self.is_loaded = True
            self.top_cont = ContainerAutoSize(name='top_cont', align=Align.TOTOP, parent=self, padBottom=16)
            self.reconstruct_top_cont()
            self.toolbarContainer = ContainerAutoSize(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
            self.construct_button_group()
            self.scroll = Scroll(parent=self)
            corpUISignals.on_alliance_changed.connect(self.OnAllianceChanged)
        if session.allianceid is None:
            corpNotInAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CorporationNotInAlliance', corpName=cfg.eveowners.Get(session.corpid).ownerName)
            self.scroll.Load(fixedEntryHeight=19, contentList=[], noContentHint=corpNotInAllianceLabel)
        else:
            self.LoadScroll()

    def reconstruct_top_cont(self):
        self.top_cont.Flush()
        if session.allianceid is None:
            return
        OwnerIcon(ownerID=session.allianceid, parent=self.top_cont, align=uiconst.CENTERLEFT, pos=(0,
         0,
         ICON_SIZE,
         ICON_SIZE))
        caption = carbonui.TextHeadline(text=cfg.eveowners.Get(session.allianceid).ownerName, parent=self.top_cont, align=uiconst.CENTERLEFT, left=ICON_SIZE + 8)
        InfoIcon(typeID=const.typeCorporation, itemID=session.allianceid, parent=self.top_cont, left=caption.left + caption.width + 6, top=2, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)

    def construct_button_group(self):
        buttons = []
        if session.allianceid is None:
            corporation = sm.GetService('corp').GetCorporation(session.corpid)
            if corporation.ceoID == session.charid:
                buttons.append(Button(label=localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreateAlliance'), func=self.CreateAllianceForm))
        elif SessionChecker(session, None).IsCorpDirector():
            buttons.append(Button(label=localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/EditAlliance'), func=self.EditAllianceForm, enabled=not IsContentComplianceControlSystemActive(sm.GetService('machoNet'))))
            buttons.append(Button(label=localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/DeclareWar'), func=self.DeclareWarForm))
        if len(buttons):
            ButtonGroup(parent=self.toolbarContainer, align=uiconst.TOBOTTOM, buttons=buttons, padTop=8)

    def LoadScroll(self):
        if not self.scroll:
            return
        try:
            scrolllist = []
            self.ShowMyAllianceDetails(scrolllist)
            self.scroll.Load(contentList=scrolllist)
        except:
            log.LogException()
            sys.exc_clear()

    def ShowMyAllianceDetails(self, scrolllist):
        scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.ShowDetails,
         'label': localization.GetByLabel('UI/Common/Details'),
         'groupItems': None,
         'id': ('alliance', 'details'),
         'tabs': [],
         'state': 'locked',
         'showicon': 'hide'}))
        uicore.registry.SetListGroupOpenState(('alliance', 'details'), 1)

    def SetHint(self, hintstr = None):
        if self.scroll:
            self.scroll.ShowHint(hintstr)

    def ShowDetails(self, *args):
        scrolllist = []
        hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/NoDetailsFound')
        if self is None or self.destroyed:
            log.LogInfo('ShowMembers Destroyed or None')
            hint = ''
        elif session.allianceid is None:
            hint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CorporationNotInAllianceATM', corpName=cfg.eveowners.Get(session.corpid).ownerName)
        else:
            rec = sm.GetService('alliance').GetAlliance()
            owners = [rec.allianceID, rec.creatorCorpID, rec.creatorCharID]
            if rec.executorCorpID is not None:
                owners.append(rec.executorCorpID)
            if len(owners):
                cfg.eveowners.Prime(owners)
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/AllianceName')
            text = cfg.eveowners.Get(rec.allianceID).ownerName
            scrolllist.append(GetFromClass(LabelTextSides, {'line': 1,
             'label': label,
             'text': text,
             'typeID': const.typeAlliance,
             'itemID': rec.allianceID}))
            executor = cfg.eveowners.GetIfExists(rec.executorCorpID)
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/Executor')
            if executor is not None:
                params = {'line': 1,
                 'label': label,
                 'text': executor.ownerName,
                 'typeID': const.typeCorporation,
                 'itemID': rec.executorCorpID}
            else:
                params = {'line': 1,
                 'label': label,
                 'text': '-'}
            scrolllist.append(GetFromClass(LabelTextSides, params))
            label = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/ShortName')
            params = {'line': 1,
             'label': label,
             'text': rec.shortName}
            scrolllist.append(GetFromClass(LabelTextSides, params))
            label = localization.GetByLabel('UI/Common/URL')
            if rec.url is not None:
                params = {'line': 1,
                 'label': label,
                 'text': '<url=%s>%s</url>' % (rec.url, rec.url)}
            scrolllist.append(GetFromClass(LabelTextSides, params))
            scrolllist.append(GetFromClass(LabelTextTop, {'line': 1,
             'label': localization.GetByLabel('UI/Common/Description'),
             'text': rec.description}))
            scrolllist.append(GetFromClass(LabelTextSides, {'line': 1,
             'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreatedByCorporation'),
             'text': cfg.eveowners.Get(rec.creatorCorpID).ownerName,
             'typeID': const.typeCorporation,
             'itemID': rec.creatorCorpID}))
            scrolllist.append(GetFromClass(LabelTextSides, {'line': 1,
             'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreatedBy'),
             'text': cfg.eveowners.Get(rec.creatorCharID).ownerName,
             'typeID': const.typeCharacter,
             'itemID': rec.creatorCharID}))
            scrolllist.append(GetFromClass(LabelTextSides, {'line': 1,
             'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/Dictatorial'),
             'text': localization.GetByLabel('UI/Common/Buttons/Yes') if rec.dictatorial else localization.GetByLabel('UI/Common/Buttons/No')}))
            scrolllist.append(GetFromClass(LabelTextSidesMoreInfo, {'line': 1,
             'label': localization.GetByLabel('UI/WarPermit/WarPermitStatus'),
             'text': localization.GetByLabel(GetLabelPathForAllowWar(rec.allowWar)),
             'moreInfoHint': localization.GetByLabel('UI/WarPermit/WarPermitExplanation')}))
        self.scroll.adjustableColumns = 1
        self.scroll.sr.id = 'alliances_members'
        if not scrolllist:
            self.SetHint(hint)
        return scrolllist

    def GetTabHint(self):
        eHint = ''
        if session.allianceid is None:
            corporation = sm.GetService('corp').GetCorporation(session.corpid)
            if corporation.ceoID != session.charid:
                eHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CEODeclareWarOnlyHint')
        if not SessionChecker(session, None).IsCorpDirector():
            eHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/DirectorsCanEdit')
        return eHint

    def OnAllianceChanged(self, allianceID, change):
        if session.allianceid != allianceID:
            return
        if self.state != uiconst.UI_NORMAL:
            return
        if self.scroll is None:
            return
        self.ShowDetails()
        self.reconstruct_top_cont()

    def CreateAllianceForm(self, *args):
        wnd = CreateAllianceWnd.Open()

    def EditAllianceForm(self, *args):
        wnd = EditAllianceWnd.Open()

    def DeclareWarForm(self, *args):
        GetMenuService().DeclareWar()


class FormAlliancesBulletins(Container):
    is_loaded = False

    def Load(self, *args):
        if not self.is_loaded:
            self.is_loaded = True
            self.construct_layout()
        if session.allianceid is not None:
            self.LoadBulletins()

    def construct_layout(self):
        self.toolbarContainer = ContainerAutoSize(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
        self.construct_button_group()
        bulletinParent = Container(name='bulletinParent', parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        if session.allianceid and SessionChecker(session, None).IsCorpDirector():
            self.sr.sortOrderCont = Container(name='sortOrderCont', parent=bulletinParent, align=uiconst.TOTOP, height=20)
            UtilMenu(menuAlign=uiconst.TOPRIGHT, parent=self.sr.sortOrderCont, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/Icons/77_32_49.png', pos=(4, 0, 20, 20), GetUtilMenu=self.GetSortOrderMenu, iconSize=24)
        Container(name='push', parent=bulletinParent, align=uiconst.TOLEFT, width=const.defaultPadding)
        self.messageArea = Scroll(parent=bulletinParent)

    def construct_button_group(self):
        btns = []
        if session.allianceid is None:
            corporation = sm.GetService('corp').GetCorporation(session.corpid)
            if corporation.ceoID == session.charid:
                createAllianceLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/CreateAlliance')
                btns.append([createAllianceLabel,
                 self.CreateAllianceForm,
                 None,
                 None])
        elif SessionChecker(session, None).IsCorpDirector() and not IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
            addBulletinLabel = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/AddBulletin')
            btns.append([addBulletinLabel,
             self.AddBulletin,
             None,
             None])
        if len(btns):
            ButtonGroup(btns=btns, parent=self.toolbarContainer)

    def AddBulletin(self, *args):
        sm.GetService('corp').EditBulletin(None, isAlliance=True)

    def LoadBulletins(self):
        scrollEntries = sm.GetService('corp').GetBulletinEntries(isAlliance=True)
        if self.sr.sortOrderCont:
            self.sr.sortOrderCont.display = len(scrollEntries) > 1
        self.messageArea.LoadContent(contentList=scrollEntries, noContentHint=localization.GetByLabel('UI/Corporations/BaseCorporationUI/NoBulletins'))

    def GetSortOrderMenu(self, menuParent):
        cont = menuParent.AddContainer(align=uiconst.TOTOP, height=50, padding=const.defaultPadding)
        bulletins = sm.GetService('corp').GetBulletins(True)
        orderCont = BulletinsOrder(parent=cont, align=uiconst.TOTOP, bulletins=bulletins, saveFunc=self.SaveSortOrder)
        orderContContentWidth = orderCont.GetContentWidth()
        cont.GetEntryWidth = lambda mc = cont: orderContContentWidth

    def SaveSortOrder(self, sortOrder):
        sm.GetService('alliance').UpdateBulletinOrder(sortOrder)
        self.LoadBulletins()


class CreateAllianceWnd(Window):
    __guid__ = 'form.CreateAllianceWnd'
    default_fixedWidth = 350
    default_fixedHeight = 380
    default_windowID = 'CreateAllianceWindow'
    default_captionLabelPath = 'UI/Corporations/CorporationWindow/Alliances/Home/CreateAlliance'

    def ApplyAttributes(self, attributes):
        super(CreateAllianceWnd, self).ApplyAttributes(attributes)
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        self.ConstructLayout()

    def ConstructLayout(self):
        cont = Container(parent=self.sr.main, align=uiconst.TOALL)
        if boot.region == 'optic':
            nameValue = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/NameAlliance', allianceName=cfg.eveowners.Get(session.corpid).ownerName)
        else:
            nameValue = localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/NameAlliance', languageID=localization.const.LOCALE_SHORT_ENGLISH, allianceName=cfg.eveowners.Get(session.corpid).ownerName)
        maxLength = allianceNameMaxLenSR if boot.region == 'optic' else allianceNameMaxLenTQ
        self.nameEdit = SingleLineEditText(parent=cont, label=localization.GetByLabel('UI/Common/Name'), align=uiconst.TOTOP, maxLength=maxLength, padTop=16, setvalue=nameValue)
        shortNameCont = Container(parent=cont, align=uiconst.TOTOP, height=Button.default_height, padTop=24)
        Button(parent=shortNameCont, align=uiconst.TORIGHT, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/SuggestCommand'), func=self.GetSuggestedTickerNames, padLeft=4)
        self.shortNameEdit = SingleLineEditText(parent=shortNameCont, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Home/ShortName'), align=uiconst.TOTOP, maxLength=5)
        self.urlEdit = SingleLineEditText(parent=cont, label=localization.GetByLabel('UI/Common/URL'), align=uiconst.TOTOP, maxLenght=2048, padTop=24)
        eveLabel.EveLabelSmall(parent=cont, text=localization.GetByLabel('UI/Common/Description'), height=16, align=uiconst.TOTOP, padTop=8)
        self.descriptionEdit = EditPlainText(parent=cont, align=uiconst.TOALL, maxLength=5000, padBottom=8)

    def GetSuggestedTickerNames(self, *args):
        wnd = SetShortNameWnd.Open(allianceName=self.nameEdit.GetValue())
        if wnd.ShowModal() == 1:
            retval = wnd.result
        else:
            retval = None
        if retval is None:
            return
        self.shortNameEdit.SetValue(retval)

    def Confirm(self, *args):
        allianceName = self.nameEdit.GetValue()
        shortName = self.shortNameEdit.GetValue()
        url = self.urlEdit.GetValue()
        description = self.descriptionEdit.GetValue()
        uthread.new(self.Confirm_thread, allianceName, shortName, description, url)

    def Confirm_thread(self, allianceName, shortName, description, url):
        sm.GetService('sessionMgr').PerformSessionChange('alliance.addalliance', sm.GetService('corp').CreateAlliance, allianceName, shortName, description, url)
        self.Close()

    def Cancel(self, *args):
        self.Close()


class SetShortNameWnd(Window):
    __guid__ = 'form.SetShortNameWnd'
    default_fixedWidth = 300
    default_windowID = 'SetShortNameWindow'
    default_captionLabelPath = 'UI/Corporations/CorporationWindow/Alliances/Home/SelectShortName'
    default_isMinimizable = False

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.allianceName = attributes.get('allianceName')
        self.checkBoxes = []
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        self.ConstructLayout()
        self.UpdateFixedHeight()

    def ConstructLayout(self):
        self.checkBoxCont = ContainerAutoSize(parent=self.sr.main, name='checkBoxCont', align=uiconst.TOTOP, callback=self.UpdateFixedHeight)
        shortNames = sm.GetService('corp').GetSuggestedAllianceShortNames(self.allianceName)
        checked = True
        for shortNameRow in shortNames:
            shortName = shortNameRow.shortName
            if shortName is None:
                continue
            checkBox = RadioButton(text=shortName, parent=self.checkBoxCont, settingsKey='shortNames', retval=shortName, checked=checked, groupname='state', align=uiconst.TOTOP, height=19)
            self.checkBoxes.append(checkBox)
            checked = False

    def UpdateFixedHeight(self, *args):
        _, height = self.GetWindowSizeForContentSize(height=self.checkBoxCont.height + self.sr.bottom.height)
        self.SetFixedHeight(height)

    def Confirm(self, *args):
        self.result = self.checkBoxes[0].GetGroupValue()
        self.SetModalResult(1)

    def Cancel(self, *args):
        self.result = None
        self.SetModalResult(0)


class EditAllianceWnd(Window):
    __guid__ = 'form.EditAllianceWnd'
    default_width = 420
    default_height = 300
    default_minSize = (default_width, default_height)
    default_windowID = 'EditAllianceWindow'
    default_captionLabelPath = 'UI/Corporations/CorporationWindow/Alliances/Home/UpdateAlliance'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.ConstructLayout()

    def ConstructLayout(self):
        alliance = sm.GetService('alliance').GetAlliance()
        self.sr.bottom = ContainerAutoSize(parent=self.content, align=uiconst.TOBOTTOM, padTop=16)
        self.DefineButtons(uiconst.OKCANCEL, okFunc=self.Confirm, cancelFunc=self.Cancel)
        eveLabel.EveLabelSmall(parent=self.content, align=uiconst.TOTOP, padTop=0, padBottom=4, text=localization.GetByLabel('UI/Common/URL'))
        self.urlEdit = SingleLineEditText(parent=self.content, align=uiconst.TOTOP, maxLength=2048, setvalue=alliance.url)
        eveLabel.EveLabelSmall(parent=self.content, align=uiconst.TOTOP, padding=(0, 16, 0, 4), text=localization.GetByLabel('UI/Common/Description'))
        self.descriptionEdit = EditPlainText(parent=self.content, align=uiconst.TOALL, maxLength=5000, setvalue=alliance.description)

    def Confirm(self, *args):
        url = self.urlEdit.GetValue()
        if url:
            url = FormatUrl(url)
        description = self.descriptionEdit.GetValue()
        self.result = (url, description)
        sm.GetService('alliance').UpdateAlliance(description, url)
        sm.GetService('corpui').ResetWindow(bShowIfVisible=1)
        self.Close()

    def Cancel(self, *args):
        self.Close()


class PrimeTimeHourEntryHorizontal(LabelTextSides):
    __guid__ = 'listentry.PrimeTimeHourEntryHorizontal'

    def Startup(self, *args):
        LabelTextSides.Startup(self, args)
        self.primeTimeInfo = None

    def Load(self, node):
        self.primeTimeInfo = node.primeTimeInfo
        text, infoText = self.GetText()
        node.text = text
        LabelTextSides.Load(self, node)
        if infoText:
            self.sr.infoLabel = EveLabelSmall(text=infoText, parent=self, top=6, state=uiconst.UI_DISABLED, align=uiconst.CENTERRIGHT, left=8)
            self.sr.text.top = -6

    def GetCurrentPrimeHour(self):
        currentPrimeHour = 0
        if self.primeTimeInfo and self.primeTimeInfo.currentPrimeHour is not None:
            currentPrimeHour = self.primeTimeInfo.currentPrimeHour
        return currentPrimeHour

    def GetText(self):
        infoText = ''
        if self.primeTimeInfo is None or self.primeTimeInfo.currentPrimeHour is None:
            text = localization.GetByLabel('UI/Common/Unknown')
        else:
            newPrimeHour = self.primeTimeInfo.newPrimeHour
            validAfter = self.primeTimeInfo.newPrimeHourValidAfter
            now = blue.os.GetWallclockTime()
            if newPrimeHour and now < validAfter:
                text = localization.GetByLabel('UI/Sovereignty/VulnerabilityTimerChangesTime', hour=self.primeTimeInfo.currentPrimeHour, newHour=self.primeTimeInfo.newPrimeHour)
                infoText = localization.GetByLabel('UI/Sovereignty/VulnerabilityTimerChangesInfo', validAfterDate=self.primeTimeInfo.newPrimeHourValidAfter)
            else:
                currentPrimeHour = self.GetCurrentPrimeHour()
                text = localization.GetByLabel('UI/Sovereignty/VulnerabilityTime', hour=currentPrimeHour)
        return (text, infoText)
