#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\probehangar.py
import argparse
import os
import subprocess
import tempfile
import shutil
import sys
import evetypes
import fsdBuiltData.common.graphicIDs as graphicIDs
import devenv
import geo2

class Hangar(object):

    def __init__(self, scene_gid, model_gid, ship_tid, ship_pos = (0, 0, 0), camera_dir = (0.4, -0.4, -3), controller_variables = {}):
        self.scene_gid = scene_gid
        self.model_gid = model_gid
        self.ship_tid = ship_tid
        self.camera_dir = camera_dir
        self.ship_pos = ship_pos
        self.controller_variables = controller_variables


HANGARS = {'amarr': Hangar(20273, 24407, 16233),
 'caldari': Hangar(20271, 24408, 16227),
 'capital': Hangar(21260, 24412, 3764),
 'gallente': Hangar(20274, 24409, 16229),
 'generic': Hangar(21259, 24411, 16229),
 'minmatar': Hangar(20272, 24410, 16231),
 'jita': Hangar(24526, 24525, 47466, camera_dir=(9.0, 2.7, 2.2), controller_variables={'activityLevel': 2}),
 'upwell': Hangar(25263, 25235, 16229, ship_pos=(-6337, -600, 881), camera_dir=(-3, 0.4, 0.2))}
CAMERA_BEHAVIORS = {'none': '',
 'orbit': 'Orbit, 360, 30, {duration}, 0.8',
 'zoom_in': 'Zoom, -1, {duration}, 0.8',
 'zoom_out': 'Zoom, 1, {duration}, 0.8',
 'pan': 'Combo, [[Pan, 100, 0, 0, {duration_over_4}, 0.8], [Pan, 0, 100, 0, {duration_over_4}, 0.8], [Pan, -100, 0, 0, {duration_over_4}, 0.8], [Pan, -0, -100, 0, {duration_over_4}, 0.8]]',
 'orbit_zoom': 'Combo, [[Orbit, 360, 0, {duration}, 0.8], [1.5, Combo, [[Zoom, -1, {duration_over_2}, 0.8], [Zoom, 1, {duration_over_2}, 0.8]]]]'}

def _get_sof_dna(graphic):
    if getattr(graphic, 'sofLayout', ''):
        return '%s:%s:%s:layout?%s' % (graphic.sofHullName,
         graphic.sofFactionName,
         graphic.sofRaceName,
         ';'.join(graphic.sofLayout))
    return '%s:%s:%s' % (graphic.sofHullName, graphic.sofFactionName, graphic.sofRaceName)


def _vec_to_str(vec):
    return '%s, %s, %s' % vec


def create_sequence(hangar, output_path, camera_behavior, time = 12, telemetry = True, title = 'Hangar scene'):
    radius = evetypes.GetRadius(hangar.ship_tid)
    with open(output_path, 'w') as out_file:
        ship_pos = geo2.Vec3Add(hangar.ship_pos, (0, 1.5 * radius, 0))
        camera_pos = geo2.Vec3Add(ship_pos, geo2.Vec3Scale(hangar.camera_dir, radius))
        camera_behavior = '' if camera_behavior == 'none' else '  - [camera_add_behavior, %s]' % CAMERA_BEHAVIORS[camera_behavior]
        camera_behavior = camera_behavior.format(duration=time, duration_over_2=time / 2.0, duration_over_4=time / 4.0)
        out_file.write('name: "{title}"\ndescription: |\n  Performance Benchmark\ncommands:\n  - [renderjob_attr, useReflectionProbe, False]\n  - [scene, "{scene}"]\n  - [set_camera_position, [{camera_pos}]]\n  - [set_camera_focus, [{ship_pos}]]\n  - [set_camera_fov, 1.0]\n  - [actor, ship, "{ship}"]\n  - [actor, hangar, "{hangar}"]\n{variables}\n  - [set_position, ship, [{ship_pos}]]\n  - [set_rotation, ship, [130, 0, 0]]\n  - [setup_hangar_lights, hangar, ship]\n  - [add_actor, hangar]\n  - [add_actor, ship]\n  - [preload_lods]\n  - [wait_for_loads]\n  - [sleep, 3]\n{camera_behavior}\n'.format(title=title, scene=graphicIDs.GetGraphicFile(hangar.scene_gid), hangar=_get_sof_dna(graphicIDs.GetGraphic(hangar.model_gid)), ship_pos=_vec_to_str(ship_pos), camera_pos=_vec_to_str(camera_pos), ship=_get_sof_dna(graphicIDs.GetGraphic(evetypes.GetGraphicID(hangar.ship_tid))), variables='\n'.join(('  - [controller_var, hangar, "%s", %s]' % (x, y) for x, y in hangar.controller_variables.items())), camera_behavior=camera_behavior))
        if telemetry:
            out_file.write('  - [sleep, %s]\n  - [telemetry, start, localhost]\n  - [start_measurement, "%s"]\n  - [sleep, %s]\n  - [stop_measurement, "%s"]\n  - [telemetry, stop]\n' % (max(time - 8, 3),
             title,
             min(time, 8),
             title))
        else:
            out_file.write('\n  - [start_measurement, "%s"]\n  - [sleep, %s]\n  - [stop_measurement, "%s"]\n' % (title, time, title))


def run_benchmark(hangar, camera_behavior = 'none', time = 12, telemetry = True, additional_args = None):
    additional_args = additional_args or []
    temp_dir = tempfile.mkdtemp()
    try:
        sequence = os.path.join(temp_dir, 'benchmark.yaml')
        create_sequence(hangar, sequence, camera_behavior, time, telemetry)
        if sys.platform == 'win32':
            interpreter = 'launch.bat'
        else:
            interpreter = './launch.sh'
        args = [interpreter, '/scenes=%s' % sequence, '/fullmeasurement'] + additional_args
        subprocess.check_call(' '.join(args), shell=True, cwd=os.path.join(devenv.BRANCHROOT, 'evemark'))
    finally:
        shutil.rmtree(temp_dir)


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hangar', choices=HANGARS.keys(), default='amarr', help='hangar name (default is amarr)')
    parser.add_argument('--time', type=int, default=12, help='time to show the benchmark')
    parser.add_argument('--telemetry', action='store_true', help='capture telemetry snapshot')
    parser.add_argument('--dumpscene', default='', help='dump scene file into the specified path rather than running probe')
    parser.add_argument('--camera_behavior', choices=CAMERA_BEHAVIORS.keys(), default='none', help='dump scene file into the specified path rather than running probe')
    parser.add_argument('--name', default='Hangar Scene', help='scene name (appears in performance results)')
    args, probe_args = parser.parse_known_args()
    if args.dumpscene:
        create_sequence(HANGARS[args.hangar], args.dumpscene, args.camera_behavior, args.time, args.telemetry, title=args.name)
    else:
        run_benchmark(HANGARS[args.hangar], args.camera_behavior, args.time, args.telemetry, probe_args)


if __name__ == '__main__':
    _main()
