#!/usr/bin/env python

# imports and load libraries
import array
from sys import argv,exit
import sys
from os import environ,system,path,remove
from argparse import ArgumentParser
import subprocess

input_dir = argv[1]
output_dir = argv[2]
input_splitting = float(argv[3])
output_splitting = float(argv[4])

print("Will merge files in %s into %s, going from %d events per file to %d" %(input_dir, output_dir,input_splitting,output_splitting))

float_files_to_merge = output_splitting/input_splitting
int_files_to_merge = int(float_files_to_merge)
if float_files_to_merge % 1.0 > 0.5: 
    int_files_to_merge += 1

input_files = subprocess.check_output('xrdfs root://cmseos.fnal.gov ls -u '+input_dir,shell=True).split()
num_in_files = len(input_files)

num_out_files = 0

print("Total files = %d, want to merge %d into one file" %(num_in_files,int_files_to_merge))
for i in range(1,num_in_files,int_files_to_merge):
    last_file = i+int_files_to_merge-1
    if last_file >= num_in_files:
        last_file = num_in_files
    print("Will merge %d to %d" %(i,last_file))
    num_out_files+=1
    mergers = ""
    for j in range(i-1,last_file):
        mergers = mergers+" "+input_files[j]
    print("python haddnano.py nano_%s.root %s" %(num_out_files,mergers))
    print("Copying file to output directory")
    print("xrdcp nano_%s.root root://cmseos.fnal.gov/%s" %(num_out_files,output_dir))
    print("rm nano_%s.root" %(num_out_files))
    print("++++++++++++++++++++++++++++++++++++++++++++++")

print("Will go from %d to %d total files" %(num_in_files, num_out_files))
