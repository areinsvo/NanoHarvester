import subprocess, time, sys, getopt, os, glob
from pythreader import TaskQueue, Subprocess, Task

class FileLoaderTask(Task):

    def __init__(self, nfiles, ifile, script_name, filename, rgsize, tree_top, config, bucket_name, dataset_name, corrector, override):
        Task.__init__(self)
        self.Filename = filename
        self.ScriptName = script_name
        self.RowGroupSize = rgsize
        self.TreeTop = tree_top
        self.BucketName = bucket_name
        self.Config = config
        self.DatasetName = dataset_name
        self.NFiles = nfiles
        self.IFile = ifile
        self.Corrector = corrector
	self.Override = override
        
    def run(self):
        corr_option = "" if self.Corrector is None else "-C %s" % (self.Corrector,)
        conf_option = "" if self.Config is None else "-c %s" % (self.Config,)
	over_option = "" if not self.Override else "-O"
        command = "python %s -n %d %s %s %s %s %s %s %s" % (
            self.ScriptName, self.RowGroupSize, conf_option, corr_option, over_option,
            self.Filename,
            self.TreeTop, self.BucketName, self.DatasetName)
        print "\nStaring %d/%d: %s" % (self.IFile, self.NFiles, command)
        sp = Subprocess(command.split(), env=os.environ)
        sp.wait()
        print "\n%d is done" % (self.IFile,)


Usage = """
python loadDataset.py [options] <directory> <tree top> <bucket name>

Options:
    -c <CouchBase config file>
    -m <max workers>, default = 5
    -n <row group size>, default = 10000
    -d <dataset name>, defult = directory name
    -s <stagger>, default = 10 (seconds)
    -C <data correction module file>
    -O override existing files
    -w <worker script name>
        worker script arguments: 
            -n <row group size> <file name> <tree top> <bucket url> <dataset name>
"""

MaxWorkers = 5
RGSize = 10000
DatasetName = None
Stagger = 10
WorkerScript = "loadUprootBatch3.py"
Corrector = None
Config = None
Override = False

opts, args = getopt.getopt(sys.argv[1:], "m:n:d:s:w:c:C:O")
for opt, val in opts:
    if opt == "-m":     MaxWorkers = int(val)
    elif opt == "-n":   RGSize = int(val)
    elif opt == "-s":   Stagger = int(val)
    elif opt == "-d":   DatasetName = val
    elif opt == "-w":   WorkerScript = val
    elif opt == "-c":   Config = val
    elif opt == "-C":   Corrector = val
    elif opt == "-O":   Override = True

if len(args) != 3:
    print Usage
    sys.exit(1)
    
Directory, TreeTop, BucketName = args

if DatasetName is None:
    DatasetName = Directory.rsplit("/",1)[-1]

files = sorted(glob.glob("%s/*.root" % (Directory,)))

tq = TaskQueue(MaxWorkers)
for i, fp in enumerate(files):
    t = FileLoaderTask(len(files), i, WorkerScript, fp, RGSize, TreeTop, Config, BucketName, DatasetName, Corrector, Override)
    tq << t
    time.sleep(Stagger)

    
