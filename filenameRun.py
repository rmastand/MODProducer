import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import FWCore.PythonUtilities.LumiList as LumiList
import sys

data_file_link = sys.argv[2]
registry_file_path = sys.argv[3]

file_name = data_file_link[len(data_file_link) - 41:len(data_file_link)]

process = cms.Process("FilenameMapProducer")

process.load("FWCore.MessageLogger.MessageLogger_cfi")

print "Running filenameRun.py on ", file_name

process.source = cms.Source ("PoolSource", fileNames=cms.untracked.vstring( data_file_link ) )
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))


goodJSON = "file_paths/Cert_136033-149442_7TeV_Apr21ReReco_Collisions10_JSON_v2.txt"
myLumis = LumiList.LumiList(filename = goodJSON).getCMSSWString().split(',')
process.source.lumisToProcess = cms.untracked.VLuminosityBlockRange()
process.source.lumisToProcess.extend(myLumis)

process.FilenameMapProducer = cms.EDProducer("FilenameMapProducer", 
						filename = cms.string(file_name), 
						outputFile = cms.string(registry_file_path) 
						)

process.MessageLogger = cms.Service("MessageLogger",
        				default   =  cms.untracked.PSet(
                                                     timespan = cms.untracked.int32(60)
       )                                                  
)       
						
process.producer = cms.Path(process.FilenameMapProducer)
process.schedule = cms.Schedule( process.producer )
