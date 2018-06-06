#include <memory>
#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <iomanip> 
#include <limits>
#include <cmath>
#include <map>
#include <algorithm>



#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "SimDataFormats/GeneratorProducts/interface/GenRunInfoProduct.h"
#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"
#include "FWCore/Utilities/interface/Exception.h"

#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
#include "HLTrigger/HLTcore/interface/HLTConfigData.h"




using namespace std;
using namespace edm;

HLTConfigProvider hltConfig_;
InputTag hltInputTag_;
int totEvents = 0;
int validEvents = 0;
long double intLumiTotDel = 0.;
long double intLumiTotRec = 0.;
list<string> usedLumis;
double crossSection;

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
   map<string, long double> lumiDelData; 
   map<string, long double> lumiRecData; 
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

     
  if (dataType_ == "Data") 
      {
	  lumiLumin_.open(outputLsFile_.c_str());
	  int line_number = 1;

	  string line;
	  while (getline(lumiLumin_, line)) {

	      istringstream iss(line);
	      string lumiId; 
	      long double lumiDel, lumiRec;

	      iss >> lumiId >> lumiDel >> lumiRec;     
	      lumiDelData[lumiId]=lumiDel;
	      lumiRecData[lumiId]=lumiRec;   


	      line_number++;
  }
   }


     
    
}




FilenameMapProducer::~FilenameMapProducer() {

}

void FilenameMapProducer::produce(Event& iEvent, const EventSetup& iSetup) {
   
   int runNum = iEvent.id().run();
   int eventNum = iEvent.id().event();
   int lumiBlock = iEvent.luminosityBlock();

   // registry file output
   fileOutput_ << eventNum << " " << runNum  << " " << currentProcessingFilename_ << endl;
   
   // easy map between lumi id to lumi run, lumi block
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
   
   // on the real data: checks for valid events, keeps counter of integrated luminosity
   if (dataType_ == "Data"){
	   if (lumiDelData.count(std::to_string(runNum)+"_"+std::to_string(lumiBlock))==1) {
	      ++validEvents;

	      if (std::find(std::begin(usedLumis), std::end(usedLumis), std::to_string(runNum)+"_"+std::to_string(lumiBlock)) != std::end(usedLumis))
	      {
		// my_list has my_var

	      }
		   else {
			   usedLumis.push_front(std::to_string(runNum)+"_"+std::to_string(lumiBlock));
			   intLumiTotDel = intLumiTotDel + lumiDelData[std::to_string(runNum)+"_"+std::to_string(lumiBlock)];
			   intLumiTotRec = intLumiTotRec + lumiRecData[std::to_string(runNum)+"_"+std::to_string(lumiBlock)];
		   }
	   }

   }
   

   
   
   
   
}

void FilenameMapProducer::beginJob() {

}

void FilenameMapProducer::endJob() {


   statsOutput_.open(statsFilename_.c_str(), ios::out | ios::app );
	
   statsOutput_ << "BeginFile Version " << version_ << " CMS_" << dataYear_ << " " << dataType_ << " " << triggerCat_ << endl;
   


   if (dataType_ == "Data") {
	   
	   statsOutput_ << "#   File                                Filename    TotalEvents    ValidEvents          IntLumiDel          IntLumiRec" << endl;
   string LumiTotDel = std::to_string(intLumiTotDel);
   LumiTotDel.erase(LumiTotDel.find_last_not_of("0")+1,std::string::npos);
   string LumiTotRec = std::to_string(intLumiTotRec);
   LumiTotRec.erase(LumiTotRec.find_last_not_of("0")+1,std::string::npos);
   statsOutput_ <<fixed<< "    File"
	   	<< setw(40) << currentProcessingFilename_.substr(0,currentProcessingFilename_.length()-5)
		<< setw(15) << totEvents
	   	<< setw(15) << validEvents
		<< setw(20) << LumiTotDel 
		<< setw(20) << LumiTotRec
	 	<< endl;   
	   
	   
	   
   }
	
   if (dataType_ == "Sim") {
	   
	   statsOutput_ << "#   File                                Filename    TotalEvents    ValidEvents        CrossSection" << endl;
   
	   statsOutput_ <<fixed<< "    File"
			<< setw(40) << currentProcessingFilename_.substr(0,currentProcessingFilename_.length()-5)
			<< setw(15) << totEvents
			<< setw(15) << validEvents
			<< setw(20) << crossSection 
			<< endl;   
	   
	   
	   
   }
   
   if (dataType_ == "Data") {
	   
	   statsOutput_ << "#LumiBlock         RunNum      Lumi    Events    Valid?     IntLumiDel     IntLumiRec" << endl;
	
   std::map<std::string, int>::iterator it = lumiNumEvents.begin();
   while (it != lumiNumEvents.end())
  
            {
            string k =  it->first;  
	   
	    
	    if (lumiDelData.count(k)==1) {
		        string LumiDel = std::to_string(lumiDelData[k]);
   	    		LumiDel.erase(LumiDel.find_last_not_of("0")+1,std::string::npos);
   	    		string LumiRec = std::to_string(lumiRecData[k]);
   	    		LumiRec.erase(LumiRec.find_last_not_of("0")+1,std::string::npos);
	
		        statsOutput_ <<" LumiBlock"
	   		   	     << setw(15) << lumiToRun[k]
		                     << setw(10) << lumiToLumiB[k]
	   	      		     << setw(10) << lumiNumEvents[k]
		         	     << setw(10) << "1"
		         	     << setw(15) << LumiDel
				     << setw(15) << LumiRec
	 	          	     << endl;   
		    
	    }
     		else
		{
			statsOutput_ << " LumiBlock"
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
	   
	   
   }
	
	
      if (dataType_ == "Sim") {
	   
	   statsOutput_ << "#LumiBlock         RunNum      Lumi    Events    Valid?        CrossSection" << endl;
	
   std::map<std::string, int>::iterator it = lumiNumEvents.begin();
   while (it != lumiNumEvents.end())
  
            {
            string k =  it->first;  
	   
	    
	   
		statsOutput_ <<" LumiBlock"
			     << setw(15) << lumiToRun[k]
			     << setw(10) << lumiToLumiB[k]
			     << setw(10) << lumiNumEvents[k]
			     << setw(10) << "-1"
			     << setw(20) << crossSection
			     << endl;   
		    
	   
     		
	      ++it;
 
           
            }
	   
	   
   }
	
   

 
 	
   statsOutput_ << "EndFile" << endl;
   fileOutput_.close();
   lumiLumin_.close();
   statsOutput_.close();

}

void FilenameMapProducer::beginRun(edm::Run & iRun, edm::EventSetup const & iSetup){
	
	bool changed = true;
   if ( hltConfig_.init(iRun, iSetup, hltInputTag_.process(), changed) ) {
      // if init returns TRUE, initialisation has succeeded!
      
 	if (dataType_=="Sim") {
        edm::Handle<GenRunInfoProduct> genRunInfo;
        iRun.getByLabel("generator", genRunInfo );


        crossSection = genRunInfo->crossSection();

	}
   }


}

void FilenameMapProducer::endRun(edm::Run&, edm::EventSetup const&) {
}

void FilenameMapProducer::beginLuminosityBlock(edm::LuminosityBlock& iLumi, edm::EventSetup const& iSetup) {

}

void FilenameMapProducer::endLuminosityBlock(edm::LuminosityBlock& iLumi, edm::EventSetup const& iSetup) {

}


DEFINE_FWK_MODULE(FilenameMapProducer);
