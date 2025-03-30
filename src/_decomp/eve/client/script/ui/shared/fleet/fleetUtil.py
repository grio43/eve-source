#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetUtil.py
import evetypes
from carbon.common.script.util.format import FmtDate
import blue

def ExportLootHistory():
    lootHistory = sm.GetService('fleet').GetLootHistory()
    rows = []
    for kv in lootHistory:
        row = [FmtDate(kv.time, 'ss'),
         cfg.eveowners.Get(kv.charID).name,
         evetypes.GetName(kv.typeID),
         kv.quantity,
         evetypes.GetGroupName(kv.typeID)]
        rows.append(row)

    fileNameExtension = 'Loot'
    header = 'Time\tCharacter\tItem Type\tQuantity\tItem Group'
    _ExportToDisk(header, rows, fileNameExtension)


def _ExportToDisk(header, rows, fileNameExtension):
    date = FmtDate(blue.os.GetWallclockTime())
    f = blue.classes.CreateInstance('blue.ResFile')
    directory = blue.sysinfo.GetUserDocumentsDirectory() + '/EVE/logs/Fleetlogs/'
    filename = '%s - %s.txt' % (fileNameExtension, date.replace(':', '.'))
    fullPath = directory + filename
    if not f.Open(fullPath, 0):
        f.Create(fullPath)
    f.Write('%s\r\n' % header)
    for r in rows:
        row = ''
        for col in r:
            row += '%s\t' % unicode(col).encode('utf-8')

        f.Write('%s\r\n' % row)

    f.Write('\r\n')
    f.Close()
    eve.Message('FleetExportInfo', {'filename': filename,
     'folder': directory})


def OnDropInMyFleet(dropObj, nodes):
    if not sm.GetService('fleet').IsCommanderOrBoss():
        return
    myNode = nodes[0]
    try:
        charID = myNode.charID
    except:
        return

    if not charID:
        return
    fleetSvc = sm.GetService('fleet')
    members = fleetSvc.GetMembers()
    if charID in members:
        return
    fleetSvc.Invite(charID, None, None, None)
    eve.Message('CharacterAddedAsSquadMember', {'char': charID})
