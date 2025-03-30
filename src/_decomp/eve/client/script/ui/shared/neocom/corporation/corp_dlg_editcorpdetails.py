#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_dlg_editcorpdetails.py
import random
import localization
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.format import FormatUrl
from carbonui import ButtonVariant, uiconst
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.entries.icon import Icons
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveIcon import CorpIcon
from carbonui.control.window import Window
from carbonui.decorative.menuUnderlay import MenuUnderlay
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.util import uix
from eve.client.script.ui.control import eveIcon, eveLabel, eveScroll
from eve.client.script.ui.shared.neocom.wallet.walletUtil import FmtWalletCurrency
from eve.common.lib.appConst import corpNameMaxLenSR, corpNameMaxLenTQ
from eveexceptions import UserError
from eveprefs import boot

class CorpDetails(Window):
    default_minSize = (400, 500)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.ShowLoad()
        self.DefineButtons(uiconst.OK, okLabel=localization.GetByLabel('UI/Generic/Submit'), okFunc=self.Submit)
        self.pickingTicker = 0
        self.layerNumSelected = None
        self.sr.prefs = [None,
         None,
         None,
         None,
         None,
         None]
        self.sr.priorlogo = (None, None, None, None, None, None)
        self.sr.priordesc = self.description
        self.sr.priorurl = self.url
        self.sr.priorISKTaxRate = self.iskTaxRate
        self.sr.priorLPTaxRate = self.loyaltyPointTaxRate
        par = Container(name='logoControl', parent=self.sr.main, align=uiconst.TOTOP, height=100, width=310, padding=(5, 5, 5, 0))
        self.sr.logocontrol = Container(name='controlpanel', parent=par, height=100, width=160, align=uiconst.CENTER)
        self.sr.inputcontrol = Container(name='controlpanel', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(5, 5, 5, 0))
        top = uix.GetTextHeight(localization.GetByLabel('UI/Corporations/CorpDetails/CorpName'))
        if boot.region == 'optic':
            defaultCorpName = localization.GetByLabel('UI/Corporations/CorpDetails/DefaultCorpName')
        else:
            defaultCorpName = localization.GetByLabel('UI/Corporations/CorpDetails/DefaultCorpName', localization.const.LOCALE_SHORT_ENGLISH)
        self.sr.corpNameEdit_container = Container(name='corpNameEdit_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP, height=56)
        maxLength = corpNameMaxLenSR if boot.region == 'optic' else corpNameMaxLenTQ
        self.sr.corpNameEdit = SingleLineEditText(name='nameEdit', parent=self.sr.corpNameEdit_container, setvalue=defaultCorpName, align=uiconst.TOTOP, maxLength=maxLength, label=localization.GetByLabel('UI/Corporations/CorpDetails/CorpName'), top=top)
        self.sr.corpNameEdit_container.height = self.sr.corpNameEdit.height + top + const.defaultPadding
        top = uix.GetTextHeight(localization.GetByLabel('UI/Corporations/CorpDetails/Ticker'))
        self.sr.corpTickerEdit_container = Container(name='corpTickerEdit_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP, height=56)
        btn = Button(parent=self.sr.corpTickerEdit_container, label=localization.GetByLabel('UI/Corporations/CorpDetails/Ticker'), align=uiconst.BOTTOMRIGHT, func=self.GetPickTicker, idx=0)
        self.sr.corpTickerEdit = SingleLineEditText(name='corpTickerEdit', parent=self.sr.corpTickerEdit_container, setvalue='', align=uiconst.TOPLEFT, maxLength=5, label=localization.GetByLabel('UI/Corporations/CorpDetails/Ticker'), top=top, width=min(300 - btn.width, 240))
        self.sr.corpTickerEdit_container.height = self.sr.corpTickerEdit.height + top + const.defaultPadding
        top = uix.GetTextHeight(localization.GetByLabel('UI/Corporations/CorpDetails/MemberLimit'))
        self.sr.memberLimit_container = Container(name='memberLimit_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP, height=24)
        btn = Button(parent=self.sr.memberLimit_container, label=localization.GetByLabel('UI/Corporations/CorpDetails/UpdateWithMySkills'), align=uiconst.BOTTOMRIGHT, func=self.UpdateWithSkills, idx=0, variant=ButtonVariant.GHOST)
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Corporations/CorpDetails/MemberLimit'), parent=self.sr.memberLimit_container, left=0, top=0, state=uiconst.UI_NORMAL)
        self.sr.memberLimit = eveLabel.EveLabelMedium(text='123', parent=self.sr.memberLimit_container, left=2, top=top, state=uiconst.UI_DISABLED, idx=0)
        self.sr.memberLimit_container.height = self.sr.memberLimit.height + top + const.defaultPadding
        self._construct_isk_tax_rate()
        self._construct_lp_tax_rate()
        top = uix.GetTextHeight('http://')
        self.sr.urlEdit_container = Container(name='urlEdit_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP)
        self.sr.urlEdit = SingleLineEditText(name='urlEdit', parent=self.sr.urlEdit_container, setvalue=self.url, maxLength=2048, align=uiconst.TOTOP, label=localization.GetByLabel('UI/Corporations/CorpDetails/HomePage'), top=top)
        self.sr.urlEdit_container.height = self.sr.urlEdit.height + top + const.defaultPadding + 20
        self.friendlyFireCont = Container(name='friendlyFireCont', parent=self.sr.inputcontrol, align=uiconst.TOBOTTOM, height=24)
        self.friendlyFireCb = Checkbox(name='friendlyFireCb', parent=self.friendlyFireCont, text=localization.GetByLabel('UI/Corporations/CorpUIHome/AllowFriendlyFire'), checked=False, align=uiconst.CENTERLEFT, wrapLabel=False)
        helpIcon = MoreInfoIcon(parent=self.friendlyFireCont, align=uiconst.TOPRIGHT, hint=localization.GetByLabel('UI/Corporations/FriendlyFire/Description'))
        top = uix.GetTextHeight(localization.GetByLabel('UI/Corporations/CorpDetails/Description'))
        self.sr.descEdit_container = Container(name='descEdit_container', parent=self.sr.inputcontrol, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        eveLabel.EveLabelSmall(text=localization.GetByLabel('UI/Corporations/CorpDetails/Description'), parent=self.sr.descEdit_container, top=-16)
        self.sr.descEdit = EditPlainText(setvalue=self.description, parent=self.sr.descEdit_container, maxLength=4000, showattributepanel=1, hintText=localization.GetByLabel('UI/Corporations/CreateCorp/EnterDescriptionHere'))
        self.logopicker = CorpLogoPicker(parent=self.sr.logocontrol, pos=(100, 0, 57, 90), align=uiconst.TOPLEFT)

    def _construct_isk_tax_rate(self):
        label_text = localization.GetByLabel('UI/Corporations/CorpDetails/ISKTaxRate')
        top = uix.GetTextHeight(label_text)
        self.sr.iskTaxRateEdit_container = Container(name='iskTaxRateEdit_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP, height=24)
        self.sr.iskTaxRateEdit = SingleLineEditFloat(name='iskTaxRateEdit', parent=self.sr.iskTaxRateEdit_container, maxValue=100.0, setvalue=self.iskTaxRate, align=uiconst.TOPLEFT, label=label_text, top=top)
        self.sr.iskTaxRateEdit_container.height = self.sr.iskTaxRateEdit.height + top + const.defaultPadding
        min_isk_text = FmtWalletCurrency(amt=const.minCorporationTaxAmount, currency=const.creditsISK)
        more_info_hint = localization.GetByLabel('UI/Corporations/BaseCorporationUI/ISKTaxRateDescription', min_isk_amount=min_isk_text)
        MoreInfoIcon(parent=self.sr.iskTaxRateEdit_container, align=uiconst.CENTERLEFT, hint=more_info_hint, left=self.sr.iskTaxRateEdit.width + 6, top=6)

    def _construct_lp_tax_rate(self):
        label_text = localization.GetByLabel('UI/Corporations/CorpDetails/LPTaxRate')
        top = uix.GetTextHeight(label_text)
        self.sr.lpTaxRateEdit_container = Container(name='lpTaxRateEdit_container', parent=self.sr.inputcontrol, align=uiconst.TOTOP, height=24)
        self.sr.lpTaxRateEdit = SingleLineEditFloat(name='lpTaxRateEdit', parent=self.sr.lpTaxRateEdit_container, maxValue=100.0, setvalue=self.loyaltyPointTaxRate, align=uiconst.TOPLEFT, label=label_text, top=top)
        self.sr.lpTaxRateEdit_container.height = self.sr.lpTaxRateEdit.height + top + const.defaultPadding
        more_info_hint = localization.GetByLabel('UI/Corporations/BaseCorporationUI/LPTaxRateDescription')
        MoreInfoIcon(parent=self.sr.lpTaxRateEdit_container, align=uiconst.CENTERLEFT, hint=more_info_hint, left=self.sr.lpTaxRateEdit.width + 6, top=6)

    def GetLogoLibShape(self, graphicID):
        return const.graphicCorpLogoLibShapes.get(graphicID, const.graphicCorpLogoLibShapes[const.graphicCorpLogoLibNoShape])

    def GetLogoLibColor(self, graphicID):
        color, blendMode = const.graphicCorpLogoLibColors.get(graphicID, (1.0, 1.0, 1.0, 1.0))
        return (color, blendMode)

    def SetupLogo(self, shapes = [None, None, None], colors = [None, None, None]):
        i = 0
        self.sr.layerpics = []
        for each in ['layerPic1', 'layerPic2', 'layerPic3']:
            btn = Sprite(parent=getattr(self.logopicker, each), pos=(0, 0, 0, 0), align=uiconst.TOALL, color=(1.0, 0.0, 1.0, 0.0))
            btn.OnClick = (self.ClickPic, i)
            self.sr.layerpics.append(btn)
            texturePath = self.GetLogoLibShape(shapes[i])
            btn.LoadTexture(texturePath)
            btn.SetRGBA(1.0, 1.0, 1.0, 1.0)
            self.corpLogo.SetLayerShapeAndColor(layerNum=i, shapeID=shapes[i], colorID=colors[i])
            self.sr.prefs[i] = shapes[i]
            i += 1

        i = 0
        self.sr.layercols = []
        for each in ['layerStyle1', 'layerStyle2', 'layerStyle3']:
            btn = Fill(parent=getattr(self.logopicker, each), pos=(0, 0, 0, 0), align=uiconst.TOALL, color=(1.0, 1.0, 1.0, 0.0), state=uiconst.UI_NORMAL)
            btn.OnClick = (self.ClickCol, i, btn)
            self.sr.layercols.append(btn)
            if colors[i]:
                color, blendMode = self.GetLogoLibColor(colors[i])
                btn.SetRGBA(*color)
                self.sr.prefs[i + 3] = colors[i]
            i = i + 1

    def PickPic(self, sender, *args):
        if self.layerNumSelected is not None:
            PlaySound(uiconst.SOUND_SETSELECTED)
            shapeID = sender.sr.identifier
            texturePath = self.GetLogoLibShape(shapeID)
            self.sr.layerpics[self.layerNumSelected].LoadTexture(texturePath)
            self.corpLogo.SetLayerShapeAndColor(layerNum=self.layerNumSelected, shapeID=shapeID)
            if not self.sr.prefs[self.layerNumSelected + 3]:
                self.sr.layerpics[self.layerNumSelected].SetRGBA(1.0, 1.0, 1.0, 1.0)
            self.sr.prefs[self.layerNumSelected] = sender.sr.identifier

    def PickCol(self, sender, *args):
        if self.layerNumSelected is not None:
            PlaySound(uiconst.SOUND_SETSELECTED)
            colorID = sender.sr.identifier
            color, blendMode = self.GetLogoLibColor(colorID)
            self.sr.layercols[self.layerNumSelected].SetRGBA(*color)
            self.corpLogo.SetLayerShapeAndColor(layerNum=self.layerNumSelected, colorID=colorID)
            self.sr.prefs[self.layerNumSelected + 3] = colorID

    def ClickPic(self, idx):
        if not self.sr.Get('shapes', None):
            top = self.corpLogo.top + self.corpLogo.height
            self.sr.shapes = Container(name='shapes_container', parent=self.sr.main, align=uiconst.CENTERTOP, height=240, width=280, idx=0, top=top)
            self.sr.shapes.state = uiconst.UI_HIDDEN
            shapescroll = eveScroll.Scroll(parent=self.sr.shapes, padding=8)
            self.AddCloseButton(self.sr.shapes)
            MenuUnderlay(parent=self.sr.shapes)
            x = 0
            scrolllist = []
            icons = []
            graphicIDs = const.graphicCorpLogoLibShapes.keys()
            graphicIDs.sort()
            for graphicID in graphicIDs:
                texturePath = self.GetLogoLibShape(graphicID)
                icons.append((texturePath,
                 None,
                 graphicID,
                 self.PickPic))
                x += 1
                if x == 4:
                    scrolllist.append(GetFromClass(Icons, {'icons': icons}))
                    icons = []
                    x = 0

            if len(icons):
                scrolllist.append(GetFromClass(Icons, {'icons': icons}))
            self.sr.shapes.state = uiconst.UI_NORMAL
            shapescroll.Load(fixedEntryHeight=64, contentList=scrolllist)
        self.layerNumSelected = idx
        self.sr.shapes.top = self.corpLogo.top + self.corpLogo.height
        if self.sr.Get('colors', None):
            self.sr.colors.state = uiconst.UI_HIDDEN
        self.sr.shapes.state = uiconst.UI_NORMAL
        self.sr.shapes.SetOrder(0)

    def DoNothing(self, *args):
        pass

    def AddCloseButton(self, panel):
        buttondad = ContainerAutoSize(name='btnparent', parent=panel.children[0], align=uiconst.TOBOTTOM, idx=0, padding=(0, 8, 0, 8))
        Button(parent=buttondad, label=localization.GetByLabel('UI/Generic/Close'), align=uiconst.CENTER, func=self.HidePanel, args=panel)

    def HidePanel(self, panel, *args):
        if panel:
            panel.state = uiconst.UI_HIDDEN

    def ClickCol(self, idx, sender):
        if not self.sr.Get('colors', None):
            self.sr.colors = Container(name='colors_container', parent=self.sr.main, align=uiconst.CENTERTOP, height=194, width=150, idx=0)
            colorscroll = eveScroll.Scroll(name='colorScroll', parent=self.sr.colors, padding=8)
            self.AddCloseButton(self.sr.colors)
            MenuUnderlay(parent=self.sr.colors)
            x = 0
            scrolllist = []
            icons = []
            graphicIDs = const.graphicCorpLogoLibColors.keys()
            graphicIDs.sort()
            for graphicID in graphicIDs:
                color, blendMode = self.GetLogoLibColor(graphicID)
                icons.append((None,
                 color,
                 graphicID,
                 self.PickCol))
                x += 1
                if x == 4:
                    scrolllist.append(GetFromClass(Icons, {'icons': icons}))
                    icons = []
                    x = 0

            if len(icons):
                scrolllist.append(GetFromClass(Icons, {'icons': icons[:]}))
            self.sr.colors.state = uiconst.UI_NORMAL
            colorscroll.Load(fixedEntryHeight=32, contentList=scrolllist)
        self.layerNumSelected = idx
        self.sr.colors.top = self.corpLogo.top + self.corpLogo.height
        if self.sr.Get('shapes', None):
            self.sr.shapes.state = uiconst.UI_HIDDEN
        self.sr.colors.state = uiconst.UI_NORMAL
        self.sr.colors.SetOrder(0)

    def Confirm(self, *args):
        pass

    def MouseDown(self, sender, *args):
        if self.sr.Get('colors', None):
            self.sr.colors.state = uiconst.UI_HIDDEN
        if self.sr.Get('shapes', None):
            self.sr.shapes.state = uiconst.UI_HIDDEN

    def UpdateWithSkills(self, *args):
        if sm.GetService('corp').UpdateCorporationAbilities() is None:
            return
        corp = sm.GetService('corp').GetCorporation(eve.session.corpid, 1)
        self.sr.memberLimit.text = str(corp.memberLimit)

    def GetPickTicker(self, *args):
        if self.pickingTicker == 1:
            return
        self.pickingTicker = 1
        self.PickTicker()
        self.pickingTicker = 0

    def PickTicker(self, *args):
        corpName = self.sr.corpNameEdit.GetValue()
        if len(corpName.strip()) == 0:
            eve.Message('EnterCorporationName')
            return
        suggestions = sm.GetService('corp').GetSuggestedTickerNames(corpName)
        if not suggestions or len(suggestions) == 0:
            eve.Message('NoCorpTickerNameSuggestions')
            return
        tmplist = []
        for each in suggestions:
            tmplist.append((each.tickerName, each.tickerName))

        ret = uix.ListWnd(tmplist, 'generic', localization.GetByLabel('UI/Corporations/CorpDetails/SelectTicker'), None, 1)
        if ret is not None and len(ret):
            self.sr.corpTickerEdit.SetValue(ret[0])


class EditCorpDetails(CorpDetails):
    default_windowID = 'editcorpdetails'

    def ApplyAttributes(self, attributes):
        corp = sm.GetService('corp').GetCorporation()
        self.corporationName = corp.corporationName
        self.description = corp.description
        self.url = corp.url
        self.iskTaxRate = corp.taxRate * 100.0
        self.loyaltyPointTaxRate = corp.loyaltyPointTaxRate * 100.0
        self.applicationsEnabled = corp.isRecruiting
        CorpDetails.ApplyAttributes(self, attributes)
        self.caption = localization.GetByLabel('UI/Corporations/EditCorpDetails/EditCorpDetailsCaption')
        self.friendlyFireCont.display = False
        self.sr.corpNameEdit_container.state = uiconst.UI_HIDDEN
        self.sr.corpTickerEdit_container.state = uiconst.UI_HIDDEN
        self.name = 'editcorp'
        self.result = {}
        self.sr.priorlogo = (corp.shape1,
         corp.shape2,
         corp.shape3,
         corp.color1,
         corp.color2,
         corp.color3)
        shapes = [corp.shape1, corp.shape2, corp.shape3]
        colors = [corp.color1, corp.color2, corp.color3]
        self.corpLogo = eveIcon.GetLogoIcon(itemID=session.corpid, acceptNone=False, pos=(0, 0, 90, 90))
        self.sr.logocontrol.children.insert(0, self.corpLogo)
        self.SetupLogo(shapes, colors)
        self.sr.memberLimit.text = str(corp.memberLimit)
        self.sr.main.state = uiconst.UI_NORMAL
        self.HideLoad()

    def Submit(self, *args):
        myCorp = sm.GetService('corp').GetCorporation()
        shape1, shape2, shape3, color1, color2, color3 = self.sr.prefs
        if self.sr.priorlogo != (shape1,
         shape2,
         shape3,
         color1,
         color2,
         color3):
            if eve.Message('AskAcceptLogoChangeCost', {'cost': const.corpLogoChangeCost}, uiconst.YESNO, default=uiconst.ID_NO) == uiconst.ID_YES:
                sm.GetService('corp').UpdateLogo(shape1, shape2, shape3, color1, color2, color3, None)
        if self.sr.priordesc != self.sr.descEdit.GetValue() or self.sr.priorurl != self.sr.urlEdit.GetValue() or self.sr.priorISKTaxRate != self.sr.iskTaxRateEdit.GetValue() or self.sr.priorLPTaxRate != self.sr.lpTaxRateEdit.GetValue():
            urlvalue = self.sr.urlEdit.GetValue() and self.sr.urlEdit.GetValue().strip()
            if urlvalue:
                urlvalue = FormatUrl(urlvalue)
            sm.GetService('corp').UpdateCorporation(self.sr.descEdit.GetValue().strip(), urlvalue, self.sr.iskTaxRateEdit.GetValue() / 100.0, self.applicationsEnabled, self.sr.lpTaxRateEdit.GetValue() / 100.0)
            sm.GetService('corpui').ResetWindow(bShowIfVisible=1)
        self.Close()


class CreateCorp(CorpDetails):
    __nonpersistvars__ = ['result']
    default_windowID = 'createcorp'
    default_minSize = (400, 590)

    def ApplyAttributes(self, attributes):
        self.corporationName = ''
        self.description = ''
        self.url = 'http://'
        self.iskTaxRate = 0.0
        self.loyaltyPointTaxRate = 0.0
        self.applicationsEnabled = True
        CorpDetails.ApplyAttributes(self, attributes)
        self.caption = localization.GetByLabel('UI/Corporations/CreateCorp/CreateCorpCaption')
        self.name = 'createcorp'
        self.sr.memberLimit_container.state = uiconst.UI_HIDDEN
        self.result = {}
        randomNumber = random.choice(const.graphicCorpLogoLibShapes.keys())
        self.corpLogo = CorpIcon(acceptNone=False, pos=(0, 0, 90, 90))
        self.sr.logocontrol.children.insert(0, self.corpLogo)
        self.SetupLogo([randomNumber, const.graphicCorpLogoLibNoShape, const.graphicCorpLogoLibNoShape], [None, None, None])
        self.sr.main.state = uiconst.UI_NORMAL

    def Submit(self, *args):
        corpName = self.sr.corpNameEdit.GetValue()
        if len(corpName.strip()) == 0:
            raise UserError('EnterCorporationName')
        corpTicker = self.sr.corpTickerEdit.GetValue()
        if len(corpTicker.strip()) == 0:
            raise UserError('EnterTickerName')
        if not session.stationid:
            raise UserError('CanOnlyCreateCorpInStation')
        description = self.sr.descEdit.GetValue().strip()
        iskTaxRate = self.sr.iskTaxRateEdit.GetValue() / 100.0
        loyaltyPointTaxRate = self.sr.lpTaxRateEdit.GetValue() / 100.0
        url = self.sr.urlEdit.GetValue()
        applicationsEnabled = self.applicationsEnabled
        friendlyFireEnabled = self.friendlyFireCb.GetValue()
        shape1, shape2, shape3, color1, color2, color3 = self.sr.prefs
        sm.GetService('corp').AddCorporation(corpName, corpTicker, description, url, iskTaxRate, shape1, shape2, shape3, color1, color2, color3, applicationsEnabled=applicationsEnabled, friendlyFireEnabled=friendlyFireEnabled, loyaltyPointTaxRate=loyaltyPointTaxRate)
        self.Close()


class CorpLogoPicker(Container):
    default_name = 'corplogosubpar'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        FRAME_COLOR = Color.GetGrayRGBA(0.4, 1.0)
        layer1 = Container(parent=self, name='layer1', pos=(0, 0, 50, 30), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.layerPic1 = Container(parent=layer1, name='layerPic1', pos=(3, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        Frame(parent=self.layerPic1, color=FRAME_COLOR)
        self.layerStyle1 = Container(parent=layer1, name='layerStyle1', pos=(26, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        Frame(parent=self.layerStyle1, color=FRAME_COLOR)
        layer2 = Container(parent=self, name='layer2', pos=(0, 30, 50, 30), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.layerPic2 = Container(parent=layer2, name='layerPic2', pos=(3, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        Frame(parent=self.layerPic2, color=FRAME_COLOR)
        self.layerStyle2 = Container(parent=layer2, name='layerStyle2', pos=(26, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        Frame(parent=self.layerStyle2, color=FRAME_COLOR)
        layer3 = Container(parent=self, name='layer3', pos=(0, 60, 50, 30), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.layerPic3 = Container(parent=layer3, name='layerPic3', pos=(3, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        Frame(parent=self.layerPic3, color=FRAME_COLOR)
        self.layerStyle3 = Container(parent=layer3, name='layerStyle3', pos=(26, 3, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        Frame(parent=self.layerStyle3, color=FRAME_COLOR)
