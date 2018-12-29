import os, time, itertools
import sys, getopt, json, pprint
from couchbase import FMT_BYTES, FMT_JSON
from couchbase.exceptions import KeyExistsError, TemporaryFailError, TimeoutError, NotFoundError
import numpy as np
#from RowGroupMap import RowGroupMap
from striped.client import CouchBaseBackend
from striped.common import Stopwatch, Tracer
from striped.common import stripe_key, format_array, rginfo_key, RGInfo, ProvenanceSegment
from pythreader import Queue, PyThread

from DataReader import DataReader

#from trace import Tracer

SIZE_ARRAY_DTYPE = "<u4"
StripeHeaderFormatVersion = "1.0"

#T = Tracer()

""" schema JSON file format

{
    "version":"2.0",
    "attributes":
    {
        "path.to.attr": {
            dtype:"dtype"
            },
        ...
    },
    "branches":
    {
        "path.to.branch":
        {
            "relative.path.to.attr": {
                "dtype":"dtype"
            },
            ...
        }
    }
}
    
some branches will look like this:

{
    "branches":
    {
        "path.to.branch":
        {
            "":{
                "dtype":"dtype"
            }
        },
        ...
    }
}

This is special case where the branch is in fact is an attribute with
a homogenous array as value. In this case, the array() will return a jagged
array of shape: [nevents, width] with constant width.

This needs to be converted to stripe "path.to.branch" 
with size array "path.to.branch.@size" which will look like [width]*nevents

"""

def stripeArray(groups, array):
    i = 0
    for n in groups:
        yield array[i:i+n]
        i += n

def parseSchema(schema):
    return schema["attributes"], schema["branches"]

class BufferedStripeWriter:

        BUFSIZE = 50

        def __init__(self, backend, dataset_name):
            self.DatasetName = dataset_name            
            self.Backend = backend
            self.Buf = {}
            self.TotalBytes = 0

        def write(self, rgid, column_name, array):
            key = stripe_key(self.DatasetName, column_name, rgid)
            self.Buf[key] = format_array(array)
            if len(self.Buf) >= self.BUFSIZE:
                    self.flush()

        def flush(self):
            if self.Buf:
                self.Backend.put_data(self.Buf)
                # verify
                read_back = self.Backend.get_data(self.Buf.keys())
                for k, d in self.Buf.items():
                    rbd = read_back.get(k)
                    if rbd != d:
                        raise RuntimeError("Read-back data verification failed for key %s: data length:%d, read back:%d" % (
                            k, len(d), len(rbd)))
                self.TotalBytes += sum([len(data) for data in self.Buf.values()])
            self.Buf = {}

class StripedWriter(PyThread):

        BUFSIZE = 5
        QUEUESIZE = 50
        
        def __init__(self, backend, dataset_name):
            PyThread.__init__(self)
            self.Queue = Queue(self.QUEUESIZE)
            self.DatasetName = dataset_name            
            self.Backend = backend
            self.Buf = {}
            self.TotalBytes = 0
            self.Shutdown = False
            self.T = Tracer()
            
        def add(self, rgid, column_name, array):
            self.Queue.append((rgid, column_name, array))
            
        def shutdown(self):
            self.Shutdown = True
            
        def run(self):
            while not (self.Shutdown and len(self.Queue) == 0):
                rgid, column_name, array = self.Queue.pop()
                self.write(rgid, column_name, array)
            self.flush()

        def write(self, rgid, column_name, array):
            key = stripe_key(self.DatasetName, column_name, rgid)
            self.Buf[key] = format_array(array)
            if len(self.Buf) >= self.BUFSIZE:
                    self.flush()

        def flush(self):
            if self.Buf:
                with self.T["flush/put_data"]:
                    self.Backend.put_data(self.Buf)
                # verify
                if False:
                    with self.T["flush/verify"]:
                        read_back = self.Backend.get_data(self.Buf.keys())
                        for k, d in self.Buf.items():
                            rbd = read_back.get(k)
                            if rbd != d:
                                raise RuntimeError("Read-back data verification failed for key %s: data length:%d, read back:%d" % (
                                    k, len(d), len(rbd)))
                self.TotalBytes += sum([len(data) for data in self.Buf.values()])
            self.Buf = {}
                        

