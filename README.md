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

### Upload to the Striped database

To upload datasets on the database ask Igor for an account by email (ivm@fnal.gov). Provide you FNAL username in the request. Input rootfiles need to be copied first the Striped machine ifdb01 and then into the database. The capability to read remotely input rootfiles is currenlty under development.

To the Striped machine you need to have a FNAL computing account. Then:

```bash
kinit FNAL_USERNAME@FNAL.GOV
ssh FNAL_USERNAME@ifdb01.fnal.gov 
```

Assuming your files are already copied, you can move forward with the following steps.

**Step 1**: generate the input file schema

You will create a json file that describes the structure of the input rootfiles. You should expect a different schema for data and MC simulations. Schema can be also different due to specific reasons. For instance, in NanoAOD trigger bits are stored singly and the list of triggers can vary in each file. Taking this into account, you can generate the schema as follows.

First, from your home directory in ifdb01,  go to bigdata/ingestion/uproot/nanoaod, or, instead of nanoaod, panda, bacon ecc depending on the type of input file you will be uploading.

```bash
cd $HOME/bigdata/ingestion/uproot/yourFileFormat
```

To create the schema you need uproot version 3.2.13

```bash
pip install uproot==3.2.13
```

And source the scripts

```bash
source setup.sh
```

Now run the following script

```bash
python make_schema.py <file_path> <schema>
```

Where file_path is the absolute path to one of the files from the dataset you want to upload and schema is the name you will give to the created json file.


**Step 2**: create the datasets in the database

Before uploading your files you need to define datasets. Datasets can be defined based on the physics process taken into account for simulation or the primary dataset for data. This step is fairly elastic. As an example, one can define a W+jets dataset and pass the HT/pT bin information as metadata, or generate different datasets based on the HT/pT bin.

To do this run

```bash
python createDataset.py <schema> <bucket name> <dataset name>
```

Schema is the previously created schema json file and dataset name is whatever name you want to give to the dataset, you will be using this name to access the files when running an analysis. 

**Step 3** Uploading

Finally to upload the dataset make sure you are back with uproot 2.8.17

```bash
pip install uproot==2.8.17 
```

And run this script:

```bash
python loadDataset.py  -d <dataset-name> <path to dataset > <top of root tree> <bucket name>
```

Where <path to dataset> is the full path to the directory containing the root files to be uploaded and <top of root tree> is the top directory inside the root file (it is Events in nanoAOD)
