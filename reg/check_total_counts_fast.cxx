#include "TFile.h"
#include "TTree.h"
#include <iostream>
#include <fstream>
#include <string>


using namespace std;
Long64_t total_counts = 0;
int check_total_counts_fast(string inputFile, string output){
	ofstream outputFile(output.c_str());
	std::ifstream input(inputFile.c_str());
	for( std::string line; getline( input, line ); )
		{
		TFile *f = TFile::Open(line.c_str());
		TTree *t3 = (TTree*)f->Get("Events");
		Long64_t nentries = t3->GetEntries();
		outputFile << line << "   " << nentries << endl;
		total_counts = total_counts + nentries;
		delete f;
		}
	outputFile << total_counts << endl;
	return 0;

}



