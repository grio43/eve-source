#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\samplePage.py
import imp
import inspect
import os
import blue
import re
from carbonui import uiconst
from eve.client.script.ui.control.treeData import TreeData
from eve.devtools.script.uiControlCatalog.sample import Sample

def _natural_sort(l):
    convert = lambda text: (int(text) if text.isdigit() else text.lower())
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key.__name__) ]
    return sorted(l, key=alphanum_key)


def get_control_data(dirName = 'controls', filter_txt = ''):
    path = os.path.dirname(__file__)
    path += '\\' + dirName
    if filter_txt:
        return get_sample_group_nodes_filtered(path, filter_txt)
    else:
        return get_sample_group_nodes(path)


def get_sample_group_nodes(path):
    rootNode = TreeData()
    for name in os.listdir(path):
        filePath = path + '\\' + name
        if os.path.isdir(filePath):
            children = get_sample_group_nodes(filePath).children
            if children:
                rootNode.AddNode(label=name, children=children)
        elif is_valid_sample(filePath):
            rootNode.AddChild(SamplePage(filePath))

    rootNode.children.sort(key=lambda x: (isinstance(x, SamplePage), x.GetLabel()))
    return rootNode


def get_sample_group_nodes_filtered(path, filter_txt = ''):
    rootNode = TreeData()
    for name in os.listdir(path):
        filePath = path + '\\' + name
        if os.path.isdir(filePath):
            children = get_sample_group_nodes_filtered(filePath, filter_txt).children
            if children:
                rootNode.AddNode(label=name, children=children)
        elif is_valid_sample(filePath):
            page = SamplePage(filePath)
            if filter_txt.lower() in page.GetLongName().lower():
                rootNode.AddChild(page)

    rootNode.children.sort(key=lambda x: (isinstance(x, SamplePage), x.GetLabel()))
    return rootNode


def is_valid_sample(filePath):
    baseName = os.path.basename(filePath)
    if baseName == '__init__.py':
        return False
    else:
        return baseName.endswith('.py')


def is_sample_func(name, val):
    return inspect.isfunction(val) and name.startswith('Sample')


def is_sample_class(val):
    return inspect.isclass(val) and issubclass(val, Sample) and val != Sample and not val.__name__.startswith('_')


def browse_controls():
    blue.os.ShellExecute(os.path.dirname(__file__) + '\\controls')


class SamplePage(TreeData):

    def __init__(self, label, parent = None, children = None):
        TreeData.__init__(self, label, parent, children)
        self.cls = None
        self.numSamples = 0
        self.samples = []
        self.ParseDataFromFile()
        self.description = None
        self._labelText = self._GetLabel()

    def GetLabel(self):
        return self._labelText

    def _GetLabel(self):
        m = self._GetModule()
        fileName = m.__doc__ or os.path.basename(self.GetFilePath()).replace('.py', '')
        if self.IsDeprecated():
            fileName = '{} <color=red>DEPRECATED</color>'.format(fileName)
        return fileName

    def GetLongName(self):
        if self.cls:
            return self.GetImportPath()
        else:
            return self.GetLabel()

    def GetDescription(self):
        if self.description:
            return self.description
        elif self.cls:
            doc = self.GetBaseClass().__doc__ or ''
            return doc.strip().split('\n')[0]
        else:
            return ''

    def GetFilePath(self):
        return self._label

    def GetBaseClass(self):
        return self.cls

    def ParseDataFromFile(self):
        module = self._GetModule()
        self.samples = []
        for name, val in module.__dict__.iteritems():
            if is_sample_class(val):
                self.samples.append(val)
            elif is_sample_func(name, val):
                self.samples.append(val)

        self.samples = _natural_sort(self.samples)

    def _GetModule(self):
        path = self.GetFilePath()
        dir_name, file_name = os.path.split(path)
        module_name = file_name.split('.')[0]
        module_info = imp.find_module(module_name, [dir_name])
        module = imp.load_module(module_name, *module_info)
        return module

    def GetSample(self, sampleNum):
        return self.samples[sampleNum]()

    def GetNumSamples(self):
        return len(self.samples)

    def GetImportPath(self):
        if self.cls:
            return self.cls.__module__ + '.' + self.cls.__name__

    def GetSampleCode(self, sampleNum = None):
        if sampleNum is not None:
            return self.GetSampleCodeForPage(sampleNum)
        return self.GetAllCode()

    def GetSampleCodeForPage(self, sampleNum):
        return self.samples[sampleNum]().get_snippet()

    def GetAllCode(self):
        return open(self.GetFilePath()).read()

    def OpenSampleCodeInEditor(self):
        blue.os.ShellExecute(self.GetFilePath())

    def IsDeprecated(self):
        doc = self.GetBaseClass().__doc__ or ''
        for line in doc.splitlines():
            if line.strip().lower().startswith('deprecated'):
                return True
        else:
            return False

    def GetHint(self):
        return self.GetDescription()

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2
