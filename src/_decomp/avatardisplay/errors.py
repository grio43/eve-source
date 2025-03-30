#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\avatardisplay\errors.py


class FailedToPlaybackScene(RuntimeError):

    def __init__(self, scene_dir, file_missing):
        self.message = 'Failed to find avatar scene file {file_missing} under {scene_dir}'.format(file_missing=file_missing, scene_dir=scene_dir)

    def __str__(self):
        return self.message
