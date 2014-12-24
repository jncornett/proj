import os

def mkdirp(path):
    try:
        os.makedirs(path)
    except os.error:
        if not os.path.exists(path):
            raise


def touch(path):
    with open(path, "a"):
        os.utime(path)

def find_dirs(root):
    dirs = {}
    for dirpath, dirnames, filenames in os.walk(root):
        pass

