import os, time, itertools
import sys, getopt, json, pprint
from couchbase import FMT_BYTES, FMT_JSON
from couchbase.exceptions import KeyExistsError, TemporaryFailError, TimeoutError, NotFoundError
import numpy as np
import uproot
from RowGroupMap import RowGroupMap
from uprootArray3 import UprootArray
from striped.client import CouchBaseBackend
from striped.common import Stopwatch


#from trace import Tracer

SIZE_ARRAY_DTYPE = "<i8"
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

def parseSchema(schema):
    return schema["attributes"], schema["branches"]

class CBInterface:

        def __init__(self, backend, dataset_name):
                self.Backend = backend
                self.DatasetName = dataset_name
                self.DocumentCache = {}

        def ____upsertAndRetryMulti(self, data, retries=10, format=FMT_JSON):
                        done = False
                        while retries and not done:
                                try:    self.CB.upsert_multi(data, format=format)
                                except TimeoutError:
                                        print sys.exc_info()
                                        time.sleep(5)
                                        retries -= 1
                                except TemporaryFailError:
                                        print sys.exc_info()
                                        time.sleep(5)
                                        retries -= 1
                                else:
                                        done = True
                        if not done:
                                raise ValueError("Number of retries exceeded. DB insert operation failed")

        def allocateRGIDs(self, n):
                return self.Backend.counter("%s:@@nextRGID" % (self.DatasetName,), delta=n).value - n

        def getDocument(self, key):
                doc = None
                if key in self.DocumentCache:
                        doc = self.DocumentCache[key]
                else:
                        #print "desc for %s not found" % (key,)
                        try:    doc = self.Backend[key].json
                        except NotFoundError:
                                doc = None
                        self.DocumentCache[key] = doc
                return doc

        def getColumnDescriptor(self, column_name):
                key = "%s:%s:@@desc.json" % (self.DatasetName, column_name)
                return self.getDocument(key)
                
        def getRGMap(self):
            try:
                rgmap = self.getDocument("%s:@@rgmap.json" % (self.DatasetName,)).value
            except:
                print "Can not get row group map from the database"
                raise
            return RowGroupMap.fromDict(rgmap)

class Striper(object):

    def __init__(self, data, groups, todtype=None):
        # data is iterable, each element is either scalar or ndarray
        self.Data = data
        self.Groups = groups
        self.ToDtype = None if todtype is None else np.dtype(todtype)
        
    def stripes(self):
        l = len(self.Data)
        i = 0
        for n in self.Groups:
            try:
                segment = np.array(self.Data[i:i+n], dtype=self.ToDtype)
            except:
                print "Error in %s: %s %s" % (root_file, self.Data[i:i+n], self.ToDtype)
                raise
            i += n
            yield segment, n
            
