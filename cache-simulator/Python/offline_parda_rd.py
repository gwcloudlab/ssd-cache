from collections import defaultdict
import ctypes
import os
import csv

class Offline_parda_rd():
    def __init__(self):
        self.trace_size = defaultdict(lambda: 0)
        self.trace_list = defaultdict(list)
        self.trace_files = defaultdict()   #self.trace_files = {0:'0.trace',1:'1.trace',2:'2.trace',3:'3.trace'}
        self.rd_array = defaultdict(list)
        current_path=os.path.split(os.path.realpath(__file__))[0]
        os.path.walk(current_path, self.scan, ())
        
    def calculate_rd(self, disk_id, block_address):
        self.trace_list[disk_id].append(block_address)
        if disk_id not in self.trace_files:
            self.trace_files[disk_id]=str(disk_id)+".trace"

    def get_rd_values(self):
        self.rd_array.clear()
        for k, v in self.trace_files.iteritems():    #k means disk_id, v means trace_file.
            if len (self.trace_list[k]):
                #write block_address into the file (*.trace) with parda input format, and "*" means disk_id.
                with open(os.path.join(v), 'a') as out_file:
                    for block_address in self.trace_list[k]:
                        out_file.write(str(block_address) + '\n')
                        self.trace_size[k]+= 1
                self.trace_list[k] = []
        ll =ctypes.cdll.LoadLibrary
        for k,v in self.trace_files.iteritems():
            #print self.trace_size[k]
            lines=int(self.trace_size[k])
            #print lines
            parda=ll("./parda.so")
            #print v
            #print lines
            parda.classical_tree_based_stackdist(v, lines)  #invoke the parda algorithm.
            #lib = ll("./test.so")  
            #result= lib.foo(100, 3)
        current_path=os.path.split(os.path.realpath(__file__))[0]
        os.path.walk(current_path, self.loadresult, ())
        #print self.rd_array
        return self.rd_array
        
    def scan(self, arg, dirname, names):
        for file in names:
            if file[-6:]==".trace" or file[-9:]=="_hist.csv":
                os.remove(file)
                print "delete PARDA input and output files: ", file

    #load the parda output from the *_hist.csv file, and "*" means disk_id.
    def loadresult(self, arg, dirname, names):
        for file in names:
            if file[-9:]=="_hist.csv":
                disk_id=file[:-9]
                #print file
                rd=0
                total_hit=0
                with open(file, 'rb') as trace:
                    for item in csv.reader(trace, delimiter='\t'):
                        rd_times = int(item[0])
                        if rd_times>0:
                            #print rd_times
                            total_hit +=rd_times
                            for time in range (0, rd_times):
                                self.rd_array[int(disk_id)].append(rd)
                                #print rd
                        rd+=1
                total_refer=self.trace_size[int(disk_id)]
                total_miss=total_refer - total_hit
                rd_infinity = 999999999
                for time in range (0, total_miss):
                    self.rd_array[int(disk_id)].append(rd_infinity)
