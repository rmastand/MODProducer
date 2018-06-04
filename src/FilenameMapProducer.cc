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
   ofstream statsOutput_;
   string currentProcessingFilename_;
   string outputFilename_;
   string statsFilename_;
   ifstream lumiLumin_;
   string outputLsFile_;
   string outputDir_;
   string dataType_;
   string version_;
   string triggerCat_;
   string dataYear_;
   
   
   map<string, int> lumiNumEvents; 
   map<string, float> lumiDelData; 
   map<string, float> lumiRecData; 
   map<string, string> lumiToRun; 
   map<string, string> lumiToLumiB; 
    
};



FilenameMapProducer::FilenameMapProducer(const ParameterSet& iConfig)
: currentProcessingFilename_(iConfig.getParameter<string>("filename")),
  outputFilename_(iConfig.getParameter<string>("outputFile")),
  outputLsFile_(iConfig.getParameter<string>("outputLsFile")),
  outputDir_(iConfig.getParameter<string>("outputDir")),
  dataType_(iConfig.getParameter<string>("dataType")),
  version_(iConfig.getParameter<string>("version")),
  triggerCat_(iConfig.getParameter<string>("triggerCat")),
  dataYear_(iConfig.getParameter<string>("dataYear"))
  
  
  
{
  fileOutput_.open(outputFilename_.c_str(), std::fstream::out | std::fstream::app);
  
     
  statsFilename_ = outputDir_ + "/" + currentProcessingFilename_.substr(0,currentProcessingFilename_.length()-5) + ".stats";

     
   
  lumiLumin_.open(outputLsFile_.c_str());
  int line_number = 1;

  string line;
  while (getline(lumiLumin_, line)) {
      
      istringstream iss(line);
      string lumiId; 
      float lumiDel, lumiRec;
      iss >> lumiId >> lumiDel >> lumiRec;     
      lumiDelData[lumiId]=lumiDel;
      lumiRecData[lumiId]=lumiRec;   
      
      line_number++;
   }


     
    
}




FilenameMapProducer::~FilenameMapProducer() {

}

void FilenameMapProducer::produce(Event& iEvent, const EventSetup& iSetup) {
   
   int runNum = iEvent.id().run();
   int eventNum = iEvent.id().event();
   int lumiBlock = iEvent.luminosityBlock();

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
	
   statsOutput_ << "BeginFile Version " << version_ << " CMS_" << dataYear_ << " " << dataType_ << " " << triggerCat_ << endl;
   


   
   statsOutput_ << "#   File                                Filename    TotalEvents    ValidEvents          IntLumiDel          IntLumiRec" << endl;
      
   statsOutput_ <<fixed<< "    File"
	   	<< setw(40) << currentProcessingFilename_.substr(0,currentProcessingFilename_.length()-5)
		<< setw(15) << totEvents
	   	<< setw(15) << validEvents
		<< setw(20) <<fixed<< std::setprecision(3)<< intLumiTotDel
		<< setw(20) <<fixed<< std::setprecision(3)<< intLumiTotRec
	 	<< endl;   
	
   statsOutput_ << "#LumiBlock         RunNum      Lumi    Events    Valid?     IntLumiDel     IntLumiRec" << endl;
	
   std::map<std::string, int>::iterator it = lumiNumEvents.begin();
   while (it != lumiNumEvents.end())
  
            {
            string k =  it->first;  
	    cout.setf(0, ios::floatfield);
	    if (lumiDelData.count(k)==1) {
		        statsOutput_ <<default<<" LumiBlock"
	   		   	     << setw(15) << lumiToRun[k]
		                     << setw(10) << lumiToLumiB[k]
	   	      		     << setw(10) << lumiNumEvents[k]
		         	     << setw(10) << "1"
		         	     << setw(15) << lumiDelData[k]
				     << setw(15) << lumiRecData[k]
	 	          	     << endl;   
		    
	    }
     		else
		{
			statsOutput_ <<default<< " LumiBlock"
	   		   	     << setw(15) << lumiToRun[k]
		                     << setw(10) << lumiToLumiB[k]
	   	      		     << setw(10) << lumiNumEvents[k]
		         	     << setw(10) << "0"
		         	     << setw(15) << "0.000"
				     << setw(15) << "0.000"
	 	          	     << endl;   
		}
	      ++it;
 
           
            }

 
 	
   statsOutput_ << "EndFile" << endl;
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