class UTreeScanner:

        def __init__(self, utree, schema, groups, data_corrector_class = None):
                self.UTree = utree
                self.Schema = schema
                fields, branches = parseSchema(schema)
                self.Branches = branches
                self.Fields = fields
                self.Events = utree.numentries
                assert sum(groups) == self.Events
                print "%d events in the file" % (self.Events,)
                self.GroupSizes = groups
                print "total size of all the groups: %d" % (sum(self.GroupSizes),)
                self.Corrector = None if data_corrector_class is None else \
                    data_corrector_class(self.UTree, schema)

        @property
        def group_count(self):
                return len(self.GroupSizes)

        @property
        def group_sizes(self):
                return enumerate(self.GroupSizes)


        def stripes(self):
        
            #
            # Attributes
            #
            for fn, fd in self.Fields.items():
                ft = fd["dtype"]
                src = fd["source"]
                b = self.UTree[src]
                arr = UprootArray.create(b)
                dtype = arr.DType
                if self.Corrector.has_key(src):
                    parent, fn, data, dtype, shape = self.Corrector.correct(src, arr)
                    assert parent is None, "Corrected parent expected to be None for field:%s (source:%s). Parent returned:%s" % (
                            fn, src, parent)
                    arr = UprootArray.fromSimple(dtype, shape, data)
                for rgid, part in enumerate(arr.stripes(self.GroupSizes)):
                        yield fn, rgid, part
                        
                #
                # size stripes if var length
                #
                if arr.hasSizes():
                    for rgid, segment in enumerate(arr.stripeSizes(self.GroupSizes)):
                            yield fn + ".@size", rgid, segment
                            
                #print "%s done" % (fn,)

            #
            # Branches
            #
            
            branch_sizes = {}
            
            for bn, fdict in self.Branches.items():
                first = True
                for fn, fdesc in fdict.items():
                    #print "Element: %s.%s" % (bn, fn)
                    ftype = fdesc["dtype"]
                    src = fdesc["source"]
                    #print fpath
                    b = self.UTree[src]
                    arr = UprootArray.create(b)
                    parent = bn

                    if self.Corrector.has_key(src):
                        parent, fn, data, dtype, shape = self.Corrector.correct(src, arr)
                        arr = UprootArray.fromSimple(dtype, shape, data)
                        
                    fpath = parent + "." + fn if fn else parent

                    if parent in branch_sizes:
                        #if src == "Jets":   print "Jets"
                        old_sizes = branch_sizes[parent]
                        for rgid, (stripe, size_array) in enumerate(arr.stripesAndSizes(self.GroupSizes)):
                            if np.any(size_array != old_sizes[rgid]):
                                raise ValueError("Inconsistent stripe sizes array for parent=%s, rgid=%d, old:%s, new:%s" % (
                                    parent,rgid,old_sizes[rgid],size_array))
                            yield fpath, rgid, stripe
                    else:
                        sizes = []
                        for rgid, (stripe, size_array) in enumerate(arr.stripesAndSizes(self.GroupSizes)):
                            sizes.append(size_array)
                            yield fpath, rgid, stripe
                        branch_sizes[parent] = sizes
                    #print "%s.%s done" % (bn, fn)
                #print "%s done" % (bn,)
            
            #
            # Branch sizes
            #
            
            for bn, sizes in branch_sizes.items():
                fpath = "%s.@size" % (bn,)
                for rgid, segment in enumerate(sizes):
                    yield fpath, rgid, np.array(segment)
                    
                

class BufferedWriter:

        BUFSIZE = 50

        def __init__(self, backend, format):
                self.Backend = backend
                self.Buf = {}
                self.Format = format

        def __setitem__(self, key, data):
                self.Buf[key] = data
                #print "Buffer.__setitem__:", key, len(data)
                if len(self.Buf) >= self.BUFSIZE:
                        #print "Flush at %d" % (len(self.Buf),)
                        self.flush()

        def flush(self):
            if self.Buf:
                if self.Format == FMT_BYTES:
                    self.Backend.put_data(self.Buf)
                    # verify
                    read_back = self.Backend.get_data(self.Buf.keys())
                    for k, d in self.Buf.items():
                        rbd = read_back.get(k)
                        if rbd != d:
                            raise RuntimeError("Read-back data verification failed for key %s: data length:%d, read back:%d" % (
                                k, len(d), len(rbd)))
                else:
                    self.Backend.put_json(self.Buf)
            self.Buf = {}
                        

class FSWriter:

    def __init__(self, path, mode):
        self.Path = path
        self.Mode = mode        # "json" or "bin"
        
    def __setitem__(self, key, data):
        if self.Mode == "json":
            data = json.dumps(data, sort_keys = True, indent=4, separators=(',',': '))
        open(self.Path + "/" + key, "wb").write(data)
        
    def flush(self):
        pass                        

def getRGMap(cbi, filename):
    rgmap = cbi.getRGMap()
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
    
                

