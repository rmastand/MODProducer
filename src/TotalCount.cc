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

int tcounts = 0;

class TotalCount : public EDProducer 
{
public: 
   explicit TotalCount(const ParameterSet&);
   ~TotalCount();
private:
   virtual void beginJob();
   virtual void produce(edm::Event&, const edm::EventSetup&);
   virtual void endJob() ;
   virtual void beginRun(edm::Run&, edm::EventSetup const&);
   virtual void endRun(edm::Run&, edm::EventSetup const&);
   virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
   virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
   
   ofstream numOutput_;
   string currentProcessingFilename_;
   string numFilename_;
    
};



TotalCount::TotalCount(const ParameterSet& iConfig)
: currentProcessingFilename_(iConfig.getParameter<string>("filename")),
  numFilename_(iConfig.getParameter<string>("numFile"))
{
}




TotalCount::~TotalCount() {

}

void TotalCount::produce(Event& iEvent, const EventSetup& iSetup) {
   
   tcounts = tcounts + 1;  
}

void TotalCount::beginJob() {

}

void TotalCount::endJob() {
 	
   numOutput_.open(numFilename_.c_str(), std::fstream::out | std::fstream::app);	
   numOutput_ << currentProcessingFilename_ << " " << tcounts << endl;
   numOutput_.close();
}

void TotalCount::beginRun(edm::Run & iRun, edm::EventSetup const & iSetup){

}

void TotalCount::endRun(edm::Run&, edm::EventSetup const&) {
}

void TotalCount::beginLuminosityBlock(edm::LuminosityBlock& iLumi, edm::EventSetup const& iSetup) {

}

void TotalCount::endLuminosityBlock(edm::LuminosityBlock& iLumi, edm::EventSetup const& iSetup) {

}


DEFINE_FWK_MODULE(TotalCount);
