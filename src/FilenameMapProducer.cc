#include <memory>
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <iomanip> 
#include <limits>
#include <cmath>

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"




using namespace std;
using namespace edm;

int counts = 0;
int totEvents = 0;
int validEvents = 0;
float intLumiTotDel = 0.;
float intLumiTotRec = 0.;

class FilenameMapProducer : public EDProducer 
{
public: 
   explicit FilenameMapProducer(const ParameterSet&);
   ~FilenameMapProducer();
private:
   virtual void beginJob();
   virtual void produce(edm::Event&, const edm::EventSetup&);
   virtual void endJob() ;
   virtual void beginRun(edm::Run&, edm::EventSetup const&);
   virtual void endRun(edm::Run&, edm::EventSetup const&);
   virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
   virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
   
   ofstream fileOutput_;
   ofstream numOutput_;
   string currentProcessingFilename_;
   string outputFilename_;
   string numFilename_;
   string statsFilename_;
   ifstream lumiLumin_;
   string outputDir_;
    
};



FilenameMapProducer::FilenameMapProducer(const ParameterSet& iConfig)
: currentProcessingFilename_(iConfig.getParameter<string>("filename")),
  outputFilename_(iConfig.getParameter<string>("outputFile")),
  numFilename_(iConfig.getParameter<string>("numFile")),
  outputDir_(iConfig.getParameter<string>("outputDir"))
{
  fileOutput_.open(outputFilename_.c_str(), std::fstream::out | std::fstream::app);
  lumiLumin_.open("skimmed.txt");
     
  statsFilename_ = outputDir_ + "/" + outputFilename_ + ".stats";

     
    
}




FilenameMapProducer::~FilenameMapProducer() {

}

void FilenameMapProducer::produce(Event& iEvent, const EventSetup& iSetup) {
   
   int runNum = iEvent.id().run();
   int eventNum = iEvent.id().event();
   counts = counts + 1;  
   fileOutput_ << eventNum << " " << runNum  << " " << currentProcessingFilename_ << endl;
}

void FilenameMapProducer::beginJob() {

}

void FilenameMapProducer::endJob() {
 	
   numOutput_.open(numFilename_.c_str(), std::fstream::out | std::fstream::app);
   numOutput_ << currentProcessingFilename_ << " " << counts << endl;
   numOutput_.close();
   fileOutput_.close();
   lumiLumin_.close();

}

void FilenameMapProducer::beginRun(edm::Run & iRun, edm::EventSetup const & iSetup){

}

void FilenameMapProducer::endRun(edm::Run&, edm::EventSetup const&) {
}

void FilenameMapProducer::beginLuminosityBlock(edm::LuminosityBlock& iLumi, edm::EventSetup const& iSetup) {

}

void FilenameMapProducer::endLuminosityBlock(edm::LuminosityBlock& iLumi, edm::EventSetup const& iSetup) {

}


DEFINE_FWK_MODULE(FilenameMapProducer);
