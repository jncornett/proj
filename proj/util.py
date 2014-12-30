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
            os.utime(path)
        else:
            f.write(text)



def find_dirs_containing(root, pattern, top_only=True):
    for dirpath, dirnames, filenames in os.walk(root):
        if fnmatch.filter(filenames, pattern):
            yield os.path.relpath(dirpath, root)
            if top_only:
                dirnames[:] = []



class ChainedDictView(object):
    def __init__(self, *dicts):
        self._dicts = list(dicts)
        # Topmost dict in the stack takes precedence
        self._keymap = {key: i for i, d in enumerate(self._dicts)
                        for key in d}


    def __getitem__(self, key):
        return self._dicts[self._keymap[key]][key]


    def __iter__(self):
        return iter(self.keys())


    def __len__(self):
        return len(self.keys())


    def keys(self):
        return self._keymap.keys()


    def get(self, key, *default):
        if len(default) == 1:
            try:
                return self[key]
            except KeyError:
                return default[0]
        elif not default:
            return self[key]
        else:
            raise TypeError(
                ("{} expected at most "
                 "{} default value, got {}").format(
                    self.__class__.__name__,
                    1,
                    len(default)
                    )
                )


    def items(self):
        return set((key, self[key]) for key in self)

    
    def values(self):
        return (self[key] for key in self)



    
