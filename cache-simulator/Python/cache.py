class Cache(object):

   __miss_lookup__ = {
      16:  40,
      32:  42,
      64:  44,
      128: 46 }

   __access_time__ = {
      16:   1,
      32:   5,
      64:  10,
      128: 15 }

   """docstring for Cache"""
   def __init__(self, blocksize=16, size=64):
      self.lru       = 0
      self.accesses  = 0
      self.valid     = 0
      self.dirty     = 0

   def get_lru(self):
      return self.lru

   def get_accesses(self):
      return self.accesses

   def is_valid(self):
      return 1 if True else 0

   def is_dirty(self):
      return 1 if True else 0

   def increment_lru(self):
      self.lru += 1

   def increment_accesses(self):
      self.accesses += 1

   #For printing object values
   def __repr__(self):
      return "<Cache lru:%s accesses:%s>" % (self.lru, self.accesses)
'''
   def access_time(self):
        return self.__access_time__[self.size]

   def miss_time(self):
        return self.__miss_lookup__[self.blocksize]
'''

if __name__ == "__main__": main()