Usage = """
python loadUprootBatch3.py [options] <root file> <tree top> [<bucket name> <dataset name>]

Options: 
    -c <CouchBase config file>
    -o <path>       - write data into the specified directory instead of the DB
    -n <row group size target> default=5000
    -C <correction module>  - Python module to correct the data
    -O = override existing file
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
events_per_group = 10000
tree_top = None
correction_file = None
data_corrector_class = None
SchemaCorrector = None
out_dir = None
schema = None
config_file = None
no_file_override = True
log_file_name = None

opts, args = getopt.getopt(sys.argv[1:], "n:g:C:o:s:c:Ol:")
for opt, val in opts:
    if opt == '-c':
        config_file = val
    if opt == '-g': 
        assert val in ("a", "m")
        group_assignment = val
    if opt == "-n":
        events_per_group = int(val)
    if opt == '-C':
        correction_file = val
    if opt == '-o':
        out_dir = val
    if opt == '-O':
        no_file_override = False
    if opt == '-s':
        schema = json.load(open(val, "r"))
    if opt == '-l':
        log_file_name = val


if len(args) < 2:
    print Usage
    sys.exit(1)


root_file = args[0]
tree_top = args[1]

file_name = root_file.rsplit("/", 1)[-1]

utree = uproot.open(root_file)[tree_top]

if out_dir is None:
    BucketName = args[2]
    dataset_name = args[3]
    backend = CouchBaseBackend(BucketName, print_errors = True, config = config_file)
    
else:
    out_dir = out_dir + "/" + file_name
    try:    os.makedirs(out_dir)
    except: pass

if correction_file:
    env = {}
    execfile(correction_file, env)
    if "DataCorrector" in env:
        data_corrector_class = env["DataCorrector"]


cbi = None

if BucketName != None:

    #
    # Load schema and descroiptors
    #

    try:
        schema = backend["%s:@@schema.json" % (dataset_name,)].json
    except:
        print "Can not get dataset schema from the database"
        raise


    cbi = CBInterface(backend, dataset_name)
else:
    cbi = None
    assert schema is not None




nevents = utree.numentries
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
	    if out_dir is None:
		start_rgid = cbi.allocateRGIDs(len(groups))
	    else:
		start_rgid = 0
	else:
	    start_rgid, groups = getRGMap(cbi, dataset_name)
        rgids_to_use = range(start_rgid, start_rgid+len(groups))


average_row_group_size = int(float(nevents)/len(groups)+0.5)

print "Starting RGID: %d, %d row groups, average row group size:%d" % (start_rgid, len(groups), average_row_group_size)


up = UTreeScanner(utree, schema, groups, data_corrector_class)



#
# Write stripes
#

stripe_buf = BufferedWriter(backend, FMT_BYTES) if out_dir is None else FSWriter(out_dir, "bin")
column_type = None
last_stripe_name = None

nstripes = 0

with Stopwatch("Writing stripes"):
    for stripe_name, r, arr in up.stripes():
            rgid = rgids_to_use[r]
            if last_stripe_name != stripe_name:
                    column_type = None
                    if cbi is not None:
                        desc = cbi.getColumnDescriptor(stripe_name)
                        if desc is not None:    column_type = desc["type_np"]
                    last_stripe_name = stripe_name
            if column_type is not None:
                    arr = np.asarray(arr, desc["type_np"])
            key = "%s:%s:%d.bin" % (dataset_name, stripe_name, rgid)
            #if stripe_name == 'evtwgt_funcname':
            #    print "evtwgt_funcname:", arr
            header = "#__header:version=%s;dtype=%s#" % (StripeHeaderFormatVersion, arr.dtype.str)
            stripe_buf[key] = bytes(header) + bytes(arr.data) 
            #print "stripe %s: %s %d bytes" % (key, arr.dtype, len(arr.data))
            nstripes += 1
    stripe_buf.flush()
#
# Write RGInfo records
#

with Stopwatch("Writing RGInfo's"):

    ievent = 0
    writer = BufferedWriter(backend, FMT_JSON) if out_dir is None else FSWriter(out_dir, "json")

    for r, gs in up.group_sizes:
            rgid = rgids_to_use[r]
            key = "%s:@@rginfo:%s.json" % (dataset_name, rgid)
            segment = ProvenanceSegment(file_name, begin_event = ievent, nevents = gs)
            rginfo = RGInfo(rgid, segment)
            writer[key] = rginfo.toDict()
            #print "RGInfo %s: %s" % (key, rginfo)
            ievent += gs
    writer.flush()

        
        
        




