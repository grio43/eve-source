#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\statisticsController.py
import blue
from carbon.common.script.util.format import FmtAmt
from characterdata.races import get_race_name
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.common.script.net import eveMoniker
from eve.common.script.sys import idCheckers
from localization import GetByLabel
import eve.common.lib.appConst as appConst

class StatisticsController(object):

    def __init__(self, infoScroll):
        self.infoScroll = infoScroll

    def LoadStatisticsScrollData(self, key):
        stats = self.GetStatisticsScrollData(key)
        scrolllist, header = self.GetStatisticsScrolllist(stats)
        self.infoScroll.Load(contentList=scrolllist, headers=header, ignoreSort=True)

    def GetStatisticsScrolllist(self, stats, *args):
        caption = stats.get('label', '')
        header = stats.get('header', [])
        dataList = stats.get('data', [])
        scrolllist = []
        for each in dataList:
            scrolllist.append(GetFromClass(Generic, {'label': each,
             'vspace': 0,
             'GetMenu': self.CopyTable,
             'selectable': 0}))

        return (scrolllist, header)

    def GetStatisticsScrollData(self, key):
        stats = self.GetStatsData(key)
        if not stats:
            return
        statsHeader = stats.get('header')
        statsData = stats.get('data')
        data = [self.GetLine(GetByLabel('UI/FactionWarfare/Stats/KillsYesterday'), statsHeader, statsData.get('killsY')),
         self.GetLine(GetByLabel('UI/FactionWarfare/Stats/KillsLastWeek'), statsHeader, statsData.get('killsLW')),
         self.GetLine(GetByLabel('UI/FactionWarfare/Stats/KillsTotal'), statsHeader, statsData.get('killsTotal')),
         self.GetLine(GetByLabel('UI/FactionWarfare/Stats/VictoryPointsYesterday'), statsHeader, statsData.get('vpY')),
         self.GetLine(GetByLabel('UI/FactionWarfare/Stats/VictoryPointsLastWeek'), statsHeader, statsData.get('vpLW')),
         self.GetLine(GetByLabel('UI/FactionWarfare/Stats/VictoryPointsTotal'), statsHeader, statsData.get('vpTotal'))]
        factionInfo = sm.StartService('facwar').GetStats_FactionInfo()
        if key == 'militia':
            memberCount = self.ChangeFormat(factionInfo, 'totalMembersCount')
            sysControlled = self.ChangeFormat(factionInfo, 'systemsCount')
            data.insert(0, self.GetLine(GetByLabel('UI/FactionWarfare/Pilots'), statsHeader, memberCount))
            data.append(self.GetLine(GetByLabel('UI/FactionWarfare/Stats/SystemsControlled'), statsHeader, sysControlled))
        if key == 'corp':
            corpPilots = self.GetCorpPilots(factionInfo)
            data.insert(0, self.GetLine(GetByLabel('UI/FactionWarfare/Pilots'), statsHeader, corpPilots))
        return {'label': self.GetStatsLabel(key),
         'configname': key,
         'header': self.GetStatsHeader(key, statsHeader),
         'data': data}

    def GetCorpPilots(self, factionInfo):
        pilots = {}
        if idCheckers.IsNPC(session.corpid):
            yourFactionInfo = factionInfo.get(session.warfactionid, None)
            pilots['your'] = getattr(yourFactionInfo, 'militiaMembersCount', 0)
        else:
            reg = eveMoniker.GetCorpRegistry()
            pilots['your'] = reg.GetCorporation().memberCount
        topFWCorp = 0
        topCorps = self.ChangeFormat(factionInfo, 'topMemberCount')
        for each in topCorps.itervalues():
            if topFWCorp < each:
                topFWCorp = each

        pilots['top'] = topFWCorp
        allMembers = 0
        members = self.ChangeFormat(factionInfo, 'totalMembersCount')
        for each in members.itervalues():
            allMembers += each

        pilots['all'] = allMembers
        return pilots

    def ChangeFormat(self, data, attributeName):
        temp = {}
        for key, value in data.iteritems():
            temp[key] = getattr(value, attributeName, 0)

        return temp

    def GetStatsData(self, what):
        if what == 'militia':
            return sm.StartService('facwar').GetStats_Militia()
        if what == 'personal':
            return sm.StartService('facwar').GetStats_Personal()
        if what == 'corp':
            return sm.StartService('facwar').GetStats_Corp(session.corpid)
        if what == 'alliance':
            return sm.StartService('facwar').GetStats_Alliance(session.allianceid)

    def GetStatsLabel(self, what):
        if what == 'militia':
            return GetByLabel('UI/FactionWarfare/Militia')
        if what == 'personal':
            return GetByLabel('UI/Generic/Personal')
        if what == 'corp':
            return GetByLabel('UI/Generic/Corporation')
        if what == 'alliance':
            return GetByLabel('UI/Common/Alliance')
        return ''

    def GetStatsHeader(self, what, header):
        if what in ('personal', 'corp', 'alliance'):
            return self.GetPersonalCorpHeader(header)
        if what == 'militia':
            return self.GetMilitiaHeader(header, short=1)
        return []

    def GetLine(self, text, header, data):
        temp = '%s<t>' % text
        for each in header:
            temp = '%s%s<t>' % (temp, FmtAmt(data.get(each, 0), fmt='sn'))

        temp = temp[:-3]
        return temp

    def GetMilitiaHeader(self, header, short = 0):
        temp = ['']
        for each in header:
            if short:
                try:
                    raceID = appConst.raceByFaction[each]
                    name = get_race_name(raceID)
                except KeyError:
                    name = cfg.eveowners.Get(each).name

            else:
                name = cfg.eveowners.Get(each).name
            temp.append(name)

        return temp

    def GetPersonalCorpHeader(self, header):
        translation = {'you': GetByLabel('UI/FactionWarfare/You'),
         'your': GetByLabel('UI/FactionWarfare/Your'),
         'top': GetByLabel('UI/FactionWarfare/Top'),
         'all': GetByLabel('UI/FactionWarfare/All')}
        temp = ['']
        for each in header:
            name = translation.get(each, '')
            temp.append(name)

        return temp

    def CopyTable(self, *args):
        menu = [(GetByLabel('UI/FactionWarfare/CopyTable'), self.CopyScroll, (self.infoScroll,))]
        return menu

    def CopyScroll(self, scroll, *args):
        t = ''
        if hasattr(scroll, 'sr') and hasattr(scroll.sr, 'headers'):
            for header in getattr(scroll.sr, 'headers', None):
                if header == '':
                    header = '-'
                t = t + '%s, ' % header

        for each in scroll.GetNodes():
            t = t + '\r\n%s' % each.label.replace('<t>', ',  ').replace('<b>', '').replace('</b>', '')

        blue.pyos.SetClipboardData(t)
