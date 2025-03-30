#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Typography.py
import itertools
import random
import eveformat
import eveicon
import uthread2
from carbonui import Density, TextAlign, TextBody, TextColor, TextCustom, TextDetail, TextHeader, TextHeadline, uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.comboEntryData import ComboEntryDataSeparator
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.slider import Slider
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.devtools.script.uiControlCatalog.sample import Sample
from eve.devtools.script.uiControlCatalog.sampleUtil import GetHorizCollapsableCont

class Sample1(Sample):
    name = 'Styles'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, align=uiconst.TOPLEFT, cellSpacing=(64, 32), columns=2)
        headline_group = LayoutGrid(parent=grid, align=uiconst.TOPLEFT, columns=1)
        TextHeadline(parent=headline_group, align=uiconst.TOPLEFT, text='Headline')
        TextHeadline(parent=headline_group, align=uiconst.TOPLEFT, text='Headline Bold', bold=True)
        TextHeadline(parent=headline_group, align=uiconst.TOPLEFT, text='Headline Italic', italic=True)
        TextDetail(parent=headline_group, align=uiconst.TOPLEFT, text='TextHeadline - 24px font size - 30px line-height', color=TextColor.DISABLED)
        TextBody(parent=grid, align=uiconst.TOPLEFT, width=320, text="A large and attention-grabbing text at the top of a window or larger content section that summarizes the content and helps to attract the reader's attention.", color=TextColor.SECONDARY)
        header_group = LayoutGrid(parent=grid, align=uiconst.TOPLEFT, columns=1)
        TextHeader(parent=header_group, align=uiconst.TOPLEFT, text='Header')
        TextHeader(parent=header_group, align=uiconst.TOPLEFT, text='Header Bold', bold=True)
        TextHeader(parent=header_group, align=uiconst.TOPLEFT, text='Header Italic', italic=True)
        TextDetail(parent=header_group, align=uiconst.TOPLEFT, text='TextHeader - 18px font size - 24px line-height', color=TextColor.DISABLED)
        TextBody(parent=grid, align=uiconst.TOPLEFT, width=320, text="A header that usually appears at the top of a content section. It's smaller and less attention-grabbing than a headline.", color=TextColor.SECONDARY)
        body_group = LayoutGrid(parent=grid, align=uiconst.TOPLEFT, columns=1)
        TextBody(parent=body_group, align=uiconst.TOPLEFT, text='Body')
        TextBody(parent=body_group, align=uiconst.TOPLEFT, text='Body Bold', bold=True)
        TextBody(parent=body_group, align=uiconst.TOPLEFT, text='Body Italic', italic=True)
        TextDetail(parent=body_group, align=uiconst.TOPLEFT, text='TextBody - 14px font size - 18px line-height', color=TextColor.DISABLED)
        TextBody(parent=grid, align=uiconst.TOPLEFT, width=320, text='The default style used for long-form writing as well as most inner text in UI elements, such as buttons and input fields. It is smaller in size than headlines and subheadings.', color=TextColor.SECONDARY)
        detail_group = LayoutGrid(parent=grid, align=uiconst.TOPLEFT, columns=1)
        TextDetail(parent=detail_group, align=uiconst.TOPLEFT, text='Detail')
        TextDetail(parent=detail_group, align=uiconst.TOPLEFT, text='Detail Bold', bold=True)
        TextDetail(parent=detail_group, align=uiconst.TOPLEFT, text='Detail Italic', italic=True)
        TextDetail(parent=detail_group, align=uiconst.TOPLEFT, text='TextDetail - 12px font size - 16px line-height', color=TextColor.DISABLED)
        TextBody(parent=grid, align=uiconst.TOPLEFT, width=320, text='A small piece of text that identifies or describes an adjacent element, such as an icon, a data value or a form field. It is smaller than body text and designed to be easily readable in a limited space.', color=TextColor.SECONDARY)

    def sample_code(self, parent):
        import carbonui
        carbonui.TextHeadline(parent=parent, text='Headline')
        carbonui.TextHeader(parent=parent, text='Header')
        carbonui.TextBody(parent=parent, text='Text')
        carbonui.TextDetail(parent=parent, text='Detail')


