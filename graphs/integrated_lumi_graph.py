import numpy as np
import datetime
import time
import sys
import ast
import matplotlib.pyplot as plt
import os

from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox, AnchoredOffsetbox, HPacker
from matplotlib._png import read_png
from mpl_toolkits.axes_grid.anchored_artists import AnchoredDrawingArea
from matplotlib.cbook import get_sample_data

colors = ["b","g","orange","purple","c","maroon","limegreen","deeppink","orangered"]

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 16
plt.rcParams['font.weight'] = "bold"
plt.rcParams['axes.labelsize'] = 24
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['legend.fontsize'] = 24
plt.rc('mathtext', rm='serif')
#plt.rcParams['text.usetex'] = True
#plt.rcParams['text.latex.unicode']=True
plt.rcParams['figure.facecolor'] = "white"

logo_location = "/Users/mod/CMSOpenData/MODProducer/graphs/mod_logo.png"

logo_text = "Preliminary     CMS 2011 Open Data"

from matplotlib import pyplot as plt
from matplotlib import patches
from matplotlib import text as mtext
import numpy as np
import math

class CurvedText(mtext.Text):
    """
    A text object that follows an arbitrary curve.
    """
    def __init__(self, x, y, text, axes, color, **kwargs):
        super(CurvedText, self).__init__(x[0],y[0],' ', axes, **kwargs)

        axes.add_artist(self)

        ##saving the curve:
        self.__x = x
        self.__y = y
        self.__zorder = self.get_zorder()

        ##creating the text objects
        self.__Characters = []
        for c in text:
            if c == ' ':
                ##make this an invisible 'a':
                t = mtext.Text(0,0,'a')
                t.set_alpha(0.0)
            else:
                t = mtext.Text(0,0,c,color, **kwargs)

            #resetting unnecessary arguments
            t.set_ha('center')
            t.set_rotation(0)
            t.set_zorder(self.__zorder +1)

            self.__Characters.append((c,t))
            axes.add_artist(t)


    ##overloading some member functions, to assure correct functionality
    ##on update
    def set_zorder(self, zorder):
        super(CurvedText, self).set_zorder(zorder)
        self.__zorder = self.get_zorder()
        for c,t in self.__Characters:
            t.set_zorder(self.__zorder+1)

    def draw(self, renderer, *args, **kwargs):
        """
        Overload of the Text.draw() function. Do not do
        do any drawing, but update the positions and rotation
        angles of self.__Characters.
        """
        self.update_positions(renderer)

    def update_positions(self,renderer):
        """
        Update positions and rotations of the individual text elements.
        """

        #preparations

        ##determining the aspect ratio:
        ##from https://stackoverflow.com/a/42014041/2454357

        ##data limits
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        ## Axis size on figure
        figW, figH = self.axes.get_figure().get_size_inches()
        ## Ratio of display units
        _, _, w, h = self.axes.get_position().bounds
        ##final aspect ratio
        aspect = ((figW * w)/(figH * h))*(ylim[1]-ylim[0])/(xlim[1]-xlim[0])

        #points of the curve in figure coordinates:
        x_fig,y_fig = (
            np.array(l) for l in zip(*self.axes.transData.transform([
            (i,j) for i,j in zip(self.__x,self.__y)
            ]))
        )

        #point distances in figure coordinates
        x_fig_dist = (x_fig[1:]-x_fig[:-1])
        y_fig_dist = (y_fig[1:]-y_fig[:-1])
        r_fig_dist = np.sqrt(x_fig_dist**2+y_fig_dist**2)

        #arc length in figure coordinates
        l_fig = np.insert(np.cumsum(r_fig_dist),0,0)

        #angles in figure coordinates
        rads = np.arctan2((y_fig[1:] - y_fig[:-1]),(x_fig[1:] - x_fig[:-1]))
        degs = np.rad2deg(rads)


        rel_pos = 10
        for c,t in self.__Characters:
            #finding the width of c:
            t.set_rotation(0)
            t.set_va('center')
            bbox1  = t.get_window_extent(renderer=renderer)
            w = bbox1.width
            h = bbox1.height

            #ignore all letters that don't fit:
            if rel_pos+w/2 > l_fig[-1]:
                t.set_alpha(0.0)
                rel_pos += w
                continue

            elif c != ' ':
                t.set_alpha(1.0)

            #finding the two data points between which the horizontal
            #center point of the character will be situated
            #left and right indices:
            il = np.where(rel_pos+w/2 >= l_fig)[0][-1]
            ir = np.where(rel_pos+w/2 <= l_fig)[0][0]

            #if we exactly hit a data point:
            if ir == il:
                ir += 1

            #how much of the letter width was needed to find il:
            used = l_fig[il]-rel_pos
            rel_pos = l_fig[il]

            #relative distance between il and ir where the center
            #of the character will be
            fraction = (w/2-used)/r_fig_dist[il]

            ##setting the character position in data coordinates:
            ##interpolate between the two points:
            x = self.__x[il]+fraction*(self.__x[ir]-self.__x[il])
            y = self.__y[il]+fraction*(self.__y[ir]-self.__y[il])

            #getting the offset when setting correct vertical alignment
            #in data coordinates
            t.set_va(self.get_va())
            bbox2  = t.get_window_extent(renderer=renderer)

            bbox1d = self.axes.transData.inverted().transform(bbox1)
            bbox2d = self.axes.transData.inverted().transform(bbox2)
            dr = np.array(bbox2d[0]-bbox1d[0])

            #the rotation/stretch matrix
            rad = rads[il]
            rot_mat = np.array([
                [math.cos(rad), math.sin(rad)*aspect],
                [-math.sin(rad)/aspect, math.cos(rad)]
            ])

            ##computing the offset vector of the rotated character
            drp = np.dot(dr,rot_mat)

            #setting final position and rotation:
            t.set_position(np.array([x,y])+drp)
            t.set_rotation(degs[il])

            t.set_va('center')
            t.set_ha('center')

            #updating rel_pos to right edge of character
            rel_pos += w-used


