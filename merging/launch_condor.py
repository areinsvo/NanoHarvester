#These should be passed as input parameters to the python script
YEAR=2018
REDIRECTOR = root://cmseos.fnal.gov//
OUTPUTDIR = /store/group/lpccoffea/coffeabeans/NanoAODv6_merged/nano_2018
INDIR = /store/group/lpccoffea/coffeabeans/NanoAODv6/nano_2018/

dataset_list = all directories under INDIR

for ds in dataset_list:
    if test in ds or Sandeep in ds:
        continue
    ds_dir = INDIR/ds
    array_crab_tasks = list of directories that are within ds_dir  #check if there are multiple crab outputs for this dataset name
    num_crab_tasks = size(array_crab_tasks)

    if num_crab_tasks == 0:
        print ds_dir is an empty directory!
        continue

    if num_crab_tasks >= 1:
        if num_crab_tasks > 1:
            print "Multiple directories within ds_dir! Going to copy all of them to their own OUTPUTDIR/ds/timestamps folders"

        for timestamp in array_crab_tasks:
            for num in range(0,total number of directories in ds_dir/timestamp):
                num_string = “0000” + num
                in_dir_full = ds_dir/timestamp/num_string
                out_dir_full = OUTPUTDIR/ds/timestamp/num_string

                printf("Going to merge %s into %s",%in_dir_full,%out_dir_full)

                #Now need to edit the corresponding bash script that the condor job will execute
                #The shell script would need to use haddCoffeaBeans.py, passing in_dir_full and out_dir_full as parameters
                #The other input to haddCoffeaBeans.py is the average number of files to merge together
