#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\icongenerator.py
import os
import osutils
import tempfile
import subprocess
import shutil
import imgdiff
import blue
from iconrendering2.factory.factory import IconRendererFactory
from iconrendering2.const import IconStyle, InputType, Language, DEFAULT_ICON_DIFF_TOLERANCE, ALL_METAGROUPS
try:
    from platformtools.compatibility.exposure import perforceutils
    try:
        perforceutils.get_connection()
        p4enabled = True
    except perforceutils.P4Exception:
        p4enabled = False

except ImportError:
    perforceutils = None
    p4enabled = False

class Options(object):
    NONE = 0
    USE_TMP_FOLDER = 1
    CHECKOUT = 2
    CLEAN_TMP_FOLDER = 4
    VIEW_OUTPUT = 8
    ONLY_USE_EXISTING_BASE_ICONS = 16
    DONT_RENDER_METAGROUP_OVERLAYS = 32


class _JobInfo(object):

    def __init__(self, options, outputFolder, tmpOutputFolder, renderers, errors):
        self.options = options
        self.outputFolder = outputFolder
        self.tmpOutputFolder = tmpOutputFolder
        self.renderers = renderers
        self.errors = errors


class IconGenerator(object):

    def __init__(self, resourceMapper = None, sofFactory = None, changelist = None, language = Language.ENGLISH, preRenderCallback = None, postRenderCallback = None, options = Options.NONE):
        self._resourceMapper = resourceMapper
        self._sofFactory = sofFactory
        self._changelist = changelist
        self._language = language
        self._preRenderCallback = preRenderCallback
        self._postRenderCallback = postRenderCallback
        self._factory = IconRendererFactory(self._resourceMapper, self._sofFactory)
        self._options = options
        self._options &= ~Options.VIEW_OUTPUT
        self._viewOutput = options & Options.VIEW_OUTPUT
        self._openedFolders = []
        self._scheduledJobs = {}

    def Generate(self, inputType, input, outputFolder = None, metadata = None, desiredStyles = IconStyle.ALL, desiredMetagroups = ALL_METAGROUPS, desiredSizes = None):
        errors = []
        try:
            job = self._CreateJob(inputType, input, outputFolder, metadata, desiredStyles, desiredMetagroups, desiredSizes)
            if job:
                errors.extend(job.errors)
                errors.extend(self._Run(input, [job]))
        except Exception:
            import traceback
            errors.append(''.join(traceback.format_exc()))

        return errors

    def Schedule(self, inputType, input, outputFolder = None, metadata = None, desiredStyles = IconStyle.ALL, desiredMetagroups = ALL_METAGROUPS, desiredSizes = None):
        job = self._CreateJob(inputType, input, outputFolder, metadata, desiredStyles, desiredMetagroups, desiredSizes)
        if job:
            self._Schedule(input, job)

    def Unschedule(self, input):
        if input in self._scheduledJobs:
            self._scheduledJobs.pop(input)

    def RenderScheduled(self):
        errors = []
        for input, jobs in self._scheduledJobs.iteritems():
            for job in jobs:
                errors.extend(job.errors)

            errors.extend(self._Run(input, jobs))

        self._scheduledJobs = {}
        return errors

    def CancelScheduled(self):
        self._scheduledJobs = {}

    def _Schedule(self, input, job):
        if input not in self._scheduledJobs:
            self._scheduledJobs[input] = []
        self._scheduledJobs[input].append(job)

    def _Run(self, input, jobs):
        outputFolders = set()
        errors = []

        def _callback(outputList):
            if self._postRenderCallback:
                self._postRenderCallback(input, outputList)

        for j in jobs:
            outputInfos = []
            for r in j.renderers:
                renderErrors = r.Render()
                outputInfos.extend(r.GetOutputList())
                for e in renderErrors:
                    errors.append((input, e[0], e[1]))

            outputFiles = [ info.outputPath for info in outputInfos ]
            for path in outputFiles:
                print 'Generated icon: {}'.format(path)

            if _callback:
                _callback(outputInfos)
            if j.options & Options.USE_TMP_FOLDER:
                errors.extend(_CopyToFinalFolder(j.outputFolder, outputFiles, self._changelist if p4enabled else None))
            _CleanTmpFolder(j.tmpOutputFolder, j.options)
            outputFolders.add(j.outputFolder)

        if self._viewOutput:
            for output in outputFolders:
                if output not in self._openedFolders:
                    self._openedFolders.append(output)
                    resolvedPath = blue.paths.ResolvePath(output)
                    subprocess.Popen('explorer %s' % resolvedPath.replace('/', '\\'))

        return errors

    def _CreateJob(self, inputType, input, outputFolder, metadata, desiredStyles, desiredMetagroups, desiredSizes = None):
        if not desiredSizes:
            desiredSizes = [64, 128, 512]
        if metadata and metadata.get('skip', False):
            print 'Skipping icons, as indicated in the metadata.'
            return None
        if not self._resourceMapper and inputType in [InputType.RED_FILE, InputType.GRAPHIC_ID]:
            print "No Resource Mapper defined, can't generate icons for %s (%s)" % (input, inputType)
            return None
        if not self._sofFactory and inputType in [InputType.RED_FILE, InputType.GRAPHIC_ID, InputType.DNA]:
            print "No SOF Factory defined, can't generate icons for %s (%s)" % (input, inputType)
            return None
        options = _ReviewOptions(self._options)
        outputFolder, tmpOutputFolder = _GetCorrectFolders(outputFolder, options)
        onlyUseExistingBaseIcons = Options.ONLY_USE_EXISTING_BASE_ICONS & self._options
        renderMetagroupOverlays = not Options.DONT_RENDER_METAGROUP_OVERLAYS & self._options
        renderers, errors = self._factory.CreateRenderers(inputType, input, tmpOutputFolder, desiredStyles, desiredMetagroups, desiredSizes, onlyUseExistingBaseIcons, renderMetagroupOverlays, metadata, self._language)
        if self._preRenderCallback:
            outputInfos = []
            for r in renderers:
                outputInfos.extend(r.GetOutputList())

            self._preRenderCallback(input, outputInfos)
        return _JobInfo(options, outputFolder, tmpOutputFolder, renderers, errors)


