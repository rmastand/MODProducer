import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox, AnchoredOffsetbox, HPacker
from matplotlib._png import read_png
from mpl_toolkits.axes_grid.anchored_artists import AnchoredDrawingArea
from matplotlib.cbook import get_sample_data
from matplotlib import patches
from matplotlib import text as mtext
import math

plot_eff_lumi_file = sys.argv[1]
plot_fired_over_lumi = sys.argv[2]
logo_location = "/Users/mod/CMSOpenData/MODProducer/graphs/mod_logo.png"

colors = ["b","g","orange","purple","c","maroon","limegreen","deeppink","orangered"]
logo_text = "Preliminary        CMS 2011 Open Data"
rev_ordered_triggers = ["HLT_Jet30","HLT_Jet60","HLT_Jet80","HLT_Jet110","HLT_Jet150","HLT_Jet190","HLT_Jet240","HLT_Jet300","HLT_Jet370"][::-1]


plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 16
plt.rcParams['font.weight'] = "bold"
plt.rcParams['axes.labelsize'] = 24
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 18
plt.rcParams['legend.fontsize'] = 24
plt.rc('mathtext', rm='serif')
plt.rcParams['figure.facecolor'] = "white"

id_spacing = 25

def zero_to_nan(values):
    """Replace every 0 with 'nan' and return a copy."""
    return [float('nan') if x==0 else x for x in values]



def logo_box():
        
        logo_offset_image = OffsetImage(read_png(get_sample_data(logo_location, asfileobj=False)), zoom=0.25, resample=1, dpi_cor=1)
        text_box = TextArea(logo_text, textprops=dict(color='#444444', fontsize=20, weight='bold'))
        logo_and_text_box = HPacker(children=[logo_offset_image, text_box], align="center", pad=0, sep=10)
        anchored_box = AnchoredOffsetbox(loc=2, child=logo_and_text_box, pad=0.2, frameon=False, borderpad=0., bbox_to_anchor=[0.114, .95], bbox_transform = plt.gcf().transFigure)
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
	plt.figure(figsize= (12,10)) 
	ax = plt.gca()
	color_index = 0
	
	
	eff_lumi_file =  open(plot_eff_lumi_file)
	lines = eff_lumi_file.readlines()
	# for the total luminosity file:
	master_index = [int(x) for x in lines[0].split(",")]
	master_lumin = [float(x) for x in lines[1].split(",")]
	time_ordered_lumi_id = lines[2].split(",")
	plt.plot(np.array(master_index)+1,master_lumin,"ro")

	
	x = .4
	plt.text(x,20000,"Total Luminosity",color = "r")

	trig_name_positions = {"HLT_Jet30":(x,.1),"HLT_Jet60":(x,1),"HLT_Jet80":(x,10),
			      "HLT_Jet110":(x,100),"HLT_Jet150":(x,300),"HLT_Jet190":(x,1000),
			      "HLT_Jet240":(x,3000),"HLT_Jet300":(x,5000),"HLT_Jet370":(x,10000)}
	
	for trig_index,trig in enumerate(rev_ordered_triggers):
		index = [int(x) for x in lines[2*trig_index+3].split(",")]
		eff_lumin = [float(x) for x in lines[2*trig_index+4].split(",")]
		plt.plot(np.array(index)+1,eff_lumin,colors[color_index])
		plt.text(trig_name_positions[trig][0],trig_name_positions[trig][1],trig[4:],color = colors[color_index])

			
		color_index += 1
	#plt.xlabel("Run:LumiBlock")
	#plt.xticks(range(len(time_ordered_lumi_id))[::id_spacing], time_ordered_lumi_id[::id_spacing], rotation=30)
	ax = plt.gca()
	ax.set_xlim(left = .3)
	plt.xlabel("Number of lumiblocks")
	
	ax.add_artist(logo_box())
	plt.ylabel("Effective Luminosity " +"ub^{-1}")
	plt.yscale("log")
	plt.xscale("log")
	plt.savefig("eff_lumi.pdf")
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
	
	plt.figure(figsize=(12,10))
	color_index = 0
	x = 5
	trig_name_positions = {"HLT_Jet30":(x,300),"HLT_Jet60":(x,12),"HLT_Jet80":(x,3),
			      "HLT_Jet110":(x,.5),"HLT_Jet150":(x,.12),"HLT_Jet190":(x,.04),
			      "HLT_Jet240":(x,.01),"HLT_Jet300":(x,.003),"HLT_Jet370":(x,.0015)}
	
	for trig in rev_ordered_triggers:	
		index = [int(x) for x in lines[color_index*3+1].split(",")]
		yaxis = [float(x) for x in lines[color_index*3+2].split(",")]
		

		plt.text(trig_name_positions[trig][0],trig_name_positions[trig][1],trig[4:],color = colors[color_index])
		plt.plot(np.array(index)+1,zero_to_nan(yaxis),colors[color_index])
		color_index += 1

	#plt.xlabel("Run:Lumiblock")
	plt.xlabel("# pf Luminosity Blocks (time-ordered)")

	#plt.xticks(range(len(lines[0].split(",")))[::id_spacing],lines[0].split(",")[::id_spacing], rotation=30)
	plt.ylabel("Times Fired / Effective Luminosity (ub)")
	plt.yscale("log")
	ax = plt.gca()
	ax.set_xlim(left = .3)
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

	# Put a legend to the right of the current axis
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)
	
	ax.add_artist(logo_box())
	plt.savefig("fired_over_lumin.pdf")
	plt.show()
	
	


#graph_eff_lumin()
graph_fired_over_eff_lumin()

