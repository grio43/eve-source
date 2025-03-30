#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_sanctionableactions.py
import blue
import evetypes
from carbon.common.script.util.format import FmtDate
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.button import ButtonEntry
from eve.client.script.ui.control.entries.divider import DividerEntry
from eve.client.script.ui.control.entries.label_text import LabelText
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.util import uix
import carbonui.const as uiconst
import localization
from carbonui.uicore import uicore
from corporation import voting
from eve.common.lib import appConst as const
from eveexceptions import ExceptionEater

class CorpSanctionableActions(Container):
    __guid__ = 'form.CorpSanctionableActions'
    __nonpersistvars__ = []

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sr.inited = 0
        corpUISignals.on_sanctioned_action_changed.connect(self.OnSanctionedActionChanged)

    def Load(self, *args, **kwargs):
        self.voteTypes = {voting.voteCEO: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/NewCEO'),
         voting.voteWar: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/DeclarationOfWar'),
         voting.voteShares: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/CreationOfShares'),
         voting.voteKickMember: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Expulsion'),
         voting.voteGeneral: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/GeneralVote'),
         voting.voteItemUnlock: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/UnlockBlueprint'),
         voting.voteItemLockdown: localization.GetByLabel('UI/Corporations/CorpSanctionableActions/LockBlueprint')}
        self.headers = [localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Type'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Title'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Description'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Expires'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ActedUpon'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/InEffect'),
         localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Rescinded')]
        if not self.sr.Get('inited', 0):
            self.sr.inited = 1
            self.toolbarContainer = Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self)
            buttonOptions = [[localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ShowAll'),
              self.ShowSanctionableActionsNotInEffect,
              True,
              81]]
            btns = ButtonGroup(btns=buttonOptions, parent=self.toolbarContainer)
            self.toolbarContainer.height = btns.height
            self.sr.mainBtns = btns
            self.sr.scroll = eveScroll.Scroll(name='sanctionableactions', parent=self, padding=(const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding,
             const.defaultPadding))
            self.sr.tabs = ToggleButtonGroup(parent=self, idx=0, align=uiconst.TOTOP, callback=self.Refresh, padBottom=8)
            self.sr.tabs.AddButton('ineffect', localization.GetByLabel('UI/Corporations/CorpSanctionableActions/InEffect'))
            self.sr.tabs.AddButton('notineffect', localization.GetByLabel('UI/Corporations/CorpSanctionableActions/NotInEffect'))
            self.sr.tabs.SelectByID('ineffect')

    def Refresh(self, *args, **kwargs):
        if self is None or self.destroyed or not self.sr.inited:
            return
        selectedTab = self.sr.tabs.GetSelected()
        if selectedTab == 'ineffect':
            self.ShowSanctionableActionsInEffect()
        elif selectedTab == 'notineffect':
            self.ShowSanctionableActionsNotInEffect()

    def OnSanctionedActionChanged(self, corpID, voteCaseID):
        self.Refresh()

    def ShowSanctionableActionsInEffect(self, *args):
        with sm.GetService('corpui').ShowLoad('ShowSanctionableActionsInEffect'):
            uix.HideButtonFromGroup(self.sr.mainBtns, localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ShowAll'))
            self.sr.scroll.Clear()
            if not sm.GetService('corpvotes').CanViewVotes(session.corpid):
                self.SetHint(localization.GetByLabel('UI/Corporations/AccessRestrictions/MustBeCEODirectorOrShareholder'))
                return
            corpVoting = sm.GetService('corpvotes')
            voteCases = corpVoting.GetVoteCasesByCorporation(session.corpid).Index('voteCaseID')
            actions = corpVoting.GetSanctionedActions(voting.SANCTIONED_ACTION_STATUS_IN_EFFECT)
            owners = {a.parameter for a in actions if a.voteType in (voting.voteCEO, voting.voteWar, voting.voteKickMember) and a.parameter}
            if len(owners):
                cfg.eveowners.Prime(owners)
            scrolllist = []
            for row in actions:
                if row.voteType in [voting.voteItemUnlock,
                 voting.voteCEO,
                 voting.voteWar,
                 voting.voteShares,
                 voting.voteKickMember,
                 voting.voteItemLockdown] and row.parameter == 0:
                    continue
                if row.voteCaseID not in voteCases:
                    voteCases[row.voteCaseID] = corpVoting.GetVoteCase(session.corpid, row.voteCaseID)
                voteType = self.voteTypes[row.voteType]
                title = voteCases[row.voteCaseID].voteCaseText.split('<br>')[0]
                description = self.GetDescription(voteCases[row.voteCaseID].description.split('<br>')[0])
                expires = FmtDate(row.expires)
                actedUpon = [localization.GetByLabel('UI/Generic/No'), localization.GetByLabel('UI/Generic/Yes')][row.actedUpon]
                inEffect = [localization.GetByLabel('UI/Generic/No'), localization.GetByLabel('UI/Generic/Yes')][row.inEffect]
                rescended = localization.GetByLabel('UI/Generic/No')
                if row.timeRescended:
                    rescended = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/AnswerWithTimestamp', answer=rescended, timestamp=FmtDate(row.timeRescended))
                if row.timeActedUpon:
                    actedUpon = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/AnswerWithTimestamp', answer=actedUpon, timestamp=FmtDate(row.timeActedUpon))
                label = '<t>'.join((voteType,
                 title,
                 description,
                 expires,
                 actedUpon,
                 inEffect,
                 rescended))
                scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetInEffectSanctionedActionSubContent,
                 'label': label,
                 'groupItems': None,
                 'id': ('corpsaie', row.voteCaseID),
                 'tabs': [],
                 'state': 'locked',
                 'row': row,
                 'voteCases': voteCases,
                 'showicon': 'hide',
                 'BlockOpenWindow': 1}))
                uicore.registry.SetListGroupOpenState(('corpsaie', row.voteCaseID), 0)

            self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.headers, noContentHint=localization.GetByLabel('UI/Corporations/CorpSanctionableActions/NoSanctionableActionsInEffect'))

    def GetInEffectSanctionedActionSubContent(self, nodedata, *args):
        with ExceptionEater('GetInEffectSanctionedActionSubContent'):
            row = nodedata.row
            if row.voteType == voting.voteGeneral:
                voteCaseOptions = sm.GetService('corpvotes').GetVoteCaseOptions(row.voteCaseID)
                return self.AddSanctionableEntry([{'Decision': voteCaseOptions[row.optionID].optionText}, None])
            entry = {'line': 1}
            if row.voteType in [voting.voteWar, voting.voteKickMember, voting.voteCEO]:
                owner = cfg.eveowners.Get(row.parameter)
                entry['text'] = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/MoreInfoEntry', ownerName=owner.ownerName)
                entry['itemID'] = row.parameter
                entry['typeID'] = owner.typeID
            elif row.voteType in [voting.voteItemLockdown, voting.voteItemUnlock]:
                entry['text'] = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/MoreInfoTypeNameAndLocation', typeID=row.parameter1, location=row.parameter2)
                entry['itemID'] = row.parameter
                entry['typeID'] = row.parameter1
            return [GetFromClass(Text, entry)]

    def ShowSanctionableActionsNotInEffect(self, showExpired = False, *args):
        with sm.GetService('corpui').ShowLoad('ShowSanctionableActionsNotInEffect'):
            if not sm.GetService('corpvotes').CanViewVotes(session.corpid):
                self.SetHint(localization.GetByLabel('UI/Corporations/AccessRestrictions/MustBeCEODirectorOrShareholder'))
                return
            if showExpired:
                if not eve.Message('ConfirmShowAllSanctionableActions', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                    return
                uix.HideButtonFromGroup(self.sr.mainBtns, localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ShowAll'))
                state = voting.SANCTIONED_ACTION_STATUS_EXPIRED
            else:
                uix.ShowButtonFromGroup(self.sr.mainBtns, localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ShowAll'))
                state = voting.SANCTIONED_ACTION_STATUS_NOT_IN_EFFECT
            scrolllist = []
            self.sr.scroll.Clear()
            corpVoting = sm.GetService('corpvotes')
            voteCases = corpVoting.GetVoteCasesByCorporation(session.corpid).Index('voteCaseID')
            actions = corpVoting.GetSanctionedActions(state)
            owners = {a.parameter for a in actions if a.voteType in (voting.voteCEO, voting.voteWar, voting.voteKickMember) and a.parameter}
            if len(owners):
                cfg.eveowners.Prime(owners)
            for row in actions:
                if row.voteType in [voting.voteItemUnlock,
                 voting.voteCEO,
                 voting.voteWar,
                 voting.voteShares,
                 voting.voteKickMember,
                 voting.voteItemLockdown] and row.parameter == 0:
                    continue
                if row.voteCaseID not in voteCases:
                    voteCases[row.voteCaseID] = corpVoting.GetVoteCase(session.corpid, row.voteCaseID)
                voteCase = voteCases[row.voteCaseID]
                voteType = self.voteTypes[row.voteType]
                title = voteCase.voteCaseText
                description = self.GetDescription(voteCase.description)
                expires = FmtDate(row.expires)
                actedUpon = [localization.GetByLabel('UI/Generic/No'), localization.GetByLabel('UI/Generic/Yes')][row.actedUpon]
                inEffect = [localization.GetByLabel('UI/Generic/No'), localization.GetByLabel('UI/Generic/Yes')][row.inEffect]
                rescended = localization.GetByLabel('UI/Generic/No')
                if row.timeRescended:
                    rescended = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/AnswerWithTimestamp', answer=rescended, timestamp=FmtDate(row.timeRescended))
                if row.timeActedUpon:
                    actedUpon = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/AnswerWithTimestamp', answer=actedUpon, timestamp=FmtDate(row.timeActedUpon))
                label = '<t>'.join((voteType,
                 title,
                 description,
                 expires,
                 actedUpon,
                 inEffect,
                 rescended))
                scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetNotInEffectSanctionedActionSubContent,
                 'label': label,
                 'groupItems': None,
                 'id': ('corpsanie', row.voteCaseID),
                 'tabs': [],
                 'state': 'locked',
                 'row': row,
                 'voteCases': voteCases,
                 'showicon': 'hide',
                 'BlockOpenWindow': 1}))
                uicore.registry.SetListGroupOpenState(('corpsanie', row.voteCaseID), 0)

            self.sr.scroll.Load(fixedEntryHeight=19, contentList=scrolllist, headers=self.headers, noContentHint=localization.GetByLabel('UI/Corporations/CorpSanctionableActions/NoNotInEffect'))

    def GetNotInEffectSanctionedActionSubContent(self, nodedata, *args):
        with ExceptionEater('GetNotInEffectSanctionedActionSubContent'):
            row = nodedata.row
            if row.voteType == voting.voteGeneral:
                voteCaseOptions = sm.GetService('corpvotes').GetVoteCaseOptions(row.voteCaseID)
                return self.AddSanctionableEntry([{'Decision': voteCaseOptions[row.optionID].optionText}, None])
            scrolllist = []
            if voting.voteCEO != row.voteType and sm.GetService('corp').UserIsActiveCEO():
                if row.expires > blue.os.GetWallclockTime():
                    if not row.actedUpon:
                        action = [localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ImplementAction'), (self.ImplementSanctionedAction, row.voteCaseID)]
                        scrolllist.append(GetFromClass(ButtonEntry, {'label': action[0],
                         'caption': localization.GetByLabel('UI/Commands/Apply'),
                         'OnClick': action[1][0],
                         'args': (action[1][1],)}))
            entry = {'line': 1}
            if row.voteType in [voting.voteWar, voting.voteKickMember, voting.voteCEO]:
                owner = cfg.eveowners.Get(row.parameter)
                label = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/MoreInfo')
                entry['text'] = label + '<t>' + owner.ownerName
                entry['itemID'] = row.parameter
                entry['typeID'] = owner.typeID
                scrolllist.append(GetFromClass(Text, entry))
            elif row.voteType in [voting.voteItemLockdown, voting.voteItemUnlock]:
                locationText = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/LocatedAt', location=row.parameter2)
                moreInfo = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/MoreInfo')
                entry['text'] = moreInfo + '<t>' + evetypes.GetName(row.parameter1) + '<t>' + locationText
                entry['itemID'] = row.parameter
                entry['typeID'] = row.parameter1
                scrolllist.append(GetFromClass(Text, entry))
            return scrolllist

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)

    def ImplementSanctionedAction(self, voteCaseID, wnd, *args):
        if not sm.GetService('corp').UserIsActiveCEO():
            label = localization.GetByLabel('UI/Corporations/CorpSanctionableActions/MustBeCEOToSanction')
            eve.Message('CustomError', {'error': label})
            return
        with sm.GetService('corpui').ShowLoad('ImplementSanctionedAction_%d' % voteCaseID):
            sm.GetService('corpvotes').ApplySanctionedAction(voteCaseID)
            self.ShowSanctionableActionsNotInEffect()

    def AddSanctionableEntry(self, _entry):
        fields = _entry[0]
        action = _entry[1]
        scrolllist = []
        theFields = {'Decision': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Decision'),
         'expires': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/Expires'),
         'actedUpon': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ActedUpon'),
         'In Effect': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/InEffect'),
         'timeActedUpon': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/TimeActedUpon'),
         'timeRescended': localization.GetByLabel('UI/Corporations/CorpSanctionableActions/TimeRescinded')}
        if len(fields) and fields.has_key('Description'):
            scrolllist.append(GetFromClass(Text, {'text': fields['Description']}))
        for key in fields.iterkeys():
            if not theFields.has_key(key):
                continue
            field = fields[key]
            title = theFields[key]
            scrolllist.append(GetFromClass(LabelText, {'label': title,
             'text': field}))

        if action is not None:
            caption = localization.GetByLabel('UI/Commands/Apply')
            scrolllist.append(GetFromClass(ButtonEntry, {'label': action[0],
             'caption': caption,
             'OnClick': action[1][0],
             'args': (action[1][1],)}))
        scrolllist.append(GetFromClass(DividerEntry))
        return scrolllist

    @staticmethod
    def GetDescription(description):
        if description.startswith('ItemInAssetSafetyWrap'):
            label, structureID = description.split('|')
            return localization.GetByLabel('UI/Corporations/CorpSanctionableActions/ItemInAssetSafetyWrap', structure=long(structureID))
        return description
