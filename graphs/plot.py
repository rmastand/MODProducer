import numpy as np
import sys
import datetime
import time
import matplotlib.pyplot as plt
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox, AnchoredOffsetbox, HPacker
from matplotlib._png import read_png
from mpl_toolkits.axes_grid.anchored_artists import AnchoredDrawingArea
from matplotlib.cbook import get_sample_data
from matplotlib.patches import Rectangle
from matplotlib import patches
from matplotlib import text as mtext
import math

plot_eff_lumi_file = sys.argv[1]
plot_fired_over_lumi = sys.argv[2]
lumibyls_file = sys.argv[3]
logo_location = "/Users/prekshan/rmastand/CMSOpenData/MODProducer/graphs/MODLogo.png"


trigger_colors = {"HLT_Jet30":"#999999","HLT_Jet60":"#f781bf","HLT_Jet80":"#a65628",
"HLT_Jet110":"#99cc00","HLT_Jet150":"#ff7f00","HLT_Jet190":"#984ea3","HLT_Jet240":"#4daf4a",
"HLT_Jet300":"#377eb8","HLT_Jet370":"#e41a1c"}
logo_text = "Preliminary"
rev_ordered_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300","HLT_Jet370"][::-1]


plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 16
plt.rcParams['font.weight'] = "bold"
plt.rcParams['axes.labelsize'] = 24
plt.rcParams['xtick.labelsize'] = 18
plt.rcParams['ytick.labelsize'] = 18
plt.rcParams['legend.fontsize'] = 24
plt.rcParams['legend.fontsize'] = 24
plt.rcParams['legend.fontsize'] = 24
plt.rcParams['axes.linewidth'] = 2


plt.rcParams['xtick.major.size'] = 10
plt.rcParams['xtick.major.width'] = 2
plt.rcParams['xtick.minor.size'] = 5
plt.rcParams['xtick.minor.width'] = 2
plt.rcParams['ytick.major.size'] = 10
plt.rcParams['ytick.major.width'] = 2
plt.rcParams['ytick.minor.size'] = 5
plt.rcParams['ytick.minor.width'] = 2

plt.rc('mathtext', rm='serif')
plt.rcParams['figure.facecolor'] = "white"
num_samples = 500
id_spacing = 30000

def zero_to_nan(values):
    """Replace every 0 with 'nan' and return a copy."""
    return [float('nan') if x==0 else x for x in values]

extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)

def lumi_id_to_dmy(lumibyls_file):
	"""
	returns two dicts with keys = (run,lumiBlock)
	1st values: gps times
	2nd values: (lumi_delivered, lumi_recorded)
	"""
	lumibyls = open(lumibyls_file)
	lines =  lumibyls.readlines()
	split_lines = [line.split(",") for line in lines][2:]
	char = ""
	lumi_id_to_date = {}
	i = 0
	while char !="#":
		run = split_lines[i][0].split(":")[0]
		lumi = split_lines[i][1].split(":")[0]
		date = split_lines[i][2].split(" ")[0]
		tim = split_lines[i][2].split(" ")[1]
		mdy = [int(x) for x in date.split("/")]
		hms = [int(x) for x in tim.split(":")]
		dt = datetime.datetime(mdy[2], mdy[0], mdy[1], hms[0], hms[1],hms[2])
		lumi_id_to_date[(run,lumi)] = str(mdy[1])+"/"+str(mdy[0])+"/"+str(mdy[2])
		i += 1
		try:
			char = split_lines[i][0][0]
		except: pass
	return lumi_id_to_date
lumi_id_to_date = lumi_id_to_dmy(lumibyls_file)


def logo_box():

        logo_offset_image = OffsetImage(read_png(get_sample_data(logo_location, asfileobj=False)), zoom=0.08, resample=1, dpi_cor=1)
        text_box = TextArea(logo_text, textprops=dict(color="#444444", fontsize=24,weight="normal"))
        logo_and_text_box = HPacker(children=[logo_offset_image, text_box], align="center", pad=0, sep=10)
        anchored_box = AnchoredOffsetbox(loc=2, child=logo_and_text_box, pad=0.2, frameon=False, borderpad=0., bbox_to_anchor=[0.114, .97], bbox_transform = plt.gcf().transFigure)
        return anchored_box


