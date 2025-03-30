#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\warpVector.py
import geo2
from carbonui import ButtonVariant, ButtonStyle, Density
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import GetClipboardData
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelSmall
from eve.common.lib import appConst
import blue

class WarpVectorWnd(Window):
    __notifyevents__ = []
    default_height = 630
    default_width = 740
    default_minSize = [450, 256]
    default_windowID = 'warpVectorWnd'

    def DebugReload(self, *args):
        self.Reload(self)

    def ApplyAttributes(self, attributes):
        super(WarpVectorWnd, self).ApplyAttributes(attributes)
        reloadBtn = Button(parent=self.content, label='Reload', align=uiconst.TOPRIGHT, func=self.DebugReload, top=0, idx=0)
        self.ConstructLayout()

    def ConstructLayout(self):
        self.vectorContainer = ScrollContainer(name='vectorContainer', parent=self.sr.main, align=uiconst.TOALL, padding=8)
        EveCaptionSmall(parent=self.vectorContainer, text='Set Warp Vectors [m]:', align=uiconst.TOTOP, top=20)
        for i in range(10):
            SetAndWarp(name='vectorEditSection', parent=self.vectorContainer, align=uiconst.TOTOP, width=self.parent.width, height=25, top=25, index=i)


class SetAndWarp(Container):

    def ApplyAttributes(self, attributes):
        super(SetAndWarp, self).ApplyAttributes(attributes)
        self.index = attributes.index
        self.default_value = 0.0
        self.vector = [self.default_value, self.default_value, self.default_value]
        self.ConstructLayout()

    def ConstructLayout(self):
        vectorName = 'Vector {}'.format(self.index + 1)
        savedValueForName = settings.user.ui.Get(self.GetVectorName())
        if savedValueForName is not None:
            vectorName = savedValueForName
        savedValueForX = settings.user.ui.Get(self.GetConfigNameForField(0))
        savedValueForY = settings.user.ui.Get(self.GetConfigNameForField(1))
        savedValueForZ = settings.user.ui.Get(self.GetConfigNameForField(2))
        self.nameEditField = SingleLineEditText(parent=self, align=uiconst.TOLEFT, setvalue=vectorName, width=80, OnChange=self.SetName)
        self.xEditField = SingleLineEditInteger(parent=self, align=uiconst.TOLEFT, setvalue=savedValueForX, OnChange=self.SetX, width=120, left=10, minValue=-appConst.maxBigint, maxValue=appConst.maxBigint)
        self.yEditField = SingleLineEditInteger(parent=self, align=uiconst.TOLEFT, setvalue=savedValueForY, OnChange=self.SetY, width=120, left=10, minValue=-appConst.maxBigint, maxValue=appConst.maxBigint)
        self.zEditField = SingleLineEditInteger(parent=self, align=uiconst.TOLEFT, setvalue=savedValueForZ, OnChange=self.SetZ, width=120, left=10, minValue=-appConst.maxBigint, maxValue=appConst.maxBigint)
        if self.index == 0:
            self.xEditField.SetLabel('x')
            self.yEditField.SetLabel('y')
            self.zEditField.SetLabel('z')
            self.nameEditField.SetLabel('Name')
        button = Button(parent=self, label='Warp!', varient=ButtonVariant.PRIMARY, style=ButtonStyle.NORMAL, align=uiconst.TOLEFT, left=10, func=self.Warp)
        button = Button(parent=self, label='Copy', varient=ButtonVariant.GHOST, align=uiconst.TOLEFT, left=10, func=self.CopyCoords)
        button = Button(parent=self, label='Paste', varient=ButtonVariant.GHOST, align=uiconst.TOLEFT, left=10, func=self.PasteCoords)

    def GetConfigNameForField(self, axis):
        return 'warpvector_%s_%s' % (self.index, axis)

    def GetVectorName(self):
        return 'vectorname_%s' % self.index

    def SetName(self, name):
        settings.user.ui.Set('warpvectorname_%s' % self.index, name)

    def SetX(self, x_value):
        self.vector[0] = x_value
        settings.user.ui.Set('warpvector_%s_%s' % (self.index, 0), x_value)
        print self.vector
        print type(self.vector[0])

    def SetY(self, y_value):
        self.vector[1] = y_value
        settings.user.ui.Set('warpvector_%s_%s' % (self.index, 1), y_value)
        print self.vector

    def SetZ(self, z_value):
        self.vector[2] = z_value
        settings.user.ui.Set('warpvector_%s_%s' % (self.index, 2), z_value)
        print self.vector

    def Warp(self, *args):
        vector_x = float(settings.user.ui.Get(self.GetConfigNameForField(0)))
        vector_y = float(settings.user.ui.Get(self.GetConfigNameForField(1)))
        vector_z = float(settings.user.ui.Get(self.GetConfigNameForField(2)))
        warpVector = [vector_x, vector_y, vector_z]
        current_pos = sm.GetService('slash').SlashCmd('/getpos')
        desired_pos = geo2.Vec3AddD(current_pos, warpVector)
        print 'warpVector.warp:'
        print ('current_pos: ', current_pos)
        print ('self.vector: ', self.vector)
        print ('desired_pos: ', desired_pos)
        sm.GetService('slash').SlashCmd('/warptopoint {} {} {}'.format(desired_pos[0], desired_pos[1], desired_pos[2]))

    def CopyCoords(self, *args):
        blue.pyos.SetClipboardData((self.xEditField.GetValue(), self.yEditField.GetValue(), self.zEditField.GetValue()))

    def PasteCoords(self, *args):
        paste = GetClipboardData()
        import re
        r = re.compile('(.*,.*,.*)')
        if r.match(paste) is None:
            return
        coords = paste.split(',')
        for i in range(len(coords)):
            coords[i] = re.sub('[( )]', '', coords[i])

        self.xEditField.SetText(coords[0])
        self.SetX(coords[0])
        self.yEditField.SetText(coords[1])
        self.SetY(coords[1])
        self.zEditField.SetText(coords[2])
        self.SetZ(coords[2])
