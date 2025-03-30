#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\ui\category.py
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import FrameThemeColored, SpriteThemeColored
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from projectdiscovery.client import const
from signals import Signal
import carbonui.const as uiconst
from eve.client.script.ui.control import tooltips
import math
import blue
import localization

class CategorySelectionManager(object):
    __notifyevents__ = ['OnCategorySelectedChange']

    def __init__(self, categories):
        super(CategorySelectionManager, self).__init__()
        self._category_ids = [ category['id'] for category in categories ]
        self._exclude_info = {}
        sm.RegisterNotify(self)

    def OnCategorySelectedChange(self, category_id, category_excludes, is_selected):
        if category_id not in self._category_ids:
            return
        if is_selected:
            self._exclude_info[category_id] = category_excludes
            excluded = self._get_all_excluded_ids()
            sm.ScatterEvent('OnUpdateExcludedCategories', excluded, True)
        else:
            not_excluded = self._exclude_info.pop(category_id, [])
            excluded = self._get_all_excluded_ids()
            not_excluded = [ cat_id for cat_id in not_excluded if category_id not in excluded ]
            sm.ScatterEvent('OnUpdateExcludedCategories', not_excluded, False)

    def _get_all_excluded_ids(self):
        excluded_ids = []
        for excluded in self._exclude_info.values():
            excluded_ids += excluded

        return list(set(excluded_ids))

    def remove_all_from_excluded(self):
        self._exclude_info.clear()


class CategoryGrid(Container):
    __notifyevents__ = ['OnProjectDiscoveryRescaled']
    default_name = 'CategoryGrid'
    default_align = uiconst.TOPLEFT
    default_width = 500
    default_height = 200
    default_clipChildren = False

    def ApplyAttributes(self, attributes):
        super(CategoryGrid, self).ApplyAttributes(attributes)
        self._categories = attributes.get('categories', [])
        self._cell_width = attributes.get('cellWidth', 56)
        self._cell_height = attributes.get('cellHeight', 56)
        self._space_between_cells = attributes.get('cellSpace', 15)
        self._row_offset = attributes.get('rowOffset', 39)
        self._category_layout = attributes.get('categoryLayout', [[ True for category in self._categories ]])
        self._category_hexagons = []
        self._category_selection_manager = CategorySelectionManager(self._categories)
        self.on_resize = Signal(signalName='on_resize')
        self._setup_layout()
        sm.RegisterNotify(self)

    def _setup_layout(self):
        for category, (x, y) in self._zip_categories_with_coordinates(self._categories):
            hexagon = CategoryCircle(parent=self, category=category, top=y, left=x, width=self._cell_width, height=self._cell_height, opacity=0)
            self._category_hexagons.append(hexagon)

        self._correct_size()

    def OnProjectDiscoveryRescaled(self, scale):
        for cat in self._category_hexagons:
            cat.rescale(scale)

    def UpdateAlignment(self, *args, **kwargs):
        budget = super(CategoryGrid, self).UpdateAlignment(*args, **kwargs)
        self._correct_size()
        return budget

    def _zip_categories_with_coordinates(self, categories):
        categories_copy = [ category for category in categories ]
        cell_half_height = self._cell_height / 2.0
        result = []
        y = 0
        for row_num, row in enumerate(self._category_layout):
            for i, is_filled in enumerate(row):
                if is_filled:
                    x = i * self._space_between_cells + i * self._cell_width
                    x += self._row_offset if row_num % 2 != 0 else 0
                    result.append((categories_copy.pop(), (x, y)))

            y += self._cell_height + self._space_between_cells

        return result

    def _correct_size(self):
        right_hexagon = sorted(self._category_hexagons, key=lambda hexagon: hexagon.left)[-1]
        bottom_hexagon = sorted(self._category_hexagons, key=lambda hexagon: hexagon.top)[-1]
        left_hexagon = sorted(self._category_hexagons, key=lambda hexagon: hexagon.left)[0]
        top_hexagon = sorted(self._category_hexagons, key=lambda hexagon: hexagon.top)[0]
        self.width = right_hexagon.left + right_hexagon.width - left_hexagon.left * 2
        self.height = bottom_hexagon.top + bottom_hexagon.height - top_hexagon.top * 2
        self.on_resize(self.width, self.height)

    def cascade_in(self, duration, callback = None, time_offset = 0):
        for i, (hexagon, offset) in enumerate(zip(self._category_hexagons, self._get_time_offsets(duration, time_offset))):
            _callback = callback if i == len(self._category_hexagons) - 1 else None
            animations.BlinkIn(hexagon, timeOffset=offset, callback=_callback)

    def cascade_out(self, duration, callback = None, time_offset = 0):
        for i, (hexagon, offset) in enumerate(zip(self._category_hexagons, self._get_time_offsets(duration, time_offset))):
            _callback = callback if i == len(self._category_hexagons) - 1 else None
            animations.BlinkOut(hexagon, timeOffset=offset, callback=_callback)

    def _get_time_offsets(self, max_duration, time_offset_added = 0):
        offsets = []
        max_distance = math.sqrt(self.width ** 2 + self.height ** 2)
        for hexagon in self._category_hexagons:
            t = math.sqrt(hexagon.left ** 2 + hexagon.top ** 2) / max_distance
            time_offset = t * max_duration + time_offset_added
            offsets.append(time_offset)

        return offsets

    def initialize(self):
        self._category_selection_manager.remove_all_from_excluded()
        for hexagon in self._category_hexagons:
            hexagon.reset()

    def Disable(self, *args):
        for hexagon in self._category_hexagons:
            hexagon.set_unclickable()

    def Enable(self, *args):
        for hexagon in self._category_hexagons:
            hexagon.set_clickable()


