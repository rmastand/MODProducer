import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import FWCore.PythonUtilities.LumiList as LumiList
import sys

data_file_link = sys.argv[2]
registry_file_path = sys.argv[3]
path_to_counts = sys.argv[4]
data_type = sys.argv[5]
data_year = sys.argv[6]

file_name = data_file_link[len(data_file_link) - 41:len(data_file_link)]

process = cms.Process("FilenameMapProducer")

process.load("FWCore.MessageLogger.MessageLogger_cfi")

print "Running filenameRun.py on ", file_name
process.source = cms.Source ("PoolSource", fileNames=cms.untracked.vstring( data_file_link ) )
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

if (data_type == "real") and (data_year == "2010"):
	goodJSON = "data/Cert_136033-149442_7TeV_Apr21ReReco_Collisions10_JSON_v2.txt"
	myLumis = LumiList.LumiList(filename = goodJSON).getCMSSWString().split(',')
	process.source.lumisToProcess = cms.untracked.VLuminosityBlockRange()
	process.source.lumisToProcess.extend(myLumis)

if (data_type == "real") and (data_year == "2011"):
	goodJSON = "data/Cert_160404-180252_7TeV_ReRecoNov08_Collisions11_JSON.txt"
	myLumis = LumiList.LumiList(filename = goodJSON).getCMSSWString().split(',')
	process.source.lumisToProcess = cms.untracked.VLuminosityBlockRange()
	process.source.lumisToProcess.extend(myLumis)

if (data_type == "sim") and (data_year == "2011"):
	pass
	

process.FilenameMapProducer = cms.EDProducer("FilenameMapProducer", 
						filename = cms.string(file_name), 
						outputFile = cms.string(registry_file_path),
					        numFile = cms.string(path_to_counts)
						)

process.MessageLogger = cms.Service("MessageLogger",
        				default   =  cms.untracked.PSet(
                                                     timespan = cms.untracked.int32(60)
       )                                                  
)       
						
process.producer = cms.Path(process.FilenameMapProducer)
process.schedule = cms.Schedule( process.producer )
