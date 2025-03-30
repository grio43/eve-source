#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\eveLabel.py
import log
import trinity
from carbonui import fontconst, TextColor, uiconst
from carbonui.control.label import LabelCore
from carbonui.control.link import Link
from carbonui.primitives.containerAutoSize import ContainerAutoSize

class Label(LabelCore):
    __guid__ = 'uicontrols.Label'
    default_name = 'Label'
    default_fontsize = fontconst.EVE_MEDIUM_FONTSIZE
    default_color = TextColor.NORMAL
    default_align = uiconst.TOPLEFT
    default_shadowOffset = (1, 1)
    default_shadowSpriteEffect = trinity.TR2_SFX_FONT
    default_shadowColor = (0.0, 0.0, 0.0, 0.6)

    @staticmethod
    def GetLinkHandlerClass():
        return Link


class EveStyleLabel(Label):
    default_name = 'EveStyleLabel'

    def ApplyAttributes(self, attributes):
        fontsize = attributes.get('fontsize', None)
        if fontsize is not None:
            attributes.fontsize = self.default_fontsize
            log.LogTraceback('You are not allowed to change fontsize of a font style - find another style to use or use uicontrols.Label for custom labels')
        uppercase = attributes.get('uppercase', None)
        if uppercase is not None:
            attributes.uppercase = self.default_uppercase
            log.LogTraceback('You are not allowed to change uppercase of a font style - find another style to use or use uicontrols.Label for custom labels')
        letterspace = attributes.get('letterspace', None)
        if letterspace is not None:
            attributes.letterspace = self.default_letterspace
            log.LogTraceback('You are not allowed to change letterspace of a font style - find another style to use or use uicontrols.Label for custom labels')
        Label.ApplyAttributes(self, attributes)


class EveLabelSmall(EveStyleLabel):
    __guid__ = 'uicontrols.EveLabelSmall'
    default_name = 'EveLabelSmall'
    default_fontsize = fontconst.EVE_SMALL_FONTSIZE
    default_fontStyle = fontconst.STYLE_SMALLTEXT


class EveHeaderSmall(EveStyleLabel):
    __guid__ = 'uicontrols.EveHeaderSmall'
    default_name = 'EveHeaderSmall'
    default_fontStyle = fontconst.STYLE_SMALLTEXT
    default_fontsize = fontconst.EVE_SMALL_FONTSIZE
    default_uppercase = 1


class EveLabelSmallBold(EveStyleLabel):
    __guid__ = 'uicontrols.EveLabelSmallBold'
    default_name = 'EveLabelSmallBold'
    default_fontStyle = fontconst.STYLE_SMALLTEXT
    default_fontsize = fontconst.EVE_SMALL_FONTSIZE
    default_bold = True


class EveLabelMedium(EveStyleLabel):
    __guid__ = 'uicontrols.EveLabelMedium'
    default_name = 'EveLabelMedium'
    default_fontsize = fontconst.EVE_MEDIUM_FONTSIZE


class EveHeaderMedium(EveStyleLabel):
    __guid__ = 'uicontrols.EveHeaderMedium'
    default_name = 'EveHeaderMedium'
    default_fontsize = fontconst.EVE_MEDIUM_FONTSIZE
    default_uppercase = 1


class EveHeaderMediumBold(EveStyleLabel):
    __guid__ = 'uicontrols.EveHeaderMediumBold'
    default_name = 'EveHeaderMediumBold'
    efault_fontsize = fontconst.EVE_MEDIUM_FONTSIZE
    default_uppercase = 1
    default_bold = True


class EveLabelMediumBold(EveStyleLabel):
    __guid__ = 'uicontrols.EveLabelMediumBold'
    default_name = 'EveLabelMediumBold'
    default_fontsize = fontconst.EVE_MEDIUM_FONTSIZE
    default_bold = True


class EveLabelLarge(EveStyleLabel):
    __guid__ = 'uicontrols.EveLabelLarge'
    default_name = 'EveLabelLarge'
    default_fontsize = fontconst.EVE_LARGE_FONTSIZE


class EveHeaderLarge(EveStyleLabel):
    __guid__ = 'uicontrols.EveHeaderLarge'
    default_name = 'EveHeaderLarge'
    default_fontsize = fontconst.EVE_LARGE_FONTSIZE
    default_uppercase = 1
    default_fontStyle = fontconst.STYLE_HEADER


class EveHeaderLargeBold(EveStyleLabel):
    __guid__ = 'uicontrols.EveHeaderLarge'
    default_name = 'EveHeaderLarge'
    default_fontsize = fontconst.EVE_LARGE_FONTSIZE
    default_uppercase = 1
    default_fontStyle = fontconst.STYLE_HEADER
    default_bold = True


class EveLabelLargeBold(EveStyleLabel):
    __guid__ = 'uicontrols.EveLabelLargeBold'
    default_name = 'EveLabelLargeBold'
    default_fontsize = fontconst.EVE_LARGE_FONTSIZE
    default_bold = True


class EveLabelLargeUpper(EveLabelLarge):
    __guid__ = 'uicontrols.EveLabelLargeUpper'
    default_name = 'EveLabelLargeUpper'
    default_uppercase = True


class EveCaptionSmall(EveStyleLabel):
    __guid__ = 'uicontrols.EveCaptionSmall'
    default_name = 'EveCaptionSmall'
    default_fontsize = fontconst.EVE_XLARGE_FONTSIZE
    default_fontStyle = fontconst.STYLE_HEADER
    default_lineSpacing = -0.12
    default_color = TextColor.HIGHLIGHT


class EveCaptionMedium(EveStyleLabel):
    __guid__ = 'uicontrols.EveCaptionMedium'
    default_name = 'EveCaptionMedium'
    default_fontsize = 20
    default_fontStyle = fontconst.STYLE_HEADER
    default_lineSpacing = -0.12
    default_color = TextColor.HIGHLIGHT


class EveCaptionLarge(EveStyleLabel):
    __guid__ = 'uicontrols.EveCaptionLarge'
    default_name = 'EveCaptionLarge'
    default_fontsize = 24
    default_fontStyle = fontconst.STYLE_HEADER
    default_lineSpacing = -0.12
    default_color = TextColor.HIGHLIGHT


class CaptionLabel(Label):
    __guid__ = 'uicontrols.CaptionLabel'
    default_name = 'caption'
    default_fontsize = 20
    default_letterspace = 1
    default_align = uiconst.TOALL
    default_idx = -1
    default_state = uiconst.UI_DISABLED
    default_uppercase = True
    default_bold = True


class WndCaptionLabel(ContainerAutoSize):
    __guid__ = 'uicontrols.WndCaptionLabel'
    default_left = 70
    default_text = ''
    default_subcaption = None
    default_align = uiconst.CENTERLEFT

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        text = attributes.get('text', self.default_text)
        subcaption = attributes.get('subcaption', self.default_subcaption)
        self.caption = EveCaptionMedium(align=uiconst.TOPLEFT, parent=self, text=text)
        self.subcapt = EveLabelSmall(name='subcaption', parent=self, align=uiconst.TOPLEFT, top=self.caption.textheight, state=uiconst.UI_HIDDEN)
        if subcaption:
            self.SetSubcaption(subcaption)

    def SetText(self, text):
        self.caption.text = text

    def SetSubcaption(self, text):
        self.subcapt.text = text
        self.subcapt.state = uiconst.UI_DISABLED


from carbonui.control.label import LabelOverride
LabelOverride.__bases__ = (Label,)
