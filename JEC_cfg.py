import FWCore.ParameterSet.Config as cms

process = cms.Process("myprocess")

process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

# UNCOMMENT for 2011 data
#process.GlobalTag.connect = cms.string('sqlite_file:/cvmfs/cms-opendata-conddb.cern.ch/FT_53_LV5_AN1_RUNA.db')
# UNCOMMENT FOR 2011 SIM DATA
#process.GlobalTag.connect = cms.string('sqlite_file:/cvmfs/cms-opendata-conddb.cern.ch/START53_LV6A1.db')

# for 2010 data
process.GlobalTag.globaltag = 'GR_R_42_V25::All'

process.maxEvents = cms.untracked.PSet(
        input = cms.untracked.int32(1)
        )

process.source = cms.Source("EmptySource")

process.ak5 = cms.EDAnalyzer('JetCorrectorDBReader', 
        payloadName    = cms.untracked.string('AK5PF'),
	globalTag      = cms.untracked.string('GR_R_42_V25'),  
        printScreen    = cms.untracked.bool(False),
        createTextFile = cms.untracked.bool(True)
)


process.p = cms.Path(process.ak5)
