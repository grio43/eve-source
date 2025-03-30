#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\utils.py
import blue

def IsExeFile():
    try:
        import stackless
        return True
    except:
        return False


def Pump():
    if IsExeFile():
        blue.synchro.Yield()
    else:
        blue.os.Pump()


def GetIconFileFromSheet(iconNo):

    def _GetIconSize(sheetNum):
        sheetNum = int(sheetNum)
        one = [90,
         91,
         92,
         93]
        two = [17,
         18,
         19,
         28,
         29,
         32,
         33,
         59,
         60,
         61,
         65,
         66,
         67,
         80,
         85,
         86,
         87,
         88,
         89,
         102,
         103,
         104]
        eight = [22,
         44,
         75,
         77,
         105]
        sixteen = [38, 73]
        if sheetNum in one:
            return 256
        if sheetNum in two:
            return 128
        if sheetNum in eight:
            return 32
        if sheetNum in sixteen:
            return 16
        return 64

    if not iconNo:
        return
    if 'res:' in iconNo or 'cache:' in iconNo:
        return iconNo
    if iconNo.startswith('ui_'):
        return iconNo.replace('ui_', 'res:/ui/texture/icons/')
    parts = iconNo.split('_')
    if len(parts) == 2:
        sheet, ix = parts
        size = _GetIconSize(sheet)
        return 'res:/ui/texture/icons/%s_%s_%s.png' % (int(sheet), int(size), int(ix))
