#!/usr/bin/env python

'''
Main Function for cache for class
'''
import sim

def main():
    world = sim.Sim("sample.trace")
    world.run()

if __name__ == '__main__':
    main()