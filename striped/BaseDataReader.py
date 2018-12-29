class BaseDataReader(object):

    #def __init__(self, *params, **args):
    #    pass

    # Abstract base class for the data reader
    
    def profile(self):
        return None

    def stripesAndSizes(self, group_sizes, branch, attr_name, descriptor):
        raise NotImplementedError
        
    def branchSizeArray(self, branch_name, bdesc):
        raise NotImplementedError
        
    def nevents(self):
        raise NotImplementedError
                

