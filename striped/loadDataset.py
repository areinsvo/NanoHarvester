import subprocess, time, sys, getopt, os, glob
from pythreader import TaskQueue, Subprocess, Task

class FileLoaderTask(Task):

    def __init__(self, nfiles, ifile, script_name, config, filename, rgsize, bucket_name, dataset_name, override):
        Task.__init__(self)
        self.Filename = filename
        self.ScriptName = script_name
        self.RowGroupSize = rgsize
        self.BucketName = bucket_name
        self.DatasetName = dataset_name
        self.NFiles = nfiles
        self.IFile = ifile
        self.Override = override
        self.Config = config
        
    def run(self):
        conf_option = "" if self.Config is None else "-c %s" % (self.Config,)
        over_option = "" if not self.Override else "-O"
        command = "python %s -p file -n %d %s %s %s %s %s" % (
            self.ScriptName, self.RowGroupSize, conf_option, over_option,
            self.Filename,
            self.BucketName, self.DatasetName)
        print "\nStaring %d/%d: %s" % (self.IFile, self.NFiles, command)
        sp = Subprocess(command.split(), env=os.environ)
        sp.wait()
        print "\n%d is done" % (self.IFile,)


Usage = """
python loadDataset.py [options] <directory> <tree top> <bucket name>

Options:
    -c <CouchBase config file>
    -m <max workers>, default = 5
    -n <row group size>, default = 20000
    -d <dataset name>, defult = directory name
    -s <stagger>, default = 10 (seconds)
    -O override existing files
"""

MaxWorkers = 5
RGSize = 20000
DatasetName = None
Stagger = 10
WorkerScript = "loadStripedThreaded.py"
Corrector = None
Config = "./couchbase.cfg"
Override = False

opts, args = getopt.getopt(sys.argv[1:], "m:n:d:s:w:c:O")
for opt, val in opts:
    if opt == "-m":     MaxWorkers = int(val)
    elif opt == "-n":   RGSize = int(val)
    elif opt == "-s":   Stagger = int(val)
    elif opt == "-d":   DatasetName = val
    elif opt == "-w":   WorkerScript = val
    elif opt == "-c":   Config = val
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
    t = FileLoaderTask(len(files), i, WorkerScript, Config, fp, RGSize, BucketName, DatasetName, Override)
    tq << t
    time.sleep(Stagger)

    
