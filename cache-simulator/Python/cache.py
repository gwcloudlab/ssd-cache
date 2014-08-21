#!/usr/bin/python

import os
import sys
import signal 
import string

class g:
"""  
This class doesn't have a constructor. It will just be used
to hold global variables.
"""
#  default cache parameters--can be changed
   WORD_SIZE = 4
   WORD_SIZE_OFFSET = 2
   DEFAULT_CACHE_SIZE = (8 * 1024)
   DEFAULT_CACHE_BLOCK_SIZE = 16
   DEFAULT_CACHE_ASSOC = 1
   DEFAULT_CACHE_WRITEBACK = False
   DEFAULT_CACHE_WRITEALLOC = False

   cache_split = 0;
   cache_usize = DEFAULT_CACHE_SIZE
   cache_isize = DEFAULT_CACHE_SIZE
   cache_dsize = DEFAULT_CACHE_SIZE
   cache_block_size = DEFAULT_CACHE_BLOCK_SIZE
   words_per_block = DEFAULT_CACHE_BLOCK_SIZE / WORD_SIZE
   cache_assoc = DEFAULT_CACHE_ASSOC
   cache_writeback = DEFAULT_CACHE_WRITEBACK
   cache_writealloc = DEFAULT_CACHE_WRITEALLOC

class cache_stat():
   accesses = 0
   misses = 0
   replacements = 0
   demand_fetch = 0

class Cache(object):
   
   """docstring for Cache"""
   def __init__(self):
      super(Cache, self).__init__()
      self.lru = {}
      self.clearCache()

   def set_cache_param():

      #Set all the cache parameters

   def perform_access():
      
      # Handle cache accesses

   def flush():
      
      # Flush the cache

   def delete():

      # Delete a cache line based on lru or fifo

   def insert():

      # Insert a cache line

   def dump_settings():

      # Print current cache settings

   def print_stats():

      # Print current cache statistics

def main():

   # Receive command line arguments

   if not len(sys.argv) == 4: # Check for command line arguments
      print "Usage: %s [ cache size ] [ associativity] [ trace filename ]\n" % \
      os.path.basename(sys.argv[0])
      sys.exit(0)

if __name__ == "__main__": main()