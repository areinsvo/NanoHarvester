# NanoHarvester (NanoAOD coffeabeans producer)

### Set up CMSSW

```
cmsrel CMSSW_10_2_18
cd CMSSW_10_2_18/src
cmsenv
```

### Get customized NanoAOD producers

```bash
git clone https://github.com/LPC-DM/NanoHarvester.git PhysicsTools/NanoTuples
```

### Compile

```bash
scram b -j12
```
### Get config files

```bash
cd PhysicsTools/NanoTuples/crab
```
This directory contains the config files to use for 2016 to 2018 data and mc NanoAOD production in CMSSW_10_2_18. 
Test one of the config files with the following command:
```bash
cmsRun mc_NANO_2016.py
```

For completeness, the cmsDriver commands used to generate the config files are listed below. You should not need to run these commands yourself. These follow the instructions on https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD#Recipe_for_the_current_HEAD_of_N, https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVDataReprocessingNanoAODv6, and https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVAnalysisSummaryTable.

2016 MC (RunIISummer16):
```bash
cmsDriver.py mc_NANO_2016.py -n -1 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM \
--conditions 102X_mcRun2_asymptotic_v7 --step NANO --era Run2_2016,run2_nanoAOD_94X2016 \
--customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC \
--filein file:step-1.root --fileout file:nano.root \
--no_exec
```

2017 MC (RunIIFall17):
```bash
cmsDriver.py mc_NANO_2017.py -n -1 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM \
--conditions 102X_mc2017_realistic_v7 --step NANO --era Run2_2017,run2_nanoAOD_94XMiniAODv2 \
--customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC \
--filein file:step-1.root --fileout file:nano.root \
--no_exec
```

2018 MC (RunIIAutumn18):
```bash
cmsDriver.py mc_NANO_2018.py -n -1 --mc --eventcontent NANOAODSIM --datatier NANOAODSIM \
--conditions 102X_upgrade2018_realistic_v20 --step NANO --era Run2_2018,run2_nanoAOD_102Xv1  \
--customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeMC \
--filein file:step-1.root --fileout file:nano.root \
--no_exec
```

2016 Data :
```bash
cmsDriver.py data_NANO_2016.py --data --eventcontent NANOAOD --datatier NANOAOD \
--conditions 102X_dataRun2_v12 --step NANO --era Run2_2016,run2_nanoAOD_94X2016 \
--customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData \
--fileout file:nano.root \
--no_exec
```

2017 Data :
```bash
cmsDriver.py data_NANO_2017.py --data --eventcontent NANOAOD --datatier NANOAOD \
--conditions 102X_dataRun2_v12 --step NANO --era Run2_2017,run2_nanoAOD_94XMiniAODv2 \
--customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData \
--fileout file:nano.root \
--no_exec
```

2018 Data Rereco for eras ABC :
```bash
cmsDriver.py data_NANO_2018ABC.py --data --eventcontent NANOAOD --datatier NANOAOD \
--conditions 102X_dataRun2_v12 --step NANO --era Run2_2018,run2_nanoAOD_102Xv1 \
--customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData \
--fileout file:nano.root \
--no_exec
```

2018 Data Prompt Reco for era D :
```bash
cmsDriver.py data_NANO_2018D --data --eventcontent NANOAOD --datatier NANOAOD \
--conditions 102X_dataRun2_Prompt_v15 --step NANO --era Run2_2018,run2_nanoAOD_102Xv1 \
--customise PhysicsTools/NanoTuples/nanoTuples_cff.nanoTuples_customizeData \
--fileout file:nano.root \ 
--no_exec
```

### Production

**Step 0**: switch to the crab production directory and set up grid proxy, CRAB environment, etc.

```bash
cd $CMSSW_BASE/src/PhysicsTools/NanoTuples/crab
cmsenv
# set up grid proxy
voms-proxy-init -rfc -voms cms --valid 168:00
# set up CRAB env (must be done after cmsenv)
source /cvmfs/cms.cern.ch/crab3/crab.sh
```

**Step 1**: Choose the right python config file. This is the -p argument to crab.py. (See section above for how the configs were generated). Note that you need a different config file for Run2018ABC vs Run2018D. The eras for 2018 are also separated into two input text files with the dataset names.

**Step 2**: use the `crab.py` script to submit the CRAB jobs. Replace [year] with the appropriate value

For MC:

```bash
python crab.py -p mc_NANO_[year].py -o /store/group/lpccoffea/coffeabeans/NanoAODv6/nano_[year] -t NanoTuples-[year] -i miniaod[year].txt  --send-external -s EventAwareLumiBased -n 50000 --work-area crab_projects_mc_[year] --dryrun
```

For data:

```bash
python crab.py -p data_NANO_[year][era if using 2018].py -o /store/group/lpccoffea/coffeabeans/NanoAODv6/nano_[year] -t NanoTuples-[year] -i miniaod[year][era if using 2018]_data.txt --send-external -s EventAwareLumiBased -n 50000 --work-area crab_projects_data_[year] -j [jsonfilename] --dryrun
```

A JSON file can be applied for data samples with the `-j` options. Make sure to apply the appropriate golden JSON based on year. These can be found in the /files folder:
For 2016:
```
https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt
```
For 2017:
```
https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt
```
For 2018:
```bash
https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions18/13TeV/ReReco/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt
```

For updated information, check: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVAnalysisSummaryTable

These command will perform a "dryrun" to print out the CRAB configuration files. Please check everything is correct (e.g., the output path, version number, requested number of cores, etc.) before submitting the actual jobs. To actually submit the jobs to CRAB, just remove the `--dryrun` option at the end.

**Step 3**: check job status

The status of the CRAB jobs can be checked with:

```bash
./crab.py --status --work-area crab_projects_[mc/data]_[year]
```

Note that this will also resubmit failed jobs automatically.

The crab dashboard can also be used to get a quick overview of the job status:
`https://dashb-cms-job.cern.ch/dashboard/templates/task-analysis`

More options of this `crab.py` script can be found with:

```bash
./crab.py -h
```