def logo_box():
        
        logo_offset_image = OffsetImage(read_png(get_sample_data(logo_location, asfileobj=False)), zoom=0.25, resample=1, dpi_cor=1)
        text_box = TextArea(logo_text, textprops=dict(color='#444444', fontsize=20, weight='bold'))

        logo_and_text_box = HPacker(children=[logo_offset_image, text_box], align="center", pad=0, sep=10)

        anchored_box = AnchoredOffsetbox(loc=2, child=logo_and_text_box, pad=0.2, frameon=False, borderpad=0., bbox_to_anchor=[0.104, 1.0], bbox_transform = plt.gcf().transFigure)
       
        return anchored_box





lumibyls_file = sys.argv[1]
mod_file_inpur_dir = sys.argv[2]

def read_lumi_by_ls(lumibyls_file):
	"""
	returns two dicts with keys = (run,lumiBlock)
	1st values: gps times
	2nd values: (lumi_delivered, lumi_recorded)
	"""
	lumibyls = open(lumibyls_file)
	lines =  lumibyls.readlines()
	split_lines = [line.split(",") for line in lines][2:]
	char = ""
	lumi_id_to_gps_times = {}
	lumi_id_to_lumin = {}
	i = 0
	while char !="#":
		run = split_lines[i][0].split(":")[0]
		lumi = split_lines[i][1].split(":")[0]
		date = split_lines[i][2].split(" ")[0]
		tim = split_lines[i][2].split(" ")[1]
		mdy = [int(x) for x in date.split("/")]
		hms = [int(x) for x in tim.split(":")]
		dt = datetime.datetime(mdy[2], mdy[0], mdy[1], hms[0], hms[1],hms[2])
		lumi_id_to_gps_times[(run,lumi)] = time.mktime(dt.timetuple())
		lumi_id_to_lumin[(run,lumi)] = (float(split_lines[i][5]),float(split_lines[i][6]))
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return lumi_id_to_gps_times,lumi_id_to_lumin

