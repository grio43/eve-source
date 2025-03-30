#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_autokicks.py
import carbonui.const as uiconst
import localization
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.lib.appConst import defaultPadding
from eve.common.lib import appConst as const

class CorpAutoKicks(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.autoKicksScroll = Scroll(name='applicationsScroll', parent=self, align=uiconst.TOALL, padding=(defaultPadding,
         defaultPadding,
         defaultPadding,
         defaultPadding))

    def Load(self, panel_id, *args):
        pendingKicks = sm.GetService('corp').GetPendingAutoKicks()
        scrolllist = []
        for characterID, kickedByCharacterID in pendingKicks:
            characterIDLink = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(characterID).name, info=('showinfo', const.typeCharacter, characterID))
            kickedByCharacterIDLink = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=cfg.eveowners.Get(kickedByCharacterID).name, info=('showinfo', const.typeCharacter, kickedByCharacterID))
            scrolllist.append(GetFromClass(KickEntry, {'label': '%s<t>%s' % (characterIDLink, kickedByCharacterIDLink)}))

        headers = [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/CorpMemberName'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/KickCreatedBy')]
        self.autoKicksScroll.Load(contentList=scrolllist, headers=headers, noContentHint=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/NoPendingAutoKicks'))


class KickEntry(Generic):

    def Load(self, node):
        Generic.Load(self, node)
        self.sr.label.state = uiconst.UI_NORMAL
