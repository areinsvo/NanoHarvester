# CoffeaHarvester (NanoAOD coffeabeans producer)

### Set up CMSSW

```
cmsrel CMSSW_9_4_11_cand2
cd CMSSW_9_4_11_cand2/src
cmsenv
```

### Hack NanoAOD framework (when running over 94X MiniAODv3)

```bash
git cms-addpkg PhysicsTools/NanoAOD

# comment out L183 of PhysicsTools/NanoAOD/python/nano_cff.py
run2_nanoAOD_94X2016.toModify(process, nanoAOD_addDeepFlavourTagFor94X2016) 
```

### Apply changes on PhysicsTools/NanoAOD

```bash
# this one contains the updated EGM corrections for electron/photons (**only needed for legacy 2016**)
git cms-merge-topic -u hqucms:deep-boosted-jets-94X-custom-nano
```

### Get customized NanoAOD producers

```bash
git clone https://github.com/CoffeaTeam/CoffeaHarvester PhysicsTools/NanoTuples
```

### Compile

```bash
scram b -j16
```
### Test

```bash
cd PhysicsTools/NanoTuples/test
```
MC (80X, MiniAODv2):

```bash
cmsDriver.py mc -n -1 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 94X_mcRun2_asymptotic_v2 --step NANO --nThreads 4 --era Run2_2016,run2_miniAOD_80XLegacy --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC --filein file:step-1.root --fileout file:nano.root --no_exec

# test file: /store/mc/RunIISummer16MiniAODv2/ttHToCC_M125_TuneCUETP8M2_13TeV_powheg_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/106F8E1B-23ED-E711-9F58-0025905B861C.root
```

Data (2016 ReReco):

```bash
cmsDriver.py data -n -1 --data --eventcontent NANOAOD --datatier NANOAOD --conditions 94X_dataRun2_v4 --step NANO --nThreads 4 --era Run2_2016,run2_miniAOD_80XLegacy --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData_METMuEGClean --filein file:step-1.root --fileout file:nano.root --no_exec

# test file: /store/data/Run2016H/MET/MINIAOD/03Feb2017_ver3-v1/80000/2A9DE5C7-ADEA-E611-9F9C-008CFA111290.root
```

MC (2016 Legacy):

```bash
cmsDriver.py mc -n -1 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 94X_mcRun2_asymptotic_v3 --step NANO --nThreads 4 --era Run2_2016,run2_miniAOD_80XLegacy --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC --filein file:step-1.root --fileout file:nano.root --no_exec

# test file: /store/mc/RunIISummer16MiniAODv2/ttHToCC_M125_TuneCUETP8M2_13TeV_powheg_pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/106F8E1B-23ED-E711-9F58-0025905B861C.root
```

Data (2016 Legacy):

```bash
cmsDriver.py data -n -1 --data --eventcontent NANOAOD --datatier NANOAOD --conditions 94X_dataRun2_v10 --step NANO --nThreads 4 --era Run2_2016,run2_nanoAOD_94X2016 --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData --filein file:step-1.root --fileout file:nano.root --no_exec

# test file: /store/data/Run2016H/MET/MINIAOD/17Jul2018-v2/00000/0A0B71F7-75B8-E811-BAB7-0425C5DE7BE4.root
```

MC (94X, re-miniAOD 12Apr2018):

```bash
cmsDriver.py mc -n 100 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 94X_mc2017_realistic_v14 --step NANO --nThreads 4 --era Run2_2017,run2_miniAOD_94XFall17 --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC --filein /store/mc/RunIIFall17MiniAODv2/ttHToCC_M125_TuneCP5_13TeV-powheg-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/70000/EED096D8-EE98-E811-A327-0CC47A7C3572.root --fileout nano_mc2017.root --no_exec

```

Data (94X, re-miniAOD 31Mar2018):

```bash
cmsDriver.py data -n 100 --data --eventcontent NANOAOD --datatier NANOAOD --conditions 94X_dataRun2_v6 --step NANO --nThreads 4 --era Run2_2017,run2_miniAOD_94XFall17 --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData --filein /store/data/Run2017F/MET/MINIAOD/31Mar2018-v1/910000/A0858FDD-E73B-E811-803F-0CC47A7C34A6.root --fileout nano_data2017.root --no_exec

```

### Production

**Step 0**: switch to the crab production directory and set up grid proxy, CRAB environment, etc.

```bash
cd $CMSSW_BASE/PhysicsTools/NanoTuples/crab
# set up grid proxy
voms-proxy-init -rfc -voms cms --valid 168:00
# set up CRAB env (must be done after cmsenv)
source /cvmfs/cms.cern.ch/crab3/crab.sh
```

**Step 1**: generate the python config file with `cmsDriver.py` with the following commands:

MC (80X, MiniAODv2):

```bash
cmsDriver.py mc -n -1 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 94X_mcRun2_asymptotic_v2 --step NANO --nThreads 4 --era Run2_2016,run2_miniAOD_80XLegacy --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC --filein file:step-1.root --fileout file:nano.root --no_exec
```

Data (`23Sep2016` ReReco):

