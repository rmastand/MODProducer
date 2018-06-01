#include <memory>
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <iomanip> 
#include <limits>
#include <cmath>
#include <map>



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
   ofstream statsOutput_;
   string currentProcessingFilename_;
   string outputFilename_;
   string numFilename_;
   string statsFilename_;
   ifstream lumiLumin_;
   string outputDir_;
   
   map<string, int> lumiNumEvents; 
   map<string, float> lumiDelData; 
   map<string, float> lumiRecData; 
   map<string, string> lumiToRun; 
   map<string, string> lumiToLumiB; 
    
};



FilenameMapProducer::FilenameMapProducer(const ParameterSet& iConfig)
: currentProcessingFilename_(iConfig.getParameter<string>("filename")),
  outputFilename_(iConfig.getParameter<string>("outputFile")),
  numFilename_(iConfig.getParameter<string>("numFile")),
  outputDir_(iConfig.getParameter<string>("outputDir"))
{
  fileOutput_.open(outputFilename_.c_str(), std::fstream::out | std::fstream::app);
  
     
  statsFilename_ = outputDir_ + "/" + outputFilename_ + ".stats";
     
     
  
   
  lumiLumin_.open("skimmed.txt");
  int line_number = 1;

  string line;
  while (getline(lumiLumin_, line)) {
      
      istringstream iss(line);
      string lumiId; 
      float lumiDel, lumiRec;
      iss >> lumiId >> lumiDel >> lumiRec;     
      lumiDelData[lumiId]=lumiDel;
      lumiRecData[lumiId]=lumiRec;   
      cout << lumiId << " " << lumiDel << " " << lumiRec << endl;
      line_number++;
   }


     
    
}




FilenameMapProducer::~FilenameMapProducer() {

}

void FilenameMapProducer::produce(Event& iEvent, const EventSetup& iSetup) {
   
   int runNum = iEvent.id().run();
   int eventNum = iEvent.id().event();
   int lumiBlock = iEvent.luminosityBlock();
   counts = counts + 1;  
   fileOutput_ << eventNum << " " << runNum  << " " << currentProcessingFilename_ << endl;
   
   
   lumiToRun[std::to_string(runNum)+"_"+std::to_string(lumiBlock)] = std::to_string(runNum);
   lumiToLumiB[std::to_string(runNum)+"_"+std::to_string(lumiBlock)] = std::to_string(lumiBlock);
   
   // counter for number of events per lumi block
   if (lumiNumEvents.count(std::to_string(runNum)+"_"+std::to_string(lumiBlock)) == 1) {
      ++lumiNumEvents[std::to_string(runNum)+"_"+std::to_string(lumiBlock)];     
      }
   else {
      lumiNumEvents[std::to_string(runNum)+"_"+std::to_string(lumiBlock)] = 1;
      }
   ++totEvents;
   
   if (lumiDelData.count(std::to_string(runNum)+"_"+std::to_string(lumiBlock))==1) {
      ++validEvents;
      intLumiTotDel = intLumiTotDel + lumiDelData[std::to_string(runNum)+"_"+std::to_string(lumiBlock)];
      intLumiTotRec = intLumiTotRec + lumiRecData[std::to_string(runNum)+"_"+std::to_string(lumiBlock)];
   }
   
   
   
   
}

void FilenameMapProducer::beginJob() {

}

void FilenameMapProducer::endJob() {


   statsOutput_.open(statsFilename_.c_str(), ios::out | ios::app );
   statsOutput_ << "BeginFile Version 6 CMS Dataset" << endl;
   statsOutput_ << "#   File                                Filename    TotalEvents    ValidEvents     IntLumiDel     IntLumiRec" << endl;
      
   statsOutput_ << "    File"
	   	<< setw(40) << currentProcessingFilename_
		<< setw(15) << totEvents
	   	<< setw(15) << validEvents
		<< setw(15) << intLumiTotDel
		<< setw(15) << intLumiTotDel
	 	<< endl;   
	
   statsOutput_ << "#LumiBlock         RunNum      Lumi    Events    Valid?     IntLumiDel     IntLumiRec" << endl;
	
   for(std::map<Key,Val>::iterator iter = lumiNumEvents.begin(); iter != lumiNumEvents.end(); ++iter)
            {
            Key k =  iter->first;  
	    if (lumiDelData.count(std::to_string(runNum)+"_"+std::to_string(lumiBlock))==1) {
		        statsOutput_ << " LumiBlock"
	   		   	     << setw(15) << lumiToRun[k]
		                     << setw(10) << lumiToLumi[k]
	   	      		     << setw(10) << lumiNumEvents[k]
		         	     << setw(10) << "1"
		         	     << setw(15) << lumiDelData[k]
				     << setw(15) << lumiRecData[k]
	 	          	     << endl;   
		    
	    }
     		else
		{
			statsOutput_ << " LumiBlock"
	   		   	     << setw(15) << lumiToRun[k]
		                     << setw(10) << lumiToLumi[k]
	   	      		     << setw(10) << lumiNumEvents[k]
		         	     << setw(10) << "0"
		         	     << setw(15) << "0.0"
				     << setw(15) << "0.0"
	 	          	     << endl;   
		}
 
           
            }

 
 	
   numOutput_.open(numFilename_.c_str(), std::fstream::out | std::fstream::app);
   numOutput_ << currentProcessingFilename_ << " " << counts << endl;
   numOutput_.close();
   fileOutput_.close();
   lumiLumin_.close();
   statsOutput_.close();

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
