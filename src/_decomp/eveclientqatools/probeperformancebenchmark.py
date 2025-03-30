#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\probeperformancebenchmark.py
import argparse
import os
import math
import random
import subprocess
import sys
import tempfile
import shutil
import evetypes
import devenv
import fsdBuiltData.common.graphicIDs as graphicIDs
import shipskins
import performancebenchmarkdata as data
from evegraphics.utils import BuildSOFDNAFromGraphicID

def _enumerate_ships(start_pos, test_case):
    yCount = 0
    xPos = start_pos[0]
    index = 0
    for cntr in xrange(test_case.number_of_rows ** 2):
        typeId = test_case.ship_list[cntr % len(test_case.ship_list)]
        if yCount >= test_case.number_of_rows:
            xPos += test_case.distance_between_ships
            yCount = 0
        for zCount in xrange(test_case.number_of_rows):
            yield (index,
             typeId,
             xPos,
             yCount * test_case.distance_between_ships + start_pos[1],
             zCount * test_case.distance_between_ships + start_pos[2])
            index += 1

        yCount += 1


CAMERA_BEHAVIORS = {'none': '',
 'orbit': 'Orbit, 360, 30, {duration}, 0.8',
 'zoom_in': 'Zoom, -1, {duration}, 0.8',
 'zoom_out': 'Zoom, 1, {duration}, 0.8',
 'pan': 'Combo, [[Pan, 5000, 0, 0, {duration_over_4}, 0.8], [Pan, 0, 5000, 0, {duration_over_4}, 0.8], [Pan, -5000, 0, 0, {duration_over_4}, 0.8], [Pan, -0, -5000, 0, {duration_over_4}, 0.8]]',
 'orbit_zoom': 'Combo, [[Orbit, 360, 0, {duration}, 0.8], [1.5, Combo, [[Zoom, -1, {duration_over_2}, 0.8], [Zoom, 1, {duration_over_2}, 0.8]]]]'}

def create_sequence(name, benchmark, camera, camera_behavior, output_path, time = 12, telemetry = True, fit_turrets = False, fight = False, skins = True):
    if isinstance(benchmark, tuple):
        test_case = data.TestCase([benchmark[1]], 10, data.SHIP_DISTANCE_DEFAULT)
    else:
        test_case = data.TEST_CASES[benchmark]
    yaw = data.CAMERA_PRESETS[camera][1] / 180.0 * math.pi
    pitch = data.CAMERA_PRESETS[camera][0] / 180.0 * math.pi
    distance = data.CAMERA_PRESETS[camera][2]
    x = distance * math.cos(yaw) * math.cos(pitch)
    y = -distance * math.sin(pitch)
    z = distance * math.sin(yaw) * math.cos(pitch)
    skin_data = None
    skin_rand = random.Random(456)
    if skins:
        skin_data = shipskins.SkinStaticData('')
    camera_behavior = '' if camera_behavior == 'none' else '  - [camera_add_behavior, %s]' % CAMERA_BEHAVIORS[camera_behavior]
    camera_behavior = camera_behavior.format(duration=time, duration_over_2=time / 2.0, duration_over_4=time / 4.0)
    with open(output_path, 'w') as out_file:
        out_file.write('name: "%s"\ndescription: |\n  Performance Benchmark\ncommands:\n  - [scene, m10]\n  - [set_camera_position, [%s, %s, %s]]\n  - [set_camera_focus, [0.0, 0.0, 0.0]]\n  - [set_camera_fov, 1.0]\n' % (name,
         x,
         y,
         z))
        start_pos = (0, 0, 0)
        count = 0
        for index, type_id, x, y, z in _enumerate_ships(start_pos, test_case):
            sof = BuildSOFDNAFromGraphicID(evetypes.GetGraphicID(type_id))
            if skin_data:
                typeSkins = list(skin_data.GetSkinsForTypeID(type_id) or [])
                if typeSkins:
                    skin = typeSkins[skin_rand.randint(0, len(typeSkins) - 1)]
                    material = skin_data.GetMaterialByID(skin.skinMaterialID)
                    sof = BuildSOFDNAFromGraphicID(evetypes.GetGraphicID(type_id), material.materialSetID)
            out_file.write("  - [actor, ship%s, '%s']\n" % (index, sof))
            if fit_turrets or fight:
                out_file.write('  - [fit_random_turrets, ship%s]\n' % index)
            count += 1

        for index, type_id, x, y, z in _enumerate_ships(start_pos, test_case):
            out_file.write('  - [set_position, ship%s, [%s, %s, %s]]\n' % (index,
             x,
             y,
             z))
            out_file.write('  - [add_actor, ship%s]\n' % index)

        out_file.write('  - [preload_lods]\n  - [wait_for_loads]\n')
        if fight:
            rand = random.Random(123)
            for index in xrange(count):
                out_file.write('  - [fire_all_turrets, ship%s, ship%s, random]\n' % (index, rand.randint(0, count - 1)))

        out_file.write('  - [sleep, 1]\n')
        if telemetry:
            out_file.write('  - [sleep, %s]\n%s\n  - [telemetry, start, localhost]\n  - [start_measurement, "%s"]\n  - [sleep, %s]\n  - [stop_measurement, "%s"]\n  - [telemetry, stop]\n' % (max(time - 8, 3),
             camera_behavior,
             name,
             min(time, 8),
             name))
        else:
            out_file.write('\n  - [sleep, 3]\n%s\n  - [start_measurement, "%s"]\n  - [sleep, %s]\n  - [stop_measurement, "%s"]\n' % (camera_behavior,
             name,
             time,
             name))


