#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\controller\drawing.py
from projectdiscovery.client.projects.covid.ui.drawing import models
from projectdiscovery.client.projects.covid.ui.drawing.controller import cursor
from projectdiscovery.client.projects.covid.ui.drawing.controller import configs
from projectdiscovery.client.projects.covid.ui.drawing.controller import newpoly
from projectdiscovery.client.projects.covid.ui.drawing.controller import feedback
from projectdiscovery.client.projects.covid.ui.drawing.controller import update
from projectdiscovery.client.projects.covid.ui.drawing.controller import movement
from projectdiscovery.client.projects.covid.ui.drawing.controller import adjustment
from projectdiscovery.client.projects.covid.ui.drawing.controller import golden
from projectdiscovery.client.projects.covid.ui.drawing.controller.states import DrawingState
import signals
import logging
log = logging.getLogger('projectdiscovery.covid.controller')

class DrawingController(object):
    STATES = DrawingState

    def __init__(self):
        self._state = DrawingState.UNKNOWN
        self.cursor = cursor.Cursor()
        self.drawing = newpoly.NewDrawingController()
        self._cursor_segment = models.Segment(models.Coord(0, 0), models.Coord(1, 1))
        self.mover = movement.MovementController()
        self.adjuster = adjustment.AdjustmentController()
        self.feedback = feedback.FeedbackController()
        self.golden_solution = golden.GoldenController()
        self.polygons = {}
        self.polygon_order = []
        self.selected_polygon_uuid = None
        self.area_boundary = models.Rect(models.Coord(0, 0), models.Coord.from_args(configs.DRAWING_AREA_SIZE))
        self._last_state = DrawingState.READY
        self.updater_polygons = update.UpdateController()
        self.updater_segment_chain = update.UpdateController()
        self.updater_cursor_segment = update.UpdateController()
        self.on_polygon_added = signals.Signal(signalName='on_polygon_added')
        self.on_polygon_deleted = signals.Signal(signalName='on_polygon_deleted')
        self.on_polygons_changed = signals.Signal(signalName='on_polygons_changed')
        self.on_wip_polygon_cleared = signals.Signal(signalName='on_wip_polygon_cleared')
        self.on_polygon_started = signals.Signal(signalName='on_polygon_started')
        self.on_polygon_selected = signals.Signal(signalName='on_polygon_selected')
        self.on_polygon_deselected = signals.Signal(signalName='on_polygon_deselected')
        self.on_point_added = signals.Signal(signalName='on_point_added')

    def _report_updates(self):
        self.updater_polygons.report_update()
        self.updater_segment_chain.report_update()
        self.updater_cursor_segment.report_update()
        self.feedback.updater.report_update()
        self.cursor.updater.report_update()
        self.mover.updater.report_update()
        self.adjuster.updater.report_update()
        self.golden_solution.updater.report_update()

    def enable(self):
        if self._state in (DrawingState.DISABLED, DrawingState.UNKNOWN):
            log.debug('enabling drawing controller')
            self._state = self._last_state
            self.drawing.enable()
            self.mover.enable()
            self.adjuster.enable()
            self.cursor.state = self.cursor.STATES.READY
            self.cursor.polygons_left = self.polygons_left
            self.cursor.vertices_left = self.drawing.vertices_left
            self.set_cursor_target()
            self._report_updates()
        else:
            log.debug('drawing controller already enabled')

    def disable(self):
        log.debug('disabling drawing controller')
        self._last_state = self._state
        self._state = DrawingState.DISABLED
        self._report_updates()

    def set_cursor_pos(self, new_coord):
        if self._state == DrawingState.DISABLED:
            return
        if self.cursor.target == self.cursor.TARGETS.OFF_CANVAS:
            return
        self.cursor.pos = new_coord
        if self._state == DrawingState.DRAWING:
            self._cursor_segment.end = self.cursor.pos
            self._snap_check()
            self._drawing_crossing_check()
            self.updater_cursor_segment.tick()
        elif self._state == DrawingState.MOVING_VERTEX:
            self.adjuster.set_current_pos(self.cursor.pos)
            self._step_vertex_move()
        elif self._state == DrawingState.MOVING_POLYGON:
            self.mover.set_current_pos(self.cursor.pos)
            self._step_polygon_move()
        elif self._state == DrawingState.READY:
            self.cursor.is_invalid = False
            if self.mover.state == self.mover.STATES.STARTING:
                self.mover.set_current_pos(self.cursor.pos)
                if self.mover.state == self.mover.STATES.MOVING:
                    self._start_polygon_move()
        else:
            self.cursor.is_invalid = False
        self._report_updates()

    def set_cursor_target(self, polygon_uuid = None, vertex_index = None, x_button = False):
        if self._state in (DrawingState.DISABLED, DrawingState.UNKNOWN):
            return
        if polygon_uuid:
            poly = self.polygons.get(polygon_uuid, None)
            if not poly:
                raise ValueError('targeted polygon not found: %r' % polygon_uuid)
            if not self.cursor.target_polygon or self.cursor.target_polygon.uuid != polygon_uuid:
                self.updater_polygons.tick()
            self.cursor.target_polygon = poly
            self.cursor.target_polygon.is_targeted = True
            self.cursor.target = self.cursor.TARGETS.POLYGON
            if vertex_index is not None:
                self.cursor.target_vertex_idx = vertex_index
                self.cursor.target = self.cursor.TARGETS.VERTEX
            if x_button:
                self.cursor.target = self.cursor.TARGETS.X_BUTTON
            log.info('set target as %r poly=%r, vidx=%r, xbtn=%r', self.cursor.target.name, poly, vertex_index, x_button)
        else:
            log.info('set target as canvas')
            self.cursor.target = self.cursor.TARGETS.CANVAS
            if self.cursor.target_polygon:
                self.cursor.target_polygon.is_targeted = False
                self.updater_polygons.tick()
            self.cursor.target_polygon = None
            self.cursor.target_vertex_idx = None
        if self._state == DrawingState.DRAWING:
            self.updater_cursor_segment.tick()
        self._report_updates()

    def set_cursor_off_canvas(self):
        log.info('set target as off canvas')
        self.cursor.target = self.cursor.TARGETS.OFF_CANVAS
        if self._state == DrawingState.MOVING_VERTEX:
            self._cancel_vertex_move()
        self.updater_cursor_segment.tick()
        self._report_updates()

    def _start_vertex_move(self):
        log.info('_start_vertex_move')
        self._select_polygon()
        self._state = DrawingState.MOVING_VERTEX
        self.cursor.state = self.cursor.STATES.MODIFYING
        self.adjuster.begin_move(target_polygon=self.cursor.target_polygon, target_vertex_index=self.cursor.target_vertex_idx, starting_pos=self.cursor.pos.as_copy)

    def _start_polygon_move(self):
        self._state = DrawingState.MOVING_POLYGON
        self.cursor.state = self.cursor.STATES.MODIFYING
        self._step_polygon_move()

    def _step_polygon_move(self):
        self._moving_oob_check()
        if self.mover.is_out_of_bounds:
            self.cursor.is_invalid = True
            return
        self._moving_overlap_check()
        if self.mover.is_overlapping:
            self.cursor.is_invalid = True
            return
        self.cursor.is_invalid = False

    def _step_vertex_move(self):
        if self._adjusting_overlap_any():
            self.adjuster.is_overlapping = True
            self.cursor.is_invalid = True
        else:
            self.adjuster.is_overlapping = False
            self.cursor.is_invalid = False

    def _adjusting_overlap_any(self):
        left = self.adjuster.left_segment
        right = self.adjuster.right_segment
        for other_poly in self.polygons.values():
            if other_poly.uuid == self.adjuster.target_polygon.uuid:
                continue
            for other_segment in other_poly.segments:
                log.info('Checking... intersection-left: %r | %r @ %r', left, other_segment, other_poly)
                if left.intersects(other_segment):
                    return True
                log.info('Checking... intersection-right: %r | %r @ %r', right, other_segment, other_poly)
                if right.intersects(other_segment):
                    return True

        left_of_left = self.adjuster.left_of_left_segment
        right_of_right = self.adjuster.right_of_right_segment
        if len(self.adjuster.target_polygon.verticies) > 3:
            statics = self.adjuster.static_segment_chain.segments
            for other_segment in statics:
                if other_segment != left_of_left:
                    log.info('Checking... static_intersection-left: %r | %r @ %r', left, other_segment, statics)
                    if left.intersects(other_segment):
                        return True
                if other_segment != right_of_right:
                    log.info('Checking... static_intersection-right: %r | %r @ %r', right, other_segment, statics)
                    if right.intersects(other_segment):
                        return True

        if self._overlay_check(left, left_of_left):
            return True
        if self._overlay_check(right, right_of_right):
            return True
        if self._overlay_check(right, left):
            return True
        return False

    @staticmethod
    def _overlay_check(segment_a, segment_b):
        if segment_a.slope == segment_b.slope:
            if segment_a.as_reversed.as_vector.as_sign_tuple == segment_b.as_vector.as_sign_tuple:
                return True
        return False

    def _moving_oob_check(self):
        bounds = self.mover.target_polygon.bounding_rect.as_copy
        bounds.bottom_left = bounds.bottom_left + self.mover.translation
        if bounds not in self.area_boundary:
            self.mover.is_out_of_bounds = True
        else:
            self.mover.is_out_of_bounds = False

    def _moving_overlap_check(self):
        if self._moving_overlaps_any():
            self.mover.is_overlapping = True
        else:
            self.mover.is_overlapping = False

    def _moving_overlaps_any(self):
        for other_poly in self.polygons.values():
            if other_poly.uuid == self.mover.target_polygon.uuid:
                continue
            for other_segment in other_poly.segments:
                for moving_segment in self.mover.translated_segments:
                    if moving_segment.intersects(other_segment):
                        return True

        return False

    def _snap_check(self):
        start = self.drawing.first_vertex
        before = self.cursor.is_snapping
        if start:
            self.cursor.is_snapping = start.is_within_dist(self.cursor.pos, configs.SNAP_RADIUS)
            if self.cursor.is_snapping and not before:
                self.cursor.snap_pos = start.as_copy
        else:
            self.cursor.is_snapping = False

    def _drawing_crossing_check(self):
        if self._current_intersects_any():
            self.cursor.is_invalid = True
        else:
            self.cursor.is_invalid = False

    def _current_intersects_any(self):
        cursor_segment = self.visual_cursor_segment
        if cursor_segment:
            segments = self.drawing.segment_chain.segments
            if segments:
                last = segments.pop(-1)
                if self.cursor.is_snapping:
                    segments.pop(0)
                for s in segments:
                    if cursor_segment.intersects(s):
                        return True

                if self._overlay_check(last, cursor_segment):
                    return True
            for p in self.polygons.values():
                for s in p.segments:
                    if cursor_segment.intersects(s):
                        return True

        return False

    def action_begin(self):
        log.info('action_begin:controller=%r, cursor=%r', self, self.cursor)
        if self._state == DrawingState.DISABLED:
            log.debug('begin action while drawing controller is disabled')
            return
        if self.cursor.target == self.cursor.TARGETS.OFF_CANVAS:
            return
        if self._state == DrawingState.READY:
            if self.cursor.target == self.cursor.TARGETS.VERTEX:
                if self.cursor.target_polygon:
                    self._start_vertex_move()
                else:
                    log.error('targetted polygon not found')
            elif self.cursor.target == self.cursor.TARGETS.POLYGON:
                if self.cursor.target_polygon:
                    self._select_polygon()
                    self.mover.begin_move(target_polygon=self.cursor.target_polygon, starting_pos=self.cursor.pos.as_copy)
                else:
                    log.error('targetted polygon not found')
            elif self.cursor.target == self.cursor.TARGETS.X_BUTTON:
                pass
        self.feedback.clear()
        self._report_updates()

    def action_cancel(self):
        log.info('action_cancel:controller=%r, cursor=%r', self, self.cursor)
        if self._state == DrawingState.DISABLED:
            log.debug('cancel action while drawing controller is disabled')
            return
        if self.cursor.target == self.cursor.TARGETS.OFF_CANVAS:
            return
        if self._state == DrawingState.READY:
            self.clear_selection()
        elif self._state == DrawingState.DRAWING:
            self._cancel_drawing()
        elif self._state == DrawingState.MOVING_VERTEX:
            self._cancel_vertex_move()
        elif self._state == DrawingState.MOVING_POLYGON:
            self._cancel_polygon_move()
        else:
            log.error('cancel action while in unknown state: %r', self._state)
        self._report_updates()

    def action_delete(self):
        log.info('action_delete:controller=%r, cursor=%r', self, self.cursor)
        if self._state == DrawingState.DISABLED:
            log.debug('delete action while drawing controller is disabled')
            return
        if self.cursor.target == self.cursor.TARGETS.OFF_CANVAS:
            return
        if self._state == DrawingState.READY:
            self._delete_polygon()
        elif self._state == DrawingState.DRAWING:
            self._undo()
        else:
            log.error('delete action while in unknown state: %r', self._state)
        self._report_updates()

    def action_back(self):
        log.info('action_back:controller=%r, cursor=%r', self, self.cursor)
        if self._state == DrawingState.DISABLED:
            log.debug('back action while drawing controller is disabled')
            return
        if self.cursor.target == self.cursor.TARGETS.OFF_CANVAS:
            return
        if self._state == DrawingState.READY:
            self.clear_selection()
        elif self._state == DrawingState.DRAWING:
            self._undo()
        elif self._state == DrawingState.MOVING_VERTEX:
            self._cancel_vertex_move()
        elif self._state == DrawingState.MOVING_POLYGON:
            self._cancel_polygon_move()
        else:
            log.error('back action while in unknown state: %r', self._state)
        self._report_updates()

    def action_execute(self):
        log.info('action_execute:controller=%r, cursor=%r', self, self.cursor)
        if self._state == DrawingState.DISABLED:
            log.debug('primary action while drawing controller is disabled')
            return
        if self.cursor.target == self.cursor.TARGETS.OFF_CANVAS:
            return
        if self._state == DrawingState.READY:
            self._action_execute_ready()
        elif self._state == DrawingState.DRAWING:
            self._action_execute_drawing()
        elif self._state == DrawingState.MOVING_VERTEX:
            self._action_execute_moving_vertex()
        elif self._state == DrawingState.MOVING_POLYGON:
            self._action_execute_moving_polygon()
        else:
            log.error('primary action while in unknown state: %r', self._state)
        self._report_updates()

    def _action_execute_ready(self):
        if self.cursor.target == self.cursor.TARGETS.CANVAS:
            if self.is_full:
                log.warning('maximum polygons reached')
                self.feedback.error('maximum_polygons_reached')
            else:
                self._start_new_polygon()
        elif self.cursor.target in (self.cursor.TARGETS.POLYGON, self.cursor.TARGETS.VERTEX):
            log.info('selecting polygon')
            self._select_polygon()
            if self.mover.state == self.mover.STATES.STARTING:
                self.mover.cancel()
        elif self.cursor.target == self.cursor.TARGETS.X_BUTTON:
            self._delete_polygon()
        elif self.cursor.target == self.cursor.TARGETS.OFF_CANVAS:
            log.debug('_primary_action_ready picked up action while cursor was off canvas')
            self.clear_selection()
        else:
            log.error('unknown cursor target in _primary_action_ready')

    def _action_execute_drawing(self):
        if self.cursor.target == self.cursor.TARGETS.CANVAS:
            if self.cursor.is_invalid:
                log.warning('trying to draw while crossing the streams')
                self.feedback.error('no_overlapping')
            elif self.cursor.is_snapping:
                if self.drawing.is_closable:
                    self._close_polygon()
                else:
                    log.info('adding vertex to new drawing (withing snapping distance)')
                    self._add_vertex_to_polygon()
            elif self.drawing.is_full:
                self._out_of_vertices()
            else:
                self._add_vertex_to_polygon()
        elif self.cursor.target == self.cursor.TARGETS.VERTEX:
            log.warning('trying to draw on existing vertex')
            self.feedback.error('no_overlapping')
        elif self.cursor.target == self.cursor.TARGETS.POLYGON:
            log.warning('trying to draw on existing polygon')
            self.feedback.error('no_overlapping')
        elif self.cursor.target == self.cursor.TARGETS.X_BUTTON:
            log.error('_primary_action_drawing targetting x_button')
            self.feedback.error('no_overlapping')
        elif self.cursor.target == self.cursor.TARGETS.OFF_CANVAS:
            log.error('_primary_action_drawing picked up action while cursor was off canvas...?')
        else:
            log.error('unknown cursor target in _primary_action_drawing')

    def _action_execute_moving_vertex(self):
        log.warning('drop vertex: _action_execute_moving_vertex')
        if self.adjuster.is_overlapping:
            self._cancel_vertex_move()
            self.feedback.error('no_adjust_overlapping')
        else:
            self.adjuster.execute_move()
            self._state = DrawingState.READY
            self.cursor.state = self.cursor.STATES.READY
            self.feedback.clear()
            self.updater_polygons.tick()

    def _action_execute_moving_polygon(self):
        log.warning('drop polygon')
        if self.mover.is_overlapping:
            self._cancel_polygon_move()
            self.feedback.error('no_move_overlapping')
        elif self.mover.is_out_of_bounds:
            self._cancel_polygon_move()
            self.feedback.error('no_move_out_of_bounds')
        else:
            self.mover.execute_move()
            self._state = DrawingState.READY
            self.cursor.state = self.cursor.STATES.READY
            self.feedback.clear()
            self.updater_polygons.tick()

    def select_polygon(self, uuid):
        self.clear_selection()
        if uuid in self.polygons:
            self.selected_polygon_uuid = uuid
            self.polygons[self.selected_polygon_uuid].is_selected = True
            self.updater_polygons.tick()
            self.on_polygon_selected(self.polygon_order.index(self.selected_polygon_uuid))
        else:
            log.error('targeted polygon uuid not found in polygon registry')

    def _select_polygon(self):
        log.info('_select_polygon')
        if self.cursor.target_polygon:
            self.select_polygon(self.cursor.target_polygon.uuid)

    def _cancel_drawing(self):
        log.info('_cancel_drawing')
        if self.drawing.vertex_count > 0:
            self.on_wip_polygon_cleared()
        self.drawing.reset()
        self._state = DrawingState.READY
        self.cursor.state = self.cursor.STATES.READY
        self.cursor.vertices_left = self.drawing.vertices_left
        self.feedback.clear()
        self.updater_segment_chain.tick()
        self.updater_cursor_segment.tick()

    def clear_selection(self):
        log.info('_clear_selection')
        if self.selected_polygon_uuid:
            if self.selected_polygon_uuid in self.polygons:
                self.polygons[self.selected_polygon_uuid].is_selected = False
                self.updater_polygons.tick()
                self.on_polygon_deselected(self.polygon_order.index(self.selected_polygon_uuid))
            else:
                log.error('selected polygon uuid not found in polygon registry')
            self.selected_polygon_uuid = None

    def _undo(self):
        log.info('_undo')
        if self.drawing.vertex_count > 1:
            self.drawing.undo()
            self.cursor.vertices_left = self.drawing.vertices_left
            self.feedback.clear()
            self._cursor_segment.start = self.drawing.last_vertex
            self.updater_segment_chain.tick()
            self.updater_cursor_segment.tick()
        else:
            self._cancel_drawing()

    def _cancel_vertex_move(self):
        log.info('_cancel_vertex_move')
        self.adjuster.cancel()
        self.adjuster.state = self.adjuster.STATES.READY
        self.cursor.state = self.cursor.STATES.READY
        self.cursor.is_invalid = False
        self._state = self.STATES.READY

    def _cancel_polygon_move(self):
        log.info('_cancel_polygon_move')
        self.mover.cancel()
        self.mover.state = self.mover.STATES.READY
        self.cursor.state = self.cursor.STATES.READY
        self.cursor.is_invalid = False
        self._state = self.STATES.READY

    def _delete_polygon(self):
        log.info('deleting polygon')
        if self.cursor.target == self.cursor.TARGETS.OFF_CANVAS:
            return
        sel_uuid = None
        if self.cursor.target == self.cursor.TARGETS.X_BUTTON:
            if self.cursor.target_polygon:
                sel_uuid = self.cursor.target_polygon.uuid
                if sel_uuid in self.polygons:
                    if sel_uuid == self.selected_polygon_uuid:
                        self.clear_selection()
                    self.cursor.target_polygon = None
                else:
                    log.error('targeted polygon (%r) NOT found in polygon registery: %r', self.cursor.target_polygon.uuid)
            else:
                log.error('no polygon targeted when x-button pushed')
        else:
            sel_uuid = self.selected_polygon_uuid
            self.selected_polygon_uuid = None
        if sel_uuid:
            del self.polygons[sel_uuid]
            old_index = self.polygon_order.index(sel_uuid)
            self.polygon_order.remove(sel_uuid)
            self.cursor.target_vertex_idx = None
            self.cursor.target = self.cursor.TARGETS.CANVAS
            self.cursor.state = self.cursor.STATES.READY
            self.cursor.polygons_left = self.polygons_left
            self.cursor.vertices_left = self.drawing.vertices_left
            self.cursor.is_snapping = False
            self.on_polygon_deleted(old_index, True)
            self.on_polygons_changed(len(self.polygon_order))
        self.updater_polygons.tick()

    def _start_new_polygon(self):
        log.info('starting new drawing')
        self.clear_selection()
        self.drawing.start_new(self.cursor.pos)
        self._state = DrawingState.DRAWING
        self.cursor.state = self.cursor.STATES.DRAWING
        self.cursor.vertices_left = self.drawing.vertices_left
        self.feedback.clear()
        self._cursor_segment.start = self.drawing.last_vertex
        self._cursor_segment.end = self.drawing.last_vertex
        self.updater_cursor_segment.tick()
        self.on_polygon_started()

    def _add_vertex_to_polygon(self):
        log.info('adding vertex to new drawing')
        self.drawing.add_vertex(self.cursor.pos)
        self.cursor.vertices_left = self.drawing.vertices_left
        self.feedback.clear()
        self._cursor_segment.start = self.drawing.last_vertex
        self._cursor_segment.end = self.drawing.last_vertex
        self.updater_segment_chain.tick()
        self.updater_cursor_segment.tick()
        self.on_point_added()

    def _close_polygon(self):
        log.info('closing polygon in new drawing')
        new_polygon = self.drawing.close()
        self.polygons[new_polygon.uuid] = new_polygon
        self.polygon_order.append(new_polygon.uuid)
        self._state = DrawingState.READY
        self.cursor.state = self.cursor.STATES.READY
        self.cursor.polygons_left = self.polygons_left
        self.cursor.vertices_left = self.drawing.vertices_left
        self.cursor.is_snapping = False
        self.cursor.is_invalid = False
        self.set_cursor_target(new_polygon.uuid)
        self.feedback.clear()
        self.updater_polygons.tick()
        self.updater_segment_chain.tick()
        self.updater_cursor_segment.tick()
        self.on_polygon_added(len(self.polygon_order) - 1)
        self.on_polygons_changed(len(self.polygon_order))

    def _out_of_vertices(self):
        log.warning('trying to draw while out of vertices')
        self.feedback.error('maximum_vertices_reached')

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        raise AttributeError('state should not be changed from the outside')

    @property
    def polygon_count(self):
        return len(self.polygons)

    @property
    def polygons_left(self):
        return configs.MAX_POLYGONS - self.polygon_count

    @property
    def is_full(self):
        return self.polygons_left <= 0

    @property
    def has_minimum_required(self):
        return self.polygon_count >= configs.MIN_POLYGONS

    @property
    def cursor_segment(self):
        if self.drawing.state == self.drawing.STATES.DRAWING:
            if self.cursor.target != self.cursor.TARGETS.OFF_CANVAS:
                return self._cursor_segment

    @property
    def visual_cursor_segment(self):
        if self.drawing.state == self.drawing.STATES.DRAWING:
            if self.cursor.target != self.cursor.TARGETS.OFF_CANVAS:
                if self.cursor.is_snapping:
                    return models.Segment(self.drawing.last_vertex, self.drawing.first_vertex)
                if not self.drawing.is_full:
                    return self._cursor_segment

    @property
    def selected_polygon(self):
        if self.selected_polygon_uuid:
            return self.polygons.get(self.selected_polygon_uuid, None)

    def __repr__(self):
        return '<DrawingController:{s} [p={p}] sel={sel}>'.format(s=self._state.name, p=self.polygon_count, sel=self.selected_polygon_uuid)

    def scale(self, ratio):
        for p in self.polygons.itervalues():
            p.scale(ratio)

        self.area_boundary.scale(ratio)
        self.updater_polygons.tick()
        self.updater_cursor_segment.tick()
        self.updater_segment_chain.tick()
        self._report_updates()

    def resize(self, new_size):
        self.scale(float(new_size) / self.area_boundary.size.right)

    def reset(self):
        self.cursor.target_polygon = None
        self.cursor.target_vertex_idx = None
        self.cursor.target = self.cursor.TARGETS.OFF_CANVAS
        self.cursor.is_invalid = False
        self.cursor.is_snapping = False
        self.cursor.vertices_left = self.drawing.vertices_left
        self.cursor.polygons_left = self.polygons_left
        self.cursor.state = self.cursor.STATES.READY
        self.drawing.reset()
        self.mover.cancel()
        self.adjuster.cancel()
        self.feedback.clear()
        self.golden_solution.clear()
        self.polygons = {}
        self.polygon_order = []
        self.selected_polygon_uuid = None
        self._state = DrawingState.READY
        self.updater_polygons.tick()
        self.updater_segment_chain.tick()
        self.updater_cursor_segment.tick()
        self._report_updates()

    def logdump_states(self):
        log.warning('controller=%s', self)
        log.warning('cursor=%s', self.cursor)
        log.warning('drawing=%s', self.drawing)
        log.warning('feedback=%s', self.feedback)
        log.warning('mover=%s', self.mover)
        log.warning('adjuster=%s', self.adjuster)
        log.warning('polygons=%s', self.polygons)
