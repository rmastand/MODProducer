import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import FWCore.PythonUtilities.LumiList as LumiList
import sys

data_file_link = sys.argv[2]
path_to_total_counts = sys.argv[3]

file_name = data_file_link[len(data_file_link) - 41:len(data_file_link)]

process = cms.Process("TotalCount")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

print "Running filenameRun.py on ", file_name

process.source = cms.Source ("PoolSource", fileNames=cms.untracked.vstring( data_file_link ) )
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

process.TotalCount = cms.EDProducer("TotalCount", 
						filename = cms.string(file_name), 
						numFile = cms.string(path_to_total_counts) 
		       				)

process.MessageLogger = cms.Service("MessageLogger",
        				default   =  cms.untracked.PSet(
                                                     timespan = cms.untracked.int32(60)
       )                                                  
)       
						
process.producer = cms.Path(process.TotalCount)
process.schedule = cms.Schedule( process.producer )
