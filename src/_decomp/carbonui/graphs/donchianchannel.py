#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\donchianchannel.py
from graphsutil import MovingHigh, MovingLow
from carbonui.graphs.minmaxareagraph import MinMaxAreaGraph

class DonchianChannel(MinMaxAreaGraph):
    default_name = 'donchianchannel'

    def ApplyAttributes(self, attributes):
        attributes['values'] = zip(MovingLow(attributes['values'][0]), MovingHigh(attributes['values'][1]))
        MinMaxAreaGraph.ApplyAttributes(self, attributes)