class Hexagon(Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_pickRadius = -1
    default_width = 52
    default_height = 46

    def ApplyAttributes(self, attributes):
        super(Hexagon, self).ApplyAttributes(attributes)
        self.hexagon_outline = Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexOutline.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(0.32, 0.32, 0.32, 1))


class Circle(Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_pickRadius = -1
    default_width = 32
    default_height = 32
    default_clipChildren = False

    def ApplyAttributes(self, attributes):
        super(Circle, self).ApplyAttributes(attributes)
        self._outline = Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/CircleOutline.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=(0.32, 0.32, 0.32, 1))


class CategoryCircle(Container):
    __notifyevents__ = ['OnUpdateExcludedCategories', 'OnCategoryVoteResult']
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    GLOW_ANIMATION = {'duration': 0.3,
     'curveType': uiconst.ANIM_OVERSHOT2}
    MIN_COLOR_VALUE = (0.5, 0.22, 0.17)
    MAX_COLOR_VALUE = (0.33, 0.49, 0.26)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.category = attributes.get('category')
        self.attributes = attributes
        self.id = self.category['id']
        self.excludes = self.category['excludes']
        self.unavailable = False
        self.unclickable = False
        self._vote_percentage = 0
        self._original_left = self.attributes.get('left')
        self._original_top = self.attributes.get('top')
        self._original_width = self.attributes.get('width')
        self._original_height = self.attributes.get('height')
        attributes['tooltipHeader'] = self.category['name']
        attributes['tooltipText'] = self.category.get('descriptionIdentification', self.category['description'])
        sm.RegisterNotify(self)
        self.consensus_percentage = Label(parent=self, align=uiconst.CENTER, text='0', fontsize=12, state=uiconst.UI_HIDDEN)
        self.exclude_texture = Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryUnavailable.png', state=uiconst.UI_HIDDEN, align=uiconst.TOALL)
        self.selected_texture = GlowSprite(name='selectedTexture', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/circleSelected.png', align=uiconst.TOALL, idx=0, state=uiconst.UI_DISABLED, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.3)
        self._selected_glow = SpriteThemeColored(name='selectedGlow', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/selectedGlow.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, opacity=0)
        self.image = GlowSprite(name='image', parent=self, align=uiconst.CENTER, height=32, width=32, texturePath='res:/UI/Texture/classes/ProjectDiscovery/exoplanets/' + self.category['url'], state=uiconst.UI_DISABLED, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self._inner_glow = SpriteThemeColored(name='innerGlow', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/innerGlow.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, opacity=0.1, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self._base = SpriteThemeColored(name='Base', parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/circleBaseWhite.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.4)
        self._gauge = GaugeCircular(name='Gauge', parent=self, align=uiconst.CENTER, colorStart=Color.GRAY2, colorEnd=Color.GRAY2, bgPortion=0, showMarker=False, radius=self.width / 2, lineWidth=4, state=uiconst.UI_DISABLED)
        self.tooltipPanelClassInfo = CategoryTooltipWrapper(header=attributes['tooltipHeader'], description=attributes['tooltipText'], imagePath='res:/UI/Texture/classes/ProjectDiscovery/exoplanets/' + self.category['conceptUrl'], category=self.category)

    def rescale(self, scale):
        pass

    def OnCategoryVoteResult(self, voting_dictionary):
        if self.category['id'] in voting_dictionary:
            animations.FadeTo(self.image, self.image.opacity, 0.3)
            percentage = voting_dictionary[self.category['id']]
            self.set_percentage(percentage)

    def OnMouseEnter(self, *args):
        if not self.unavailable:
            animations.FadeTo(self._base, 0.4, 0.6)
            if not self.unavailable and not self.unclickable and not self.category['selected']:
                animations.FadeTo(self.image, 1, 1.3)
                animations.SpGlowFadeIn(self.image)

    def OnMouseExit(self, *args):
        if not self.unavailable:
            animations.FadeTo(self._base, 0.6, 0.4)
            if not self.unavailable and not self.unclickable and not self.category['selected']:
                animations.FadeTo(self.image, 1.3, 1)
                animations.SpGlowFadeOut(self.image)

    def set_percentage(self, percentage):
        animations.MorphScalar(self, '_percentage', self._vote_percentage, percentage)

    def _update_ui_percentage(self, percentage):
        self.consensus_percentage.state = uiconst.UI_DISABLED
        self.consensus_percentage.SetText('%s%%' % percentage)
        self._gauge.SetValue(percentage / 100.0, animate=False)

    def set_unavailable(self):
        self.unavailable = True
        self.image.SetTexturePath('res:/UI/Texture/classes/ProjectDiscovery/subcellular/gray_' + self.category['url'])
        self.tooltipPanelClassInfo = None

    def set_available(self):
        self.unavailable = False
        self.image.SetTexturePath('res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + self.category['url'][:-4] + '_NA.png')
        self.tooltipPanelClassInfo = CategoryTooltipWrapper(header=self.attributes['tooltipHeader'], description=self.attributes['tooltipText'], imagePath='res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + self.category['url'][:-4] + '_NA.png', category=self.category)

    def set_unclickable(self):
        self.unclickable = True

    def set_clickable(self):
        self.unclickable = False

    def lerp(self, value, maximum, start_point, end_point):
        return start_point + (end_point - start_point) * value / maximum

    def lerp_color(self, value, maximum, start_point = MIN_COLOR_VALUE, end_point = MAX_COLOR_VALUE):
        r = self.lerp(value, maximum, start_point[0], end_point[0])
        g = self.lerp(value, maximum, start_point[1], end_point[1])
        b = self.lerp(value, maximum, start_point[2], end_point[2])
        return (r,
         g,
         b,
         1)

    def OnClick(self, *args):
        if self.exclude_texture.state is not uiconst.UI_HIDDEN or self.unclickable is True:
            return
        sm.GetService('audio').SendUIEvent(const.Sounds.CategorySelectPlay)
        self.category['selected'] = not self.category['selected']
        if self.category['selected']:
            animations.FadeTo(self.selected_texture, 0.3, 1, duration=0.2)
            animations.FadeTo(self.image, 1, 1.3)
            animations.SpGlowFadeIn(self.image)
            animations.FadeIn(self._selected_glow, **self.GLOW_ANIMATION)
        else:
            animations.FadeTo(self.selected_texture, 1, 0.3, duration=0.2)
            animations.FadeOut(self._selected_glow, **self.GLOW_ANIMATION)
        sm.ScatterEvent('OnCategorySelectedChange', self.category['id'], self.category['excludes'], self.category['selected'])

    def GetTooltipPosition(self, *args):
        return self.GetAbsolute()

    def OnUpdateExcludedCategories(self, categories_changed, is_excluded):
        cat_id = self.category['id']
        if cat_id in categories_changed:
            if is_excluded:
                self.category['excluded'] = True
                self.exclude_texture.state = uiconst.UI_DISABLED
                self.selected_texture.opacity = 0
            else:
                self.category['excluded'] = False
                self.exclude_texture.state = uiconst.UI_HIDDEN
                if self.category['selected']:
                    self.selected_texture.opacity = 1

    def reset(self):
        self.category['selected'] = False
        self.category['excluded'] = False
        self._vote_percentage = 0
        self.image.opacity = 1
        animations.SpGlowFadeOut(self.image)
        self.selected_texture.opacity = 0.3
        self._gauge.SetValue(0, animate=False)
        self._selected_glow.opacity = 0
        self.exclude_texture.state = uiconst.UI_HIDDEN
        self.consensus_percentage.state = uiconst.UI_HIDDEN

    @property
    def _percentage(self):
        return self._vote_percentage

    @_percentage.setter
    def _percentage(self, value):
        self._vote_percentage = round(value, 1)
        self._update_ui_percentage(self._vote_percentage)


class CategoryTooltipWrapper(TooltipBaseWrapper):
    IMAGE_SIZE = 300
    __notifyevents__ = ['OnSwitchTooltipImage', 'OnToolTipExampleClicked']

    def __init__(self, header, description, imagePath, category, *args, **kwargs):
        super(CategoryTooltipWrapper, self).__init__(*args, **kwargs)
        self._start_position = None
        self._end_position = None
        self._is_right_direction = True
        self._headerText = header
        self._descriptionText = description
        self._imagePath = imagePath
        self.category = category
        sm.RegisterNotify(self)

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.add_description_label()
        self.add_main_image_container()
        self.add_example_images()
        return self.tooltipPanel

    def get_image_paths_for_category(self):
        image_paths = []
        for imageFileName in blue.paths.listdir('res:/UI/Texture/classes/ProjectDiscovery/exoplanets/%s/examples' % str(self.category['id'])):
            path = 'res:/UI/Texture/classes/ProjectDiscovery/exoplanets/%s/examples/%s' % (str(self.category['id']), imageFileName)
            image_paths.append(path)

        return image_paths

    def add_example_images(self):
        image_paths = self.get_image_paths_for_category()
        self.tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/ProjectDiscovery/TooltipExamplesLabel'), bold=True, cellPadding=(0, 5, 0, 5), wrapWidth=300)
        image_icon_container = Container(width=self.IMAGE_SIZE, height=75, align=uiconst.TOPLEFT)
        FrameThemeColored(bgParent=image_icon_container, colorType=uiconst.COLORTYPE_UIHILIGHT)
        for imagePath in image_paths:
            TooltipExampleSprite(name='TooltipExampleSprite', parent=Container(parent=image_icon_container, width=self.IMAGE_SIZE / len(image_paths), align=uiconst.TOLEFT), align=uiconst.TOALL, padding=(5, 5, 5, 5), texturePath=imagePath)

        self.tooltipPanel.AddCell(image_icon_container, cellPadding=(0, 5, 0, 5))

    def add_main_image_container(self):
        image_container = Container(width=self.IMAGE_SIZE, height=self.IMAGE_SIZE, align=uiconst.TOPLEFT, clipChildren=True)
        FrameThemeColored(bgParent=image_container, colorType=uiconst.COLORTYPE_UIHILIGHT)
        inner_image_container = Container(parent=image_container, width=self.IMAGE_SIZE - 2, height=self.IMAGE_SIZE - 2, align=uiconst.CENTER, clipChildren=True)
        self.imageSprite = Sprite(parent=inner_image_container, width=self.IMAGE_SIZE - 2, height=self.IMAGE_SIZE - 2, texturePath=self._imagePath, align=uiconst.CENTERLEFT)
        self.tooltipPanel.AddCell(image_container, cellPadding=(0, 5, 0, 5))

    def add_description_label(self):
        self.tooltipPanel.AddLabelMedium(text=self._headerText, bold=True, cellPadding=(0, 5, 0, 5), wrapWidth=300)
        self.tooltipPanel.AddLabelMedium(text=self._descriptionText, align=uiconst.TOPLEFT, wrapWidth=300, color=(0.6, 0.6, 0.6, 1))

    def OnSwitchTooltipImage(self, tooltip_example_sprite = None):
        if hasattr(self, 'imageSprite'):
            self.fade_out_tooltip_image(tooltip_example_sprite)

    def fade_out_tooltip_image(self, sprite):
        path = sprite.path if sprite else self._imagePath
        self.imageSprite.width = sprite.actual_width - 2 if sprite else self.IMAGE_SIZE - 2
        self.imageSprite.height = sprite.actual_height - 2 if sprite else self.IMAGE_SIZE - 2
        self.imageSprite.left = 0
        self._is_right_direction = True
        if self.imageSprite.width > self.IMAGE_SIZE:
            self._pan_image()
            sprite.display_animation_icons()
        else:
            self.imageSprite.opacity = 1
            self.imageSprite.StopAnimations()
            self.imageSprite.left = 0
        animations.FadeOut(self.imageSprite, duration=0.15, callback=lambda : self.set_image_path(path))

    def _pan_image(self):

        def flip():
            self._is_right_direction = not self._is_right_direction
            self._pan_image()

        self._start_position = self._get_animation_start_position()
        self._end_position = self._get_animation_end_position()
        animations.MorphScalar(self.imageSprite, 'left', self._start_position, self._end_position, duration=self._get_animation_duration(), curveType=uiconst.ANIM_SMOOTH, callback=flip)

    def _get_animation_duration(self):
        start = 0 if self._is_right_direction else -(self.imageSprite.width - self.IMAGE_SIZE)
        end = 0 if not self._is_right_direction else -(self.imageSprite.width - self.IMAGE_SIZE)
        t = float(self.imageSprite.left - start) / float(end - start)
        return (1.0 - t) * 15

    def _get_animation_end_position(self):
        if self._is_right_direction:
            return -(self.imageSprite.width - self.IMAGE_SIZE)
        return 0

    def _get_animation_start_position(self):
        if self._start_position is not None:
            return self.imageSprite.left
        if not self._is_right_direction:
            return -(self.imageSprite.width - self.IMAGE_SIZE)
        return 0

    def set_image_path(self, path):
        self.imageSprite.SetTexturePath(path)
        animations.FadeIn(self.imageSprite, duration=0.15)

    def OnToolTipExampleClicked(self, is_play):
        if hasattr(self, 'imageSprite'):
            if is_play:
                self._pan_image()
            else:
                self.imageSprite.opacity = 1
                self.imageSprite.StopAnimations()


class TooltipExampleSprite(Container):
    default_state = uiconst.UI_NORMAL
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(TooltipExampleSprite, self).ApplyAttributes(attributes)
        self.frame = FrameThemeColored(bgParent=self.parent, colorType=uiconst.COLORTYPE_UIHILIGHT)
        self.frame.SetAlpha(0)
        self._path = attributes.get('texturePath')
        self._actual_width = attributes.get('actualWidth', 1170)
        self._actual_height = attributes.get('actualWidth', 300)
        self._is_play = True
        self._is_animation_icons_displayed = False
        self._icon_container = Container(name='IconContainer', parent=self, align=uiconst.TOALL, opacity=0)
        self._icon_container.pickState = uiconst.TR2_SPS_OFF
        self._play = Sprite(name='PlaySprite', parent=self._icon_container, align=uiconst.CENTER, width=16, height=16, texturePath='res:/UI/Texture/Icons/play.png')
        self._pause = Sprite(name='PauseSprite', parent=self._icon_container, align=uiconst.CENTER, width=16, height=16, texturePath='res:/UI/Texture/Icons/pause.png')
        width_ratio = float(self._actual_width) / float(self._actual_height)
        self._image = Sprite(name='ExampleSprite', parent=self, align=uiconst.CENTER, width=self.displayHeight * width_ratio, height=self.displayHeight, texturePath=self._path, state=uiconst.UI_DISABLED)

    def UpdateAlignment(self, *args, **kwargs):
        budget = super(TooltipExampleSprite, self).UpdateAlignment(*args, **kwargs)
        if hasattr(self, '_image'):
            width_ratio = float(self._actual_width) / float(self._actual_height)
            self._image.width = self.displayHeight * width_ratio
            self._image.height = self.displayHeight
        return budget

    def display_animation_icons(self, is_displayed = True, is_play = True):
        self._is_play = is_play
        self._is_animation_icons_displayed = is_displayed
        if is_displayed:
            animations.FadeIn(self._icon_container)
        else:
            animations.FadeOut(self._icon_container)
        if is_play:
            self._play.state = uiconst.UI_HIDDEN
            self._pause.state = uiconst.UI_DISABLED
        else:
            self._pause.state = uiconst.UI_HIDDEN
            self._play.state = uiconst.UI_DISABLED

    def OnMouseEnter(self, *args):
        sm.ScatterEvent('OnSwitchTooltipImage', self)
        self.frame.SetAlpha(1)

    def OnMouseExit(self, *args):
        animations.FadeOut(self._icon_container, duration=0.25)
        sm.ScatterEvent('OnSwitchTooltipImage')
        self.frame.SetAlpha(0)

    def OnMouseDown(self, *args):
        if self._is_animation_icons_displayed:
            self.display_animation_icons(is_play=not self._is_play)
            sm.ScatterEvent('OnToolTipExampleClicked', self._is_play)

    @property
    def path(self):
        return self._path

    @property
    def actual_width(self):
        return self._actual_width

    @property
    def actual_height(self):
        return self._actual_height
