#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\medals.py
import types
import carbonui.control.radioButton
import localization
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.util import uix, utilWindows
from eve.common.script.util import eveFormat
from eveexceptions import UserError

class Medals(Service):
    __exportedcalls__ = {'CreateMedal': [],
     'SetMedalStatus': [],
     'GetAllCorpMedals': [],
     'GetRecipientsOfMedal': [],
     'GetMedalsReceived': [],
     'GetMedalDetails': [],
     'GiveMedalToCharacters': []}
    __guid__ = 'svc.medals'
    __servicename__ = 'medals'
    __displayname__ = 'Medals'
    __dependencies__ = ['objectCaching']
    __notifyevents__ = ['OnCorporationMedalAdded', 'OnMedalIssued', 'OnMedalStatusChanged']

    def __init__(self):
        Service.__init__(self)

    def Run(self, memStream = None):
        self.LogInfo('Starting Medal Svc')

    def CreateMedal(self, title, description, graphics):
        roles = const.corpRoleDirector | const.corpRolePersonnelManager
        if session.corprole & roles == 0:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/CreateDecorationWindow/NeedRolesError')})
        if len(title) > const.medalMaxNameLength:
            raise UserError('MedalNameTooLong', {'maxLength': str(const.medalMaxNameLength)})
        if len(description) > const.medalMaxDescriptionLength:
            raise UserError('MedalDescriptionTooLong', {'maxLength': str(const.medalMaxDescriptionLength)})
        try:
            sm.RemoteSvc('corporationSvc').CreateMedal(title, description, graphics)
        except UserError as e:
            if e.args[0] == 'ConfirmCreatingMedal':
                d = dict(cost=localization.GetByLabel('UI/Map/StarMap/lblBoldName', name=eveFormat.FmtISK(e.dict.get('cost', 0))))
                ret = eve.Message(e.msg, d, uiconst.YESNO, suppress=uiconst.ID_YES)
                if ret == uiconst.ID_YES:
                    sm.RemoteSvc('corporationSvc').CreateMedal(title, description, graphics, True)
            else:
                raise

    def SetMedalStatus(self, statusdict = None):
        if statusdict is None:
            return
        sm.RemoteSvc('corporationSvc').SetMedalStatus(statusdict)

    def GetAllCorpMedals(self, corpID):
        medals, medalDetails = sm.RemoteSvc('corporationSvc').GetAllCorpMedals(corpID)
        return [medals, medalDetails]

    def GetRecipientsOfMedal(self, medalID):
        recipients = sm.RemoteSvc('corporationSvc').GetRecipientsOfMedal(medalID)
        for recipient in recipients:
            recipient.reason = recipient.reason

        return recipients

    def GetMedalsReceivedWithFlag(self, characterID, status = None):
        if status is None:
            status = [2, 3]
        ret = {}
        medals = self.GetMedalsReceived(characterID)
        medalInfo, medalGraphics = medals
        for medal in medalInfo:
            if medal.status in status:
                if ret.has_key(medal.medalID):
                    ret[medal.medalID].append(medal)
                else:
                    ret[medal.medalID] = [medal]

        return ret

    def GetMedalsReceived(self, characterID):
        return sm.RemoteSvc('corporationSvc').GetMedalsReceived(characterID)

    def GetMedalDetails(self, medalID):
        return sm.RemoteSvc('corporationSvc').GetMedalDetails(medalID)

    def GiveMedalToCharacters(self, medalID, recipientID, reason = ''):
        roles = const.corpRoleDirector | const.corpRolePersonnelManager
        if session.corprole & roles == 0:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/CreateDecorationWindow/NeedRolesError')})
        if reason == '':
            ret = utilWindows.NamePopup(localization.GetByLabel('UI/Corporations/CorporationWindow/Members/AwardReasonTitle'), localization.GetByLabel('UI/Corporations/CorporationWindow/Members/PromptForReason'), reason, maxLength=200)
            if ret:
                reason = ret
            else:
                return
        if type(recipientID) == types.IntType:
            recipientID = [recipientID]
        try:
            sm.RemoteSvc('corporationSvc').GiveMedalToCharacters(medalID, recipientID, reason)
        except UserError as e:
            if e.args[0].startswith('ConfirmGivingMedal'):
                d = dict(amount=len(recipientID), members=localization.GetByLabel('UI/Corporations/MedalsToUsers', numMembers=len(recipientID)), cost=eveFormat.FmtISK(e.dict.get('cost', 0)))
                ret = eve.Message(e.msg, d, uiconst.YESNO, suppress=uiconst.ID_YES)
                if ret == uiconst.ID_YES:
                    sm.RemoteSvc('corporationSvc').GiveMedalToCharacters(medalID, recipientID, reason, True)
            elif e.args[0] == 'NotEnoughMoney':
                eve.Message(e.msg, e.dict)
            else:
                raise

    def OnCorporationMedalAdded(self, *args):
        invalidate = [('corporationSvc', 'GetAllCorpMedals', (session.corpid,)), ('corporationSvc', 'GetRecipientsOfMedal', (args[0],))]
        self.objectCaching.InvalidateCachedMethodCalls(invalidate)
        corpUISignals.on_corporation_medal_added()

    def OnMedalIssued(self, *args):
        invalidate = [('corporationSvc', 'GetMedalsReceived', (session.charid,))]
        self.objectCaching.InvalidateCachedMethodCalls(invalidate)
        sm.ScatterEvent('OnUpdatedMedalsAvailable')

    def OnMedalStatusChanged(self, *args):
        invalidate = [('corporationSvc', 'GetMedalsReceived', (session.charid,))]
        self.objectCaching.InvalidateCachedMethodCalls(invalidate)
        sm.ScatterEvent('OnUpdatedMedalStatusAvailable')