"""
plot_eff_luminosity.txt:
Total Integrated Luminosity, number index
Total Integrated Luminosity, cumsum value
Time ordered luminosity ids for all represented lumiblocks (use for x axis labels)
For each trigger, going from BIGGEST TO SMALLEST:
Effective Luminosity, number index
Effective Luminosity, cumsum value
"""

def graph_eff_lumin():
	plt.figure(figsize= (10,10))
	ax = plt.gca()


	eff_lumi_file =  open(plot_eff_lumi_file)
	lines = eff_lumi_file.readlines()
	# for the total luminosity file:
	master_index = np.array([int(x) for x in lines[1].split(",")])+1

	master_lumin = np.array([float(x) for x in lines[2].split(",")])
	time_ordered_lumi_id = lines[3].split(",")

        #print np.logspace(min(master_index),max(master_index),num_samples)
        good_indices = np.logspace(np.log10(min(master_index)),np.log10(max(master_index)),num_samples).astype(int) -min(master_index)

	plt.plot(np.take(master_index,good_indices),np.take(master_lumin,good_indices),"k",linewidth=9.0)


	x = .2
	plt.text(x,11000,"Total Luminosity",color = "k")

	trig_name_positions = {"HLT_Jet30":(x,.05),"HLT_Jet60":(x,1),"HLT_Jet80":(x,6),
			      "HLT_Jet110":(x,20),"HLT_Jet150":(x,70),"HLT_Jet190":(x,300),
			      "HLT_Jet240":(x,700),"HLT_Jet300":(x,2000),"HLT_Jet370":(x,5000)}

	for trig_index,trig in enumerate(rev_ordered_triggers):
	        print trig

		index = np.array([int(x) for x in lines[3*trig_index+5].split(",")])+1

		eff_lumin = np.array([float(x) for x in lines[3*trig_index+6].split(",")])
                good_indices = np.logspace(np.log10(min(index)),np.log10(max(index)),num_samples).astype(int) - min(index)
                print len(index), len(eff_lumin)

        	plt.plot(np.take(index,good_indices),np.take(eff_lumin,good_indices),trigger_colors[trig],linewidth=4.0)

		plt.text(trig_name_positions[trig][0],trig_name_positions[trig][1],trig[4:],color = trigger_colors[trig])


	#plt.xlabel("Run:LumiBlock")
	#plt.xticks(range(len(time_ordered_lumi_id))[::id_spacing], time_ordered_lumi_id[::id_spacing], rotation=30)
	ax = plt.gca()

	ax.set_xlim(left = .15,right = max(master_index)*1.25)

	plt.xlabel("Cumulative Luminosity Blocks")
	ax.add_artist(logo_box())
	plt.ylabel("Effective Luminosity [ub"+r"$^{-1}$]")
	plt.yscale("log")


        outside_text = ax.legend( [extra], ["CMS 2011 Open Data"], frameon=0, borderpad=0, fontsize=12, bbox_to_anchor=(1.0, 1.005), loc='lower right',prop = {'weight':'normal',"size":16})
        ax.add_artist(outside_text)
	plt.xscale("log")
        plt.text(.2,2.5*10**8,"1223 of 1223 AOD Files",weight="normal")


	plt.savefig("eff_lumi.pdf")
	plt.show()