def is_lumi_valid(lumi_id, lumi_id_to_lumin):
	"""
	lumi_id = (run,lumiBlock)
	"""
	try:
		luminosity = lumi_id_to_lumin[lumi_id]
		return 1
	except KeyError:
		pass

lumi_id_to_gps_times,lumi_id_to_lumin = read_lumi_by_ls(lumibyls_file)


def read_mod_file(mod_file):
	"""
	returns a dict of triggers FOR EACH MOD file
	keys are triggers names (with versions)
	subdicts are lists of good lumis the trigger was present for and the corresponding good prescale values
	"""
	trig_dict = {}

	with open(mod_file) as file:
		for line in file:
			# MOST CODE TAKEN FROM GET_TRIGGER_INFO.py
			# keeps track of the run, lumiBlock
			# this should signal each separate event
			if ("Cond" in line.split()) and ("#" not in line.split()):
				run,lumiBlock = line.split()[1],line.split()[3]

			if ("Trig" in line.split()) and ("#" not in line.split()):
				# all within 1 event
				# given line: [Trig identifier, trig name, prescale1, prescale2, fired?]
				if line.split()[1] not in trig_dict.keys():
					trig_dict[line.split()[1]] = {
								      "good_lumis":[],
								      # corresponds to the prescale for a given GOOD LUMI BLOCK
								      "good_prescales":[],
									  "fired":{}

								     }

					# if the lumi block is valid and if not alredy been analyzed (so present by definition)
					if is_lumi_valid((run,lumiBlock),lumi_id_to_lumin):
						if (run,lumiBlock) not in trig_dict[line.split()[1]]["good_lumis"]:
							trig_dict[line.split()[1]]["good_lumis"].append((run,lumiBlock))
							trig_dict[line.split()[1]]["good_prescales"].append(float(line.split()[2])*float(line.split()[3]))
						try:
							trig_dict[line.split()[1]]["fired"][(run,lumiBlock)]+= int(line.split()[4])
						except KeyError:
							trig_dict[line.split()[1]]["fired"][(run,lumiBlock)] = int(line.split()[4])



				else:

					if is_lumi_valid((run,lumiBlock),lumi_id_to_lumin):
						if (run,lumiBlock) not in trig_dict[line.split()[1]]["good_lumis"]:
							trig_dict[line.split()[1]]["good_lumis"].append((run,lumiBlock))
							trig_dict[line.split()[1]]["good_prescales"].append(float(line.split()[2])*float(line.split()[3]))
						try:
							trig_dict[line.split()[1]]["fired"][(run,lumiBlock)]+= int(line.split()[4])
						except KeyError:
							trig_dict[line.split()[1]]["fired"][(run,lumiBlock)] = int(line.split()[4])

		return trig_dict

def cut_trigger_name(name):
	return name.rsplit("_", 1)[0]




# good_lumis,good_prescales
master_trig_dict = {"HLT_Jet190":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet370":{"good_lumis":[],"good_prescales":[],"fired":{}},
					"HLT_Jet150":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet240":{"good_lumis":[],"good_prescales":[],"fired":{}},
					"HLT_Jet110":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet80":{"good_lumis":[],"good_prescales":[],"fired":{}},
						"HLT_Jet60":{"good_lumis":[],"good_prescales":[],"fired":{}},
						"HLT_Jet30":{"good_lumis":[],"good_prescales":[],"fired":{}},"HLT_Jet300":{"good_lumis":[],"good_prescales":[],"fired":{}}}
ordered_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300","HLT_Jet370"]


for file in os.listdir(mod_file_inpur_dir):

	file_trig_dict = read_mod_file(mod_file_inpur_dir+"/"+file)

	for trig in file_trig_dict.keys():
		if cut_trigger_name(trig) in master_trig_dict.keys():
			master_trig_dict[cut_trigger_name(trig)]["good_lumis"] = master_trig_dict[cut_trigger_name(trig)]["good_lumis"]+file_trig_dict[trig]["good_lumis"]
			master_trig_dict[cut_trigger_name(trig)]["good_prescales"] = master_trig_dict[cut_trigger_name(trig)]["good_prescales"]+file_trig_dict[trig]["good_prescales"]
			for lumi_id in file_trig_dict[trig]["fired"].keys():
				try:
					master_trig_dict[cut_trigger_name(trig)]["fired"][lumi_id] += file_trig_dict[trig]["fired"][lumi_id]
				except KeyError:
					master_trig_dict[cut_trigger_name(trig)]["fired"][lumi_id] = file_trig_dict[trig]["fired"][lumi_id]




