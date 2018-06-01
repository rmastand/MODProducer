import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import FWCore.PythonUtilities.LumiList as LumiList
import sys

data_file_link = sys.argv[2]
registry_file_path = sys.argv[3]
output_dir = sys.argv[4]
output_ls_file = sys.argv[5]
data_type = sys.argv[6]
data_year = sys.argv[7]

file_name = data_file_link[len(data_file_link) - 41:len(data_file_link)]


process = cms.Process("FilenameMapProducer")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

print "Running filenameRun.py on ", file_name
process.source = cms.Source ("PoolSource", fileNames=cms.untracked.vstring( data_file_link ) )
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

if (data_type == "Data") and (data_year == "2010B"):
	#goodJSON = "data/Cert_136033-149442_7TeV_Apr21ReReco_Collisions10_JSON_v2.txt"
	#myLumis = LumiList.LumiList(filename = goodJSON).getCMSSWString().split(',')
	#process.source.lumisToProcess = cms.untracked.VLuminosityBlockRange()
	#process.source.lumisToProcess.extend(myLumis)
	pass

if (data_type == "Data") and (data_year == "2011A"):
	#goodJSON = "data/Cert_160404-180252_7TeV_ReRecoNov08_Collisions11_JSON.txt"
	#myLumis = LumiList.LumiList(filename = goodJSON).getCMSSWString().split(',')
	#process.source.lumisToProcess = cms.untracked.VLuminosityBlockRange()
	#process.source.lumisToProcess.extend(myLumis)
	pass

if (data_type == "Sim") and (data_year == "2011"):
	pass
	


process.FilenameMapProducer = cms.EDProducer("FilenameMapProducer", 
						filename = cms.string(file_name), 
						outputFile = cms.string(registry_file_path),
						outputLsFile = cms.string(output_ls_file),
					     	outputDir = cms.string(output_dir),
					        dataType = cms.string(data_type),
					        dataYear = cms.string(data_year)			     
						)

#process.MessageLogger = cms.Service("MessageLogger",
#        				default   =  cms.untracked.PSet(
#                                                     timespan = cms.untracked.int32(60)
#       )                                                  
#)       
						
process.producer = cms.Path(process.FilenameMapProducer)
process.schedule = cms.Schedule( process.producer )
