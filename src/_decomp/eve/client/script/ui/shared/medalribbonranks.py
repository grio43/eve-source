#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\medalribbonranks.py
import sys
import utillib
from carbon.common.script.util.commonutils import GetAttrs
from carbonui import fontconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE, EVE_SMALL_FONTSIZE
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.control.window import Window
from eve.client.script.ui.util import uix
import localization
import carbonui.const as uiconst
import trinity
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.control.colorpicker import ColorPreview
from eve.client.script.ui.control.entries.label_text import LabelTextTop
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.shared.neocom.wallet import walletUtil

class Rank(Container):
    __guid__ = 'xtriui.Rank'
    rank = None
    warFactionID = None

    def Startup(self, warFactionID = None, rank = None):
        self.SetWarFaction(warFactionID)
        self.SetRank(rank)
        self.Flush()
        self.sr.rank = uix.GetRankSprite(rank, warFactionID, uiconst.TOALL)
        self.children.insert(0, self.sr.rank)

    def SetWarFaction(self, warFactionID):
        self.warFactionID = warFactionID

    def SetRank(self, rank):
        self.rank = rank


class LayerBase(Container):
    __guid__ = 'xtriui.LayerBase'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.lname = None
        self.inited = False
        self.typeID = None
        self.selected = False
        self.idx = None
        self.data = []
        self.retdata = {}
        self.prettydata = {}
        self.sr.dad = None
        self.type = ''

    def Startup(self, name = 'Layer', data = None):
        self.name = '%sBase' % name
        if self.lname is None:
            self.lname = name
        self.Flush()
        self.LoadData(data)
        self.sr.selection = Fill(parent=self, padding=(1, 2, 2, 2), color=(1.0, 1.0, 1.0, 0.25))
        self.sr.selection.name = 'selected'
        self.SetSelected()

    def GetData(self, *args):
        return self.retdata

    def GetPrettyData(self, *args):
        self.prettydata = {}
        i = 1
        for lid, (type, mapping, color) in self.retdata.iteritems():
            if type and mapping:
                self.prettydata[i] = (type, mapping, color)
                i = i + 1

        return self.prettydata

    def LoadData(self, data = None, layerid = 0):
        if data is None:
            return
        self.data = data
        for lid, (type, mapping, color) in enumerate(data):
            if len(data) == 1:
                lid = layerid
            par = self.GetLayer(lid)
            if not par:
                par = Container(parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), clipChildren=0, state=uiconst.UI_HIDDEN)
                par.name = '%sLayer%s' % (self.lname, lid)
            spr = self.GetSprite(lid)
            if not spr:
                sprite = Sprite(parent=par, align=uiconst.TOALL, left=0, lockAspect=1, state=uiconst.UI_DISABLED)
                sprite.name = '%sSprite%s' % (self.lname, lid)
            if mapping != None:
                self.SetSprite(lid, type, mapping)
            if color is not None and color != -1:
                self.SetSpriteColor(lid, color)

    def SetSelected(self, selected = False):
        self.selected = selected
        if selected:
            self.sr.selection.state = uiconst.UI_DISABLED
        else:
            self.sr.selection.state = uiconst.UI_HIDDEN
        par = self.FindParentByName('ImageSlider')
        if par:
            par.mastertype = self.type

    def IsSelected(self):
        return bool(self.sr.selection.state == uiconst.UI_DISABLED)

    def GetLayer(self, id):
        obj = self.FindChild('%sLayer%s' % (self.lname, id))
        if obj:
            return obj

    def GetSprite(self, id):
        obj = self.FindChild('%sSprite%s' % (self.lname, id))
        if obj:
            return obj

    def GetSpriteColor(self, id):
        obj = self.GetSprite(id)
        if obj:
            return trinity.TriColor(*obj.color.GetRGBA()).AsInt()

    def ClearSprite(self, id):
        self.SetSprite(id, '', '')

    def SetSprite(self, id, type, mapping):
        obj = self.GetSprite(id)
        if not obj:
            return
        self.type = type
        lay = self.GetLayer(id)
        if lay:
            if type and mapping:
                lay.state = uiconst.UI_PICKCHILDREN
            else:
                lay.state = uiconst.UI_HIDDEN
            if not self.retdata.has_key(lay):
                self.retdata[id] = (type, mapping, self.GetSpriteColor(id))
            curr = self.retdata[id]
            self.retdata[id] = (type, mapping, self.GetSpriteColor(id))
        return obj

    def SetSpriteColor(self, id, color):
        obj = self.GetSprite(id)
        if obj:
            c = trinity.TriColor()
            c.FromInt(color)
            obj.color = (c.r,
             c.g,
             c.b,
             c.a)
            if not self.retdata.has_key(id):
                self.retdata[id] = ('', None, 0)
            curr = self.retdata[id]
            self.retdata[id] = (curr[0], curr[1], color)

    def SetHSV(self, id, hsv):
        if not self or self.destroyed:
            return
        obj = self.GetSprite(id)
        if obj:
            obj.color.SetHSV(*hsv)
            if not self.retdata.has_key(id):
                self.retdata[id] = ('', 0)
            curr = self.retdata[id]
            colInt = trinity.TriColor(*obj.color.GetRGBA()).AsInt()
            self.retdata[id] = (curr[0], curr[1], colInt)

    def MapLogo(self, iconNum, sprite, root):
        texpix, num = iconNum.split('_')
        while texpix.find('0') == 0:
            texpix = texpix[1:]

        texturePath = '%s%s%s.dds' % (root, ['', '0'][int(texpix) < 10], texpix)
        sprite.SetTexturePath(str(texturePath))
        num = int(num)
        sprite.rectWidth = sprite.rectHeight = 128
        sprite.rectLeft = [0, 128][num in (2, 4)]
        sprite.rectTop = [0, 128][num > 2]