def CompareIcons(iconA, iconB, tolerance = DEFAULT_ICON_DIFF_TOLERANCE):
    diffResult = imgdiff.ImgDiff(iconA, iconB, normal=False, alpha=False)
    error = diffResult['Color']['MeanAbsoluteError']
    return error <= tolerance


def _ReviewOptions(options):
    if options & Options.CHECKOUT:
        options = options | Options.USE_TMP_FOLDER
    return options


def _GetCorrectFolders(outputFolder, options):
    if options & Options.USE_TMP_FOLDER:
        tmpOutputFolder = os.path.join(tempfile.mkdtemp('Icons'))
        if outputFolder is None:
            outputFolder = tmpOutputFolder
    else:
        if outputFolder is None:
            print
            return (None, None, ["No output folder or temp folder defined, can't generate icons."])
        tmpOutputFolder = outputFolder
    return (outputFolder, tmpOutputFolder)


def _ProcessCopyErrors(failed):
    errors = []
    for src, dst, excstring in failed:
        if os.path.exists(dst):
            errors.append('Failed to copy new icon to target directory:\n    icon: {}\n    target: {}\n{}'.format(src, dst, excstring))
        else:
            errors.append('Failed to overwrite existing icon with new generated version:\n    new icon: {}\n    old icon: {}\n{}'.format(src, dst, excstring))

    return errors


def _CreateGenerationFailedErrors(copyOps, outputFiles):
    if len(copyOps) != len(outputFiles):
        return [ "Failed to finalize icon, icon wasn't generated: {}".format(x) for x in outputFiles if not os.path.exists(x) ]
    else:
        return []


def _CopyToFinalFolder(outputFolder, outputFiles, changelist):
    resolvedOutputFolder = blue.paths.ResolvePath(outputFolder)
    copyOps = [ (os.path.abspath(x), os.path.abspath(os.path.join(resolvedOutputFolder, os.path.basename(x)))) for x in outputFiles if os.path.exists(x) ]
    errors = _CreateGenerationFailedErrors(copyOps, outputFiles)

    def copyFiles():
        failed = []
        for src, dst in copyOps:
            if dst != src and os.path.exists(src):
                try:
                    if not os.path.exists(dst):
                        open(dst, 'a').close()
                    shutil.copy(src, dst)
                except (IOError, OSError):
                    import traceback
                    failed += (src, dst, ''.join(traceback.format_exc()))

        return failed

    if changelist is not None and perforceutils is not None:
        with perforceutils.checkout([ dst for _, dst in copyOps ], changelist):
            failed = copyFiles()
    else:
        failed = copyFiles()
    errors.extend(_ProcessCopyErrors(failed))
    return errors


def _CleanTmpFolder(tmpOutputFolder, options):
    if options & Options.CLEAN_TMP_FOLDER and options & Options.USE_TMP_FOLDER:
        osutils.SafeRmTree(tmpOutputFolder)
