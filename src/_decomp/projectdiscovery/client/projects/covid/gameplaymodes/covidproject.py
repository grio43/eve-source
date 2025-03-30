#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\gameplaymodes\covidproject.py
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbon.common.script.util.timerstuff import AutoTimer
import carbonui.const as uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.urlSprite import UrlSprite
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eveexceptions import UserError
from gametime import GetTimeDiffInMs, GetWallclockTime
from localization import GetByLabel
import log
from projectdiscovery.client.projects.covid.sounds import Sounds
from projectdiscovery.client.projects.covid.ui.cells import Cells, CELLS_CONTAINER_WIDTH
from projectdiscovery.client.projects.covid.ui.drawing import adapter
from projectdiscovery.client.projects.covid.ui.drawingtool import DrawingTool
from projectdiscovery.client.projects.covid.ui.instructions import Instructions
from projectdiscovery.client.projects.covid.ui.rewards import Rewards, SECTION_HEADER_HEIGHT
from projectdiscovery.client.projects.covid.ui.resultbanner import ResultBanner
from projectdiscovery.client.projects.covid.ui.results import Statistics
from projectdiscovery.client.projects.covid.ui.taskid import TaskID
from projectdiscovery.client.projects.covid.ui.tutorial.errormessage import ErrorMessage
from projectdiscovery.client.ui.projectcontainer import BaseProjectContainer
from uthread2 import StartTasklet
MARGIN_TOP = 91
MARGIN_LEFT = 30
MARGIN_RIGHT = 60
MARGIN_REWARDS_CONTAINER_TOP = SECTION_HEADER_HEIGHT
MAX_SAMPLE_IMAGE_WIDTH = 530
MAX_SAMPLE_IMAGE_HEIGHT = 530
CELLS_CONTAINER_LEFT = 17
CONTINUE_BUTTON_WIDTH = 322
CONTINUE_BUTTON_HEIGHT = 64
REWARDS_CONTAINER_HEIGHT = 560 + MARGIN_REWARDS_CONTAINER_TOP
REWARDS_CONTAINER_WIDTH = 790
LABEL_PATHS_FOLDER = 'UI/ProjectDiscovery/Covid/'
ERROR_MESSAGE_TOP = 0.79
ERROR_MESSAGE_CROSSINGS = LABEL_PATHS_FOLDER + 'Validation/Crossings'
ERROR_MESSAGE_INTERSECTIONS = LABEL_PATHS_FOLDER + 'Validation/Intersections'
SUBMIT_LABEL_PATH = LABEL_PATHS_FOLDER + 'Submit'
CONTINUE_LABEL_PATH = LABEL_PATHS_FOLDER + 'Continue'
INSTRUCTIONS_TITLE_LABEL_PATH = LABEL_PATHS_FOLDER + 'Instructions/Title'
INSTRUCTIONS_TEXT_LABEL_PATHS = [LABEL_PATHS_FOLDER + 'Instructions/BulletPoint1',
 LABEL_PATHS_FOLDER + 'Instructions/BulletPoint2',
 LABEL_PATHS_FOLDER + 'Instructions/BulletPoint3',
 LABEL_PATHS_FOLDER + 'Instructions/BulletPoint4']
LOADING_WHEEL_SIZE = 64
VALIDATION_UPDATES_MSEC = 500

class FlowStep(object):
    DRAW = 0
    RESULTS = 1
    REWARDS = 2


NUMBER_OF_STEPS = 3
SOLUTION_PERIMETER_WIDTH = 2
SOLUTION_COLOR_PERIMETER = (1.0, 0.78, 0.0, 0.8)
SOLUTION_COLOR_FILL = (1.0, 0.78, 0.0, 0.5)
SOLUTION_COLOR_FILL_BG = (0.0, 0.0, 0.0, 0.0)
DRAWING_COLOR_PERIMETER_IN_RESULTS = (1.0, 1.0, 1.0, 1.0)
MAX_POLYGONS = 8
DRAWING_BUFFER_SIZE = 40

