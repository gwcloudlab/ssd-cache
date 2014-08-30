Build and run ```cache-sim.py```

To change the caching algorithm, change the value of
```
self.EVICT_POLICY = "weightedLRU"
```
in the ```__init__``` function in ```sim.py``` to ```globalLRU``` or ```staticLRU```


To debug using pdb, uncomment the following two lines in sim.py

```
print self.ssd.keys()
pdb.set_trace()
```
and from the command line run
```
python -m pdb cache-sim.py
```
The above command will invoke the debugger and keep hitting ```c``` to see what elements are being added and cross reference it with the input file to see if the elements are added in the right order.
