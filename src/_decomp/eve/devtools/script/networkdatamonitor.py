#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\networkdatamonitor.py
import operator
import carbonui.const as uiconst
from carbon.common.script.util.format import FmtDate, HoursMinsSecsFromSecs, SecsFromBlueTimeDelta
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.window import Window
from eve.common.lib import appConst as const
import log
import uthread2
PROPS = [('Packets out', 'packets_out', 0),
 ('Packets in', 'packets_in', 0),
 ('Kilobytes out', 'bytes_out', 1),
 ('Kilobytes in', 'bytes_in', 1)]

class NetworkDataMonitor(Window):
    default_caption = 'Network Data Monitor'
    default_windowID = 'networkdatamonitor'
    default_minSize = (490, 390)
    default_height = 640
    refreshDelaySeconds = 1.0

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.Reset()
        self.settingsContainer = Container(name='settingsContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, top=8, height=16, padding=8)
        Button(parent=self.settingsContainer, label='Reset', align=uiconst.CENTER, func=self.Reset)
        dataContainer = ScrollContainer(name='dataContainer', parent=self.sr.main, align=uiconst.TOALL, padding=8)
        statusHeader = ' '
        for tme in self.intvals:
            statusHeader += '<t><right>%s' % FmtDate(long(tme * 10000), 'ss')

        statusHeader += '<t><right>total'
        self.statusLabels = []
        Label(parent=dataContainer, align=uiconst.TOTOP, text=statusHeader, tabs=[110,
         150,
         200,
         250,
         300,
         350,
         400], state=uiconst.UI_DISABLED, left=2)
        for i in xrange(11):
            labelCont = Container(parent=dataContainer, align=uiconst.TOTOP, height=20)
            statusLabel = Label(parent=labelCont, text='', align=uiconst.CENTERLEFT, tabs=[110,
             150,
             200,
             250,
             300,
             350,
             400], state=uiconst.UI_DISABLED, left=2)
            self.statusLabels.append(statusLabel)

        self.grpc_event_publisher_details = []
        event_publisher_details_container = ContainerAutoSize(parent=dataContainer, align=uiconst.TOTOP)
        event_publisher_details = Label(parent=event_publisher_details_container, text='')
        self.grpc_event_publisher_details.append(event_publisher_details)
        self.grpc_request_broker_details = []
        request_broker_details_container = ContainerAutoSize(parent=dataContainer, align=uiconst.TOTOP, padTop=16)
        request_broker_details = Label(parent=request_broker_details_container, text='')
        self.grpc_request_broker_details.append(request_broker_details)
        self.PopulateLabels(initialize=True)
        uthread2.StartTasklet(self.Refresh)

    def Reset(self, *args):
        self.intvals = [5000,
         10000,
         15000,
         30000,
         60000]
        self.counter = [[],
         [],
         [],
         [],
         [],
         []]
        self.ticker = 0
        self.packets_outTotal = 0
        self.packets_inTotal = 0
        self.bytes_outTotal = 0
        self.bytes_inTotal = 0
        self.laststats = {}
        self.lastresetstats = sm.GetService('machoNet').GetConnectionProperties()

    def Refresh(self):
        while not self.destroyed:
            uthread2.Sleep(self.refreshDelaySeconds)
            self.PopulateLabels()

    def PopulateLabels(self, initialize = False):
        self.ticker += self.intvals[0]
        if self.ticker > self.intvals[-1]:
            self.ticker = self.intvals[0]
        stats = sm.GetService('machoNet').GetConnectionProperties()
        if self.laststats == {}:
            self.laststats = stats
        if self.lastresetstats != {}:
            for key in stats.iterkeys():
                stats[key] = stats[key] - self.lastresetstats[key]

        for i in xrange(len(self.counter) - 1):
            self.counter[i].append([ stats[key] - self.laststats[key] for header, key, K in PROPS ])
            self.counter[i] = self.counter[i][-(self.intvals[i] / 1000):]

        self.counter[-1].append([ stats[key] - self.laststats[key] for header, key, K in PROPS ])
        if not self.display and not initialize:
            self.laststats = stats
            return
        valueIdx = 0
        for header, key, K in PROPS:
            statusstr = '%s' % header
            for intvals in self.counter:
                value = reduce(operator.add, [ intval[valueIdx] for intval in intvals ], 0)
                if not value:
                    statusstr += '<t><right>-'
                else:
                    statusstr += '<t><right>%s' % [value, '%.1f' % (value / 1024.0)][K]

            self.statusLabels[valueIdx].text = statusstr
            valueIdx += 1

        self.statusLabels[valueIdx].text = 'Outstanding<t><right>%s' % stats['calls_outstanding']
        valueIdx += 1
        self.statusLabels[valueIdx].text = 'Blocking Calls<t><right>%s' % stats['blocking_calls']
        valueIdx += 1
        block_time = stats['blocking_call_times']
        if block_time >= 0:
            secs = SecsFromBlueTimeDelta(block_time)
            self.statusLabels[valueIdx].text = 'Blocking time<t><right>%sH<t><right>%sM<t><right>%sS' % HoursMinsSecsFromSecs(secs)
            valueIdx += 1
        elif not hasattr(self, 'warnedBlockingTimeNegative'):
            self.warnedBlockingTimeNegative = True
            log.LogTraceback('Blocking time is negative?')
        machonet_ping = self.get_machonet_ping_time()
        self.statusLabels[valueIdx].text = 'Machonet Ping<t><right>%s' % machonet_ping
        valueIdx += 1
        grpc_stats = self.get_grpc_stats()
        self.statusLabels[valueIdx].text = 'Event Publ. Ping<t><right>%s' % grpc_stats['event_publisher_ping']
        valueIdx += 1
        self.statusLabels[valueIdx].text = 'Req. Broker Ping<t><right>%s' % grpc_stats['request_broker_ping']
        valueIdx += 1
        self.grpc_event_publisher_details[0].text = 'Event Publisher: %s' % grpc_stats['event_publisher_details']
        self.grpc_request_broker_details[0].text = 'Request Broker: %s' % grpc_stats['request_broker_details']
        self.laststats = stats

    def get_machonet_ping_time(self):
        if sm.services['machoNet'] is not None and sm.services['machoNet'].IsConnected():
            stat = sm.services['machoNet'].Ping(1, silent=True)
            startTime = stat[0][1]
            endTime = stat[-1][1]
            took = endTime - startTime
            return took / const.MSEC
        else:
            return -1

    def get_grpc_stats(self):
        publicGateway = sm.services['publicGatewaySvc']
        if publicGateway is None:
            return
        result = {'event_publisher_ping': publicGateway.get_event_publisher_rtt(),
         'event_publisher_details': self.format_details(publicGateway.get_event_publisher_details()),
         'request_broker_ping': publicGateway.get_request_broker_rtt(),
         'request_broker_details': self.format_details(publicGateway.get_request_broker_details())}
        return result

    def format_details(self, details):
        import pprint
        return pprint.pformat(details, width=1)
