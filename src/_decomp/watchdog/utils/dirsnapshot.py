#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\watchdog\utils\dirsnapshot.py
import errno
import os
from stat import S_ISDIR
from watchdog.utils import stat as default_stat
from watchdog.utils.compat import scandir

class DirectorySnapshotDiff(object):

    def __init__(self, ref, snapshot, ignore_device = False):
        created = snapshot.paths - ref.paths
        deleted = ref.paths - snapshot.paths
        if ignore_device:

            def get_inode(directory, full_path):
                return directory.inode(full_path)[0]

        else:

            def get_inode(directory, full_path):
                return directory.inode(full_path)

        for path in ref.paths & snapshot.paths:
            if get_inode(ref, path) != get_inode(snapshot, path):
                created.add(path)
                deleted.add(path)

        moved = set()
        for path in set(deleted):
            inode = ref.inode(path)
            new_path = snapshot.path(inode)
            if new_path:
                deleted.remove(path)
                moved.add((path, new_path))

        for path in set(created):
            inode = snapshot.inode(path)
            old_path = ref.path(inode)
            if old_path:
                created.remove(path)
                moved.add((old_path, path))

        modified = set()
        for path in ref.paths & snapshot.paths:
            if get_inode(ref, path) == get_inode(snapshot, path):
                if ref.mtime(path) != snapshot.mtime(path) or ref.size(path) != snapshot.size(path):
                    modified.add(path)

        for old_path, new_path in moved:
            if ref.mtime(old_path) != snapshot.mtime(new_path) or ref.size(old_path) != snapshot.size(new_path):
                modified.add(old_path)

        self._dirs_created = [ path for path in created if snapshot.isdir(path) ]
        self._dirs_deleted = [ path for path in deleted if ref.isdir(path) ]
        self._dirs_modified = [ path for path in modified if ref.isdir(path) ]
        self._dirs_moved = [ (frm, to) for frm, to in moved if ref.isdir(frm) ]
        self._files_created = list(created - set(self._dirs_created))
        self._files_deleted = list(deleted - set(self._dirs_deleted))
        self._files_modified = list(modified - set(self._dirs_modified))
        self._files_moved = list(moved - set(self._dirs_moved))

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        fmt = '<{0} files(created={1}, deleted={2}, modified={3}, moved={4}), folders(created={5}, deleted={6}, modified={7}, moved={8})>'
        return fmt.format(type(self).__name__, len(self._files_created), len(self._files_deleted), len(self._files_modified), len(self._files_moved), len(self._dirs_created), len(self._dirs_deleted), len(self._dirs_modified), len(self._dirs_moved))

    @property
    def files_created(self):
        return self._files_created

    @property
    def files_deleted(self):
        return self._files_deleted

    @property
    def files_modified(self):
        return self._files_modified

    @property
    def files_moved(self):
        return self._files_moved

    @property
    def dirs_modified(self):
        return self._dirs_modified

    @property
    def dirs_moved(self):
        return self._dirs_moved

    @property
    def dirs_deleted(self):
        return self._dirs_deleted

    @property
    def dirs_created(self):
        return self._dirs_created


class DirectorySnapshot(object):

    def __init__(self, path, recursive = True, stat = default_stat, listdir = scandir):
        self.recursive = recursive
        self.stat = stat
        self.listdir = listdir
        self._stat_info = {}
        self._inode_to_path = {}
        st = self.stat(path)
        self._stat_info[path] = st
        self._inode_to_path[st.st_ino, st.st_dev] = path
        for p, st in self.walk(path):
            i = (st.st_ino, st.st_dev)
            self._inode_to_path[i] = p
            self._stat_info[p] = st

    def walk(self, root):
        try:
            paths = [ os.path.join(root, entry if isinstance(entry, str) else entry.name) for entry in self.listdir(root) ]
        except OSError as e:
            if e.errno in (errno.ENOENT, errno.ENOTDIR, errno.EINVAL):
                return
            raise

        entries = []
        for p in paths:
            try:
                entry = (p, self.stat(p))
                entries.append(entry)
                yield entry
            except OSError:
                continue

        if self.recursive:
            for path, st in entries:
                try:
                    if S_ISDIR(st.st_mode):
                        for entry in self.walk(path):
                            yield entry

                except (IOError, OSError) as e:
                    if e.errno != errno.EACCES:
                        raise

    @property
    def paths(self):
        return set(self._stat_info.keys())

    def path(self, id):
        return self._inode_to_path.get(id)

    def inode(self, path):
        st = self._stat_info[path]
        return (st.st_ino, st.st_dev)

    def isdir(self, path):
        return S_ISDIR(self._stat_info[path].st_mode)

    def mtime(self, path):
        return self._stat_info[path].st_mtime

    def size(self, path):
        return self._stat_info[path].st_size

    def stat_info(self, path):
        return self._stat_info[path]

    def __sub__(self, previous_dirsnap):
        return DirectorySnapshotDiff(previous_dirsnap, self)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str(self._stat_info)


class EmptyDirectorySnapshot(object):

    @staticmethod
    def path(_):
        return None

    @property
    def paths(self):
        return set()
