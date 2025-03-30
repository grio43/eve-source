#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_member_decorations.py
import carbonui.const as uiconst
import localization
from carbon.common.script.sys.cfg import Row
from carbon.common.script.util.format import FmtDate
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.medalribbonranks import MedalRibbonPickerWindow
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from globalConfig.getFunctions import IsContentComplianceControlSystemActive
from eve.common.lib import appConst as const

class CorpDecorations(Container):
    __guid__ = 'form.CorpDecorations'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sr.notext = None
        self.sr.fromDate = None
        self.sr.toDate = None
        self.sr.mostRecentItem = None
        self.sr.oldestItem = None
        self.sr.memberID = None
        corpUISignals.on_corporation_medal_added.connect(self.OnCorporationMedalAdded)

    def Load(self, *args):
        if not self.sr.Get('inited', 0):
            if const.corpRolePersonnelManager & eve.session.corprole == const.corpRolePersonnelManager and not IsContentComplianceControlSystemActive(sm.GetService('machoNet')):
                buttons = ButtonGroup(parent=self, align=uiconst.TOBOTTOM, padTop=16)
                Button(parent=buttons, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Decorations/CreateDecorationButton'), func=self.CreateDecorationForm)
            self.sr.scroll = eveScroll.Scroll(name='decorations', parent=self)
            self.sr.scroll.sr.id = 'corp_decorations_scroll'
            self.sr.inited = 1
        self.LoadDecorations()

    def CreateDecorationForm(self, *args):
        MedalRibbonPickerWindow.Open()

    def LoadDecorations(self, *args):
        scrolllist = []
        medals, medalDetails = sm.GetService('medals').GetAllCorpMedals(session.corpid)
        for medal in medals:
            medalid = medal.medalID
            title = medal.title
            description = medal.description
            createdate = medal.date
            creator = cfg.eveowners.Get(medal.creatorID).name
            recipients = medal.noRecepients
            details = medalDetails.Filter('medalID')
            if details and details.has_key(medalid):
                details = details.get(medalid)
            scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetDecorationSubContent,
             'label': '%s<t>%s<t>%s<t><t>%s' % (title,
                       creator,
                       FmtDate(createdate, 'ss'),
                       recipients),
             'groupItems': None,
             'medal': medal,
             'details': details,
             'id': ('corpdecorations', medalid),
             'tabs': [],
             'state': 'locked',
             'showicon': 'hide',
             'hint': description}))

        headers = [localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Decorations/DecorationRecipient'),
         localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Decorations/DecorationIssuer'),
         localization.GetByLabel('UI/Common/Date'),
         localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Decorations/DecorationReason'),
         localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Decorations/DecorationAwardedCount')]
        self.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Decorations/NoDecorationsFound'))

    def GetDecorationSubContent(self, nodedata, *args):
        m = nodedata.medal
        d = nodedata.details
        medalid = m.medalID
        scrolllist = []
        entry = sm.StartService('info').GetMedalEntry(m, d)
        if entry:
            scrolllist.append(entry)
        scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetMedalSubContent,
         'label': localization.GetByLabel('UI/Corporations/CorporationWindow/Members/Decorations/ViewAwardees'),
         'groupItems': None,
         'medal': m,
         'id': ('corpdecorationdetails', medalid),
         'tabs': [],
         'state': 'locked',
         'showicon': 'hide',
         'sublevel': 1}))
        return scrolllist

    def GetMedalSubContent(self, nodedata, *args):
        m = nodedata.medal
        medalid = m.medalID
        recipients = sm.GetService('medals').GetRecipientsOfMedal(medalid)
        scrolllist = []
        recipientsunified = {}
        if recipients:
            for recipient in recipients:
                if not recipientsunified.has_key(recipient.recepientID):
                    recipientsunified[recipient.recepientID] = [recipient]
                else:
                    recipientsunified[recipient.recepientID].append(recipient)

        if recipientsunified:
            for recipient, data in recipientsunified.iteritems():
                theyareallthesame = data[0]
                recipientID = recipient
                issuerID = theyareallthesame.issuerID
                date = theyareallthesame.date
                reason = theyareallthesame.reason
                awarded = len(data)
                label = '%s<t>%s<t>%s<t>%s<t>%s' % (cfg.eveowners.Get(recipientID).name,
                 cfg.eveowners.Get(issuerID).name,
                 FmtDate(date, 'ss'),
                 reason,
                 awarded)
                scrolllist.append(GetFromClass(Generic, {'label': label,
                 'sublevel': 2,
                 'id': m.medalID,
                 'line': 1,
                 'typeID': const.typeCharacter,
                 'itemID': recipientID,
                 'showinfo': 1,
                 'sort_%s' % localization.GetByLabel('UI/Corporations/Common/Title'): ''.join([ text for text in label if type(text) is str ])}))

        return scrolllist

    def GetStatus(self, st):
        res = None
        statusName = const.medalStatus.get(st, None)
        if statusName:
            res = Row()
            setattr(res, 'header', ['statusID', 'statusName'])
            setattr(res, 'line', [st, statusName])
            setattr(res, 'id', st)
        return res

    def OnCorporationMedalAdded(self, *args):
        if self and not self.destroyed:
            if self.sr.Get('inited', 0):
                self.LoadDecorations()
