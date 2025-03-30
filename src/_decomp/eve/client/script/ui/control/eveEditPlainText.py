#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\eveEditPlainText.py
import agency.client
import carbonui.const as uiconst
import corporation.client
import crimewatch.util
import eve.client.script.ui.shared.fittingScreen.fittingUtil as fittingUtil
import eveformat
import evelink.client
import evetypes
import evewar.client
import localization
import sharedSettings.client
import shipfitting.client
from carbon.common.script.util import commonutils
from carbonui.control.editPlainText import EditPlainTextCore
from carbonui.uicore import uicore
from characterskills.client import format_certificate_url
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from carbonui.control.button import Button
from carbonui.decorative.inputUnderlay import InputUnderlay
from eve.client.script.ui.podGuide.link import format_pod_guide_url
from eve.client.script.ui.shared.bookmarks.link import format_bookmark_folder_url
from eve.client.script.ui.shared.killReportUtil import format_kill_report_url
from eve.client.script.ui.shared.neocom.contracts.link import format_contract_url
from eve.client.script.ui.shared.planet.colonyTemplateWindow import format_pi_template_url
from eve.client.script.ui.shared.pointerTool.link import format_help_pointer_url
from eve.client.script.ui.util import searchOld, searchUtil, uix
from eve.common.lib import appConst as const
from eve.common.script.search.const import ResultType
from eve.common.script.sys import idCheckers
from eveagent.client import format_fleet_mission_url
from eveexceptions import UserError
from menu import MenuLabel
from overviewPresets.client.link import overview_preset_link
from ownergroups.client import access_group_link

