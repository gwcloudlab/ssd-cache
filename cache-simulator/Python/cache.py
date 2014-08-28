import time


class Cache(object):

    __miss_lookup__ = {
        16: 40,
        32: 42,
        64: 44,
        128: 46}

    __access_time__ = {
        16: 1,
        32: 5,
        64: 10,
        128: 15}

    """docstring for Cache"""

    def __init__(self):
        self.lru = 0
        self.valid = 0
        self.dirty = 0

    def get_lru(self):
        return self.lru

    def is_valid(self):
        return 1 if True else 0

    def is_dirty(self):
        return 1 if True else 0

    def set_lru(self):
        self.lru = time.time()

    def __repr__(self):
        return "<Cache lru:%s>" % (self.lru)
'''
   def access_time(self):
        return self.__access_time__[self.size]

   def miss_time(self):
        return self.__miss_lookup__[self.blocksize]
'''