def graph_eff_lumin_time_ordered():
	plt.figure(figsize=(10,10))
	ax = plt.gca()


	eff_lumi_file =  open(plot_eff_lumi_file)
	lines = eff_lumi_file.readlines()
	# for the total luminosity file:
	
	master_times = np.array([float(x) for x in lines[0].split(",")])+1
	master_index = np.array([int(x) for x in lines[1].split(",")])+1

	master_lumin = np.array([float(x) for x in lines[2].split(",")])
	time_ordered_lumi_id = lines[3].split(",")

        #print np.logspace(min(master_index),max(master_index),num_samples)
        good_indices = np.linspace(min(master_index),max(master_index),num_samples).astype(int) -min(master_index)

	plt.plot(np.take(master_times,good_indices),np.take(master_lumin,good_indices),"k",linewidth=9.0)

	x = min(master_times)*.9985
	print min(master_times)
	plt.text(x,11000,"Total Luminosity",color = "k")

	trig_name_positions = {"HLT_Jet30":(x,.05),"HLT_Jet60":(x,1),"HLT_Jet80":(x,6),
			      "HLT_Jet110":(x,20),"HLT_Jet150":(x,70),"HLT_Jet190":(x,300),
			      "HLT_Jet240":(x,700),"HLT_Jet300":(x,2000),"HLT_Jet370":(x,5000)}

	for trig_index,trig in enumerate(rev_ordered_triggers):
	        print trig

		times = np.array([float(x) for x in lines[3*trig_index+4].split(",")])
		index = np.array([int(x) for x in lines[3*trig_index+5].split(",")])+1

		eff_lumin = np.array([float(x) for x in lines[3*trig_index+6].split(",")])
                good_indices = np.linspace(min(index),max(index),num_samples).astype(int) - min(index)
                print len(index), len(eff_lumin)

        	plt.plot(np.take(times,good_indices),np.take(eff_lumin,good_indices),trigger_colors[trig],linewidth=4.0)

		plt.text(trig_name_positions[trig][0],trig_name_positions[trig][1],trig[4:],color = trigger_colors[trig])

	ax = plt.gca()

	ax.set_xlim(left = min(master_times)*.998,right = max(master_times)*1.0001)
	length = len(master_times)-1
	indices_for_xaxis = np.linspace(length/20,length,5)
	indices_for_xaxis = [int(x) for x in indices_for_xaxis]
	
	plt.xticks(np.take(master_times,indices_for_xaxis))
	
	labels = [item.get_text() for item in ax.get_xticklabels()]
	for i,index in enumerate(indices_for_xaxis):
		labels[i] = lumi_id_to_date[(str(int(time_ordered_lumi_id[index].split(":")[0])),str(int(time_ordered_lumi_id[index].split(":")[1])))]
		
	ax.set_xticklabels(labels)

	plt.xlabel("Date")
	ax.add_artist(logo_box())
	plt.ylabel("Effective Luminosity [ub"+r"$^{-1}$]")
	plt.yscale("log")


        outside_text = ax.legend( [extra], ["CMS 2011 Open Data"], frameon=0, borderpad=0, fontsize=12, bbox_to_anchor=(1.0, 1.005), loc='lower right',prop = {'weight':'normal',"size":16})
        ax.add_artist(outside_text)
        plt.text(.2,2.5*10**8,"1223 of 1223 AOD Files",weight="normal")


	plt.savefig("eff_lumi_time_ordered.pdf")
	plt.show()
	