class Sample2(Sample):
    name = 'Custom'

    def construct_sample(self, parent):
        grid = LayoutGrid(parent=parent, columns=2, cellSpacing=(64, 32))
        font_size_cont = LayoutGrid(parent=grid, align=uiconst.TOPLEFT, columns=1)
        for i in xrange(13):
            TextCustom(parent=font_size_cont, align=uiconst.TOPLEFT, fontsize=8 + i, text='{}px font size'.format(8 + i))

        TextBody(parent=grid, align=uiconst.CENTER, width=360, text="For special cases where you need to display text that doesn't fit any of the pre-defined styles you can use the <b>TextCustom</b> class.<br><br>The custom class allows you to specify the font size, line spacing, and letter spacing, as well as the font path/family/variant.<br><br>Use of the custom class should be reserved for exceptional cases only where a designer has specifically requested it.", color=TextColor.SECONDARY)

    def sample_code(self, parent):
        import carbonui
        carbonui.TextCustom(parent=parent, fontsize=20, text='20px font size')


class Sample4(Sample):
    name = 'Formatting'
    description = 'You can change the format and color of parts of your text by wrapping it with the relevant tags. The most notable supported tags are: &lt;b&gt; for bold, &lt;i&gt; for italic, &lt;u&gt; for underlined, and &lt;color=0xAARRGGBB&gt; for color.'

    def construct_sample(self, parent):
        return self.sample_code(parent=ContainerAutoSize(parent=parent, align=uiconst.CENTER, alignMode=uiconst.TOTOP, width=460))

    def sample_code(self, parent):
        from eveformat import bold, italic, underline, color
        TextBody(parent=parent, align=uiconst.TOTOP, text="Here's some <b>bold text</b>, some <i>italic text</i>, and some <u>underlined text</u>\n\nYou can also <color=0xffff0000>color</color> your text\n\nFormatting <i>can <b>also <u>be <color=0xff00ff00>stacked</color></u></b></i>")
        TextBody(parent=parent, align=uiconst.TOTOP, top=24, text=''.join(['The ',
         bold('eveformat'),
         ' package also has some ',
         italic('nice'),
         ' ',
         color('convenience', '#aa00ff'),
         ' functions that can ',
         underline('help you'),
         ' format your text.']))


class Sample5(Sample):
    name = 'Color'
    description = 'The <b>TextColor</b> class contains color constants for different types of text:'

    def construct_sample(self, parent):
        variants = [(TextColor.NORMAL, 'TextColor.NORMAL', "The default color that's used for most text in the game."),
         (TextColor.HIGHLIGHT, 'TextColor.HIGHLIGHT', 'A stronger color used to emphasise text. Used f.ex. to indicate hovered or selected elements.'),
         (TextColor.SECONDARY, 'TextColor.SECONDARY', "A softer color used for text that's lower emphasis than normal text. Used f.ex. for supplementary information text, field headers, unselected tab labels etc."),
         (TextColor.DISABLED, 'TextColor.DISABLED', "A faint color that's mostly used for text associated with disabled UI components, such as buttons, checkboxes, etc."),
         (TextColor.SUCCESS, 'TextColor.SUCCESS', 'A color for highlighted text that indicates some kind of gain or a successful action by the player.'),
         (TextColor.WARNING, 'TextColor.WARNING', "A color for highlighted text that's warning the player about something risky (that can potentially be undone) or some condition that is preventing them from doing something."),
         (TextColor.DANGER, 'TextColor.DANGER', "A color for highlighted text that's warning the player about something dangerous (that can't be undone) or indicating some kind of loss."),
         (TextColor.AURA, 'TextColor.AURA', "A color that's used for instructional text from Aura.")]
        grid = LayoutGrid(parent=parent, align=uiconst.CENTER, columns=2, cellSpacing=(16, 24))
        for color, name, description in variants:
            TextBody(parent=grid, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, text=name, color=color)
            TextBody(parent=grid, align=uiconst.TOPLEFT, width=260, text=description, color=TextColor.SECONDARY)

    def sample_code(self, parent):
        from carbonui import TextBody, TextColor
        TextBody(parent=parent, align=uiconst.TOTOP, text='You gained 1.000.000 ISK', color=TextColor.SUCCESS)


class Sample6(Sample):
    name = 'Auto-fade'
    description = "The <b>audoFadeSides</b> property will make the text fade out if it doesn't fit and is clipped by its parent container.<br><br>The value determines the width of the fade effect in pixels.<br><br><i>Note that the text must be clipped by its immediate parent, not an ancestor further up the parent chain, for this effect to work. Additionally, this effect will not work if the alignment is set to TOTOP, since the parent will never clip a TOTOP aligned child.</i>"

    def construct_sample(self, parent):
        cont = Container(parent=GetHorizCollapsableCont(parent, width=376, height=64), align=uiconst.TOALL, padding=(8, 0, 0, 0))
        self.sample_code(cont)

    def sample_code(self, parent):
        TextBody(parent=parent, align=uiconst.CENTERLEFT, text='This is text that fades out if it runs out of space', autoFadeSides=16)