def run_benchmark(name, benchmark, camera, camera_behavior, time = 12, telemetry = True, additional_args = None, fit_turrets = False, fight = False, skins = False):
    additional_args = additional_args or []
    temp_dir = tempfile.mkdtemp()
    try:
        sequence = os.path.join(temp_dir, 'benchmark.yaml')
        create_sequence(name, benchmark, camera, camera_behavior, sequence, time, telemetry, fit_turrets, fight, skins=skins)
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
    parser.add_argument('--cube', choices=[ '_'.join(x.split('_')[1:]) for x in dir(data) if x.startswith('CUBE_') ] + ['CUSTOM'], default='CLASSIC', help='performance benchmark name (default is CLASSIC)')
    parser.add_argument('--customid', type=int, default=0, help='type ID for CUSTOM cube')
    parser.add_argument('--camera', choices=[ x.split('_')[-1] for x in dir(data) if x.startswith('CAMERA_PRESET_') ], default='NEAR', help='camera preset (default is NEAR)')
    parser.add_argument('--camera_behavior', choices=CAMERA_BEHAVIORS.keys(), default='none', help='dump scene file into the specified path rather than running probe')
    parser.add_argument('--time', type=int, default=12, help='time to show the benchmark')
    parser.add_argument('--telemetry', action='store_true', help='capture telemetry snapshot')
    parser.add_argument('--dumpscene', default='', help='dump scene file into the specified path rather than running probe')
    parser.add_argument('--turrets', action='store_true', help='fit turrets on ships')
    parser.add_argument('--fight', action='store_true', help='let ships shoot each other')
    parser.add_argument('--skins', action='store_true', help='assign random skins to ships')
    parser.add_argument('--name', help='scene name (appears in performance results)')
    args, probe_args = parser.parse_known_args()
    if args.cube == 'CUSTOM':
        cube = (args.cube, args.customid)
    else:
        cube = getattr(data, 'CUBE_' + args.cube)
    camera = getattr(data, 'CAMERA_PRESET_' + args.camera)
    name = args.name
    if not name:
        if args.fight:
            sub_name = 'Shooting'
        elif args.turrets:
            sub_name = 'With Turrets'
        else:
            sub_name = 'Normal'
        name = 'Death Cube (%s, %s)' % (args.cube, sub_name)
    if args.dumpscene:
        create_sequence(name, cube, camera, args.camera_behavior, args.dumpscene, args.time, args.telemetry, args.turrets, args.fight, skins=args.skins)
    else:
        run_benchmark(name, cube, camera, args.camera_behavior, args.time, args.telemetry, probe_args, args.turrets, args.fight, skins=args.skins)


if __name__ == '__main__':
    _main()
