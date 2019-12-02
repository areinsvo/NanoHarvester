from WMCore.Configuration import Configuration
config = Configuration()
config.section_('General')
config.General.transferLogs = False
config.General.transferOutputs = True
config.General.workArea = 'crab_projects_test'
config.General.requestName = 'dryrun_test'
config.section_('JobType')
config.JobType.psetName = 'data_NANO_2017.py'
config.JobType.pluginName = 'Analysis'
config.JobType.numCores = 1
config.JobType.sendExternalFolder = True
config.JobType.maxMemoryMB = 2500
config.JobType.allowUndistributedCMSSW = True
config.section_('Data')
config.Data.inputDataset = '/MET/Run2017E-31Mar2018-v1/MINIAOD'
#config.Data.inputDataset = '/ZJetsToNuNu_HT-100To200_13TeV-madgraph/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM'
config.Data.outputDatasetTag = 'test'
config.Data.unitsPerJob = 25000
config.Data.inputDBS = 'global'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.allowNonValidInputDataset = True
config.Data.outLFNDirBase = '/store/group/lpccoffea/coffeabeans/NanoAODv6/test'
config.section_('Site')
config.Site.storageSite = 'T3_US_FNALLPC'
config.section_('User')
config.section_('Debug')
