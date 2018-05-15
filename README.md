# MIT Open Data Producer

This package downloads AOD files from the [CERN Open Data Portal](http://opendata.cern.ch "CERN Open Data Portal") release and converts them into a human-readable file format called MOD (MIT Open Data). Currently, the following information are stored:
	
- 4-momentum and pdgId for PF Candidates.
- 4-momentum, Jet Area and Jet Energy Correction factors for AK5 Jets. These are stored for redundancy and validation of the jets clustered from the stored PF Candidates.
- Trigger Names, prescale values and whether or not that trigger fired for each event. 
- Run Number and Event Number.
- Luminosity Block, Average Instantaneous Luminosity and Number of Primary Vertices.


## Usage Instruction

All of the code relating to this GitHub should be run inside of a Cern Virtual Machine, which can be found [here](http://opendata.cern.ch/VM/CMS/2011 "CERN Open Data Portal"). If analyzing 2010 data, use the CMS 2010 VM; if analyzing 2011 or simulated data, use the CMS 2011 VM.

Within a terminal on the VM:

### Preparation

This section is for 2011 and simulated data. If analyzing 2010 data, replace all instances of ```CMSSW_5_3_32``` with ```CMSSW_4_2_8```.

- Create a CMSSW environment: 

    ```
    cmsrel CMSSW_5_3_32
    ```

- Change to the CMSSW_5_3_32/src/ directory:

    ```
    cd CMSSW_5_3_32/src/
    ```

- Initialize the CMSSW environment:

  ```
  cmsenv
  ```
- Clone the source code:

  ```
  git clone git://github.com/rmastand/MODProducer.git CMSOpenData/MODProducer
  ```

- Go to the source directory:

  ```
  cd CMSOpenData/MODProducer
  ```
  
- Switch branches:

  ```
  git checkout compile
  ```
- Compile everything:

  ```
  scram b
  ```
  
- Prepare a directory:

  ```
  mkdir -p ~/MITOpenDataProject
  ```
  


### Workflow

We adopt the following workflow for extracting MOD files out of the given AOD files.

1.  Download all the ROOT files into the VM environment and arrange them in the same directory structure as they live on the CMS server.

2. Create a registry that maps each event and run number to a certain ROOT file. This is done so that analysis can be performed on one file at a time (the alternative is performaning the analysis on multiple TeraBytes of data at one time, which could take several weeks). 

3. Run the Producer on those AOD files. This reads the download directory and processes only the files in there, as well as [validates](http://opendata.cern.ch/record/1000) the data. This produces N MOD files. 

4. Filter those N MOD files to get only those files for which the correct trigger fired. This process is called Skimming in this workflow. This will produce M <= N MOD files. For a certain AOD file, if none of the events in there have the correct trigger fired, a corresponding skimmed MOD file will not be written. That's why M might be less than N.

5. Read in those "skimmed" M <= N output files one by one and calculate stuff to produce a single DAT file. 

6. Produce plots using the DAT file produced in step (5).

Note that this repository is concerned with steps (1) to (3) only. Steps (4) to (6) are carried out by the [MODAnalyzer](https://github.com/tripatheea/MODAnalyzer/ "MODAnalyzer") package.

## Workflow Instructions

- The first step is to download ROOT files from the CMS server. You can start the download process using the Python script `download.py`. This script takes two arguments:
	
    1. a path to a file which contains a list of links to ROOT files to download from the CERN server (one link per line). You will probably need to manually create this and place it in the ```file_paths``` folder. There are many examples in ```file_paths/samples```; the number at the end of each sample is the record number and going to http://opendata.cern.ch/record/# will tell you what year this dataset is from. This example will use a 2011 sample: ```Jet_21.txt```.  
    2. a destination path to write the files to. Note that the ROOT files are each ~1 GB, so make sure that the destination has enough storage to hold all of the files you're trying to download. 

    ```
    python download.py ./file_paths/samples/Jet_21.txt ~/MITOpenDataProject/
    ```
    The download script will skip any ROOT file that you have already downloaded and will resume any broken downloads. So you don't have to download all the files at once as long as you are downloading all of them to the same directory. Note that each file may take 5-10 minutes to download, depending on the quality of your internet connection.
    
    ** Note: you may skip this step if desired and access all the root files from online. This will save lots of hard drive space, as these root files are huge and there are lots of them.**

### Create the registry

Once you've downloaded the AOD files (these are ROOT files), you need to create what's called a "registry". A registry creates a map between event and run number, and the corresponding ROOT file. The registry creator is just an [EDProducer](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookEDMTutorialProducer "EDProducer") that you run N times for N files, each time simply recording which events and runs are there in a certain ROOT file, in a human readable format. Because this is an [EDProducer](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookEDMTutorialProducer "EDProducer"), you need to initialize CMSSW environment variables first with `cmsenv`. You then create the registry using the Python script ```create_registry.py```. This script takes three arguments: 
	
   1. a path to the ROOT files that you want to process. Note that this is the same as the second argument in the previous command. 
   2. a path to the registry file.
   3. a path to a text file that will count the number of validated events.
   6. data type, Data or Sim
   7. data year, 2010B, 2011A, or 2011

   ```
   cmsenv
   ```
   If you downloaded the root files beforehand, use:
   ```
   python ./reg/create_registry.py ~/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/AOD/12Oct2013-v1/20000/ ~/MITOpenDataProject/registry.txt ~/MITOpenDataProject/valid_events.txt Data 2011A
   ```
   Or, use:
   ```
   python ./reg/create_registry_online.py ./file_paths/samples/Jet_21.txt ~/MITOpenDataProject/registry.txt  ~/MITOpenDataProject/valid_events.txt Data 2011A
   ```
   
### (Optional) Count the total number of events 

You may want to run this step as a cross check to ensure that your VM can actually access all of the events that CERN cites to be in the dataset.
   
   In the virtual machine environment, type ```root```. Then in the root environment, type:
   ```
   .x reg/check_total_counts_fast.cxx("file_paths/samples/Jet_21.txt","Jet21counts.txt")
   ```    
   Replace the arguments of the function as necessary. Note that running this script will initially produce a lot of warnings; you can ignore them all.
   
   When the script stops running, exit the root environment and type:
   ```
   tail -1 Jet21counts.txt
   ```
   The number you see should be the number of events in the ```Jet11/100000.txt``` file.
   

   

### Convert CERN AOD files to MOD files

Now that you have created a registry for all the AOD files that you want to process, you are ready to run another [EDProducer](https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookEDMTutorialProducer "EDProducer") called PFCandidateProducer to convert them into MOD (MIT Open Data) files. You can run PFCandidateProducer with the Python script `PFCandidateRun.py`. This script takes three arguments: 

   1. input directory (path to the directory which contains all the AOD files). This is the same as the second argument that you supplied in the previous step.
   2. output directory (path to the directory where you'd like to store all the MOD files). If this directory is not already present, it will create the directory.
   3. path to the registry file, including the filename. 
   4. The trigger category you want to use (Jet, Photon, Mu, etc)
   5. path to the JEC triggers, starting within the "data" folder. i.e. FT_53/FT_53_LV5_AN1, GR_R/GR_R_42_V25_AK5PF, S53/START53_LV6A1
   6. data type, Data or Sim
   7. data year, 2010B, 2011A, or 2011
   8. whether to process from the beginning or not (1 or 0). If set to 1, the Producer will start AOD->MOD conversion from the first file in the registry. However, because it's desirable to break this step into multiple instances, you can run the producer once, quit it and come back later to resume it. So if set to 0, the producer will skip the files already in the MOD output directory and resume from there. Note that, the smallest discrete interval that the producer can detect is one ROOT (or MOD) file. So if you interrupted the producer while it's running, make sure you remove that particular MOD file from the output directory because else, the producer will skip that the next time even though < 100% events of that file are done.
   
 
   As mentioned earlier, the "download" step above maintains the directory structure of CMS servers. This includes a directory named "AOD". 

   Note that to get trigger prescales, PFCandidateProducer needs to load GlobalTags and so, it takes a long time before anything happens (it takes ~10 minutes on my computer).
   
   
#### Check that you have the correct global tags 

If using 2010 data, no extra steps are needed.

If using 2011 data, first set up the symbolic links to properly access the 2011 global tags.
   ```
   ln -sf /cvmfs/cms-opendata-conddb.cern.ch/FT_53_LV5_AN1_RUNA FT_53_LV5_AN1
   ln -sf /cvmfs/cms-opendata-conddb.cern.ch/FT_53_LV5_AN1_RUNA.db FT_53_LV5_AN1_RUNA.db
   ```
   
   Check that the cms-opendata-conddb.cern.ch directory has actually expanded in the VM. 
   ```
   ls -l
   ls -l /cvmfs/
   ```
   
If using simulated data, the opendata page for that record will tell you which global tag to use. Set up the symbolic links as before:

  ```
  ln -sf /cvmfs/cms-opendata-conddb.cern.ch/START53_LV6A1 START53_LV6A1
  ln -sf /cvmfs/cms-opendata-conddb.cern.ch/START53_LV6A1.db START53_LV6A1.db
   ```

  
  
#### Check that you have the correct Jet energy correction factors (for Jet analysis)

If using 2010 or 2011 (real or simulated) data, all these corrections are in the ```data/JEC``` folder and are properly implemented in the EDProducer source files. Otherwise, see the "Notes about JEC" section before proceding.


  Now analyze the files! If you've downloaded all the AOD files, run:
    
    
   ```
   cmsRun ./analysis/PFCandidateRun.py ~/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/AOD/12Oct2013-v1/20000/ ~/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000/ ~/MITOpenDataProject/registry.txt Jet FT_53/FT_53_LV5_AN1 Data 2011A 1
   ```
   Or, use:
   ```
   cmsRun ./analysis/PFCandidateRun_online.py file_paths/samples/Jet_21.txt ~/MITOpenDataProject/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000/ ~/MITOpenDataProject/registry.txt Jet FT_53/FT_53_LV5_AN1 Data 2011A 1
   ```
   
   Or for simulated data, use:
   ```
   cmsRun ./analysis/PFCandidateRun_online.py file_paths/samples/sim_1369.txt ~/MITOpenDataProject/eos/opendata/cms/MonteCarlo2011/Summer11LegDR/QCD_Pt-170to300_TuneZ2_7TeV_pythia6/AODSIM/PU_S13_START53_LV6-v1/00000/ ~/MITOpenDataProject/registry.txt Jet S53/START53_LV6A1 Sim 2011 1
   ```
   
   If you're getting odd outputs (i.e. "File already processed" where you think there shouldn't be), try deleting the files 0 and / or 1 and try again.

## Move MOD files to host machine

Finally, we need to transfer all of the MOD files from the CernVM to a host computer, which is where all of the code for MODAnalyzer will be run.

- On your host machine:

	1. Create a directory to store all of the MOD files. Be sure that this directory is in a location where it has enough storage to hold all of your MOD files!

	```
	mkdir ProducedMOD
	```
- On the CernVM:

	1. Mount the shared folder in the CernVM by, in VirtualBox, going to Settings -> Shared Folders. Add the folder path as shown on the host machine. Check "Auto-Mount" and "Make Permanent", if available.


 	2. In the terminal application of the CernVM, type `id`. Note the values of uid and gid.

	3. Type
	
	```
	sudo mount -t vboxsf -o uid=<value>,gid=<value> ProducedMOD ~/MITOpenDataProject
	``` 	

- You should see all of the MOD files on your host machine in the shared folder.

  
- Congratulations! You've successfully converted all the AOD files that you downloaded to MOD files. In other words, you've completed steps (1) to (3) in the workflow given above. Heaad over to [MODAnalyzer](https://github.com/tripatheea/MODAnalyzer/ "MODAnalyzer") to see how you can analyze data in these MOD files to produce all sorts of super-interesting plots. 



### Notes about JEC
While this repository already contains the necessary files to calculate JEC factors inside the directory `data/JEC/`, if you want to regenerate them or need to use a global tag other than GR_R_42:V25, you can use the Python script `JEC_cfg.py`. The global tag can be edited on line 9 and 19. It might take a while (~20 minutes or more) for the script to complete. 

```
cmsRun JEC_cfg.py
```

If you're using a global tag other than GR_R_42:V25, the filenames will be different from what they are in the repository. For those cases, take all the JEC files that the aove code generates and place them in a directory in "data". Then change argument 5 of PFCandidateRun(online).py accordingly.

## Other Notes
Some random notes that might be helpful as you play around with the code here:

1. Do not forget to run `scram b` to compile your code any time you make a change to a C++ source file. 

2. It's a pain to wait ~10 mins every time you want to run PFCandidateProducer. So for debugging/hacking purposes, you might want to turn off loading the GlobalTags. You can do this by commenting lines 55 and 56 in `PFCandidateRun.py`. You also have to comment out lines 291-307 in `src/PFCandidateProducer.cc`. Those lines are responsible to write out trigger information so if you need to test stuff pretaining to triggers, you cannot get around waiting (technically, you need to load the GlobalTags for trigger prescales only).

3. If you use a new module/component inside `src/PFCandidateProducer.cc`, do not forget to include the corresponding module in the buildfile. Likewise, if you're not using a certain module, remove the corresponding module from the buildfile so that it doesn't slow down compilation of your code.  

4. If you're using something like an external hard drive to store the MOD files into, you'll have to use a "shared directory". Here's how to set it up:
   - Add whatever directory you'd like to use under Shared Folder in the VM settings.
   - Create a user group called `vboxsf` and add the user cms-opendata to that group with `sudo usermod -aG vboxsf cms-opendata`. The root password is `password`.
   - Restart your VM.

## Troubleshooting

    Standard library exception caught in cmsRun:
  
    Can not get data (Additional Information: [frontier.c:793]: No more servers/proxies. 
  
This error message generally means that you didn't use  an encrypted Internet connection. If you are on MIT campus that means you should be using either the MIT SECURE access point or an Ethernet cable.


## TODO



####create_registry.py:
- [x] Is there a reason this isn't in the utilities folder?  Alternatively, does download.py need to be in a separate utilities folder?
- [ ] Can you put comments at the beginning of this file saying how to run it?  (i.e. what the arguments are and what this does?)  This comment holds for all of the .py files that the user might call directly.

####data:
- [ ] This directory has a bit misleading name, since it isn't data.  I would call this "databases" instead.  I would put the list of validated runs here.

####file_paths:
- [ ] It is a bad idea to have many nested folders if you don't need them.  If you move the list of validated runs to the databases folder, then inside in the file_paths, you can directly have a jet_primary_remote folder and jet_primary_small.txt

####JEC_cfg.py:
- [ ] Can this be moved to the utilities folder, or does it have to stay here?

####PFCanidateProducer.cc:
- [x] Line 200: You shouldn't hard code "CMS_2010" and "Jet_Primary_Dataset".  Rather, they should be parameters just like the version number that can be changed easily.  Note that it should be "CMS_2010B".
- [x] Line 273:  You shouldn't hard code "Jet" here.  Rather, the name of the primary data set should correlate with the name given in the header.  That way, we can run other primary datasets without having to change too much.
- [ ] Line 453:  What's up with "TopPairElectronPlusJetsSelectionFilter"?
- [x] add more spaces for trigger names'
- [x] Get simulated data working!
- [ ] Add DOI and name of AOD file to header for each event