class PermissionEntry(Generic):
    __guid__ = 'listentry.PermissionEntry'
    __params__ = ['label', 'itemID']

    def ApplyAttributes(self, attributes):
        super(PermissionEntry, self).ApplyAttributes(attributes)
        self.columns = [0, 1, 2]

    def Startup(self, *args):
        super(PermissionEntry, self).Startup(*args)
        self.sr.checkBoxes = {}
        i = 220
        for column in self.columns:
            cbox = carbonui.control.radioButton.RadioButton(text='', parent=self, settingsKey='', retval=column, callback=self.VisibilityFlagsChange, align=uiconst.TOPLEFT, pos=(i + 7,
             1,
             16,
             0))
            self.sr.checkBoxes[column] = cbox
            i += 30

        self.sr.label.top = 0
        self.sr.label.left = 6
        self.sr.label.SetAlign(uiconst.CENTERLEFT)
        self.flag = 0

    def Load(self, node):
        Generic.Load(self, node)
        data = self.sr.node
        self.flag = data.visibilityFlags
        if data.Get('tempFlag', None) is not None:
            self.flag = data.tempFlag
        for cboxID, cbox in self.sr.checkBoxes.iteritems():
            cbox.state = uiconst.UI_NORMAL
            cbox.SetGroup(data.itemID)
            if self.flag == cboxID:
                cbox.SetChecked(1, 0)
            else:
                cbox.SetChecked(0, 0)

        if self.sr.node.scroll.sr.tabs:
            self.OnColumnChanged()

    def OnColumnChanged(self, *args):
        tabs = self.sr.node.scroll.sr.tabs
        for i, key in enumerate(self.columns):
            width = tabs[i + 1] - tabs[i]
            self.sr.checkBoxes[key].left = self.sr.node.scroll.sr.tabs[i] + width / 2 - 8

    def GetHeight(self, *args):
        node, _ = args
        node.height = max(19, uix.GetTextHeight(node.label, maxLines=1) + 4)
        return node.height

    def VisibilityFlagsChange(self, radioButton):
        self.flag = radioButton.GetReturnValue()

    def HasChanged(self):
        return self.flag != self.sr.node.visibilityFlags


class DecorationPermissionsEntry(PermissionEntry):
    __guid__ = 'listentry.DecorationPermissions'
    __params__ = ['label', 'itemID']

    def ApplyAttributes(self, attributes):
        PermissionEntry.ApplyAttributes(self, attributes)
        self.columns = [2, 3, 1]

    def Startup(self, *args):
        PermissionEntry.Startup(self)

    def Load(self, node):
        PermissionEntry.Load(self, node)
