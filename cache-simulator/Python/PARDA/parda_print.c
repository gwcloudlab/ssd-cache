#include "parda.h"

void parda_print_front(const program_data_t* pdt) {
  narray_t* ga = pdt->ga;
  int i;
  unsigned len = narray_get_len(ga);
  printf("< ");
  for (i = 0; i < len; i++) {
    printf("%s ", ((HKEY*)ga->data)[i]);
  }
  printf(">\n");
}

void parda_print_end(const end_keytime_t* ekt) {
  narray_t* gkeys = ekt->gkeys;
  narray_t* gtimes = ekt->gtimes;
  //printf("ekt=%p gkeys=%p gtimes=%p in print_end\n",ekt,gkeys,gtimes);
  unsigned len = narray_get_len(gkeys);
  //  printf("len=%u\n",len);
  int i;
  printf("[ ");
  for ( i = 0; i < len; i++) {
    printf("(%s:%d) ", ((HKEY*)(gkeys->data))[i],
        ((T*)(gtimes->data))[i]);
  }
  printf("]\n");
}

void parda_print_tree(const program_data_t* pdt) {
  Tree* root = pdt->root;
  printtree(root,0);
}

void print_iterator(gpointer key, gpointer value, gpointer ekt) {
  printf("(%s:%d) ", (char*)key, *(T*)value);
}

void parda_print_hash(const program_data_t* pdt) {
  printf("[ ");
  g_hash_table_foreach(pdt->gh, (GHFunc)print_iterator, NULL);
  printf("]\n");
}

void parda_print(const program_data_t* pdt) {
  parda_print_front(pdt);
  parda_print_tree(pdt);
  parda_print_hash(pdt);
}

void parda_print_histogram(char* outputFileName, const unsigned* histogram) {
  unsigned long long last_bucket;
  unsigned long long i;//duan
  unsigned long long sum = 0;  // For normalizing
  unsigned long long cum = 0;  // Cumulative output
  //int fd_stdout = dup( fileno(stdout) );
  //freopen (outputFileName,"w",stdout);
  // Find the last non-zero bucket
  last_bucket = nbuckets-1;
  while (histogram[last_bucket] < 1)
    last_bucket--;

  for (i = 0; i <= last_bucket; i++){
    sum += histogram[i];}
  sum += histogram[B_OVFL];
  sum += histogram[B_INF];

  //printf("# Dist\t     Refs\t   Refs(%%)\t  Cum_Ref\tCum_Ref(%%)\n");
  FILE * fp;
  fp=fopen(outputFileName, "w");
  char buffer[80];
  for (i = 0; i <= last_bucket; i++) {
    cum += histogram[i];
    //printf("%6d\t%9u\t%0.8lf\t%9llu\t%0.8lf\n", i, histogram[i],
    //histogram[i] / (double)sum, cum, cum / (double)sum);
    //printf("%u\n", histogram[i]);  
    sprintf(buffer, "%u \n", histogram[i]);
    fputs(buffer,fp);
  }
    fclose(fp);
    cum += histogram[B_OVFL];
  //printf("#OVFL \t%9u\t%0.8f\t%9llu\t%0.8lf\n", histogram[B_OVFL], histogram[B_OVFL]/(double)sum, cum, cum/(double)sum);
  //printf("%llu\t%0.8lf\n", last_bucket, cum/(double)sum);
  cum += histogram[B_INF];
  //printf("#INF  \t%9u\t%0.8f\t%9llu\t%0.8lf\n", histogram[B_INF], histogram[B_INF]/(double)sum, cum, cum/(double)sum);
  //printf("%llu\t%0.8lf\n", last_bucket, cum/(double)sum);
  //printf("#INF  \t%9u\n", histogram[B_INF]);
  //fclose(stdout);
  //fdopen( fd_stdout, "w" );
}