class EditPlainText(EditPlainTextCore):
    __guid__ = 'uicls.EditPlainText'
    default_align = uiconst.TOALL
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    allowPrivateDrops = 0
    default_hasUnderlay = True

    def Prepare_Underlay_(self):
        if getattr(self, 'hasUnderlay', self.default_hasUnderlay):
            self.sr.underlay = InputUnderlay(name='background', bgParent=self, align=uiconst.TOALL)

    def OnDropDataDelegate(self, node, nodes):
        EditPlainTextCore.OnDropDataDelegate(self, node, nodes)
        if self.readonly:
            return
        uicore.registry.SetFocus(self)
        for entry in nodes:
            guid = getattr(entry, '__guid__', None)
            if getattr(entry, 'get_link', None):
                if not self.allowPrivateDrops and getattr(entry, 'is_private', False):
                    return
                link = entry.get_link()
                if link:
                    self.CheckLinkFits(entry)
                    self.AddLink(link.text, link.url)
                    self.CheckHintText()
            if guid in AllUserEntries():
                link = evelink.character_link(entry.charID, entry.info.name)
                self.AddLink(link.text, link.url)
            elif guid == 'listentry.CorpAllianceEntry':
                link = evelink.type_link(entry.typeID, entry.itemID, entry.name)
                self.AddLink(link.text, link.url)
            elif guid in ('listentry.InvItem', 'xtriui.InvItem', 'xtriui.ShipUIModule', 'listentry.InvAssetItem'):
                itemID = None
                if not isinstance(entry.rec.itemID, tuple):
                    itemID = entry.rec.itemID
                if idCheckers.IsShipType(entry.rec.typeID):
                    link = evelink.ship_link(entry.rec.typeID, itemID, entry.rec.ownerID if entry.rec.singleton else None, entry.name)
                else:
                    link = evelink.type_link(entry.rec.typeID, itemID, entry.name)
                self.AddLink(link.text, link.url)
            elif guid == 'listentry.VirtualAgentMissionEntry':
                link = format_fleet_mission_url(entry.agentID, entry.charID)
                self.AddLink(entry.label, link)
            elif guid == 'listentry.CertEntry':
                label = entry.genericDisplayLabel or entry.label
                link = format_certificate_url(entry.certID, entry.level)
                self.AddLink(label, link)
            elif guid and guid.startswith('listentry.ContractEntry'):
                url = format_contract_url(entry.solarSystemID, entry.contractID)
                self.AddLink(entry.name.replace('&gt;', '>'), url)
            elif guid in ('xtriui.ListSurroundingsBtn', 'listentry.LocationTextEntry', 'listentry.LabelLocationTextTop', 'listentry.LocationGroup', 'listentry.LocationSearchItem'):
                if not entry.typeID and not entry.itemID:
                    return
                displayLabel = getattr(entry, 'genericDisplayLabel', None) or entry.label
                link = evelink.type_link(entry.typeID, entry.itemID, displayLabel)
                self.AddLink(link.text, link.url)
            elif guid == 'listentry.FittingEntry':
                PADDING = 12
                link = shipfitting.client.format_fitting_url(entry.fitting)
                roomLeft = self.RoomLeft()
                if roomLeft is not None:
                    roomLeft = roomLeft - PADDING
                    if len(link) >= roomLeft:
                        if roomLeft < 14:
                            raise UserError('LinkTooLong')
                        if eve.Message('ConfirmTruncateLink', {'numchar': len(link),
                         'maxchar': roomLeft}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                            return
                        link = link[:roomLeft]
                fittingName = eveformat.simple_html_unescape(entry.fitting.name)
                self.AddLink(fittingName, link)
            elif guid in ('listentry.GenericMarketItem', 'listentry.QuickbarItem', 'uicls.GenericDraggableForTypeID', 'listentry.DroneEntry', 'listentry.SkillTreeEntry'):
                link_text = getattr(entry, 'label', None) or getattr(entry, 'text', '')
                link = evelink.type_link(entry.typeID, link_text=link_text)
                self.AddLink(link.text, link.url)
            elif guid == 'TextLink':
                self.AddLink(entry.displayText, entry.url)
            elif guid in ('listentry.KillMail', 'listentry.KillMailCondensed', 'listentry.WarKillEntry'):
                killmail = entry.mail
                hashValue = crimewatch.util.GetKillReportHashValue(killmail)
                if idCheckers.IsCharacter(killmail.victimCharacterID):
                    victimName = cfg.eveowners.Get(killmail.victimCharacterID).name
                    shipName = evetypes.GetName(killmail.victimShipTypeID)
                    label = localization.GetByLabel('UI/Corporations/Wars/Killmails/KillLinkCharacter', charName=victimName, typeName=shipName)
                else:
                    shipName = evetypes.GetName(killmail.victimShipTypeID)
                    label = localization.GetByLabel('UI/Corporations/Wars/Killmails/KillLinkStructure', typeName=shipName)
                link = format_kill_report_url(entry.mail.killID, hashValue)
                self.AddLink(label, link)
            elif guid == 'listentry.WarEntry':
                link = evewar.client.war_report_link(war_id=entry.war.warID, attacker_id=entry.war.declaredByID, defender_id=entry.war.againstID)
                self.AddLink(link.text, link.url)
            elif guid == 'listentry.RecruitmentEntry':
                link = corporation.client.recruitment_ad_link(corp_id=entry.advert.corporationID, ad_id=entry.advert.adID, title=entry.adTitle)
                self.AddLink(link.text, link.url)
            elif guid == 'listentry.DirectionalScanResults':
                link = evelink.type_link(entry.typeID, entry.itemID, entry.typeName)
                self.AddLink(link.text, link.url)
            elif guid in ('listentry.SkillEntry', 'listentry.SkillQueueSkillEntry'):
                link = evelink.type_link(entry.invtype)
                self.AddLink(link.text, link.url)
            elif guid in ('listentry.Item', 'listentry.ContractItemSelect', 'listentry.RedeemToken', 'listentry.FittingModuleEntry', 'listentry.KillItems'):
                label = getattr(entry, 'genericDisplayLabel', None)
                itemID = fittingUtil.GetOriginalItemID(getattr(entry, 'itemID', None))
                if isinstance(itemID, tuple):
                    itemID = None
                link = evelink.type_link(entry.typeID, itemID, label)
                self.AddLink(link.text, link.url)
            elif guid == 'listentry.PodGuideBrowseEntry':
                self.AddLink(entry.label, format_pod_guide_url(entry.termID))
            elif guid == 'fakeentry.OverviewProfile':
                progressText = localization.GetByLabel('UI/Overview/FetchingOverviewProfile')
                sm.GetService('loading').ProgressWnd(progressText, '', 1, 2)
                try:
                    presetKeyVal = sm.RemoteSvc('overviewPresetMgr').StoreLinkAndGetID(entry.data)
                    if presetKeyVal is None:
                        raise UserError('OverviewProfileLoadingError')
                    else:
                        presetKey = (presetKeyVal.hashvalue, presetKeyVal.sqID)
                finally:
                    sm.GetService('loading').ProgressWnd(progressText, '', 2, 2)

                link = overview_preset_link(presetKey, entry.label)
                self.AddLink(link.text, link.url)
            elif guid == 'fakeentry.BroadcastSharing':
                with sharedSettings.client.ShowFetchingSettingsProgressWnd(''):
                    settingKeyVal = sm.RemoteSvc('sharedSettingsMgr').StoreSettingLinkAndGetID(sharedSettings.SHARED_SETTING_BROADCAST, entry.data)
                    settingKey = sharedSettings.GetSettingKeyFromKeyVal(settingKeyVal, 'ItemFilterLoadingError')
                link = sharedSettings.client.format_shared_settings_url(settingKey)
                label = entry.label
                self.AddLink(label, link)
            elif guid == 'listentry.PointerWndEntry':
                pointerObjects = entry.pointerObjects
                numPointers = len(pointerObjects)
                for i, pointerObj in enumerate(pointerObjects):
                    label = pointerObj.labelLong or pointerObj.label
                    link = format_help_pointer_url(pointerObj.uiElementName)
                    sm.GetService('helpPointer').LogPointerLinkCreated(pointerObj.uiElementName)
                    self.AddLink(label, link)
                    if i < numPointers - 1:
                        self.Insert(187)

            elif guid == 'listentry.AgencyHelpVideoEntry':
                link = agency.client.get_help_video_link(video_id=entry['id'])
                sm.GetService('agencyNew').LogHelpVideoLinkCreated(entry['path'])
                self.AddLink(link.text, link.url)
            elif getattr(entry, 'nodeType', None) == 'AccessGroupEntry':
                link = access_group_link(entry.groupID, entry.label)
                self.AddLink(link.text, link.url)
            elif getattr(entry, 'nodeType', None) == 'BookmarkFolderEntry':
                link = format_bookmark_folder_url(entry.folderID)
                label = entry.label
                self.AddLink(label, link)

        self.CheckHintText()

    def CheckLinkFits(self, entry):
        if not getattr(entry, 'check_link_fits', False):
            return
        link = entry.get_link()
        roomLeft = self.RoomLeft()
        if roomLeft is not None:
            if len(link) >= roomLeft:
                raise UserError('LinkTooLong')

    def ApplyGameSelection(self, what, data, changeObjs):
        if what == 6 and len(changeObjs):
            key = {}
            if data:
                key['link'] = data['link']
                t = self.DoSearch(key['link'], data['text'])
                if not t:
                    return
            else:
                format = [{'type': 'checkbox',
                  'label': '_hide',
                  'text': 'http://',
                  'key': 'http://',
                  'required': 1,
                  'setvalue': 1,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/Character'),
                  'key': 'char',
                  'required': 1,
                  'setvalue': 0,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/Corporation'),
                  'key': 'corp',
                  'required': 1,
                  'setvalue': 0,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/ItemType'),
                  'key': 'type',
                  'required': 1,
                  'setvalue': 0,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/SolarSystem'),
                  'key': 'solarsystem',
                  'required': 1,
                  'setvalue': 0,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'checkbox',
                  'label': '_hide',
                  'text': localization.GetByLabel('UI/Common/Station'),
                  'key': 'station',
                  'required': 1,
                  'setvalue': 0,
                  'group': 'link',
                  'onchange': self.OnLinkTypeChange},
                 {'type': 'push'},
                 {'type': 'edit',
                  'label': localization.GetByLabel('UI/Common/Link'),
                  'text': 'http://',
                  'width': 170,
                  'required': 1,
                  'key': 'txt'},
                 {'type': 'push'}]
                key = self.AskLink(None, format, width=400)
            anchor = -1
            if key:
                link = key['link']
                if link == None:
                    return
                if link in ('char', 'corp', 'alliance', 'solarsystem', 'station', 'type'):
                    if not self.typeID and not self.DoSearch(link, key['txt']):
                        return
                    return evelink.format_show_info_url(self.typeID, self.itemID)
                if link == 'fleet':
                    anchor = 'fleet:' + str(self.itemID)
                elif link == 'http://':
                    if key['txt'].startswith(key['link']) or key['txt'].startswith('https://'):
                        anchor = ''
                    else:
                        anchor = key['link']
                    anchor += key['txt']
                else:
                    anchor = key['link'] + key['txt']
            return anchor
        return -1

    def OnLinkTypeChange(self, chkbox, *args):
        if chkbox.GetValue():
            self.itemID = self.typeID = None
            self.key = chkbox.data['key']
            text = chkbox.GetChild('text')
            wnd = chkbox.FindParentByName(localization.GetByLabel('UI/Common/GenerateLink'))
            if not wnd:
                return
            editParent = wnd.FindChild('editField')
            if editParent is not None:
                label = editParent.FindChild('label')
                label.text = text.text
                edit = editParent.FindChild('edit_txt')
                edit.SetValue('')
                self.sr.searchbutt = editParent.FindChild('button')
                if self.key in ('char', 'corp', 'type', 'solarsystem', 'station'):
                    if self.sr.searchbutt == None:
                        self.sr.searchbutt = Button(parent=editParent, label=localization.GetByLabel('UI/Common/Search'), func=self.OnSearch, btn_default=0, align=uiconst.CENTERRIGHT, left=4)
                    else:
                        self.sr.searchbutt.state = uiconst.UI_NORMAL
                elif self.sr.searchbutt != None:
                    self.sr.searchbutt.state = uiconst.UI_HIDDEN

    def OnSearch(self, *args):
        wnd = self.sr.searchbutt.FindParentByName(localization.GetByLabel('UI/Common/GenerateLink'))
        if not wnd:
            return
        editParent = wnd.FindChild('editField')
        edit = editParent.FindChild('edit_txt')
        val = edit.GetValue().strip().lower()
        name = self.DoSearch(self.key, val)
        if name is not None:
            edit.SetValue(name)

    def DoSearch(self, key, val):
        self.itemID = None
        self.typeID = None
        id = None
        name = ''
        val = '%s*' % val
        if key == 'type':
            itemTypes = []
            results = searchUtil.GetResultsList(val, [ResultType.item_type])
            if results is not None:
                for typeID in results:
                    itemTypes.append((evetypes.GetName(typeID), None, typeID))

            if not itemTypes:
                eve.Message('NoItemTypesFound')
                return
            id = uix.ListWnd(itemTypes, 'item', localization.GetByLabel('UI/Common/SelectItemType'), None, 1)
        else:
            group = None
            hideNPC = 0
            if key == 'solarsystem':
                group = const.groupSolarSystem
            elif key == 'station':
                group = const.groupStation
            elif key == 'char':
                group = const.groupCharacter
            elif key == 'corp':
                group = const.groupCorporation
            elif key == 'alliance':
                group = const.groupAlliance
            id = searchOld.Search(val, group, hideNPC=hideNPC, listType='Generic')
        name = ''
        if id:
            self.itemID = id
            self.typeID = 0
            if key in ('char', 'corp', 'alliance'):
                o = cfg.eveowners.Get(id)
                self.typeID = o.typeID
                name = o.name
            elif key == 'solarsystem':
                self.typeID = const.typeSolarSystem
                l = cfg.evelocations.Get(id)
                name = l.name
            elif key == 'station':
                if idCheckers.IsStation(id):
                    self.typeID = sm.GetService('ui').GetStationStaticInfo(id).stationTypeID
                else:
                    structureInfo = sm.GetService('structureDirectory').GetStructureInfo(id)
                    if structureInfo:
                        self.typeID = structureInfo.typeID
                    else:
                        return
                l = cfg.evelocations.Get(id)
                name = l.name
            elif key == 'type':
                self.typeID = id[2]
                self.itemID = None
                name = id[0]
        return name

    def AskLink(self, label = '', lines = [], width = 280):
        icon = uiconst.QUESTION
        format = [{'type': 'text',
          'text': label}] + lines
        retval = uix.HybridWnd(format, caption=localization.GetByLabel('UI/Common/GenerateLink'), windowID='askLink', modal=1, buttons=uiconst.OKCANCEL, minW=width, minH=110, icon=icon)
        if retval:
            return retval
        else:
            return None

    def AddLink(self, text, link = None, addLineBreak = False):
        self.SetSelectionRange(None, None)
        node = self.GetActiveNode()
        if node is None:
            return
        text = commonutils.StripTags(text, stripOnly=['localized'])
        shiftCursor = len(text)
        stackCursorIndex = self.globalCursorPos - node.startCursorIndex + node.stackCursorIndex
        glyphString = node.glyphString
        newGlyphString = uicore.font.GetGlyphString()
        self._UpdateGlyphString(newGlyphString, text, link, shiftCursor, stackCursorIndex)
        newStringText = self.GetValueForParagraphs(1, [newGlyphString])
        if not self.IsEnoughRoomForInsert(len(newStringText)):
            uicore.Message('uiwarning03')
            return
        shift = self._UpdateGlyphString(glyphString, text, link, shiftCursor, stackCursorIndex)
        self.UpdateGlyphString(glyphString, advance=shiftCursor, stackCursorIndex=stackCursorIndex)
        self.SetCursorPos(self.globalCursorPos + shift)
        self.UpdatePosition()
        cursorAdvance = 1
        if addLineBreak:
            self.Insert(uiconst.VK_RETURN)

    def _UpdateGlyphString(self, glyphString, text, link, shiftCursor, stackCursorIndex):
        glyphStringIndex = self.GetGlyphStringIndex(glyphString)
        shift = 0
        if stackCursorIndex != 0:
            currentParams = self._activeParams.Copy()
            self.InsertToGlyphString(glyphString, currentParams, u' ', stackCursorIndex)
            shift += 1
        currentParams = self._activeParams.Copy()
        currentParams.url = link
        self.InsertToGlyphString(glyphString, currentParams, text, stackCursorIndex + shift)
        shift += shiftCursor
        currentParams = self._activeParams.Copy()
        self.InsertToGlyphString(glyphString, currentParams, u' ', stackCursorIndex + shift)
        shift += 1
        return shift

    def GetMenuDelegate(self, node = None):
        m = EditPlainTextCore.GetMenuDelegate(self, node)
        if not self.readonly:
            m.append(None)
            linkmenu = [(MenuLabel('UI/Common/Groups/Character'), self.LinkCharacter),
             (MenuLabel('UI/Common/Corporation'), self.LinkCorp),
             (MenuLabel('UI/Common/Alliance'), self.LinkAlliance),
             (MenuLabel('UI/Common/SolarSystem'), self.LinkSolarSystem),
             (MenuLabel('UI/Common/Station'), self.LinkStation),
             (MenuLabel('UI/Common/ItemType'), self.LinkItemType)]
            m.append((MenuLabel('UI/Common/AutoLink'), linkmenu))
        return m

    def LinkSomething(self, linkType):
        if not self.HasSelection():
            self.SelectWordUnderCursor()
        txt = self.GetSelectedText()
        if txt:
            txt = txt.strip()
        self.ApplySelection(6, data={'text': txt,
         'link': linkType})
        self.UpdateCharacterCounter()

    def LinkCharacter(self):
        self.LinkSomething('char')

    def LinkCorp(self):
        self.LinkSomething('corp')

    def LinkAlliance(self):
        self.LinkSomething('alliance')

    def LinkSolarSystem(self):
        self.LinkSomething('solarsystem')

    def LinkStation(self):
        self.LinkSomething('station')

    def LinkItemType(self):
        self.LinkSomething('type')
