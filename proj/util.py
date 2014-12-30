import fnmatch
import os

def mkdirp(path):
    try:
        os.makedirs(path)
    except os.error:
        if not os.path.exists(path):
            raise

def touch(path, text=None):
    with open(path, "a") as f:
        if text is None:
            os.utime(path, None)
        else:
            f.write(text)


def find_dirs_containing(root, pattern, top_only=True):
    for dirpath, dirnames, filenames in os.walk(root):
        if fnmatch.filter(filenames, pattern):
            yield os.path.relpath(dirpath, root)
            if top_only:
                dirnames[:] = []


def expand_join(*paths):
    return os.path.expanduser(os.path.join(*paths))