class Sample3(Sample):
    name = 'Playground'

    def construct_sample(self, parent):
        Playground(parent=parent, align=uiconst.CENTER)


class Playground(ContainerAutoSize):
    FIXED_TEXT_WIDTH = 200
    _text_alignment = TextAlign.LEFT
    _text_alignment_combo = None
    _text_bold = False
    _text_cached = None
    _text_color = TextColor.NORMAL
    _text_color_combo = None
    _text_element = None
    _text_fixed_width = False
    _text_fixed_width_checkbox = None
    _text_fixed_width_disabled_hint_sprite = None
    _text_font_size = 14
    _text_font_size_input = None
    _text_font_size_title = None
    _text_italic = False
    _text_layout_alignment = uiconst.CENTER
    _text_layout_alignment_combo = None
    _text_letter_spacing = 0
    _text_letter_spacing_input = None
    _text_line_spacing = 0
    _text_line_spacing_input = None
    _text_line_spacing_title = None
    _text_parent = None
    _text_style_class = TextBody
    _text_style_combo = None
    _text_underline = False
    _text_uppercase = False
    _text_word_count = 5
    _warning_icon = None

    def __init__(self, **kwargs):
        super(Playground, self).__init__(**kwargs)
        self._layout()
        self._redraw_text()

    def _layout(self):
        main = LayoutGrid(parent=self, align=uiconst.TOPLEFT, columns=2)
        self._text_parent = Container(parent=main, align=uiconst.TOPLEFT, width=500, height=560, clipChildren=True)
        Frame(bgParent=self._text_parent, align=uiconst.TOALL, opacity=0.05)
        self._warning_icon = WarningIcon(parent=self._text_parent, align=uiconst.TOPLEFT, top=8, left=8)
        option_wrap = Container(parent=main, align=uiconst.TOPLEFT, width=240, height=560, bgColor=(1.0, 1.0, 1.0, 0.05))
        options = Container(parent=option_wrap, align=uiconst.TOALL, padding=16)
        OptionTitle(parent=options, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Style', dev_hint=self._get_style_dev_hint)
        self._text_style_combo = Combo(parent=options, align=uiconst.TOTOP, options=[('Headline', TextHeadline),
         ('Header', TextHeader),
         ('Body', TextBody),
         ('Detail', TextDetail),
         ComboEntryDataSeparator(),
         ('Custom', TextCustom)], select=self._text_style_class, callback=self._on_style_changed, density=Density.COMPACT)
        OptionTitle(parent=options, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Text alignment', dev_hint=self._get_text_alignment_dev_hint)
        self._text_alignment_combo = Combo(parent=options, align=uiconst.TOTOP, options=[('Left', TextAlign.LEFT), ('Center', TextAlign.CENTER), ('Right', TextAlign.RIGHT)], select=self._text_alignment, callback=self._on_text_alignment_changed, density=Density.COMPACT)
        toggle_grid = LayoutGrid(parent=options, align=uiconst.TOTOP, padding=(0, 4, 0, 4), columns=2, cellSpacing=(24, 4))
        bold_grid = LayoutGrid(parent=toggle_grid, align=uiconst.TOPLEFT, padding=(0, 4, 0, 4), columns=2)
        Checkbox(parent=bold_grid, align=uiconst.TOPLEFT, text='Bold', checked=self._text_bold, callback=self._on_bold_changed)
        bold_dev_hint_sprite = Sprite(parent=bold_grid, align=uiconst.CENTER, left=4, width=16, height=16, texturePath=eveicon.brackets, color=TextColor.DISABLED)
        bold_dev_hint_sprite.GetHint = self._get_bold_dev_hint
        underline_grid = LayoutGrid(parent=toggle_grid, align=uiconst.TOPLEFT, padding=(0, 4, 0, 4), columns=2)
        Checkbox(parent=underline_grid, align=uiconst.TOPLEFT, text='Underline', checked=self._text_underline, callback=self._on_underline_changed)
        underline_dev_hint_sprite = Sprite(parent=underline_grid, align=uiconst.CENTER, left=4, width=16, height=16, texturePath=eveicon.brackets, color=TextColor.DISABLED)
        underline_dev_hint_sprite.GetHint = self._get_underline_dev_hint
        italic_grid = LayoutGrid(parent=toggle_grid, align=uiconst.TOPLEFT, padding=(0, 4, 0, 4), columns=2)
        Checkbox(parent=italic_grid, align=uiconst.TOPLEFT, text='Italic', checked=self._text_italic, callback=self._on_italic_changed)
        italic_dev_hint_sprite = Sprite(parent=italic_grid, align=uiconst.CENTER, left=4, width=16, height=16, texturePath=eveicon.brackets, color=TextColor.DISABLED)
        italic_dev_hint_sprite.GetHint = self._get_italic_dev_hint
        uppercase_grid = LayoutGrid(parent=toggle_grid, align=uiconst.TOPLEFT, padding=(0, 4, 0, 4), columns=2)
        Checkbox(parent=uppercase_grid, align=uiconst.TOPLEFT, text='Uppercase', checked=self._text_uppercase, callback=self._on_uppercase_changed)
        uppercase_dev_hint_sprite = Sprite(parent=uppercase_grid, align=uiconst.CENTER, left=4, width=16, height=16, texturePath=eveicon.brackets, color=TextColor.DISABLED)
        uppercase_dev_hint_sprite.GetHint = self._get_uppercase_dev_hint
        self._text_font_size_title = OptionTitle(parent=options, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Font size', dev_hint=self._get_font_size_dev_hint)
        self._text_font_size_input = SingleLineEditInteger(parent=options, align=uiconst.TOTOP, density=Density.COMPACT, minValue=1, maxValue=128, setvalue=self._text_font_size, OnChange=self._on_font_size_changed)
        self._update_font_size_enabled()
        self._text_letter_spacing_title = OptionTitle(parent=options, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Letter spacing', dev_hint=self._get_letter_spacing_dev_hint)
        self._text_letter_spacing_input = SingleLineEditInteger(parent=options, align=uiconst.TOTOP, density=Density.COMPACT, minValue=0, maxValue=128, setvalue=self._text_letter_spacing, OnChange=self._on_letter_spacing_changed)
        self._update_letter_spacing_enabled()
        self._text_line_spacing_title = OptionTitle(parent=options, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Line spacing', dev_hint=self._get_line_spacing_dev_hint)
        self._text_line_spacing_input = SingleLineEditFloat(parent=options, align=uiconst.TOTOP, density=Density.COMPACT, minValue=-128.0, maxValue=128.0, setvalue=self._text_line_spacing, OnChange=self._on_line_spacing_changed)
        self._update_line_spacing_enabled()
        OptionTitle(parent=options, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Color', dev_hint=self._get_color_dev_hint)
        self._text_color_combo = Combo(parent=options, align=uiconst.TOTOP, options=[(eveformat.color('Normal', TextColor.NORMAL), TextColorOption(name='TextColor.NORMAL', value=TextColor.NORMAL)),
         (eveformat.color('Secondary', TextColor.SECONDARY), TextColorOption(name='TextColor.SECONDARY', value=TextColor.SECONDARY)),
         (eveformat.color('Highlight', TextColor.HIGHLIGHT), TextColorOption(name='TextColor.HIGHLIGHT', value=TextColor.HIGHLIGHT)),
         (eveformat.color('Disabled', TextColor.DISABLED), TextColorOption(name='TextColor.DISABLED', value=TextColor.DISABLED)),
         (eveformat.color('Success', TextColor.SUCCESS), TextColorOption(name='TextColor.SUCCESS', value=TextColor.SUCCESS)),
         (eveformat.color('Warning', TextColor.WARNING), TextColorOption(name='TextColor.WARNING', value=TextColor.WARNING)),
         (eveformat.color('Danger', TextColor.DANGER), TextColorOption(name='TextColor.DANGER', value=TextColor.DANGER)),
         (eveformat.color('Aura', TextColor.AURA), TextColorOption(name='TextColor.AURA', value=TextColor.AURA))], select=self._text_color, callback=self._on_color_changed, density=Density.COMPACT)
        DividerLine(parent=options, align=uiconst.TOTOP, padding=(0, 16, 0, 16))
        OptionTitle(parent=options, align=uiconst.TOTOP, padding=(0, 0, 0, 4), text='Word count')
        Slider(parent=options, align=uiconst.TOTOP, value=self._text_word_count, minValue=1, maxValue=300, callback=self._set_text_word_count, on_dragging=self._set_text_word_count, getHintFunc=lambda s: '{} words'.format(int(s.value)))
        OptionTitle(parent=options, align=uiconst.TOTOP, padding=(0, 8, 0, 4), text='Layout alignment', dev_hint=self._get_layout_alignment_dev_hint)
        self._text_layout_alignment_combo = Combo(parent=options, align=uiconst.TOTOP, options=[('CENTER', uiconst.CENTER),
         ('TOLEFT', uiconst.TOLEFT),
         ('TORIGHT', uiconst.TORIGHT),
         ('TOPLEFT', uiconst.TOPLEFT),
         ('TOPRIGHT', uiconst.TOPRIGHT),
         ('TOTOP', uiconst.TOTOP)], select=self._text_layout_alignment, callback=self._on_layout_alignment_changed, density=Density.COMPACT)
        fixed_width_grid = LayoutGrid(parent=options, align=uiconst.TOTOP, padding=(0, 4, 0, 4), columns=3)
        self._text_fixed_width_checkbox = Checkbox(parent=fixed_width_grid, align=uiconst.CENTERLEFT, text='Fixed width', checked=self._text_fixed_width, callback=self._on_fixed_width_changed)
        Sprite(parent=fixed_width_grid, align=uiconst.CENTERLEFT, left=4, width=16, height=16, texturePath=eveicon.brackets, color=TextColor.DISABLED, hint='Assigns a fixed width to the text element when enabled:<br><br>    {text_style}(<br>        width={fixed_width},<br>    )'.format(text_style=self._text_style_class.__name__, fixed_width=self.FIXED_TEXT_WIDTH))
        self._text_fixed_width_disabled_hint_sprite = Sprite(parent=fixed_width_grid, align=uiconst.CENTER, left=4, width=16, height=16, texturePath=eveicon.block_ban, color=TextColor.DISABLED)
        self._text_fixed_width_disabled_hint_sprite.GetHint = self._get_fixed_width_disabled_hint
        self._update_fixed_width_enabled()

    @uthread2.debounce(wait=0.05, leading=True, max_wait=0.1)
    def _redraw_text(self):
        if self._text_element is not None:
            self._text_element.Close()
            self._text_element = None
        if self._text_style_class == TextCustom:
            self._text_element = TextCustom(parent=self._text_parent, align=self._text_layout_alignment, width=self.FIXED_TEXT_WIDTH if self._text_fixed_width else 0, text=self._get_text(), textAlign=self._text_alignment, fontsize=self._text_font_size, letterspace=self._text_letter_spacing, lineSpacing=self._text_line_spacing, bold=self._text_bold, italic=self._text_italic, underline=self._text_underline, uppercase=self._text_uppercase, color=self._text_color_combo.GetValue().value)
        else:
            self._text_element = self._text_style_class(parent=self._text_parent, align=self._text_layout_alignment, width=self.FIXED_TEXT_WIDTH if self._text_fixed_width else 0, text=self._get_text(), textAlign=self._text_alignment, bold=self._text_bold, italic=self._text_italic, underline=self._text_underline, uppercase=self._text_uppercase, color=self._text_color_combo.GetValue().value)

    def _get_text(self):
        if self._text_cached is None:
            self._generate_text()
        return self._text_cached

    def _generate_text(self):
        if self._text_cached is None:
            self._text_cached = ''
            words = []
        else:
            words = self._text_cached.split()
        if self._text_word_count > len(words):
            self._text_cached = ' '.join(itertools.chain(self._text_cached.split(), pick_random_words(self._text_word_count - len(words))))
        elif self._text_word_count < len(words):
            self._text_cached = ' '.join(words[:self._text_word_count])

    def _on_style_changed(self, combo, key, value):
        self._text_style_class = value
        self._update_font_size_enabled()
        self._update_letter_spacing_enabled()
        self._update_line_spacing_enabled()
        self._redraw_text()

    def _get_style_dev_hint(self):
        return 'Each style has a corresponding class. The class name for the {style} style is <b>{style_class_name}</b>:<br><br>    {style_class_name}(<br>        text="...",<br>    )'.format(style=self._text_style_combo.GetKey(), style_class_name=self._text_style_class.__name__)

    def _on_text_alignment_changed(self, combo, key, value):
        self._text_alignment = value
        if self._text_element is not None:
            self._text_element.SetTextAlign(value)
        self._update_warnings()

    def _get_text_alignment_dev_hint(self):
        return 'Corresponds to the <b>textAlign</b> parameter:<br><br>    {class_name}(<br>        <b>textAlign={text_alignment}</b>,<br>    )<br><br>You can also change the text alignment using:<br><br>    text.<b>SetTextAlign({text_alignment})</b>'.format(class_name=self._text_style_class.__name__, text_alignment=TEXT_ALIGNMENT_CONST_NAME[self._text_alignment_combo.GetValue()])

    def _on_font_size_changed(self, text):
        if self._text_style_class == TextCustom:
            self._text_font_size = self._text_font_size_input.GetValue()
            self._redraw_text()

    def _get_font_size_disabled_hint(self):
        return "You can't customize the font size of {}. If you need to use a custom font size you should use the <b>TextCustom</b> class (pick 'Custom' in the Style combo above).".format(self._text_style_class.__name__)

    def _update_font_size_enabled(self):
        if self._text_style_class != TextCustom:
            self._text_font_size_input.Disable()
            self._text_font_size_title.disabled_hint = self._get_font_size_disabled_hint
        else:
            self._text_font_size_input.Enable()
            self._text_font_size_title.disabled_hint = None

    def _get_font_size_dev_hint(self):
        return 'Corresponds to the <b>fontsize</b> property:<br><br>    TextCustom(<br>        <b>fontsize={fontsize}</b>,<br>    )'.format(fontsize=self._text_font_size)

    def _on_letter_spacing_changed(self, text):
        if self._text_style_class == TextCustom:
            self._text_letter_spacing = self._text_letter_spacing_input.GetValue()
            self._redraw_text()

    def _get_letter_spacing_disabled_hint(self):
        return "You can't customize the letter spacing of {}. If you need to use a custom letter spacing value you should use the <b>TextCustom</b> class (pick 'Custom' in the Style combo above).".format(self._text_style_class.__name__)

    def _update_letter_spacing_enabled(self):
        if self._text_style_class != TextCustom:
            self._text_letter_spacing_input.Disable()
            self._text_letter_spacing_title.disabled_hint = self._get_letter_spacing_disabled_hint
        else:
            self._text_letter_spacing_input.Enable()
            self._text_letter_spacing_title.disabled_hint = None

    def _get_letter_spacing_dev_hint(self):
        return 'Corresponds to the <b>letterspace</b> property:<br><br>    TextCustom(<br>        <b>letterspace={letter_spacing}</b>,<br>    )'.format(letter_spacing=self._text_letter_spacing)

    def _on_line_spacing_changed(self, text):
        if self._text_style_class == TextCustom:
            self._text_line_spacing = self._text_line_spacing_input.GetValue()
            self._redraw_text()

    def _get_line_spacing_disabled_hint(self):
        return "You can't customize the line spacing of {}. If you need to use a custom line spacing value you should use the <b>TextCustom</b> class (pick 'Custom' in the Style combo above).".format(self._text_style_class.__name__)

    def _update_line_spacing_enabled(self):
        if self._text_style_class != TextCustom:
            self._text_line_spacing_input.Disable()
            self._text_line_spacing_title.disabled_hint = self._get_line_spacing_disabled_hint
        else:
            self._text_line_spacing_input.Enable()
            self._text_line_spacing_title.disabled_hint = None

    def _get_line_spacing_dev_hint(self):
        return 'Corresponds to the <b>lineSpacing</b> property:<br><br>    TextCustom(<br>        <b>lineSpacing={line_spacing}</b>,<br>    )'.format(line_spacing=self._text_line_spacing)

    def _on_bold_changed(self, checkbox):
        self._text_bold = bool(checkbox.checked)
        self._redraw_text()

    def _get_bold_dev_hint(self):
        return 'Corresponds to the <b>bold</b> property:<br><br>    {class_name}(<br>        <b>bold={enabled}</b>,<br>    )'.format(class_name=self._text_style_class.__name__, enabled=repr(self._text_bold))

    def _on_italic_changed(self, checkbox):
        self._text_italic = bool(checkbox.checked)
        self._redraw_text()

    def _get_italic_dev_hint(self):
        return 'Corresponds to the <b>italic</b> property:<br><br>    {class_name}(<br>        <b>italic={enabled}</b>,<br>    )'.format(class_name=self._text_style_class.__name__, enabled=repr(self._text_italic))

    def _on_underline_changed(self, checkbox):
        self._text_underline = bool(checkbox.checked)
        self._redraw_text()

    def _get_underline_dev_hint(self):
        return 'Corresponds to the <b>underline</b> property:<br><br>    {class_name}(<br>        <b>underline={enabled}</b>,<br>    )'.format(class_name=self._text_style_class.__name__, enabled=repr(self._text_underline))

    def _on_uppercase_changed(self, checkbox):
        self._text_uppercase = bool(checkbox.checked)
        self._redraw_text()

    def _get_uppercase_dev_hint(self):
        return 'Corresponds to the <b>uppercase</b> property:<br><br>    {class_name}(<br>        <b>uppercase={enabled}</b>,<br>    )'.format(class_name=self._text_style_class.__name__, enabled=repr(self._text_uppercase))

    def _on_color_changed(self, combo, key, value):
        self._text_color = value.value
        self._redraw_text()

    def _get_color_dev_hint(self):
        return 'Corresponds to the <b>color</b> property:<br><br>    {class_name}(<br>        <b>color={color_name}</b>,<br>    )'.format(class_name=self._text_style_class.__name__, color_name=self._text_color_combo.GetValue().name)

    def _on_layout_alignment_changed(self, combo, key, value):
        self._text_layout_alignment = value
        if self._text_element is not None:
            self._text_element.align = value
        self._update_fixed_width_enabled()
        self._update_warnings()

    def _get_layout_alignment_dev_hint(self):
        return 'Corresponds to the <b>align</b> property:<br><br>    {class_name}(<br>        <b>align=uiconst.{align}</b>,<br>    )'.format(class_name=self._text_style_class.__name__, align=self._text_layout_alignment_combo.GetKey())

    def _set_text_word_count(self, slider):
        self._text_word_count = int(slider.value)
        self._generate_text()
        self._redraw_text()

    def _update_warnings(self):
        warnings = []
        if self._text_alignment != TextAlign.LEFT and not self._text_fixed_width and self._text_layout_alignment in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH:
            warnings.append('When you combine {text_alignment} with a {layout_alignment} layout alignment (or any other layout alignment that does not constrain the horizontal size of the text) the text element gets confused and assignes the maximum possible horizontal size to itself.<br><br>You can avoid this situation by either changing the layout alignment of the text element, or by assigning it a fixed width.'.format(text_alignment=TEXT_ALIGNMENT_CONST_NAME[self._text_alignment], layout_alignment=self._text_layout_alignment_combo.GetKey()))
        self._warning_icon.show_warnings(warnings)

    def _on_fixed_width_changed(self, checkbox):
        self._text_fixed_width = bool(checkbox.checked)
        self._redraw_text()
        self._update_warnings()

    def _get_fixed_width_disabled_hint(self):
        return 'The {layout_alignment} layout alignment derives its width from the parent container, so the text already has an implicit fixed width.'.format(layout_alignment=self._text_layout_alignment_combo.GetKey())

    def _update_fixed_width_enabled(self):
        if self._text_layout_alignment in uiconst.ALIGNMENTS_WITH_RELEVANT_WIDTH:
            self._text_fixed_width_checkbox.Enable()
            self._text_fixed_width_disabled_hint_sprite.display = False
        else:
            self._text_fixed_width_checkbox.Disable()
            self._text_fixed_width_disabled_hint_sprite.display = True


class TextColorOption(object):

    def __init__(self, name, value):
        self.name = name
        self.value = value


class OptionTitle(LayoutGrid):
    _dev_hint_sprite = None

    def __init__(self, text, dev_hint = None, disabled_hint = None, **kwargs):
        self._text = text
        self._dev_hint = dev_hint
        self._disabled_hint = disabled_hint
        super(OptionTitle, self).__init__(columns=3, **kwargs)
        self._layout()

    @property
    def dev_hint(self):
        return self._dev_hint

    @dev_hint.setter
    def dev_hint(self, value):
        if self._dev_hint != value:
            self._dev_hint = value
            self._update_dev_hint_display()

    @property
    def disabled_hint(self):
        return self._disabled_hint

    @disabled_hint.setter
    def disabled_hint(self, value):
        if self._disabled_hint != value:
            self._disabled_hint = value
            self._update_disabled_hint_display()

    def _layout(self):
        TextDetail(parent=self, align=uiconst.CENTER, text=self._text)
        self._dev_hint_sprite = Sprite(parent=self, align=uiconst.CENTER, left=4, width=16, height=16, texturePath=eveicon.brackets, color=TextColor.DISABLED)
        self._dev_hint_sprite.LoadTooltipPanel = self._get_dev_hint
        self._update_dev_hint_display()
        self._disabled_hint_sprite = Sprite(parent=self, align=uiconst.CENTER, left=4, width=16, height=16, texturePath=eveicon.block_ban, color=TextColor.DISABLED)
        self._disabled_hint_sprite.LoadTooltipPanel = self._get_disabled_hint
        self._update_disabled_hint_display()

    def _get_dev_hint(self, panel, *args):
        if callable(self._dev_hint):
            hint = self._dev_hint()
        else:
            hint = self._dev_hint
        if hint:
            panel.LoadStandardSpacing()
            panel.columns = 1
            panel.AddLabelMedium(text=hint, wrapWidth=360)

    def _update_dev_hint_display(self):
        if self._dev_hint is None:
            self._dev_hint_sprite.display = False
        else:
            self._dev_hint_sprite.display = True

    def _get_disabled_hint(self, panel, *args):
        if callable(self._disabled_hint):
            hint = self._disabled_hint()
        else:
            hint = self._disabled_hint
        if hint:
            panel.LoadStandardSpacing()
            panel.columns = 1
            panel.AddLabelMedium(text=hint, wrapWidth=360)

    def _update_disabled_hint_display(self):
        if self._disabled_hint is None:
            self._disabled_hint_sprite.display = False
        else:
            self._disabled_hint_sprite.display = True


class WarningIcon(ContainerAutoSize):
    _counter = None
    _grid = None

    def __init__(self, state = uiconst.UI_NORMAL, **kwargs):
        self._warnings = []
        super(WarningIcon, self).__init__(state=state, **kwargs)
        self._layout()

    def show_warnings(self, warnings):
        self._warnings = warnings
        self._update_visibility()
        self._update_counter_text()

    def clear_warnings(self):
        self.show_warnings([])

    def _layout(self):
        self._grid = LayoutGrid(parent=self, align=uiconst.TOPLEFT, columns=2)
        self._update_visibility()
        Sprite(parent=self._grid, align=uiconst.CENTER, width=28, height=28, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/warningGroup.png', color=TextColor.WARNING)
        self._counter = TextBody(parent=self._grid, align=uiconst.CENTERLEFT, left=4, color=TextColor.WARNING, text=self._get_counter_text())

    def _update_visibility(self):
        if self._grid:
            self._grid.display = len(self._warnings) > 0

    def _get_counter_text(self):
        return str(len(self._warnings))

    def _update_counter_text(self):
        if self._counter:
            self._counter.text = self._get_counter_text()

    def LoadTooltipPanel(self, panel, *args):
        if self._warnings:
            panel.LoadStandardSpacing()
            panel.columns = 1
            for warning in self._warnings:
                panel.AddLabelMedium(wrapWidth=360, text=warning)


TEXT_ALIGNMENT_CONST_NAME = {TextAlign.LEFT: 'TextAlign.LEFT',
 TextAlign.CENTER: 'TextAlign.CENTER',
 TextAlign.RIGHT: 'TextAlign.RIGHT'}
WORDS = ['a',
 'ac',
 'accumsan',
 'aenean',
 'aliquam',
 'amet',
 'ante',
 'arcu',
 'arcupellentesque',
 'at',
 'auctor',
 'augue',
 'bibendum',
 'commodo',
 'condimentum',
 'congue',
 'consectetur',
 'consequat',
 'convallis',
 'cras',
 'curabitur',
 'cursus',
 'cursusduis',
 'dapibus',
 'diam',
 'dis',
 'dolor',
 'dui',
 'duis',
 'efficitur',
 'eget',
 'eleifend',
 'elit',
 'erat',
 'eros',
 'est',
 'et',
 'etiam',
 'eu',
 'euismod',
 'ex',
 'facilisi',
 'facilisis',
 'faucibus',
 'felis',
 'fermentum',
 'feugiat',
 'finibus',
 'hendrerit',
 'iaculis',
 'id',
 'imperdiet',
 'in',
 'integer',
 'ipsum',
 'justo',
 'lacinia',
 'lacus',
 'lectus',
 'leo',
 'libero',
 'ligula',
 'lobortis',
 'lorem',
 'luctus',
 'maecenas',
 'magna',
 'magnis',
 'malesuada',
 'massa',
 'mauris',
 'maximus',
 'metus',
 'mi',
 'molestie',
 'mollis',
 'montes',
 'morbi',
 'mus',
 'nam',
 'nascetur',
 'natoque',
 'nec',
 'nibh',
 'non',
 'nulla',
 'nunc',
 'odio',
 'orci',
 'ornare',
 'parturient',
 'pellentesque',
 'penatibus',
 'pharetra',
 'placerat',
 'porta',
 'porttitor',
 'praesent',
 'pretium',
 'proin',
 'pulvinar',
 'purus',
 'quis',
 'quisque',
 'rhoncus',
 'ridiculus',
 'sapien',
 'scelerisque',
 'sed',
 'sit',
 'sollicitudin',
 'suscipit',
 'suspendisse',
 'tellus',
 'tempus',
 'tincidunt',
 'tortor',
 'turpis',
 'ullamcorper',
 'ultrices',
 'ultricies',
 'urna',
 'ut',
 'varius',
 'vel',
 'velit',
 'venenatis',
 'vitae',
 'vivamus',
 'volutpat',
 'vulputate']

def pick_random_words(word_count):
    return [ random.choice(WORDS) for _ in xrange(word_count) ]