def getRGMap(backend, dataset, filename):
    rgmap = RowGroupMap.fromDict(backend.RGMap(dataset))
    start_rgid, groups = rgmap[file_name]
    return start_rgid, groups
    
def generateGroupSizes(N, t):
    if N <= t:
        return [N]
        
    M = int(float(N+t-1)/t)
    k = N % M
    p = M - k
    if p == M: p = 0
    Nt = (N+p)/M
    return [Nt]*(M-p) + [Nt-1]*p
    
def parseProfile(text):
    dct = {}
    for w in text.split():
        name, val = w.split("=", 1)
        if val[0] == '"' and val[-1] == '"':
            val=val[1:-1]   # string
        else:
            try:    val = int(val)
            except:
                try:    val = float(val)
                except:
                    pass        # string
        dct[name] = val
    return dct
    
                

Usage = """
python loadUprootBatch3.py [options] <input file> <bucket name> <dataset name> [<data reader args> ...]

Options: 
    -c <CouchBase config file>
    -n <row group size target> default=20000
    -C <correction module>  - Python module to correct the data
    -O override existing file
    -p 'param=value ...' - row group profile
    -g (a|m)       - row group assigment:
            a=allocate - default - generate row groups according to the target and then 
                                allocate row group ids from the DB
            m=map - use previously generated row group map
"""

schema_file = None
ClusterURL = None
BucketName = None
dataset_name = None
skip = 0
start_rgid = None
group_assignment = "a"
events_per_group = 20000
tree_top = None
corrector_file = None
data_corrector_class = None
SchemaCorrector = None
schema = None
config_file = None
no_file_override = True
log_file_name = None
profile = None

opts, args = getopt.getopt(sys.argv[1:], "n:g:s:c:Ol:p:")
for opt, val in opts:
    if opt == '-c':
        config_file = val
    if opt == '-g': 
        assert val in ("a", "m")
        group_assignment = val
    if opt == "-n":
        events_per_group = int(val)
    if opt == '-O':
        no_file_override = False
    if opt == '-s':
        schema = json.load(open(val, "r"))
    if opt == '-p':
        profile = val
    if opt == '-l':
        log_file_name = val


if len(args) < 3:
    print Usage
    sys.exit(1)


input_file = args[0]
BucketName = args[1]
dataset_name = args[2]
reader_params = args[3:]

file_name = input_file.rsplit("/", 1)[-1]

backend = CouchBaseBackend(BucketName, print_errors = True, config = config_file)
    
try:
    schema = backend["%s:@@schema.json" % (dataset_name,)].json
except:
    print "Can not get dataset schema from the database"
    raise


data_reader = DataReader(input_file, schema, *reader_params)

if profile == "file":
    profile = data_reader.profile()
elif profile:
    profile = parseProfile(profile)
else:
    profile = None
    
if profile:
    print "Use profile: %s" % (profile,)
else:
    print "No user profile will be created"

nevents = data_reader.nevents()
if nevents == 0:
        print "Tree %s in file %s is empty. tree.numentries=0" % (tree_top, root_file)
        sys.exit(0)

groups = generateGroupSizes(nevents, events_per_group)
assert sum(groups) == nevents

#
# check if the file is already there
#
if no_file_override:
        rginfos = backend.RGInfos(dataset_name)
        n_events = 0
        min_rgid = None
        print "Checking if the file is already uploaded"
        for rginfo in rginfos:
                for segment in rginfo["Segments"]:
                        if segment["FileName"] == file_name:
                                n_events += segment["NEvents"]
        print "Found %d events from this file in the database" % (n_events,)
        if n_events:
                if n_events == nevents:
                        print "File with %d events is aleady in the database. Skipping" % (n_events,)
                        sys.exit(0)
                else:
                        print "File is in the database, but with wrong number of events: %d vs %d" % (n_events, nevents)
                        sys.exit(1)