"""
plot_fired_over_lumin.txt:
For each trigger, going from BIGGEST TO SMALLEST:
Time ordered luminosity ids for all represented lumiblocks within the trigger
Fired over eff lumi number index
fired over eff lumi value
"""
def graph_fired_over_eff_lumin():
	fired_lumi_file =  open(plot_fired_over_lumi)
	lines = fired_lumi_file.readlines()

	plt.figure(figsize=(10,10))
	color_index = 0
	x = -24000
	trig_name_positions = {"HLT_Jet30":(x,150),"HLT_Jet60":(x,6),"HLT_Jet80":(x,1.5),
			      "HLT_Jet110":(x,.3),"HLT_Jet150":(x,.095),"HLT_Jet190":(x,.025),
			      "HLT_Jet240":(x,.009),"HLT_Jet300":(x,.002),"HLT_Jet370":(x,.0007)}
        zorder = 15
	for trig in rev_ordered_triggers:
        	
		index = [int(x) for x in lines[color_index*4+2].split(",")]
		yaxis = [float(x) for x in lines[color_index*4+3].split(",")]
        	print len(index),len(yaxis)


		plt.text(trig_name_positions[trig][0],trig_name_positions[trig][1],trig[4:],color = trigger_colors[trig])
                plt.plot(np.array(index)+1,zero_to_nan(yaxis),trigger_colors[trig],rasterized=True,zorder=zorder)

		color_index += 1
                zorder -= 1


		
	#plt.xlabel("Run:Lumiblock")
	plt.xlabel("Luminosity Block (time-ordered)")
	#plt.xticks(range(len(lines[0].split(",")))[::id_spacing],lines[0].split(",")[::id_spacing], rotation=30)
	plt.ylabel("Effective Cross Section [ub]")
	plt.yscale("log")
	ax = plt.gca()
	plt.xticks(np.arange(0,max(index),id_spacing))
	
	ax.set_xlim(left = -60000,max(index)*1.25)
        outside_text = ax.legend( [extra], ["CMS 2011 Open Data"], frameon=0, borderpad=0, bbox_to_anchor=(1.0, 1.005), loc='lower right',prop = {'weight':'normal',"size":16})
        ax.add_artist(outside_text)
	
	
	ax.add_artist(logo_box())
        plt.text(x,3500,"1223 of 1223 AOD Files",weight="normal")
	
	plt.savefig("fired_over_lumin.pdf")
	plt.show()
	
def graph_fired_over_eff_lumin_time_ordered():
	fired_lumi_file =  open(plot_fired_over_lumi)
	lines = fired_lumi_file.readlines()

	plt.figure(figsize=(10,10))
	color_index = 0
	
	x = .9985*1300086884
	
	trig_name_positions = {"HLT_Jet30":(x,150),"HLT_Jet60":(x,6),"HLT_Jet80":(x,1.5),
		      "HLT_Jet110":(x,.3),"HLT_Jet150":(x,.095),"HLT_Jet190":(x,.025),
		      "HLT_Jet240":(x,.009),"HLT_Jet300":(x,.002),"HLT_Jet370":(x,.0007)}
        zorder = 15
	for trig in rev_ordered_triggers:
        	
		lumis = [x for x in lines[color_index*4].split(",")]
		times = [float(x) for x in lines[color_index*4+1].split(",")]
		index = [int(x) for x in lines[color_index*4+2].split(",")]
		yaxis = [float(x) for x in lines[color_index*4+3].split(",")]
        	print len(index),len(yaxis)
		


		plt.text(trig_name_positions[trig][0],trig_name_positions[trig][1],trig[4:],color = trigger_colors[trig])
                plt.plot(np.array(times),zero_to_nan(yaxis),trigger_colors[trig],rasterized=True,zorder=zorder)

		color_index += 1
                zorder -= 1

	plt.xlabel("Time")

	plt.ylabel("Effective Cross Section [ub]")
	plt.yscale("log")
	ax = plt.gca()

	length = len(times)-1

	indices_for_xaxis = np.linspace(length/20,length,5)
	indices_for_xaxis = [int(x) for x in indices_for_xaxis]
	
	plt.xticks(np.take(times,indices_for_xaxis))
	
	labels = [item.get_text() for item in ax.get_xticklabels()]
	for i,index in enumerate(indices_for_xaxis):
		
		labels[i] = lumi_id_to_date[(str(int(lumis[index].split(":")[0])),str(int(lumis[index].split(":")[1])))]
	ax.set_xlim(left = x*.998,right = max(times)*1.0001)
	ax.set_xticklabels(labels)
	
        outside_text = ax.legend( [extra], ["CMS 2011 Open Data"], frameon=0, borderpad=0, bbox_to_anchor=(1.0, 1.005), loc='lower right',prop = {'weight':'normal',"size":16})
        ax.add_artist(outside_text)

	ax.add_artist(logo_box())
        plt.text(x,3500,"1223 of 1223 AOD Files",weight="normal")
	plt.savefig("fired_over_lumin_time_ordered.pdf")
	plt.show()





#graph_eff_lumin()
#graph_eff_lumin_time_ordered()
graph_fired_over_eff_lumin()
graph_fired_over_eff_lumin_time_ordered()