class CovidProject(BaseProjectContainer):
    __notifyevents__ = BaseProjectContainer.__notifyevents__ + []
    default_is_validation_enabled = True

    def ApplyAttributes(self, attributes):
        super(CovidProject, self).ApplyAttributes(attributes)
        self.is_validation_enabled = attributes.get('isValidationEnabled', self.default_is_validation_enabled)
        self.service = self._get_service()
        self.client_service = sm.GetService('projectDiscoveryClient')
        self.audio = sm.GetService('audio')
        self.time_of_task_start = None
        self.task = None
        self.result = None
        self.step = 0
        self.is_changing_step = True
        self.instructions = None
        self.continue_button_container = None
        self.continue_button = None
        self.sample_image = None
        self.drawing_tool = None
        self.error_message = None
        self.validation_thread = None
        self.setup_layout()
        self.initialize()

    def Close(self):
        self.stop_validation()
        super(CovidProject, self).Close()
        self.stop_drawing_audio()

    def start_drawing_audio(self):
        if self.should_play_sample_sounds():
            self.audio.SendUIEvent(Sounds.SAMPLE_START)

    def stop_drawing_audio(self):
        if self.should_play_sample_sounds():
            self.audio.SendUIEvent(Sounds.SAMPLE_END)

    def OnMaximize(self):
        if self.step == FlowStep.DRAW:
            self.start_drawing_audio()
        if self.step == FlowStep.REWARDS:
            self.rewards.start_audio_on_maximize()

    def OnMinimize(self):
        if self.step == FlowStep.DRAW:
            self.stop_drawing_audio()
        if self.step == FlowStep.REWARDS:
            self.rewards.stop_audio_on_minimize()

    def initialize(self):
        self.step = FlowStep.DRAW
        StartTasklet(self.load_initial_task)

    def load_initial_task(self):
        self.load_task()
        self.is_changing_step = False
        if not self.is_validation_enabled and self.continue_button:
            self.continue_button.Enable()

    def setup_layout(self):
        self.setup_main_container()
        self.setup_content()

    def setup_main_container(self):
        self.main_container = Container(name='main_container', parent=self, align=uiconst.TOALL)

    def setup_content(self):
        self.add_statistics()
        self.add_task_id()
        self.add_instructions()
        self.add_result_banner()
        self.add_drawing_area()
        self.add_sample_area()
        self.add_cells()
        self.add_continue_button()
        self.add_rewards()
        self.add_error_message()
        self.add_loading_wheel()

    def add_drawing_area(self):
        self.drawing_tool_container = Container(name='drawing_tool_container', parent=self.main_container, align=uiconst.TOPLEFT)

    def add_sample_area(self):
        self.sample_container = Container(name='sample_container', parent=self.main_container, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, bgColor=(0.0, 0.0, 0.0, 1.0))

    def add_cells(self):
        self.cells = Cells(name='cells_container', parent=self.main_container, align=uiconst.TOPLEFT, width=CELLS_CONTAINER_WIDTH, max_cells=MAX_POLYGONS)

    def add_continue_button(self):
        self.continue_button_container = Container(name='continue_button_container', parent=self.main_container, align=uiconst.TOPRIGHT, width=CONTINUE_BUTTON_WIDTH, height=CONTINUE_BUTTON_HEIGHT, opacity=0.0)
        self.continue_button = Button(parent=self.continue_button_container, align=uiconst.TOTOP, label=GetByLabel(SUBMIT_LABEL_PATH), func=self.go_to_next_step)

    def add_instructions(self):
        self.instructions = Instructions(name='instructions_container', parent=self.main_container, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, title=INSTRUCTIONS_TITLE_LABEL_PATH, bullet_points_text_list=INSTRUCTIONS_TEXT_LABEL_PATHS)

    def add_statistics(self):
        self.statistics = Statistics(name='statistics_container', parent=self.main_container, align=uiconst.TOPRIGHT, state=uiconst.UI_HIDDEN)

    def add_task_id(self):
        self.task_id = TaskID(name='task_id_container', parent=self.main_container, align=uiconst.BOTTOMRIGHT, state=uiconst.UI_HIDDEN, top=10, left=10)

    def add_result_banner(self):
        self.result_banner = ResultBanner(name='result_banner', parent=self.main_container, align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)

    def add_rewards(self):
        self.rewards = Rewards(name='rewards_container', parent=self.main_container, align=uiconst.TOPLEFT, width=REWARDS_CONTAINER_WIDTH, height=REWARDS_CONTAINER_HEIGHT, state=uiconst.UI_HIDDEN, padTop=-MARGIN_REWARDS_CONTAINER_TOP)

    def add_error_message(self):
        self.error_message = ErrorMessage(name='error_message', parent=self, align=uiconst.TOPLEFT, idx=0, state=uiconst.UI_HIDDEN)

    def add_loading_wheel(self):
        self.loading_wheel = LoadingWheel(name='loading_wheel', parent=self.sample_container, align=uiconst.CENTER, width=LOADING_WHEEL_SIZE, height=LOADING_WHEEL_SIZE, state=uiconst.UI_HIDDEN)

    def get_sample_padding(self):
        if self.client_service.should_use_new_drawing_tool():
            return adapter.renderer.RULER_WIDTH * 2
        return 0

    def get_drawing_tool(self):
        if self.client_service.should_use_new_drawing_tool():
            return adapter.DrawingToolAdapter(name='drawing_tool', parent=self.drawing_tool_container, align=uiconst.BOTTOMLEFT, max_polygons=MAX_POLYGONS)
        else:
            return DrawingTool(name='drawing_tool', parent=self.drawing_tool_container, align=uiconst.CENTER, max_polygons=MAX_POLYGONS, buffer_size=DRAWING_BUFFER_SIZE)

    def load_drawing_tool(self):
        if self.drawing_tool and not self.drawing_tool.destroyed:
            self.drawing_tool.Close()
        self.drawing_tool = self.get_drawing_tool()
        self.drawing_tool.on_polygon_added.connect(self._on_polygon_added)
        self.drawing_tool.on_polygon_selected.connect(self._on_polygon_selected)
        self.drawing_tool.on_polygon_deselected.connect(self._on_polygon_deselected)
        self.drawing_tool.on_polygon_deleted.connect(self._on_polygon_deleted)
        self.drawing_tool.on_point_added.connect(self._on_point_added)
        self.cells.toggle_polygon_selection = self.drawing_tool.toggle_polygon_selection

    def load_sample_image(self):
        if self.sample_image and not self.sample_image.destroyed:
            self.sample_image.Close()
        self.sample_image = UrlSprite(name='sample_image', parent=self.sample_container, align=uiconst.CENTER, url=self.task['assets']['url'])

    def get_new_task(self):
        return self.service.get_new_task()

    def load_task(self):
        self.loading_wheel.Show()
        if self.continue_button:
            self.continue_button.Disable()
        self.start_drawing_audio()
        try:
            self.task = self.get_new_task()
            self.time_of_task_start = GetWallclockTime()
            self.load_drawing_tool()
            self.load_sample_image()
            self.update_task_id()
            self.rescale_content()
            self.start_validation()
        except UserError:
            self.window.Close()
            raise
        except Exception as exc:
            self.window.Close()
            self.window.show_task_retrieval_error()
            log.LogException('Failed to load Project Discovery task, error: %s' % exc)
        finally:
            self.loading_wheel.Hide()

    def get_time_spent_in_task(self):
        if not self.time_of_task_start:
            return 0
        return max(0, GetTimeDiffInMs(self.time_of_task_start, GetWallclockTime()))

    def _get_result(self):
        if not self.drawing_tool:
            return (None, None)
        polygons = self.drawing_tool.get_polygons()
        result = {'skip': False,
         'polygons': polygons}
        duration = {'t': self.get_time_spent_in_task(),
         'tPolygons': self.drawing_tool.get_time_spent_per_polygon()}
        return (result, duration)

    def start_validation(self):
        if self.is_validation_enabled:
            self.validation_thread = AutoTimer(VALIDATION_UPDATES_MSEC, self.validate)

    def stop_validation(self):
        if self.validation_thread:
            self.validation_thread.KillTimer()
            self.validation_thread = None

    def validate_now(self):
        self.stop_validation()
        is_valid = self.validate()
        self.start_validation()
        return is_valid

    def validate(self):
        if self.is_changing_step:
            return False
        if self.step != FlowStep.DRAW:
            return True
        is_valid, has_no_polygons, has_crossings, has_intersections, invalid_polygons = self.drawing_tool.validate()
        self.update_validation_submission(is_valid)
        self.update_validation_error(has_crossings, has_intersections)
        self.update_cells(invalid_polygons)
        self.update_polygon_colors(invalid_polygons)
        return is_valid

    def update_validation_submission(self, is_valid):
        if is_valid:
            self.continue_button.Enable()
        else:
            self.continue_button.Disable()

    def update_validation_error(self, has_crossings, has_intersections):
        if has_crossings and has_intersections:
            self.error_message.show_errors([ERROR_MESSAGE_CROSSINGS, ERROR_MESSAGE_INTERSECTIONS])
        elif has_crossings:
            self.error_message.show_errors([ERROR_MESSAGE_CROSSINGS])
        elif has_intersections:
            self.error_message.show_errors([ERROR_MESSAGE_INTERSECTIONS])
        else:
            self.error_message.hide_error()

    def update_cells(self, invalid_polygons):
        self.cells.invalidate(invalid_polygons)

    def update_polygon_colors(self, invalid_polygons):
        self.drawing_tool.invalidate(invalid_polygons)

    def go_to_next_step(self, *args):
        if self.is_validation_enabled and not self.validate_now():
            return
        self.continue_button.Disable()
        self.is_changing_step = True
        self.step = (self.step + 1) % NUMBER_OF_STEPS
        self.error_message.hide_error()
        self._update_continue_button()
        if self.step != FlowStep.DRAW:
            self.hide_instructions()
            self.drawing_tool.Disable()
            self.stop_validation()
            self.cells.Disable()
        if self.step != FlowStep.RESULTS:
            if self.step != FlowStep.REWARDS:
                self.hide_statistics()
            self.hide_result_banner()
        if self.step != FlowStep.REWARDS:
            self.hide_rewards()
        if self.step == FlowStep.DRAW:
            self.load_task()
            self.drawing_tool.Enable()
            self.cells.Enable()
            self.show_instructions()
        if self.step == FlowStep.RESULTS:
            self.stop_drawing_audio()
            self.submit_and_show_solution()
            self.show_statistics()
            self.show_result_banner()
        if self.step == FlowStep.REWARDS:
            self.show_rewards()
        if self.step != FlowStep.DRAW:
            self.continue_button.Enable()
        self.is_changing_step = False

    def _update_continue_button(self):
        label_path = SUBMIT_LABEL_PATH if self.step == FlowStep.DRAW else CONTINUE_LABEL_PATH
        self.continue_button.SetLabel(GetByLabel(label_path))

    def submit_and_show_solution(self):
        result, duration = self._get_result()
        if not result or not duration:
            return
        try:
            self.result = self.service.post_classification(result, duration)
            self.show_solution()
            self.window.header_element.update_score(self.result['player']['score'])
        except UserError:
            self.window.Close()
            raise
        except Exception as exc:
            self.window.Close()
            self.window.show_classification_error()
            log.LogException('Failed to submit Project Discovery classification, error: %s' % exc)

    def update_task_id(self):
        self.task_id.Hide()
        if 'taskID' in self.task and self.task['taskID'] is not None:
            self.task_id.load_task_id(self.task['taskID'])
            self.task_id.SetState(uiconst.UI_PICKCHILDREN)

    def show_statistics(self, show_labels = True):
        self.statistics.load_result(result=self.result, show_labels=show_labels)

    def hide_statistics(self):
        self.statistics.Hide()

    def show_result_banner(self, result_type = None):
        self.result_banner.load_result(result=self.result, result_type=result_type)

    def hide_result_banner(self):
        self.result_banner.Hide()

    def show_instructions(self):
        self.instructions.Show()

    def hide_instructions(self):
        self.instructions.Hide()

    def show_cells(self):
        self.cells.Show()

    def hide_cells(self):
        self.cells.Hide()

    def _show_low_density_only(self, polygons):
        for polygon in reversed(sorted(polygons, key=lambda polygon: polygon['densityLevel'])):
            self._show_polygon(polygon)
            return

    def _show_all_densities(self, polygons):
        for polygon in reversed(sorted(polygons, key=lambda polygon: polygon['densityLevel'])):
            self._show_polygon(polygon)

    def _show_polygon(self, polygon):
        vertices = [ [x, 1.0 - y] for x, y in polygon['vertices'] ]
        self.drawing_tool.inject_polygon(vertices, send_to_back=True, show_vertices=False, show_fill=True, perimeter_width=SOLUTION_PERIMETER_WIDTH, perimeter_color=SOLUTION_COLOR_PERIMETER, fill_color=SOLUTION_COLOR_FILL, fill_bg_color=SOLUTION_COLOR_FILL_BG)

    def show_solution(self):
        self.drawing_tool.change_perimeter_color(DRAWING_COLOR_PERIMETER_IN_RESULTS)
        try:
            solution = self.result['task'].get('solution', None)
            if solution:
                clusters = solution['clusters']
                for cluster in clusters:
                    polygons = cluster['polygons']
                    self._show_low_density_only(polygons)

        except Exception as exc:
            log.LogException('Failed to display Project Discovery solution: %s' % exc)

    def show_drawing_area(self):
        self.drawing_tool_container.Show()
        self.sample_container.Show()

    def hide_drawing_area(self):
        self.drawing_tool_container.Hide()
        self.sample_container.Hide()

    def show_rewards(self):
        sm.ScatterEvent('OnContinueToRewards', self.result)
        self.hide_drawing_area()
        self.hide_cells()
        self.rewards.show_rewards()

    def hide_rewards(self):
        self.rewards.hide_rewards()
        self.show_cells()
        self.show_drawing_area()

    def should_play_sample_sounds(self):
        return True

    def should_play_drawing_sounds(self):
        return self.drawing_tool.is_enabled

    def _on_polygon_added(self, index):
        self.cells.on_polygon_added(index)
        if self.should_play_drawing_sounds():
            self.audio.SendUIEvent(Sounds.POLYGON_COMPLETE)

    def _on_polygon_selected(self, index):
        self.cells._on_polygon_selected(index)
        if self.should_play_drawing_sounds():
            self.audio.SendUIEvent(Sounds.POLYGON_SELECT)

    def _on_polygon_deselected(self, index):
        self.cells._on_polygon_deselected(index)

    def _on_polygon_deleted(self, index, is_complete):
        self.cells.on_polygon_deleted(index)
        if self.should_play_drawing_sounds():
            if is_complete:
                self.audio.SendUIEvent(Sounds.POLYGON_DELETE)
            else:
                self.audio.SendUIEvent(Sounds.WIP_DELETE)

    def _on_point_added(self):
        if self.should_play_drawing_sounds():
            self.audio.SendUIEvent(Sounds.POINT_ADD)

    def _get_image_size(self):
        width = MAX_SAMPLE_IMAGE_WIDTH
        height = MAX_SAMPLE_IMAGE_HEIGHT
        desired_aspect_ratio = float(MAX_SAMPLE_IMAGE_WIDTH) / MAX_SAMPLE_IMAGE_HEIGHT
        if self.task:
            dimensions = self.task['assets'].get('dimensions', None)
            if dimensions and len(dimensions) == 2 and dimensions[1] > 0:
                aspect_ratio = float(dimensions[0]) / dimensions[1] * desired_aspect_ratio
                if aspect_ratio >= 1.0:
                    width = float(MAX_SAMPLE_IMAGE_WIDTH)
                    height = width / aspect_ratio
                    if height > MAX_SAMPLE_IMAGE_HEIGHT:
                        height = float(MAX_SAMPLE_IMAGE_HEIGHT)
                        width = height * aspect_ratio
                else:
                    height = float(MAX_SAMPLE_IMAGE_HEIGHT)
                    width = height * aspect_ratio
                    if width > MAX_SAMPLE_IMAGE_WIDTH:
                        width = float(MAX_SAMPLE_IMAGE_WIDTH)
                        height = width / aspect_ratio
        return (width, height)

    def rescale_content(self):
        image_width, image_height = self._get_image_size()
        width = image_width * self.scale
        height = image_height * self.scale
        top = MARGIN_TOP * self.scale
        left = MARGIN_LEFT * self.scale
        for container in [self.sample_container, self.result_banner]:
            container.pos = (left,
             top,
             width,
             height)

        self.drawing_tool_container.left = left - DRAWING_BUFFER_SIZE
        self.drawing_tool_container.top = top - DRAWING_BUFFER_SIZE
        self.drawing_tool_container.width = width + 2 * DRAWING_BUFFER_SIZE
        self.drawing_tool_container.height = height + 2 * DRAWING_BUFFER_SIZE
        if self.drawing_tool:
            self.drawing_tool.SetSize(width, height)
        if self.sample_image:
            sample_padding = self.get_sample_padding()
            self.sample_image.SetSize(width - sample_padding, height - sample_padding)
        self.cells.height = height
        self.cells.left = left + width + CELLS_CONTAINER_LEFT
        self.cells.top = top
        self.rescale_error_message()
        self.rescale_statistics()
        self.rescale_instructions()
        self.rescale_continue_button()
        self.rescale_rewards()

    def rescale_error_message(self):
        if self.error_message:
            left = self.sample_container.left + self.sample_container.width / 2
            top = self.sample_container.top + ERROR_MESSAGE_TOP * self.sample_container.height
            self.error_message.rescale(left, top)

    def rescale_rewards(self):
        self.rewards.top = self.sample_container.top
        self.rewards.left = self.sample_container.left

    def rescale_statistics(self):
        self.statistics.top = self.sample_container.top
        self.statistics.left = MARGIN_RIGHT

    def rescale_instructions(self):
        self.instructions.height = self.sample_container.height
        self.instructions.top = self.sample_container.top
        self.instructions.left = MARGIN_RIGHT

    def rescale_continue_button(self):
        if self.continue_button_container:
            self.continue_button_container.left = MARGIN_RIGHT
            self.continue_button_container.top = self.sample_container.top + self.sample_container.height - self.continue_button_container.height
            self.continue_button_container.opacity = 1.0

    def OnProjectDiscoveryRescaled(self, scale):
        is_scale_change = not FloatCloseEnough(self.scale, scale)
        super(CovidProject, self).OnProjectDiscoveryRescaled(scale)
        if is_scale_change:
            self.rescale_content()
