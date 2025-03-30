#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validate.py
import argparse
import json
from cgi import escape
import logging
import multiprocessing
import os
import subprocess
import sys
import time
import blue
import trinity
import audio2
import evegraphics.validation as graphicsValidation
import yamlext
_rules = []

def GetValidationErrors(path, options, ruleNames, pathOverride = ''):
    blue.os.Pump()
    obj = blue.resMan.LoadObject(path)
    if not obj:
        return (None, None)
    if not _rules:
        rules = graphicsValidation.FindRules()
        if ruleNames:
            rules = [ x for x in rules if x.name in ruleNames ]
        _rules.extend(rules)
    ctx = graphicsValidation.ValidationContext(obj, _rules)
    args = graphicsValidation.InitializeArgumentsFromFilePath(ctx.GetArguments(), pathOverride or path, obj)
    for cls, value in list(args.items()):
        if cls.GetName() in options:
            args[cls] = cls(options[cls.GetName()])

    ctx.Validate(args)
    return (ctx.errors, obj)


def ValidateRedFile(args):
    path, options, ruleNames, pathOverride, _ = args
    start = time.clock()
    try:
        errors, _ = GetValidationErrors(path, options, ruleNames, pathOverride)
    except:
        logging.exception('exception when validating file %s', path)
        raise

    end = time.clock()
    if errors is None:
        return (path, [('IOError', 'error loading file')], end - start)
    else:
        logging.info('processed file %s in %s sec', path, int(end - start))
        return (path, [ (each.GetRuleName(), each.GetErrorMessage()) for each in errors ], end - start)


def ValidateAndFixRedFile(args):
    path, options, ruleNames, pathOverride, skipp4 = args
    start = time.clock()
    errors, obj = GetValidationErrors(path, options, ruleNames, pathOverride)
    end = time.clock()
    if errors is None:
        return (path, [('IOError', 'error loading file')], end - start)
    else:
        logging.info('validated file %s in %s sec', path, int(end - start))
        changed = False
        for error in errors:
            for title, action, default in error.actions:
                if default:
                    try:
                        action()
                    except:
                        logging.exception('Error while running fix action %s', title)

                    changed = True
                    break

        if changed:
            logging.info('saving file %s after applying fixes', path)
            if not skipp4:
                try:
                    subprocess.check_output(['p4', 'edit', path])
                except subprocess.CalledProcessError:
                    logging.exception('error when checking out file %s', path)

            if not blue.resMan.SaveObject(obj, path):
                logging.error('error saving file %s', path)
            else:
                logging.info('saved fixed file %s', path)
        return ValidateRedFile(args)


def SetUpPaths(searchPaths):
    blue.os.sleeptime = 0
    blue.paths.SetSearchPath('root', os.path.join(os.path.dirname(__file__), '../../..'))
    blue.paths.SetSearchPath('app', 'root:/eve/client')
    blue.paths.SetSearchPath('res', searchPaths)
    trinity.device.disableGeometryLoad = True
    trinity.device.disableTextureLoad = True


def InitSlave(searchPaths, logLevel = logging.INFO):
    logging.basicConfig(level=logLevel)
    SetUpPaths(searchPaths)


def _IsExcluded(path, exclude):
    pathLower = os.path.abspath(path).lower()
    return any((pathLower.startswith(x) for x in exclude))


def ValidateDirectory(path, paths, exclude):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.lower().endswith('.red'):
                fullPath = os.path.normpath(os.path.join(root, f))
                if _IsExcluded(fullPath, exclude):
                    continue
                logging.info('queuing file %s', fullPath)
                paths.append(fullPath)


def TextReport(stream, results, duration):
    count = 0
    for path, messages, _ in results:
        count += len(messages)
        stream.write('%s: %s\n' % (path, 'OK' if len(messages) == 0 else '%s errors' % len(messages)))
        for j in messages:
            stream.write('\t%s\n' % j[1].replace('\n', '\n\t'))

    stream.write('%s errors in %s files in %s minutes and %s seconds\n' % (count,
     len(results),
     int(duration / 60),
     int(duration) % 60))


def XmlReport(searchPaths, stream, results):
    SetUpPaths(searchPaths)
    failures = sum(((1 if x[1] else 0) for x in results))
    stream.write('<testsuite name="ArtValidation" tests="%s" errors="0" failures="%s" skip="0">\n' % (len(results), failures))
    for path, messages, duration in results:
        for each in messages:
            stream.write('<testcase classname="%s" name="%s" time="%s">\n' % (blue.paths.ResolvePathToRoot('res', path), blue.paths.ResolvePathToRoot('res', path), duration))
            firstLine = each[1].split('\n')[0]
            stream.write('<failure type="%s" message="%s">%s</failure>\n' % (escape(each[0]), escape(firstLine), escape(each[1])))
            stream.write('</testcase>\n')

    stream.write('</testsuite>')