class Medal(LayerBase):
    __guid__ = 'xtriui.Medal'
    typeID = const.typeMedal

    def Startup(self, data = None):
        self.Flush()
        LayerBase.Startup(self, 'Medal', data)

    def SetSprite(self, id, type, iconNum):
        obj = LayerBase.SetSprite(self, id, type, iconNum)
        if iconNum and type and obj:
            self.MapLogo(iconNum, obj, root='res:/UI/Texture/Medals/Medals/%s' % type.lower())
        return obj


class Ribbon(LayerBase):
    __guid__ = 'xtriui.Ribbon'
    typeID = const.typeRibbon

    def Startup(self, data = None):
        self.Flush()
        LayerBase.Startup(self, 'Ribbon', data)

    def SetSprite(self, id, type, iconNum):
        obj = LayerBase.SetSprite(self, id, type, iconNum)
        if iconNum and type and obj:
            self.MapLogo(iconNum, obj, root='res:/UI/Texture/Medals/Ribbons/%s' % type.lower())
        return obj


class MedalRibbon(Container):
    __guid__ = 'xtriui.MedalRibbon'

    def Startup(self, data = None, size = 128, *args):
        ribbondata = []
        medaldata = []
        if data is None:
            data = []
        else:
            ribbon, ribbondata = data[0]
            medal, medaldata = data[1]
        top = 0
        imgSize = size / 2
        for i, (each, obj, data, toppush, size) in enumerate((('ribbon',
          ribbon,
          ribbondata,
          0,
          imgSize), ('medal',
          medal,
          medaldata,
          float(imgSize) - float(imgSize) * 20.0 / 128.0,
          imgSize))):
            mr = obj(name=each, parent=self, align=uiconst.TOPLEFT, left=0, top=top + int(toppush), width=size, height=size, state=uiconst.UI_NORMAL)
            mr.Startup(data)
            setattr(self.sr, each, mr)
            top += toppush