def plot_eff_lumin():
	# total luminosity, independent of trigger or # of MOD files used
	

	# finds time vs effective luminosity curves for all triggers while counting a total
	trigger_time_v_lumin_rec = {}
	master_lumin_ids = []
	for trigger in master_trig_dict.keys():
		trigger_time = []
		trigger_eff_lumin = []
		for i,lumi_id in enumerate(master_trig_dict[trigger]["good_lumis"]):
			if lumi_id not in master_lumin_ids:
				master_lumin_ids.append(lumi_id)
			trigger_time.append(lumi_id_to_gps_times[lumi_id])
			trigger_eff_lumin.append(lumi_id_to_lumin[lumi_id][1]/master_trig_dict[trigger]["good_prescales"][i])
		trigger_time_v_lumin_rec[trigger] = trigger_time,trigger_eff_lumin

	master_times = []
	master_lumin_rec = []
	for lumi_id in master_lumin_ids:
		master_times.append(lumi_id_to_gps_times[lumi_id])
		master_lumin_rec.append(lumi_id_to_lumin[lumi_id][1]) 
		
	# plots
	plt.figure(figsize=(4,2)) 
	ax = plt.gca()
	j = 0
	ttimes,master_lumin_rec = (list(t) for t in zip(*sorted(zip(master_times,master_lumin_rec))))
	master_time_index = range(len(master_times))
	plt.plot(master_time_index,np.cumsum(master_lumin_rec),"ro",label = "Total")
	text = CurvedText(
            	x = master_time_index[int(len(master_time_index)*(.4)):int(len(master_time_index)*(.6))],
            	y = np.cumsum(master_lumin_rec)[int(len(master_time_index)*(.4)):int(len(master_time_index)*(.6))],
		    text="Total Luminosity",#'this this is a very, very long text',
		    va = 'bottom',
		    axes = ax,color = "r" ##calls ax.add_artist in __init__
		 )
	
	lumis_in_dispay_format = [x[0]+":"+x[1] for x in lumi_id_to_gps_times.keys()]
	ttimes,ordered_ids = (list(t) for t in zip(*sorted(zip(master_times,lumis_in_dispay_format))))

	for trig in ordered_triggers[::-1]:
		times,eff_lumin = (list(t) for t in zip(*sorted(zip(trigger_time_v_lumin_rec[trig][0],trigger_time_v_lumin_rec[trig][1]))))
		overlap = []
		for i,mytime in enumerate(ttimes):
			if mytime in times:
				overlap.append(master_time_index[i])
		
		plt.plot(overlap,np.cumsum(eff_lumin),colors[j],label = trig)
		if j == 0:
			text = CurvedText(
			x = overlap[int(len(overlap)*(.6)):int(len(overlap)*(.8))],
			y = np.cumsum(eff_lumin)[int(len(overlap)*(.6)):int(len(overlap)*(.8))],
			    text=trig.replace("_"," "),#'this this is a very, very long text',
			    va = 'bottom',
			    axes = ax,color = colors[j] ##calls ax.add_artist in __init__
				
			 )
		else:
			text = CurvedText(
			x = overlap[int(len(overlap)*(.8)):],
			y = np.cumsum(eff_lumin)[int(len(overlap)*(.8)):],
			    text=trig.replace("_"," "),#'this this is a very, very long text',
			    va = 'bottom',
			    axes = ax,color = colors[j] ##calls ax.add_artist in __init__
				
			 )
		j += 1
	plt.xlabel("Run:LumiBlock")
	
	
		
	plt.xticks(range(len(ordered_ids))[::5], ordered_ids[::5], rotation=30)
	ax = plt.gca()
        #box = ax.get_position()
	#ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

	# Put a legend to the right of the current axis
	#ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)
	
	
	ax.add_artist(logo_box())
	plt.ylabel("Effective Luminosity (/ub)")
	plt.yscale("log")
	plt.show()
	plt.savefig("integrated_lumi.png")
	

