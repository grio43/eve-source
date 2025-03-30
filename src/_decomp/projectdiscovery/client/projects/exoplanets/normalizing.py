#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\normalizing.py


class Normalizer:

    def __init__(self):
        self.nboptions = [7,
         35,
         71,
         169]
        self.nboption = 1
        self.nbiter = 10
        self.cutlevel = 0.995
        self.windowSize = self.nboptions[self.nboption]

    def CutFilter(self, x, y):
        if x < self.cutlevel * y:
            return y
        else:
            return x

    def CumulativeSum(self, input):
        aggregator = 0
        output = [ 0 for _ in input ]
        for i in range(len(input)):
            aggregator += input[i]
            output[i] = aggregator

        return output

    def GetTrendCurve(self, curve = None):
        if curve is None:
            curve = self.fluxCurve
        return self.TrendAlgorithm(curve)[0]

    def GetDetrendCurve(self, curve = None):
        if curve is None:
            curve = self.fluxCurve
        return self.TrendAlgorithm(curve)[1]

    def TrendAlgorithm(self, curve = None):
        for i in range(self.nbiter):
            mean = sum(curve) / len(curve)
            normalized = [ x / mean for x in curve ]
            cumulativeSum = self.CumulativeSum(normalized)
            windowSum = cumulativeSum[:self.windowSize] + [ cumulativeSum[self.windowSize + k] - cumulativeSum[k] for k in range(len(cumulativeSum) - self.windowSize) ]
            rollingAverage = [ mean * windowSum[self.windowSize - 1 + k] / self.windowSize for k in range(len(windowSum) - (self.windowSize - 1)) ]
            trendLine = [ rollingAverage[0] for k in range(self.windowSize / 2) ] + rollingAverage + [ rollingAverage[-1] for k in range(self.windowSize / 2) ]
            if map(self.CutFilter, curve, trendLine) == curve:
                break
            curve = map(self.CutFilter, curve, trendLine)

        return [curve, trendLine]

    def DetrendCurve(self, curve):
        if not self.nbiter or not self.windowSize:
            return curve
        time_values, flux_values = zip(*curve)
        detrendCurve = self.GetDetrendCurve(flux_values)
        mean = sum(flux_values) / len(curve)
        new_flux_values = [ mean * flux_values[i] / detrendCurve[i] for i in range(len(flux_values)) ]
        return zip(time_values, new_flux_values)