```bash
cmsDriver.py data -n -1 --data --eventcontent NANOAOD --datatier NANOAOD --conditions 94X_dataRun2_v4 --step NANO --nThreads 4 --era Run2_2016,run2_miniAOD_80XLegacy --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData_METMuEGClean --filein file:step-1.root --fileout file:nano.root --no_exec
```
MC (94X, re-miniAOD 12Apr2018):

```bash
cmsDriver.py mc -n -1 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions 94X_mc2017_realistic_v14 --step NANO --nThreads 4 --era Run2_2017,run2_miniAOD_94XFall17 --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC --filein file:step-1.root --fileout file:nano.root --no_exec

```

Data (94X, re-miniAOD 31Mar2018):

```bash
cmsDriver.py data -n -1 --data --eventcontent NANOAOD --datatier NANOAOD --conditions 94X_dataRun2_v6 --step NANO --nThreads 4 --era Run2_2017,run2_miniAOD_94XFall17 --customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData --filein  file:step-1.root --fileout file:nano.root --no_exec
```
Global tags and eras are gotten from: https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD


**Step 2**: use the `crab.py` script to submit the CRAB jobs:

For MC:

```bash
python crab.py -p mc_NANO.py -o /store/group/lpccoffea/coffeabeans/nano_mc_[version] -t NanoTuples-[version] -i mc_[ABC].txt --num-cores 4 --send-external -s EventAwareLumiBased -n 50000 --work-area crab_projects_mc_[ABC] --dryrun
```

For data:

```bash
python crab.py -p data_NANO.py -o /store/group/lpccoffea/coffeabeans/nano_data_[version] -t NanoTuples-[version] -i data.txt --num-cores 4 --send-external -s EventAwareLumiBased -n 50000 --work-area crab_projects_data --dryrun
```

A JSON file can be applied for data samples with the `-j` options. By default, we use the golden JSON for 2016:

```
https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt
```
For 2017, the recommended JSON is:

```
https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt
```

For updated information, check: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2017Analysis

These command will perform a "dryrun" to print out the CRAB configuration files. Please check everything is correct (e.g., the output path, version number, requested number of cores, etc.) before submitting the actual jobs. To actually submit the jobs to CRAB, just remove the `--dryrun` option at the end.

**Step 3**: check job status

The status of the CRAB jobs can be checked with:

```bash
./crab.py --status --work-area crab_projects_[ABC]
```

Note that this will also resubmit failed jobs automatically.

The crab dashboard can also be used to get a quick overview of the job status:
`https://dashb-cms-job.cern.ch/dashboard/templates/task-analysis`

More options of this `crab.py` script can be found with:

```bash
./crab.py -h
```

### Uploading Data into striped database
#### Obtaining account at ifdb02 and setting up environment

To upload datasets on the database you need an account at ifdb02. ask Igor for one by email (ivm@fnal.gov). Provide you FNAL username in the request. Then kinit and log in into ifdb02:
```bash
kinit FNAL_USERNAME@FNAL.GOV
ssh FNAL_USERNAME@ifdb02.fnal.gov 
```
At your home directory in ifdb02 download and install Miniconda2 
```bash
wget https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh
bash Miniconda2-latest-Linux-x86_64.sh
```
Follow the screen instructions (select yes/ENTER in all cases). Once that is done, clone the data loading tools at your home directory
```bash
git clone http://cdcvs.fnal.gov/projects/nosql-ldrd bigdata
```
Change directory into bigdata/ingest folder and untar the couchbase client and pyxrootd libraries into the python site-packages directory
```bash
cd ~/bigdata/ingest
tar -xzvf couchbase_python.tar.gz -C ~/miniconda2/lib/python2.7/site-packages/
tar -xzvf pyxrootd.tar.gz -C ~/miniconda2/lib/python2.7/site-packages/
```
Now set up python with miniconda

```bash
export PATH=~/miniconda2/bin:$PATH
conda create -n py2 python
```
(select yes 'y' when asked)

Install uproot 3.3.0 
```bash
pip install uproot==3.3.0
```
Change directory into bigdata and run the setup.py script
```
cd ~/bigdata/
python setup.py install
```
Now switch into the follwing directory

```bash
cd ~/bigdata/ingest/ingestion
```
Create a file named setup.py and fill it with the following

```bash
export STRIPED_HOME=${HOME}/striped_home
export PYTHONPATH=${HOME}/build/striped:${HOME}/pythreader
export COUCHBASE_BACKEND_CFG=`pwd`/couchbase.cfg
```
In the same directory create a file named couchbase.cfg whith the following 
```bash
[CouchBase]
Username = striped
Password = Striped501
Readonly_Username = readonly
Readonly_Password = StripedReadOnly
ClusterURL = couchbase://dbdev112,dbdev115?operation_timeout=100
```
With the envirionment set up you may run the following to check if everything is working properly.
```bash
cd ~/bigdata/ingest/ingestion/
source setup.py
cd ../tools 
python deleteDataset.py Sandbox user_testDataset
python createDataset.py nanoMC2016.json Sandbox user_testDataset
cd ../ingestion
python loadFile.py root://cmseos.fnal.gov//store/group/lpccoffea/coffeabeans/nano_2016/DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NanoTuples-2016_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1/181126_171720/0000/nano_1.root Sandbox user_testDataset
```
If with the last command you receive an error complaining lzma is not installed do
```bash
conda install -c conda-forge backports.lzma
```
and re-run 
```bash
python loadFile.py root://cmseos.fnal.gov//store/group/lpccoffea/coffeabeans/nano_2016/DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NanoTuples-2016_RunIISummer16MiniAODv2-PUMoriond17_80X_v6-v1/181126_171720/0000/nano_1.root Sandbox user_testDataset
```
The output should be

