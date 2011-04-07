#!/usr/bin/env python

import os
import stat
import errno

# # pull in some spaghetti to make this stuff work without fuse-py being installed
# try:
#     import _find_fuse_parts
# except ImportError:
#     pass
import fuse
from fuse import Fuse
if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "python-fuse doesn't know of fuse.__version__, probably it's too old."
fuse.fuse_python_api = (0, 2)

import logging
LOG_FILENAME = 'dictfs.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

# Only make one of this whe getstat() is called. Real FS has one per entry (file
# or directory).
#
class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

# My FS, only stored in memory :P
#
class DictFS(Fuse):
    """
    """
    def __init__(self, *args, **kw):
        Fuse.__init__(self, *args, **kw)

        # Root dir
        self.root = {}

    # Return string path as list of path elements
    def __path_list(self, path):
        raw_path = path.split('/')
        path = []
        for entry in raw_path:
            if entry != '':
                path.append(entry)
        return path

    # Return list of path elements as string
    def __join_path(self, path):
        joined_path = '/'
        for element in path:
            joined_path += (element + '/')
        return joined_path[:-1]

    # Return dict of a given path
    def __get_dir(self, path):
        level = self.root
        path = self.__path_list(path)
        for entry in path:
            if level.has_key(entry):
                if type(level[entry]) is dict:
                    level = level[entry]
                else:
                    # Walk over files?
                    return {}
            else:
                # Walk over non-existent dirs?
                return {}
        return level

    # Return dict of a given path plus last name of path
    def __navigate(self, path):
        # Path analysis
        path = self.__path_list(path)
        entry = path.pop()
        # Get level
        level = self.__get_dir(self.__join_path(path))
        return level, entry

    ### FILESYSTEM FUNCTIONS ###

    def getattr(self, path):
        st = MyStat()
        logging.debug('*** getattr(%s)', path)

        # Ask for root dir
        if path == '/':
            #return self.root.stats
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
            return st

        level, entry = self.__navigate(path)

        if level.has_key(entry):
            # Entry found
            # is a directory?
            if type(level[entry]) is dict:
                st.st_mode = stat.S_IFDIR | 0755 # rwx r-x r-x
                st.st_nlink = 2
                logging.debug('*** getattr_dir_found: %s', entry)
                return st
            # is a file?
            if type(level[entry]) is str:
                st.st_mode = stat.S_IFREG | 0666 # rw- rw- rw-
                st.st_nlink = 1
                st.st_size = len(level[entry])
                logging.debug('*** getattr_file_found: %s', entry)
                return st

        # File not found
        logging.debug('*** getattr_entry_not_found')
        return -errno.ENOENT

    def readdir(self, path, offset):
        logging.debug('*** readdir(%s, %d)', path, offset)       

        file_entries = ['.','..']

        # Get filelist
        level = self.__get_dir(path)

        # Get all directory entries
        if len(level.keys()) > 0:
            file_entries += level.keys()

        file_entries = file_entries[offset:]
        for filename in file_entries:
            yield fuse.Direntry(filename)

    def mkdir ( self, path, mode ):
        logging.debug('*** mkdir(%s, %d)', path, mode)

        level, entry = self.__navigate(path)

        # Make new dir
        level[entry] = {}

    def mknod ( self, path, mode, dev ):
        logging.debug('*** mknod(%s, %d, %d)', path, mode, dev)

        level, filename = self.__navigate(path)

        # Make empty file
        level[filename] = ''

    # This method could maintain opened (or locked) file list and,
    # of course, it could check file permissions.
    # For now, only check if file exists...
    def open ( self, path, flags ):
        logging.debug('*** open(%s, %d)', path, flags)

        level, filename = self.__navigate(path)

        # File exists?
        if not level.has_key(filename):
            return -errno.ENOENT

        # No exception or no error means OK

    # In this example this method is the same as open(). This method
    # is called by close() syscall, it's means that if open() maintain
    # an opened-file list, or lock files, or something... this method
    # must do reverse operation (refresh opened-file list, unlock files...
    def release ( self, path, flags ):
        logging.debug('*** release(%s, %d)', path, flags)

        level, filename = self.__navigate(path)

        # File exists?
        if not level.has_key(filename):
            return -errno.ENOENT

    def read ( self, path, length, offset ):
        logging.debug('*** read(%s, %d, %d)', path, length, offset)

        level, filename = self.__navigate(path)

        # File exists?
        if not level.has_key(filename):
            return -errno.ENOENT

        # Check ranges
        file_size = len(level[filename])
        if offset < file_size:
            # Fix size
            if offset + length > file_size:
                length = file_size - offset
            buf = level[filename][offset:offset + length]
        else:
            # Invalid range returns no data, instead error!
            buf = ''
        return buf

    def rmdir ( self, path ):
        logging.debug('*** rmdir(%s)', path)

        level, entry = self.__navigate(path)

        # File exists?
        if not level.has_key(entry):
            return -errno.ENOENT

        # Delete entry
        del(level[entry])

    def truncate ( self, path, size ):
        logging.debug('*** truncate(%s, %d)', path, size)

        level, filename = self.__navigate(path)

        # File exists?
        if not level.has_key(filename):
            return -errno.ENOENT

        # Truncate file to specified size
        level[filename] = ' ' * size
        
    def unlink ( self, path ):
        logging.debug('*** unlink(%s)', path)

        level, entry = self.__navigate(path)

        # File exists?
        if not level.has_key(entry):
            return -errno.ENOENT

        # Remove entry
        del(level[entry])

    def write ( self, path, buf, offset ):
        logging.debug('*** write(%s, %s, %d)', path, str(buf), offset)

        level, filename = self.__navigate(path)

        # Write data into file
        level[filename] = level[filename][:offset] + str(buf)
        
        # Return written bytes
        return len(buf)

    # TO-DO: this!
    def rename ( self, oldPath, newPath ):
        logging.debug('*** rename(%s, %s)', oldPath, newPath)
        return -errno.ENOSYS


def main():
    usage = """
Userspace filesystem example

""" + Fuse.fusage
    
    fs = DictFS(version = '%prog' + fuse.__version__,
                usage = usage,
                dash_s_do='setsingle')
    fs.parse(errex = 1)
    fs.main()

if __name__ == '__main__':
    main()
