#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\fontExtractor.py
import logging
import os
import shutil
from collections import namedtuple
from distutils.dir_util import mkpath
from os.path import join as pjoin
from xml.etree import ElementTree
logger = logging.getLogger(__name__)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class Config:
    path_prefix = ''
    font_dir = ''
    manifest = ''
    install_path = ''


FontData = namedtuple('FontData', 'id name weight')

def get_font_metadata(manifest_path):
    tree = ElementTree.parse(manifest_path)
    fonts_subtree = tree.getroot().find('fonts')
    fonts = []
    for font_elem in fonts_subtree.findall('font'):
        props = font_elem.find('properties')
        f_id = font_elem.find('id').text
        f_name = props.find('familyName').text
        f_weight = props.find('variationName').text
        font = FontData(id=f_id, name=f_name, weight=f_weight)
        fonts.append(font)

    return fonts


def extract_fonts(fonts, font_dir, location):
    location = os.path.abspath(location)
    mkpath(location)
    for font in fonts:
        try:
            src = os.path.abspath(pjoin(font_dir, str(font.id)))
            filename = font.name + ' - ' + font.weight + '.otf'
            dest = pjoin(location, filename)
            shutil.copy(src, dest)
        except Exception as e:
            logger.exception('Failed to load font: %s', e)


def platform_setup():
    c = Config()
    c.path_prefix = os.path.expandvars('c:/users/$USERNAME/AppData/Roaming/Adobe/CoreSync/plugins/livetype')
    c.font_dir = pjoin(c.path_prefix, 'r')
    c.manifest = pjoin(c.path_prefix, 'c/entitlements.xml')
    return c


def extracFonts(folderPath):
    config = platform_setup()
    fonts = get_font_metadata(config.manifest)
    extract_fonts(fonts, config.font_dir, folderPath)


if __name__ == '__main__':
    extracFonts('../../client/res/UI/Fonts/Extracted')