```bash
Using file name: nano_1.root
No user profile will be created
Checking if the file is already uploaded
Found 0 events from this file in the database
Starting RGID: 0, 3 row groups, average row group size:16649
```


### Loading data
Before using any of the following scripts you must run the following once, everytime you log in
```bash
cd ~/bigdata/ingest/ingestion/
source setup.py
```
**Step 1**: Generate a dataset schema

You will create a json file that describes the structure of the input rootfiles. You should expect a different schema for data and MC simulations. Schema can be also different due to specific reasons. For instance, in NanoAOD trigger bits are stored singly and the list of triggers can vary in each file. Taking this into account, you can generate the schema as follows.

First, switch into 
```bash
cd $HOME/bigdata/ingest/datasets/yourFileFormat
```
where yourFileFormat is either bacon or NanoAOD

Now run the following script

```bash
python make_schema.py <file_path> <schema>
```

Where file_path is the absolute path to one of the files from the dataset you want to upload and schema is the name you will give to the created json file. You may use xrootd for the input file, the path would be: root://cmseols.fnal.gov//path/to/file/in/eos


**Step 2**: Create the datasets in the database

Before uploading your files you need to define datasets. Datasets can be defined based on the physics process taken into account for simulation or the primary dataset for data. This step is fairly elastic. As an example, one can define a W+jets dataset and pass the HT/pT bin information as metadata, or generate different datasets based on the HT/pT bin.

To do this:
```bash
cd ~/bigdata/ingest/tools/ 
```
and run
```bash
python createDataset.py <schema> <bucket name> <dataset name>
```
You may view available buckets at http://dbdev121.fnal.gov:8091/ui/index.html (user:admin password:ad___501) clicking at the "Buckets" button at the top left. <schema> would be the is the previously created schema json file and dataset name is whatever name you want to give to the dataset, you will be using this name to access the files when running an analysis. You may obtain premade schemas for nanoAOD datasets from /data3/fnavarro/schemas/. To copy all of them in to your ingestion directory:
  
 ```bash
 cp -r /data3/fnavarro/schemas ~/bigdata/ingest/ingestion/
 ```

**Step 3** Uploading

To upload the files you will need a list containing the path to the files. This may be local files or files stored at eos. Switch into the ingestion directory (bigdata/ingest/ingestion), you will use the script loadFiles.py
The minimum parameters you need are

```bash
python loadFiles.py  <bucket name> <dataset-name> @<file containing list of files>  # '@' before the name of the file is necessary
```
This will load the files with a default column size of 10000 and name them as they are originaly named.
You can increase the column size with the -n parameter. You may also give a prefix to the file paths at your list with the parameter -p <path-prefix>. Also, if files within the same dataset have the same name (for example files from a dataset may be located under dataset/.../0000/nano_1.root and dataset/.../0001/nano_1.root)
you can use the -k <n> option to add the n directories  previous to the file into its name. (in the previous example 0000 and 0001 would be aded to nano_1.root. now one would be 0000_nano_1.root and the other 0001_nano_1.root). This way they can be uploaded into the same dataset. You can find example file lists under. /data3/fnavarro/exampleUploadFiles
To see additional options run
```bash
python loadFiles.py
```
## Loading tools extras ##

**Listing Dataset info**
A tool you might whant to use to check if a dataset was uploaded properly is listDataset.py under ~/bigdata/ingest/tools/. It is used the following way

```bash
python listDataset.py [-f|-l] <bucket> <dataset>
```
Runing this without the options -f or -l wil output the number of files uploaded, the total number of events, the number of row groups and the missing rowgroups along with some other info. Using -f will list the files and -l will list the files along with the row group id they belong to. 

**Re-runing failed jobs**
If an upload gets interrupted by any reason you may either continue uploading the files remaining or start from scratch by firsts deleting the dataset and creating it again. To remove a dataset:

```bash
cd ~/bigdata/ingest/tools/
python deleteDataset.py <bucket> <dataset>
```
you may use listDataset.py to check if it was properly removed. An unexisting dataset should output
```bash
0 items removed
```
If a dataset upload fails before it is done,  you may view the files that have been uploaded with 
```bash
python listDataset.py -f <bucket> <dataset> 
```
then remove them from the file list you are using to upload and run loadFiles.py with the same options you where using before.
**Extra Tip:** If you computer gets temporarily disconected from the internet while an upload was in progress do not interact with the terminal that was doing the job by clicking or typing on it. It is likely this will log you out with a connection error. If left alone it is likely the job will continue when you reconect. 