def YamlReport(searchPaths, stream, results):
    SetUpPaths(searchPaths)
    result = []
    for path, messages, duration in results:
        result.append({'path': blue.paths.ResolvePathToRoot('res', path) or path,
         'messages': [ {'type': x[0],
                      'message': x[1]} for x in messages ]})

    yamlext.dump(result, stream)


def MsBuildReport(searchPaths, stream, results):
    SetUpPaths(searchPaths)
    for path, messages, duration in results:
        printed = set()
        for message in messages:
            msg = '%s: error %s: %s\n' % (path, message[0].replace('.', ''), message[1].replace('\n', '\n\t'))
            if msg not in printed:
                stream.write(msg)
                printed.add(msg)


def FileMapReport(searchPaths, stream, results, cl):
    SetUpPaths(searchPaths)
    files = {}
    for path, messages, duration in results:
        files[blue.paths.ResolvePathToRoot('res', path) or path] = {'messages': [ {'type': x[0],
                      'message': x[1]} for x in messages ]}

    result = {'files': files}
    if cl:
        result['cl'] = cl
    json.dump(result, stream)


def Main():
    parser = argparse.ArgumentParser(description='Art asset validation')
    parser.add_argument('files', metavar='file', nargs='+', help='path to a .red file or directory')
    parser.add_argument('--pathadd', action='append', default=[], help='additional resource search paths')
    parser.add_argument('--path', action='append', default=[], help='explicit resource paths (overrides pathadd)')
    parser.add_argument('--option', action='append', default=[], help='set validation option name=value')
    parser.add_argument('--fix', action='store_true', default=False, help='auto-fix errors')
    parser.add_argument('--outtype', choices=('text', 'msbuild', 'xml', 'yaml'), default='text', help='report type')
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout, help='redirect report output to a file')
    parser.add_argument('--exclude', action='append', default=[], help='path to a .red file or directory to exclude from validation')
    parser.add_argument('--rules', action='append', default=[], help='rule names to apply (by default applies all rules) e.g. filename.ValidationMethod')
    parser.add_argument('--pathoverride', help='override input path for the validation arguments')
    parser.add_argument('--errorfails', action='store_true', default=False, help='return non-zero code on validation errors')
    parser.add_argument('--verbose', action='store_true', default=False, help='verbose logging')
    parser.add_argument('--filemap', type=argparse.FileType('w'), default=None, help='store file->message map')
    parser.add_argument('--cl', type=long, default=0, help='perforce CL number to put into a filemap')
    parser.add_argument('--skipp4', action='store_true', help='Indicates whether file should be opened for edit by the validator.')
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    exclude = [ os.path.abspath(x).lower() for x in args.exclude ]
    ruleNames = args.rules
    start = time.clock()
    if args.path:
        searchPaths = ';'.join(args.path)
    else:
        searchPaths = 'root:/eve/client/res;root:/carbon/client/res;root:/eve/common/res;app:bin'
        if args.pathadd:
            searchPaths = ';'.join(args.pathadd) + ';' + searchPaths
    options = {}
    for each in args.option:
        k, v = each.split('=')
        options[k] = v

    logging.info('Creating worker processes')
    pool = multiprocessing.Pool(initializer=InitSlave, initargs=(searchPaths, logging.DEBUG if args.verbose else logging.INFO))
    logging.info('Created worker processes')
    errors = []
    paths = []
    for each in args.files:
        if not os.path.exists(each):
            logging.error('path %s does not exist', each)
            errors.append((each, [('IOError', 'path does not exist')], 0))
            continue
        if os.path.isdir(each):
            ValidateDirectory(each, paths, exclude)
        elif not _IsExcluded(each, exclude):
            paths.append(each)

    if args.fix:
        errors.extend(pool.map(ValidateAndFixRedFile, ((x,
         options,
         ruleNames,
         args.pathoverride,
         args.skipp4) for x in paths)))
    else:
        errors.extend(pool.map(ValidateRedFile, ((x,
         options,
         ruleNames,
         args.pathoverride,
         args.skipp4 or x) for x in paths)))
    duration = time.clock() - start
    if args.outtype == 'xml':
        XmlReport(searchPaths, args.output, errors)
    elif args.outtype == 'yaml':
        YamlReport(searchPaths, args.output, errors)
    elif args.outtype == 'msbuild':
        MsBuildReport(searchPaths, args.output, errors)
    else:
        TextReport(args.output, errors, duration)
    if args.filemap:
        FileMapReport(searchPaths, args.filemap, errors, args.cl)
    errorfails = args.errorfails
    args = None
    if any((x[1] for x in errors)) and errorfails:
        blue.os.Terminate(4)
    blue.os.Terminate(0)


if __name__ == '__main__':
    Main()
