#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\marketOrdersUtil.py
from carbon.common.script.util.format import FmtDateEng
from carbonui.util.stringManip import SanitizeFilename
import blue
from localization import GetByLabel

def ExportToFile(fileName, orders):
    if len(orders) == 0:
        eve.Message('CustomInfo', {'info': GetByLabel('UI/Market/MarketWindow/ExportNoData')})
        return
    f = blue.classes.CreateInstance('blue.ResFile')
    directory = blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/logs/Marketlogs/'
    filename = '%s-%s.txt' % (fileName, FmtDateEng(blue.os.GetWallclockTime(), 'ls').replace(':', ''))
    filename = SanitizeFilename(filename)
    if not f.Open(directory + filename, 0):
        f.Create(directory + filename)
    first = 1
    numSell = numBuy = 0
    for order in orders:
        if first:
            for key in order.__columns__:
                f.Write('%s,' % key)
                if key == 'charID':
                    f.Write('charName,')
                elif key == 'regionID':
                    f.Write('regionName,')
                elif key == 'stationID':
                    f.Write('stationName,')
                elif key == 'solarSystemID':
                    f.Write('solarSystemName,')

            f.Write('\r\n')
            first = 0
        for key in order.__columns__:
            o = getattr(order, key, None)
            if key == 'bid':
                if o > 0:
                    numBuy += 1
                else:
                    numSell += 1
            if key == 'issueDate':
                f.Write('%s,' % FmtDateEng(o, 'el').replace('T', ' '))
            elif key == 'charID':
                f.Write('%s,%s,' % (o, str(cfg.eveowners.Get(o).name.encode('utf-8'))))
            elif key in ('stationID', 'regionID', 'solarSystemID'):
                f.Write('%s,%s,' % (o, cfg.evelocations.Get(o).name.encode('utf-8')))
            else:
                f.Write('%s,' % o)

        f.Write('\r\n')

    f.Close()
    eve.Message('PersonalMarketExportInfo', {'sell': numSell,
     'buy': numBuy,
     'filename': '<b>' + filename + '</b>',
     'directory': '<b>%s</b>' % directory})
