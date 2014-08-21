#include <stdlib.h>
#include <stdio.h>
#include <getopt.h>
#include <strings.h>
#include <limits.h>

//#include "cachelab.h"

/* Always use a 64-bit variable to hold memory addresses*/
typedef unsigned long long int mem_addr_t;

/* a struct that groups cache parameters together */
typedef struct
{
   int s;                       /* 2**s cache sets */
   int b;                       /* cacheline block size 2**b bytes */
   int E;                       /* number of cachelines per set */
   int S;                       /* number of sets, derived from S = 2**s */
   int B;                       /* cacheline block size (bytes), derived from B = 2**b */
} cache_param_t;

int verbosity;

/* printUsage - Print usage info */
void printUsage( char *argv[] )
{
   printf( "Usage: %s [-hv] -s <num> -E <num> -b <num> -t <file>\n", argv[0] );
   printf( "Options:\n" );
   printf( "  -h         Print this help message.\n" );
   printf( "  -v         Optional verbose flag.\n" );
   printf( "  -s <num>   Number of set index bits.\n" );
   printf( "  -E <num>   Number of lines per set.\n" );
   printf( "  -b <num>   Number of block offset bits.\n" );
   printf( "  -t <file>  Trace file.\n" );
   printf( "\nExamples:\n" );
   printf( "  %s -s 4 -E 1 -b 4 -t traces/yi.trace\n", argv[0] );
   printf( "  %s -v -s 8 -E 2 -b 4 -t traces/yi.trace\n", argv[0] );
   exit( 0 );
}

void printSummary( int hit_count, int miss_count, int eviction_count )
{
   printf( "hits: %d   misses: %d   evictions: %d\n", hit_count, miss_count, eviction_count );
} 

int main( int argc, char **argv )
{
   cache_param_t par;

   bzero( &par, sizeof ( par ) );

   char *trace_file;
   char c;

   while ( ( c = getopt( argc, argv, "s:E:b:t:vh" ) ) != -1 )
   {
      switch ( c )
      {
         case 's':
            par.s = atoi( optarg );
            break;
         case 'E':
            par.E = atoi( optarg );
            break;
         case 'b':
            par.b = atoi( optarg );
            break;
         case 't':
            trace_file = optarg;
            break;
         case 'v':
            verbosity = 1;
            break;
         case 'h':
            printUsage( argv );
            exit( 0 );
         default:
            printUsage( argv );
            exit( 1 );
      }
   }

   if ( par.s == 0 || par.E == 0 || par.b == 0 || trace_file == NULL )
   {
      printf( "%s: Missing required command line argument\n", argv[0] );
      printUsage( argv );
      exit( 1 );
   }

   /* TODO: Compute S and B based on information passed in */

   //Compute S and B, 2^s and 2^b respectively
   par.S = ( 1 << par.s );
   par.B = ( 1 << par.b );

   /* TODO: Initialize a cache */

   //Structure for a line
   typedef struct
   {
      int valid;
      mem_addr_t tag;
      int timestamp;
   } line_st;

   //Structure for a set; a pointer to an array of lines
   typedef struct
   {
      line_st *lines;
   } cache_set;

   //Structure for a cache; a pointer to an array of sets
   typedef struct
   {
      cache_set *sets;
   } cache_t;

   //allocate space for sets and for lines
   cache_t cache;

   cache.sets = malloc( par.S * sizeof ( cache_set ) );
   for ( int i = 0; i < par.S; i++ )
   {
      cache.sets[i].lines = malloc( sizeof ( line_st ) * par.E );
   }

   //counters
   int hit_count = 0;
   int miss_count = 0;
   int eviction_count = 0;

   /* TODO: Run the trace simulation */

   char act;                    //L,S,M
   int size;                    //size read in from file
   int TSTAMP = 0;              //value for LRU
   int empty = -1;              //index of empty space
   int H = 0;                   //is there a hit
   int E = 0;                   //is there an eviction
   mem_addr_t addr;

   //open the file and read it in
   FILE *traceFile = fopen( trace_file, "r" );

   if ( traceFile != NULL )
   {
      while ( fscanf( traceFile, " %c %llx,%d", &act, &addr, &size ) == 3 )
      {
         int toEvict = 0;             //keeps track of what to evict
         if ( act != 'I' )
         {
            //calculate address tag and set index
            mem_addr_t addr_tag = addr >> ( par.s + par.b );
            int tag_size = ( 64 - ( par.s + par.b ) );
            unsigned long long temp = addr << ( tag_size );
            unsigned long long setid = temp >> ( tag_size + par.b );
            cache_set set = cache.sets[setid];
            int low = INT_MAX; // CHANGED, also added #include <limits.h>

            for ( int e = 0; e < par.E; e++ ) {
               if ( set.lines[e].valid == 1 ) {
                  // CHANGED ORDER: look for hit before eviction candidates
                  if ( set.lines[e].tag == addr_tag ) {
                     hit_count++;
                     H = 1;
                     set.lines[e].timestamp = TSTAMP;
                     TSTAMP++;
                  }
                  // CHANGED WHOLE ELSE: look for oldest for eviction.
                  else if ( set.lines[e].timestamp < low ) {
                     low = set.lines[e].timestamp;
                     toEvict = e;
                  }
               }
               // CHANGED: if we haven't yet found an empty, mark one that we found.
               else if( empty == -1 ) {
                  empty = e;
               }
            }

            //if we have a miss
            if ( H != 1 )
            {
               miss_count++;
               //if we have an empty line
               if ( empty > -1 )
               {
                  set.lines[empty].valid = 1;
                  set.lines[empty].tag = addr_tag;
                  set.lines[empty].timestamp = TSTAMP;
                  TSTAMP++; 
               }
               //if the set is full we need to evict
               else if ( empty < 0 )
               {
                  E = 1;
                  set.lines[toEvict].tag = addr_tag;
                  set.lines[toEvict].timestamp = TSTAMP;
                  TSTAMP++; // CHANGED: increment TSTAMP here too
                  eviction_count++;
               }
            }
            //if the instruction is M, we will always get a hit
            if ( act == 'M' )
            {
               hit_count++;
            }
            //if the -v flag is set print out all debug information
            if ( verbosity == 1 )
            {
               printf( "%c ", act );
               printf( "%llx,%d", addr, size );
               if ( H == 1 )
               {
                  printf( "Hit " );
               }
               else if ( H != 1 )
               {
                  printf( "Miss " );
               }
               if ( E == 1 )
               {
                  printf( "Eviction " );
               }
               // CHANGED: don't print Hit again since 'M' is always going to print Hit above.
               printf( "\n" );
            }
            empty = -1;
            H = 0;
            E = 0;
         }
      }
   }

   /* TODO: Clean up cache resources */

   /* TODO: Print out real results */
   printSummary( hit_count, miss_count, eviction_count );
   return 0;
}