else:
        # find all RGInfos for the file
        rginfos = backend.RGInfos(dataset_name)
        rgids = []
        this_file_rgids = []
        for rginfo in rginfos:
                rgid = rginfo["RGID"]
                other_files = []
                this_file = False
                for segment in rginfo["Segments"]:
                        if segment["FileName"] == file_name:
                                this_file = True
                        else:
                                other_files.append(segment["FileName"])
                if this_file and other_files:
                        print "Can not override this file because RG %d has stripes from this file and other files: %s" % (rgid, other_files)
                        sys.exit(1)
                if this_file:
                        this_file_rgids.append(rgid)
                else:
                        rgids.append(rgid)

        # if there is no mixing with other files, delete all RGInfos for this file
        print "Deleting %d RGInfos foung for this file" % (len(this_file_rgids),)
        keys = ["%s:@@rginfo:%d.json" % (dataset_name, rgid) for rgid in this_file_rgids]
        backend.delete(keys)

        if len(this_file_rgids) >= len(groups):
                rgids_to_use = sorted(this_file_rgids)
                start_rgid = rgids_to_use[0]
                print "Will reuse %d old RGIDs starting from %d" % (len(groups), start_rgid)
                

if start_rgid is None:
        if group_assignment == 'a':
            start_rgid = backend.allocateRGIDs(dataset_name, len(groups))
        else:
            raise NotImplementedError("Row group map handling not implemented")
        rgids_to_use = range(start_rgid, start_rgid+len(groups))


average_row_group_size = int(float(nevents)/len(groups)+0.5)

print "Starting RGID: %d, %d row groups, average row group size:%d" % (start_rgid, len(groups), average_row_group_size)


#
# Write stripes
#

#writer = BufferedStripeWriter(backend, dataset_name)
writer = StripedWriter(backend, dataset_name)
writer.start()
column_type = None
last_stripe_name = None

nstripes = 0

#
# writing attributes
#

for attr_name, attr_desc in schema["attributes"].items():
    for ig, (data_stripe, size_stripe) in \
                enumerate(data_reader.stripesAndSizes(groups, None, attr_name, attr_desc)):
        rgid = rgids_to_use[ig]
        data_stripe = np.asarray(data_stripe, dtype=attr_desc["dtype"])
        writer.add(rgid, attr_name, data_stripe)
        if size_stripe is not None:
            size_stripe = np.asarray(size_stripe, dtype=SIZE_ARRAY_DTYPE)
            writer.add(rgid, attr_name + ".@size", size_stripe)

#
# writing branches
#

for bname, bdict in schema["branches"].items():
    branch_size_array = data_reader.branchSizeArray(bname)
    if branch_size_array is None or len(branch_size_array) == 0:    continue
    branch_size_array = np.asarray(branch_size_array, dtype=SIZE_ARRAY_DTYPE)
    
    for ig, size_stripe in enumerate(stripeArray(groups, branch_size_array)):
        rgid = rgids_to_use[ig]
        writer.add(rgid, bname + ".@size", size_stripe)
        
    for attr_name, attr_desc in bdict.items():
        for ig, (data_stripe, size_stripe) in enumerate(data_reader.stripesAndSizes(groups, bname, attr_name, attr_desc)):
            rgid = rgids_to_use[ig]
            if data_stripe is not None:
                data_stripe = np.asarray(data_stripe, dtype=attr_desc["dtype"])
                writer.add(rgid, bname+"."+attr_name, data_stripe)
            if size_stripe is not None:
                size_stripe = np.asarray(size_stripe, dtype=SIZE_ARRAY_DTYPE)
                writer.add(rgid, bname+"."+attr_name+".@size", size_stripe)
    #data_reader.reopen()

writer.shutdown()
writer.join()

#
# Write RGInfo records
#

rginfos = {}

ievent = 0

for r, gs in enumerate(groups):
        rgid = rgids_to_use[r]
        key = rginfo_key(dataset_name, rgid)
        segment = ProvenanceSegment(file_name, begin_event = ievent, nevents = gs)
        rginfo = RGInfo(rgid, segment, profile=profile)
        rginfos[key] = rginfo.toDict()
        ievent += gs

backend.put_json(rginfos)

#print "Reader trace stats:"
#data_reader.T.printStats()

#print "Writer trace stats:"
#writer.T.printStats()
        
        
        