def plot_fired_over_eff_lumin():
	trigger_time_v_fired_lumin = {}
	for trigger in master_trig_dict.keys():
		trigger_time = []
		trigger_fired_lumin = []
		trigger_lumi = []
		for i,lumi_id in enumerate(master_trig_dict[trigger]["good_lumis"]):
			trigger_time.append(lumi_id_to_gps_times[lumi_id])
			eff_lumin = lumi_id_to_lumin[lumi_id][1]/master_trig_dict[trigger]["good_prescales"][i]
			trigger_fired_lumin.append(float(master_trig_dict[trigger]["fired"][lumi_id])/eff_lumin)
			trigger_lumi.append(lumi_id[0]+","+lumi_id[1])
		trigger_time_v_fired_lumin[trigger] = trigger_time,trigger_fired_lumin,trigger_lumi

	# plots
	plt.figure()
	for trig in ordered_triggers:
		#times,fired_lumin = (list(t) for t in zip(*sorted(zip(trigger_time_v_fired_lumin[trig][0],trigger_time_v_fired_lumin[trig][1]))))
		#plt.plot(times,fired_lumin,label = trig)
		#plt.plot(fired_lumin,label = trig)
		new_times,fired_lumin = (list(t) for t in zip(*sorted(zip(trigger_time_v_fired_lumin[trig][0],trigger_time_v_fired_lumin[trig][1]))))
		new_times, ordered_ids = (list(t) for t in zip(*sorted(zip(trigger_time_v_fired_lumin[trig][0],trigger_time_v_fired_lumin[trig][2]))))
		
		plt.plot(range(len(fired_lumin)),fired_lumin,label = trig)

	plt.xlabel("Run,Lumiblock (time-ordered)")
	plt.legend(loc='lower right', frameon=False)
	plt.xticks(range(len(fired_lumin))[::5], ordered_ids[::5], rotation=30)
	plt.ylabel("times fired / eff lumin")
	plt.yscale("log")
	ax = plt.gca()
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

	# Put a legend to the right of the current axis
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)
	
	ax.add_artist(logo_box())
	plt.show()
	plt.savefig("fired_over_lumin.png")
	
def lumi_blocks_in_file():
	
	# keys = mod files, values = dict
		# keys = lumi block id, values = counts
	lumi_blocks_in_file_dict = {}
	
	for filename in os.listdir(mod_file_inpur_dir):
		lumi_blocks_in_file_dict[filename] = {}
		with open(mod_file_inpur_dir+"/"+filename) as file:
			
			for line in file:
				if ("Cond" in line.split()) and ("#" not in line.split()):
					run,lumiBlock = line.split()[1],line.split()[3]
					try:
						lumi_blocks_in_file_dict[filename][run+"_"+lumiBlock] += 1
					except KeyError:
						lumi_blocks_in_file_dict[filename][run+"_"+lumiBlock] = 1
						
					
	
	for file in lumi_blocks_in_file_dict.keys():
		plt.figure()
		lumi_ids = lumi_blocks_in_file_dict[file].keys()
		lumi_counts = lumi_blocks_in_file_dict[file].values()
		lumi_ids,lumi_counts = (list(t) for t in zip(*sorted(zip(lumi_ids,lumi_counts))))
		print lumi_ids
		mybar = plt.bar(range(len(lumi_ids)), lumi_counts, align='center', tick_label=lumi_ids)
		for label in mybar.ax.xaxis.get_ticklabels()[::20]:
   			label.set_visible(False)
		plt.show()
		

	

plot_eff_lumin()
#plot_fired_over_eff_lumin()
# currently i am NOT checking for validity for this last one
#lumi_blocks_in_file()