class ImageSlider(Container):
    __guid__ = 'xtriui.ImageSlider'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.initing = False
        self.data = None
        self.curridx = 0
        self.cursoridx = 0
        self.visiblecount = 2
        self.isBrowsing = False
        self.sr.dad = None
        self.sr.dadlayer = None
        self.isTabStop = 1
        self.sr.activeframe = None
        self.selected = 0
        self.keepselection = False
        self.width += 4

    def Startup(self, dataset, *args):
        self.data = dataset
        self.isTabStop = 1
        l, t, w, h = self.GetAbsolute()
        self.Flush()
        self.visiblecount = w / h - 1
        self.actualcount = min(len(self.data), self.visiblecount)
        self.maximumcount = min(len(self.data), self.visiblecount) + 2
        self.boundaryLeft = 0
        self.boundaryRight = len(self.data) - self.visiblecount
        prv = Container(name='ImgSliderPrev', align=uiconst.TOLEFT, width=h / 2, parent=self)
        prv.OnClick = (self.Browse, -1)
        self.sr.prev = prv
        Frame(parent=prv, color=(1.0, 1.0, 1.0, 0.125))
        Container(name='push', align=uiconst.TOLEFT, width=2, parent=self)
        eveIcon.Icon(icon='ui_38_16_223', parent=prv, size=16, left=0, top=0, align=uiconst.CENTER, state=uiconst.UI_DISABLED, hint=localization.GetByLabel('UI/Corporations/CreateDecorationWindow/PreviousItem'))
        Fill(parent=prv, color=(0.0, 0.0, 0.0, 0.25))
        nxt = Container(name='ImgSliderNext', align=uiconst.TORIGHT, width=h / 2, parent=self)
        nxt.OnClick = (self.Browse, 1)
        self.sr.next = nxt
        Frame(parent=nxt, color=(1.0, 1.0, 1.0, 0.125))
        Container(name='push', align=uiconst.TORIGHT, width=2, parent=self)
        eveIcon.Icon(icon='ui_38_16_224', parent=nxt, size=16, left=0, top=0, align=uiconst.CENTER, state=uiconst.UI_DISABLED, hint=localization.GetByLabel('UI/Corporations/CreateDecorationWindow/NextItem'))
        Fill(parent=nxt, color=(0.0, 0.0, 0.0, 0.25))
        self.sr.mainpar = Container(name='ImgSliderMainPar', parent=self, align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        self.sr.main = Container(name='ImgSliderMain', parent=self.sr.mainpar, align=uiconst.TOALL, state=uiconst.UI_NORMAL, clipChildren=1)
        self.sr.backgroundFrame = PanelUnderlay(parent=self, padding=(-1, -1, -1, -1))
        Fill(parent=self, color=(0.0, 0.0, 0.0, 0.25))
        self.Initialize()

    def Initialize(self, *args):
        if self.initing:
            return
        self.initing = True
        self.PrepareData()
        self.Browse(0)
        self.initing = False

    def PrepareData(self):
        l, t, w, h = self.GetAbsolute()
        for i in range(self.visiblecount + 2):
            try:
                obj, ret = self.data[i - 1]
            except:
                obj, ret = (None, None)
                sys.exc_clear()

            slimdeco = self.sr.main.FindChild('cont_%s' % i)
            if slimdeco is None:
                slimdeco = Container(name='cont_%s' % i, parent=self.sr.main, align=uiconst.TOLEFT, left=0, top=0, width=h, state=uiconst.UI_NORMAL)
            self.SetObject(slimdeco, obj, ret)
            if i == 0:
                left = 0

        if self.actualcount < self.visiblecount:
            self.sr.main.children[-1].Close()

    def GetActiveFrame(self):
        if self.sr.activeframe is None:
            self.sr.activeframe = Frame(parent=self.sr.mainpar, left=0, top=0, width=0, height=0, color=(1.0,
             1.0,
             1.0,
             uiconst.ACTIVE_FRAME_ALPHA), idx=0, state=uiconst.UI_HIDDEN)

    def SetObject(self, parent, obj, ret, direction = None):
        if None in (parent, obj, ret):
            return
        se = obj(name='', parent=parent, align=uiconst.TOALL, state=uiconst.UI_NORMAL, pos=(0, 0, 0, 0), idx=0)
        se.Startup(ret)
        se.OnClick = (self.OnChildMouseClicked, se)
        if direction == -1:
            se.idx = max(0, self.curridx - 1)
        else:
            se.idx = len(self.sr.main.children) - 2 + self.curridx
        se.sr.dad = self
        parent.sr.obj = se

    def OnChildMouseClicked(self, object, *args):
        self.cursoridx = object.idx + 1
        self.OnChildClick(object)

    def OnChildClick(self, object, *args):
        for each in self.sr.main.children:
            selector = GetAttrs(each, 'sr', 'obj', 'SetSelected')
            if selector is not None:
                selector()

        object.SetSelected(True)
        self.sr.dad.LoadData(object.data, self.sr.dadlayer)
        self.PostOnClick(self)

    def PostOnClick(self, *args):
        pass

    def SetParentListener(self, object, layer = None):
        self.sr.dad = object
        self.sr.dadlayer = layer

    def GetEntry(self, idx):
        se = self.FindChild('sliderEntry_%s' % idx)
        if se:
            return se

    def OnSetFocus(self, *args):
        self.GetActiveFrame()
        if self.sr.activeframe:
            self.sr.activeframe.state = uiconst.UI_DISABLED

    def OnKillFocus(self, *args):
        self.GetActiveFrame()
        if self.sr.activeframe:
            self.sr.activeframe.state = uiconst.UI_HIDDEN

    def OnLeft(self, *args):
        self.DelegateControl(-1)

    def OnRight(self, *args):
        self.DelegateControl(1)

    def DelegateControl(self, direction, *args):
        if self.isBrowsing:
            return
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        self.cursoridx += direction
        self.cursoridx = self.GetCurrentCursor()
        index = self.cursoridx - self.curridx
        numChildren = len(self.sr.main.children)
        if index < 0:
            self.cursoridx = self.curridx + 1
            self.cursoridx = self.GetCurrentCursor()
        elif index > numChildren - 1:
            self.cursoridx = self.curridx + numChildren - 2
            self.cursoridx = self.GetCurrentCursor()
        obj = self.sr.main.children[self.cursoridx - self.curridx].sr.obj
        self.OnChildClick(obj)
        if direction == 1:
            if self.cursoridx > self.curridx + self.visiblecount:
                self.Browse(direction)
        elif direction == -1:
            if self.cursoridx <= self.curridx:
                self.Browse(direction)

    def IsRightDisabled(self, *args):
        return self.GetCurrentIndex() >= self.boundaryRight

    def IsLeftDisabled(self, *args):
        return self.GetCurrentIndex() <= self.boundaryLeft

    def GetCurrentIndex(self, *args):
        return max(0, min(self.curridx, self.boundaryRight))

    def GetCurrentCursor(self, *args):
        return max(1, min(self.cursoridx, len(self.data)))

    def Browse(self, direction, *args):
        if self.isBrowsing:
            return
        if direction == 2:
            for x in xrange(0, 8):
                self.Browse(1)

        if direction == -2:
            for x in xrange(0, 8):
                self.Browse(-1)

        l, t, w, h = self.GetAbsolute()
        self.isBrowsing = True
        self.curridx += direction
        self.curridx = self.GetCurrentIndex()
        self.cursoridx = self.GetCurrentCursor()
        colors = {'red': (0.4, 0.13, 0.13, 0.8),
         'green': (0.27, 0.53, 0.22, 0.8)}
        if self.IsRightDisabled():
            self.sr.next.state = uiconst.UI_DISABLED
            self.sr.next.opacity = 0.4
        else:
            self.sr.next.state = uiconst.UI_NORMAL
            self.sr.next.opacity = 1.0
        if self.IsLeftDisabled():
            self.sr.prev.state = uiconst.UI_DISABLED
            self.sr.prev.opacity = 0.4
        else:
            self.sr.prev.state = uiconst.UI_NORMAL
            self.sr.prev.opacity = 1.0
        if direction == -1:
            item = self.sr.main.children[-1]
            item.SetOrder(0)
            item.Flush()
            obj, data = self.data[max(0, self.curridx - 1)]
            self.SetObject(item, obj, data, direction=direction)
        elif direction == 1:
            item = self.sr.main.children[0]
            item.SetOrder(-1)
            item.Flush()
            obj, data = self.data[min(self.curridx + self.visiblecount, len(self.data) - 1)]
            self.SetObject(item, obj, data, direction=direction)
        self.sr.main.children[0].left = -h
        for i, each in enumerate(self.sr.main.children[:]):
            if i > 0:
                each.left = 0

        self.isBrowsing = False


class MedalRibbonPickerWindow(Window):
    __guid__ = 'form.MedalRibbonPickerWindow'
    default_windowID = 'MedalRibbonPickerWindow'
    default_iconNum = 'res:/ui/Texture/WindowIcons/corporationdecorations.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.submitting = False
        self.currentselection = None
        self.SetCaption(localization.GetByLabel('UI/Corporations/CreateDecorationWindow/Title'))
        self.SetMinSize([465, 630])
        self.MakeUnResizeable()
        self.AddSliders()

    def SubmitData(self, *args):
        if self.submitting:
            return
        self.submitting = True
        missingFields = []
        mName = self.sr.medalname.GetValue()
        if not bool(mName):
            missingFields.append(localization.GetByLabel('UI/Corporations/CreateDecorationWindow/DecorationName'))
        mDesc = self.sr.medaldesc.GetAllText()
        if not bool(mDesc):
            missingFields.append(localization.GetByLabel('UI/Corporations/CreateDecorationWindow/Description'))
        rData = self.sr.medalribbonobject.sr.ribbon.GetPrettyData()
        if not rData:
            missingFields.append(localization.GetByLabel('UI/Corporations/CreateDecorationWindow/Ribbon'))
        mData = self.sr.medalribbonobject.sr.medal.GetPrettyData()
        if not mData:
            missingFields.append(localization.GetByLabel('UI/Corporations/CreateDecorationWindow/Medal'))
        walletAccess = walletUtil.HaveAccessToCorpWalletDivision(session.corpAccountKey)
        if not walletAccess:
            if eve.Message('SelectWalletDivision', {}, uiconst.YESNO) == uiconst.ID_YES:
                walletUtil.SelectWalletDivision()
            else:
                missingFields.append(localization.GetByLabel('UI/Corporations/CreateDecorationWindow/ActiveWalletDivision'))
        k = getattr(eve.session, 'corpAccountKey')
        if k is None and localization.GetByLabel('UI/Corporations/CreateDecorationWindow/ActiveWalletDivision') not in missingFields:
            missingFields.append(localization.GetByLabel('UI/Corporations/CreateDecorationWindow/ActiveWalletDivision'))
        if missingFields:
            eve.Message('GenericMissingInfo', {'fields': localization.GetByLabel('UI/Map/StarMap/lblBoldName', name=', '.join(missingFields))})
            self.submitting = False
            return
        cMedalData = []
        for lid, (type, mapping, color) in rData.iteritems():
            cMedalData.append([1, '.'.join((type, mapping)), color])

        for lid, (type, mapping, color) in mData.iteritems():
            cMedalData.append([2, '.'.join((type, mapping)), color])

        try:
            sm.StartService('medals').CreateMedal(mName, mDesc, cMedalData)
            self.Close()
        finally:
            self.submitting = False

    def AddSliders(self, *args):
        self.currentselection = None
        self.ribbonsliders = []
        self.medalsliders = []
        self.sr.main.Flush()
        ribbondata = [Ribbon, [('', None, None),
          ('', None, None),
          ('', None, None),
          ('', None, None),
          ('', None, None)]]
        medaldata = [Medal, [('', None, None),
          ('', None, None),
          ('', None, None),
          ('', None, None)]]
        top = 0
        imgSize = 128
        self.sr.buttoncont = ContainerAutoSize(name='Buttons', align=uiconst.TOBOTTOM, parent=self.sr.main)
        self.sr.mainpar = Container(name='MainPar', align=uiconst.TOALL, parent=self.sr.main, pos=(0, 0, 0, 0))
        mp = Container(name='Left', align=uiconst.TOLEFT, width=imgSize, left=const.defaultPadding, top=const.defaultPadding, parent=self.sr.mainpar)
        medalribbonobject = MedalRibbon(name='MedalRibbonParent', width=128, height=256, parent=mp, align=uiconst.CENTER)
        medalribbonobject.Startup([ribbondata, medaldata], imgSize * 2)
        self.sr.medalribbonobject = medalribbonobject
        btns = []
        btns.append([localization.GetByLabel('UI/Corporations/CreateDecorationWindow/Submit'),
         self.SubmitData,
         None,
         None])
        btns.append([localization.GetByLabel('UI/Corporations/CreateDecorationWindow/Reset'),
         self.AddSliders,
         None,
         None])
        buttons = ButtonGroup(btns=btns, parent=self.sr.buttoncont, button_size_mode=ButtonSizeMode.DYNAMIC)
        self.sr.mainselector = Container(name='MainSelector', align=uiconst.TOALL, parent=self.sr.mainpar, pos=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        uix.GetContainerHeader(localization.GetByLabel('UI/Contracts/BasicInfo'), self.sr.mainselector, 0)
        Container(name='push', align=uiconst.TOTOP, height=6, parent=self.sr.mainselector)
        medalnamecont = Container(parent=self.sr.mainselector, align=uiconst.TOTOP)
        Container(name='push', align=uiconst.TOTOP, height=24, parent=medalnamecont)
        Container(name='push', align=uiconst.TOLEFT, width=4, parent=medalnamecont)
        Container(name='push', align=uiconst.TORIGHT, width=4, parent=medalnamecont)
        self.sr.medalname = SingleLineEditText(name='medalname', parent=medalnamecont, setvalue=None, pos=(0, 12, 284, 0), label=localization.GetByLabel('UI/Corporations/CreateDecorationWindow/DecorationName'), maxLength=100)
        top = const.defaultPadding + self.sr.medalname.top + self.sr.medalname.height
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Corporations/CreateDecorationWindow/Description'), parent=medalnamecont, top=top, width=100)
        self.sr.medaldesc = EditPlainText(setvalue='', parent=medalnamecont, align=uiconst.TOPLEFT, name='medaldesc', maxLength=1000, top=top + 16, left=-1, width=286, height=64)
        medalnamecont.height = self.sr.medalname.height + self.sr.medaldesc.height + 8 + 23
        Container(name='push', align=uiconst.TOTOP, height=4, parent=self.sr.mainselector)
        uix.GetContainerHeader(localization.GetByLabel('UI/Corporations/CreateDecorationWindow/Ribbon'), self.sr.mainselector, 1)
        labels = ['caldari',
         'minmatar',
         'gallente',
         'amarr']
        data = []
        for label in labels:
            data.append([Ribbon, [(label, '1_1', None),
              ('', None, None),
              ('', None, None),
              ('', None, None),
              (label, '1_2', None)]])

        slider = self.GetImageSlider(data)
        slider.SetParentListener(self.sr.medalribbonobject.sr.ribbon, None)
        slider.SetAlign(uiconst.TOPRIGHT)
        slider.PostOnClick = self.PostOnClick
        self.sr.baseribbonslider = slider
        self.ribbonsliders.append(slider)
        parent = slider.parent
        colorPreview = ColorPreview(name='colorPreview', align=uiconst.TORIGHT, height=32, width=32)
        Frame(parent=colorPreview, color=(1.0, 1.0, 1.0, 0.5))
        colorPreview.Startup()
        colorPreview.sr.layerid = 4
        colorPreview.sr.dad = self.sr.medalribbonobject.sr.ribbon
        colorPreview.FromInt(-330271)
        colorPreview.state = uiconst.UI_HIDDEN
        push = Container(name='push', align=uiconst.TORIGHT, height=32, width=4)
        slider.parent.children.insert(0, push)
        slider.parent.children.insert(0, colorPreview)
        ranger = range(1, 4)
        ranger.reverse()
        for x in ranger:
            data = []
            data = self.GetRibbonShapeData('Caldari')
            slider = self.GetImageSlider(data, True)
            slider.SetParentListener(self.sr.medalribbonobject.sr.ribbon, x)
            slider.SetAlign(uiconst.TOPRIGHT)
            slider.PostOnClick = self.PostOnClick
            parent = slider.parent
            self.AddSliderReset(slider)
            colorPreview = ColorPreview(name='colorPreview', align=uiconst.TORIGHT, width=32, height=32)
            Frame(parent=colorPreview, color=(1.0, 1.0, 1.0, 0.5))
            colorPreview.Startup()
            colorPreview.sr.layerid = x
            colorPreview.sr.dad = self.sr.medalribbonobject.sr.ribbon
            colorPreview.FromInt(-330271)
            colorPreview.state = uiconst.UI_HIDDEN
            push = Container(name='push', align=uiconst.TORIGHT, height=32, width=4)
            slider.parent.children.insert(0, push)
            slider.parent.children.insert(0, colorPreview)
            slider.parent.state = uiconst.UI_HIDDEN
            self.ribbonsliders.append(slider)

        Container(name='push', align=uiconst.TOTOP, height=4, parent=self.sr.mainselector)
        uix.GetContainerHeader(localization.GetByLabel('UI/Corporations/CreateDecorationWindow/Medal'), self.sr.mainselector, 1)
        labels = (('compass', 2),
         ('imperial', 2),
         ('pentagon', 1),
         ('rombus', 1),
         ('round', 6),
         ('shield', 1),
         ('square', 2),
         ('star', 7))
        data = []
        for label, amount in labels:
            for x in xrange(0, amount * 4):
                icon = '%s_%s' % (x / 4 + 1, x % 4 + 1)
                data.append([Medal, [(label, icon, None)]])

        slider = self.GetImageSlider(data)
        slider.SetParentListener(self.sr.medalribbonobject.sr.medal, 3)
        slider.SetAlign(uiconst.TOPRIGHT)
        slider.PostOnClick = self.PostOnClick
        self.sr.basemedalslider = slider
        self.medalsliders.append(slider)
        labels = (('elements', 33),)
        ranger = range(0, 3)
        ranger.reverse()
        for i in ranger:
            data = []
            for label, amount in labels:
                for x in xrange(0, amount * 4):
                    icon = '%s_%s' % (x / 4 + 1, x % 4 + 1)
                    data.append([Medal, [(label, icon, None)]])

            slider = self.GetImageSlider(data)
            slider.SetParentListener(self.sr.medalribbonobject.sr.medal, i)
            slider.PostOnClick = self.PostOnClick
            slider.SetAlign(uiconst.TOPRIGHT)
            slider.parent.state = uiconst.UI_HIDDEN
            self.AddSliderReset(slider)
            self.medalsliders.append(slider)

    def AddSliderReset(self, slider):
        rem = Container(name='ImgSliderRemove', align=uiconst.TOLEFT, width=16, height=32)
        Frame(parent=rem, color=(1.0, 1.0, 1.0, 0.125))
        dbtn = eveIcon.Icon(icon='ui_38_16_111', parent=rem, size=16, left=0, top=0, align=uiconst.CENTER)
        dbtn.OnClick = (self.ResetSlider, dbtn)
        dbtn.hint = localization.GetByLabel('UI/Corporations/CreateDecorationWindow/ResetItem')
        dbtn.slider = slider
        Fill(parent=rem, color=(0.0, 0.0, 0.0, 0.25))
        push = Container(name='push', align=uiconst.TOLEFT, height=32, width=4)
        slider.parent.children.insert(0, rem)
        slider.parent.children.insert(0, push)

    def ResetSlider(self, obj, *args):
        slider = obj.slider
        slider.sr.dad.ClearSprite(slider.sr.dadlayer)
        slider.parent.state = uiconst.UI_HIDDEN

    def PostOnClick(self, obj, *args):
        if obj in self.ribbonsliders:
            idx = self.ribbonsliders.index(obj)
            nidx = idx + 1
            colorPreview = obj.parent.FindChild('colorPreview')
            if colorPreview:
                colorPreview.state = uiconst.UI_PICKCHILDREN
            if len(self.ribbonsliders) <= nidx:
                return
            self.ribbonsliders[nidx].parent.state = uiconst.UI_PICKCHILDREN
            if idx == 0:
                mtype = getattr(obj, 'mastertype', None)
                if mtype is not None and self.currentselection != mtype:
                    for slider in self.ribbonsliders[1:]:
                        slider.sr.dad.ClearSprite(slider.sr.dadlayer)
                        data = self.GetRibbonShapeData(mtype)
                        slider.Startup(data)

        elif obj in self.medalsliders:
            idx = self.medalsliders.index(obj)
            nidx = idx + 1
            if len(self.medalsliders) <= nidx:
                return
            self.medalsliders[nidx].parent.state = uiconst.UI_PICKCHILDREN
        self.currentselection = getattr(self.ribbonsliders[0], 'mastertype', None)

    def GetImageSlider(self, data, ks = False, *args):
        size, amount = (32, 7)
        cont = Container(name='ImageSliderPar', parent=self.sr.mainselector, align=uiconst.TOTOP, height=size, top=const.defaultPadding, state=uiconst.UI_NORMAL)
        slider = ImageSlider(name='ImageSlider', parent=cont, clipChildren=0, align=uiconst.TOPLEFT, width=size * amount, height=size, left=const.defaultPadding + size, state=uiconst.UI_NORMAL)
        if ks:
            slider.keepselection = True
        slider.Startup(data)
        return slider

    def GetRibbonShapeData(self, selectedRace, *args):
        labels = [(selectedRace, 11)]
        ret = []
        for label, amount in labels:
            for x in xrange(4, amount):
                icon = '%s_%s' % (x / 4 + 1, x % 4 + 1)
                ret.append([Ribbon, [(label, icon, None)]])

        return ret


class RankEntry(LabelTextTop):
    __guid__ = 'listentry.RankEntry'
    __params__ = ['label',
     'text',
     'warFactionID',
     'rank']

    def Startup(self, *args):
        LabelTextTop.Startup(self, *args)
        rankobject = Rank(name='rankobject', align=uiconst.CENTERLEFT, left=3, parent=self, idx=0)
        self.sr.rankobject = rankobject

    def Load(self, node):
        LabelTextTop.Load(self, node)
        self.sr.label.left = self.sr.text.left = self.height + 10
        self.sr.label.top = 9
        self.sr.text.top = self.sr.label.top + self.sr.label.textheight
        size = node.Get('iconsize', 48)
        self.sr.rankobject.width = self.sr.rankobject.height = size
        self.sr.rankobject.Startup(node.warFactionID, node.rank)

    def ShowInfo(self, *args):
        typeID = self.sr.node.Get('typeID', None)
        warFactionID = self.sr.node.Get('warFactionID', None)
        currentRank = self.sr.node.Get('rank', None)
        if None not in (typeID, warFactionID, currentRank):
            abstractinfo = utillib.KeyVal(warFactionID=warFactionID, currentRank=currentRank)
            sm.GetService('info').ShowInfo(typeID, abstractinfo=abstractinfo)

    def GetHeight(self, *args):
        node, width = args
        iconSize = node.Get('iconsize', 48)
        labelheight = uix.GetTextHeight(node.label, fontsize=fontconst.EVE_SMALL_FONTSIZE, maxLines=1, uppercase=1)
        textheight = uix.GetTextHeight(node.text, fontsize=fontconst.EVE_MEDIUM_FONTSIZE, maxLines=1)
        node.height = max(iconSize, 18 + labelheight + textheight)
        return node.height


class MedalRibbonEntry(LabelTextTop):
    __guid__ = 'listentry.MedalRibbonEntry'
    __params__ = ['label', 'text', 'abstractinfo']

    def Startup(self, *args):
        LabelTextTop.Startup(self, *args)
        medalribbonobject = MedalRibbon(name='MedalRibbonParent', parent=self, align=uiconst.TOPLEFT, width=32, height=32, left=1, top=1)
        self.sr.medalribbonobject = medalribbonobject

    def Load(self, node):
        LabelTextTop.Load(self, node)
        self.sr.medalribbonobject.Flush()
        typeID = node.Get('typeID', None)
        itemID = node.Get('itemID', None)
        abstractinfo = node.Get('abstractinfo', None)
        if None not in (typeID, itemID, abstractinfo):
            self.sr.infoicon.state = uiconst.UI_NORMAL
        else:
            self.sr.infoicon.state = uiconst.UI_HIDDEN
        size = node.Get('iconsize', 32)
        self.sr.icon.state = uiconst.UI_HIDDEN
        self.sr.medalribbonobject.width = size * 2
        self.sr.medalribbonobject.height = size
        self.sr.medalribbonobject.left = 8
        self.sr.medalribbonobject.top = 3
        self.sr.medalribbonobject.Startup(node.abstractinfo, size)
        self.sr.label.left = self.sr.text.left = 32

    def ShowInfo(self, *args):
        if self.sr.node.Get('typeID', None) and self.sr.node.Get('abstractinfo', None):
            sm.GetService('info').ShowInfo(self.sr.node.typeID, self.sr.node.itemID, abstractinfo=self.sr.node.Get('abstractinfo', None))

    def GetHeight(self, *args):
        node, width = args
        labelheight = uix.GetTextHeight(node.label, fontsize=EVE_SMALL_FONTSIZE, maxLines=1, uppercase=1)
        textheight = uix.GetTextHeight(node.text, fontsize=EVE_MEDIUM_FONTSIZE, maxLines=1)
        size = node.Get('iconsize', 32)
        node.height = max(labelheight + textheight, size) + 2
        return node.height
