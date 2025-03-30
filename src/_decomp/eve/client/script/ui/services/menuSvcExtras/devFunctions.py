#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\menuSvcExtras\devFunctions.py
import blue
import carbonui.const as uiconst
import carbon.common.lib.serverInfo as serverInfo
import sys
from eve.client.script.ui.util import uix, utilWindows
from eveexceptions import UserError
from eveservices.menu import GetMenuService
from eveservices.xmppchat import GetChatService

def SlashCmd(cmd):
    try:
        sm.RemoteSvc('slash').SlashCmd(cmd)
    except RuntimeError:
        sm.GetService('gameui').MessageBox('This only works on items at your current location.', 'Oops!', buttons=uiconst.OK)


def SlashCmdTr(cmd):
    SlashCmd(cmd)
    GetMenuService().ClearAlignTargets()


def GagPopup(charID, channelID, numMinutes):
    reason = 'Gagged for Spamming'
    ret = utilWindows.NamePopup('Gag User', 'Enter Reason', reason)
    if ret:
        sm.GetService('chat').mute_player(charID, channelID, numMinutes * 60, ret)


def Ungag(charID, channelID):
    sm.GetService('chat').unmute_player(charID, channelID)


def BanIskSpammer(charID):
    if eve.Message('ConfirmBanIskSpammer', {'name': cfg.eveowners.Get(charID).name}, uiconst.YESNO) != uiconst.ID_YES:
        return
    SlashCmd('/baniskspammer %s' % charID)


def GagIskSpammer(charID):
    if eve.Message('ConfirmGagIskSpammer', {'name': cfg.eveowners.Get(charID).name}, uiconst.YESNO) != uiconst.ID_YES:
        return
    SlashCmd('/gagiskspammer %s' % charID)


def ReportISKSpammer(charID, channelID):
    if eve.Message('ConfirmReportISKSpammer', {'name': cfg.eveowners.Get(charID).name}, uiconst.YESNO) != uiconst.ID_YES:
        return
    if charID == session.charid:
        raise UserError('ReportISKSpammerCannotReportYourself')
    chat_svc = GetChatService()
    if chat_svc.IsSpammer(charID):
        return
    spamEntries = chat_svc.GetSpamEntries(charID, channelID)
    chat_svc.AddSpammer(charID)
    chat_svc.ReloadChannel(channelID)
    channel = chat_svc.channels.get(channelID, None)
    if channel and channel.info:
        channelID = channel.info.displayName
    sm.RemoteSvc('userSvc').ReportISKSpammer(charID, channelID, spamEntries)


def SetDogmaAttribute(itemID, attrName, actualValue):
    ret = uix.QtyPopup(None, None, actualValue, 'Set Dogma Attribute for <b>%s</b>' % attrName, 'Set Dogma Attribute', digits=5)
    if ret:
        cmd = '/dogma %s %s = %s' % (itemID, attrName, ret['qty'])
        SlashCmd(cmd)


def AttributeMenu(itemID, typeID):
    d = sm.StartService('info').GetAttributeDictForType(typeID)
    statemgr = sm.StartService('godma').GetStateManager()
    a = statemgr.attributesByID
    lst = []
    for attributeID, baseValue in d.iteritems():
        attrName = a[attributeID].name
        try:
            actualValue = statemgr.GetAttribute(itemID, attrName)
        except:
            sys.exc_clear()
            actualValue = baseValue

        lst.append(('%s - %s' % (attrName, actualValue), SetDogmaAttribute, (itemID, attrName, actualValue)))

    lst.sort(lambda x, y: cmp(x[0], y[0]))
    return lst


def GetFromESP(action):
    espaddy = serverInfo.GetServerInfo().espUrl
    blue.os.ShellExecute('http://%s/%s' % (espaddy, action))


def NPCInfoMenu(item):
    lst = []
    action = 'gd/type.py?action=Type&typeID=' + str(item.typeID)
    lst.append(('Overview', GetFromESP, (action,)))
    action = 'gd/type.py?action=TypeDogma&typeID=' + str(item.typeID)
    lst.append(('Dogma Attributes', GetFromESP, (action,)))
    action = 'gd/npc.py?action=GetNPCInfo&shipID=' + str(item.itemID) + '&solarSystemID=' + str(session.solarsystemid)
    lst.append(('Info', GetFromESP, (action,)))
    return lst
