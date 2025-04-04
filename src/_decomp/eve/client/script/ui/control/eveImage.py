#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\eveImage.py
import types
import carbonui.const as uiconst
import dogma.data as dogma_data
import localization
import log
import uthread
from carbon.common.script.util import htmlwriter
from carbonui.control.image import ImageCore
from carbonui.control.link import Link
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.util import stringManip, various_unsorted
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.control.eveIcon import DraggableIcon
from eve.client.script.ui.shared.maps.map2D import Map2D
from eve.client.script.ui.util import uix
from eve.common.script.sys import dbrow, idCheckers
from menu import MenuLabel

class Image(ImageCore):
    __guid__ = 'uicls.Image'
    __notifyevents__ = ['OnPortraitCreated']
    DRAW_LEVELS = {'universe': 0,
     'region': 1,
     'constellation': 2,
     'solarsystem': 3,
     'celestials': 4}
    IMAGE_TYPES = {'portrait',
     'corplogo',
     'factionlogo',
     'starmap',
     'typeicon',
     'icon',
     'res',
     'netres',
     'alliancelogo',
     'racelogo'}
    LOGO_IMAGE_TYPES = {'corplogo',
     'factionlogo',
     'alliancelogo',
     'racelogo'}

    def ApplyAttributes(self, attributes):
        ImageCore.ApplyAttributes(self, attributes)
        self.SetAlign(uiconst.TOPLEFT)

    def LoadAttrs(self, attrs):
        src = attrs.src
        if attrs.texture:
            sprite = Sprite(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
            sprite.texture = attrs.texture
        elif src.startswith('icon:'):
            uthread.new(self.LoadIcon)
        parts = src.split(':', 1)
        if len(parts) == 2:
            imageType, imageData = parts
            if imageType == 'portrait':
                uthread.new(self.LoadPortrait)
            elif imageType in self.LOGO_IMAGE_TYPES:
                eveIcon.GetLogoIcon(itemID=int(imageData), align=uiconst.TOALL, parent=self, state=uiconst.UI_DISABLED)
            elif src.startswith('starmap:'):
                uthread.new(self.GetMap, src)
            elif src.startswith('typeicon:'):
                uthread.new(self.LoadTypeIcon)

    def GetMap(self, src):
        if self.destroyed:
            return
        data = stringManip.PrepareArgs(src[8:])
        if 'ids' not in data:
            log.LogError('Invalid starmap data:', data, ' (missing ids)')
            return
        if 'level' in data:
            drawLevel = self.DRAW_LEVELS[data['level'].lower()]
        else:
            drawLevel = 3
        ids = []
        if type(data['ids']) == types.IntType:
            ids = [data['ids']]
        else:
            for each in data['ids'].replace(' ', '').split(','):
                try:
                    ids.append(int(each))
                except Exception as e:
                    log.LogWarn(e)

        if not ids:
            idLevel = 0
        if idCheckers.IsRegion(ids[0]):
            idLevel = 1
        if idCheckers.IsConstellation(ids[0]):
            idLevel = 2
        if idCheckers.IsSolarSystem(ids[0]):
            idLevel = 3
        pilmap = Map2D(parent=self, align=uiconst.TOALL)
        pilmap.Draw(ids, idLevel, drawLevel, int(self.attrs.size))
        if self.destroyed:
            return
        for each in pilmap.children[:]:
            if each.name == 'frame':
                each.Close()

        if 'marks' in data:
            marks = []
            for each in data['marks'].split(','):
                mark = each.split('::')
                if len(mark) == 4:
                    try:
                        id = int(mark[0])
                        hint = unicode(mark[1])
                        color = unicode(mark[2])
                        sumin = mark[3]
                        marks += [id,
                         hint,
                         color,
                         sumin]
                    except Exception as e:
                        log.LogWarn('Failed mark parsing', mark, e)

            if marks:
                pilmap.SetMarks(marks)
        pilmap.UpdateMyLocation()

    def GetMenu(self):
        m = []
        if getattr(self, 'attrs', None) and getattr(self.attrs, 'src', None) and self.attrs.src:
            src = self.attrs.src
            parts = self.attrs.src.split(':', 1)
            if len(parts) == 2:
                if parts[0] not in self.IMAGE_TYPES:
                    m += [(MenuLabel('UI/Common/ReloadImage'), self.Reload)]
            if getattr(self.attrs, 'a', None):
                m += Link().GetLinkMenu(self, self.attrs.a.href)
        return m

    def LoadPortrait(self, orderIfMissing = True):
        attrs = self.attrs
        self.Flush()
        sprite = eveIcon.Icon(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, pos=(0, 0, 0, 0))
        self.sr.sprite = sprite
        size = int(max(attrs.size, 64))
        charID = int(attrs.src[9:])
        if sm.GetService('photo').GetPortrait(charID, size, sprite, orderIfMissing, callback=True):
            self.picloaded = 1
        else:
            sm.RegisterNotify(self)

    def OnPortraitCreated(self, charID, _size):
        if hasattr(self, 'attrs') and self.attrs.src.startswith('portrait:'):
            mycharID = int(self.attrs.src[9:])
            if mycharID == charID:
                self.LoadPortrait(False)

    def LoadTypeIcon(self, *args):
        attrs = self.attrs
        src = attrs.src
        typeID = None
        try:
            typeID = int(src[9:])
        except:
            log.LogInfo("couldn't convert string to typeID, looking up constvalue, Img::Load", src)
            typeID = dbrow.LookupConstValue('type%s' % attrs.src[9:].strip().capitalize(), None)

        bumped = getattr(attrs, 'bumped', 0)
        showFitting = getattr(attrs, 'showfitting', 0)
        showTechLevel = getattr(attrs, 'showtechlevel', 0)
        isCopy = getattr(attrs, 'iscopy', 0)
        if not typeID:
            kw = htmlwriter.PythonizeArgs(src[9:])
            typeID = kw.get('typeID', None)
            bumped = kw.get('bumped', 0)
            isCopy = kw.get('isCopy', 0)
            showFitting = kw.get('showFitting', 0)
            showTechLevel = kw.get('showTechLevel', 0)
        if typeID:
            if bumped:
                if hasattr(self, 'icon') and self.icon:
                    self.icon.Close()
                self.icon = DraggableIcon(parent=self, typeID=typeID, isCopy=True if isCopy == 1 else False, state=uiconst.UI_DISABLED)
                if showFitting:
                    powerEffect = None
                    powerIcon = None
                    powerEffects = [const.effectHiPower, const.effectMedPower, const.effectLoPower]
                    for effect in dogma_data.get_type_effects(typeID):
                        if effect.effectID in powerEffects:
                            powerEffect = dogma_data.get_effect_with_default(effect.effectID, None)
                            powerIcon = {const.effectHiPower: 11,
                             const.effectMedPower: 10,
                             const.effectLoPower: 9}.get(powerEffect.effectID, None)
                            break

                    if powerIcon:
                        c = Container(name='powericon', align=uiconst.BOTTOMRIGHT, parent=self.icon, width=attrs.width / 4, height=attrs.width / 4, idx=0)
                        Line(parent=c, align=uiconst.TOLEFT, color=(1.0, 1.0, 1.0, 0.5))
                        Line(parent=c, align=uiconst.TOTOP, color=(1.0, 1.0, 1.0, 0.5))
                        Fill(parent=c, padRight=2, padBottom=2, color=(0.0, 0.0, 0.0, 1.0))
                        eveIcon.Icon(icon='ui_8_64_%s' % powerIcon, parent=c, align=uiconst.TOALL, idx=0, hint=localization.GetByLabel('UI/Common/FitsToSlot', slotType=dogma_data.get_effect_display_name(powerEffect.effectID)), ignoreSize=True)
                if showTechLevel:
                    techSprite = uix.GetTechLevelIcon(None, 0, typeID)
                    if techSprite:
                        c = Container(name='techIcon', align=uiconst.TOPLEFT, parent=self.icon, width=16, height=16, idx=0)
                        c.children.append(techSprite)
            else:
                eveIcon.Icon(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, pos=(0, 0, 0, 0), typeID=typeID, size=attrs.width, isCopy=isCopy)
        else:
            log.LogInfo('Couldnt convert', attrs.src[9:], 'to typeID')

    def LoadIcon(self, *args):
        sprite = Sprite(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, idx=0, pos=(0, 0, 0, 0))
        if not hasattr(self, 'attrs'):
            return
        icon = self.attrs.src[5:]
        if isinstance(icon, unicode):
            icon = icon.encode('ascii', 'xmlcharrefreplace')
        spl = icon.split('_')
        if len(spl) == 2:
            texpix, num = spl
            iconSize = eveIcon.GetIconSize(texpix)
            icon = 'ui_%s_%s_%s' % (texpix, iconSize, num)
        various_unsorted.MapIcon(sprite, icon, ignoreSize=True)


from carbonui.control.image import ImageCoreOverride
ImageCoreOverride.__bases__ = (Image,)
