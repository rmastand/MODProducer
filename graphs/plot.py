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
logo_text = "Preliminary     CMS 2011 Open Data"
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

# https://stackoverflow.com/questions/19353576/curved-text-rendering-in-matplotlib
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
        anchored_box = AnchoredOffsetbox(loc=2, child=logo_and_text_box, pad=0.2, frameon=False, borderpad=0., bbox_to_anchor=[0.114, .93], bbox_transform = plt.gcf().transFigure)
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
	plt.figure() 
	ax = plt.gca()
	color_index = 0
	
	
	eff_lumi_file =  open(plot_eff_lumi_file)
	lines = eff_lumi_file.readlines()
	# for the total luminosity file:
	master_index = [int(x) for x in lines[0].split(",")]
	master_lumin = [float(x) for x in lines[1].split(",")]
	time_ordered_lumi_id = lines[2].split(",")
	plt.plot(master_index,master_lumin,"ro")
	text = CurvedText(
            	x = master_index[int(len(master_index)*(.6)):int(len(master_index)*(.8))],
            	y = master_lumin[int(len(master_lumin)*(.6)):int(len(master_lumin)*(.8))],
		    text="Total Luminosity",#'this this is a very, very long text',
		    va = 'bottom',
		    axes = ax,color = "r" ##calls ax.add_artist in __init__
		 )
	
	for trig_index,trig in enumerate(rev_ordered_triggers):
		index = [int(x) for x in lines[2*trig_index+3].split(",")]
		eff_lumin = [float(x) for x in lines[2*trig_index+4].split(",")]
		plt.plot(index,eff_lumin,colors[color_index])
		if color_index == 0: # hacky way to look for the firs trigger -- need to fix!!
			text = CurvedText(
			x = index[int(len(index)*(.8)):int(len(index)*(.9))],
			y = eff_lumin[int(len(eff_lumin)*(.8)):int(len(eff_lumin)*(.9))],
			    text=trig[4:],#'this this is a very, very long text',
			    va = 'bottom',
			    axes = ax,color = colors[color_index] ##calls ax.add_artist in __init__
				
			 )
		else:
			text = CurvedText(
			x = index[int(len(index)*(.9)):],
			y = eff_lumin[int(len(eff_lumin)*(.9)):],
			    text=trig[4:],#'this this is a very, very long text',
			    va = 'bottom',
			    axes = ax,color = colors[color_index] ##calls ax.add_artist in __init__
				
			 )
		color_index += 1
	plt.xlabel("Run:LumiBlock")
	
	plt.xticks(range(len(time_ordered_lumi_id))[::id_spacing], time_ordered_lumi_id[::id_spacing], rotation=30)
	ax = plt.gca()
	
	ax.add_artist(logo_box())
	plt.ylabel("Effective Luminosity " +"ub^{-1}")
	plt.yscale("log")
	plt.show()
	plt.savefig("integrated_lumi.pdf")
	
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
	
	plt.figure()
	color_index = 0
	x = 5
	trig_name_positions = {"HLT_Jet30":(x,300),"HLT_Jet60":(x,12),"HLT_Jet80":(x,3),
			      "HLT_Jet110":(x,.5),"HLT_Jet150":(x,.12),"HLT_Jet190":(x,.04),
			      "HLT_Jet240":(x,.01),"HLT_Jet300":(x,.003),"HLT_Jet370":(x,.0015)}
	
	for trig in rev_ordered_triggers:	
		index = [int(x) for x in lines[color_index*3+1].split(",")]
		yaxis = [float(x) for x in lines[color_index*3+2].split(",")]
		

		plt.text(trig_name_positions[trig][0],trig_name_positions[trig][1],trig[4:],color = colors[color_index])
		plt.plot(index,zero_to_nan(yaxis),colors[color_index])
		color_index += 1

	plt.xlabel("Run:Lumiblock")

	plt.xticks(range(len(lines[0].split(",")))[::id_spacing],lines[0].split(",")[::id_spacing], rotation=30)
	plt.ylabel("Times Fired / Effective Luminosity (ub)")
	plt.yscale("log")
	ax = plt.gca()
	box = ax.get_position()
	ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

	# Put a legend to the right of the current axis
	ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)
	
	ax.add_artist(logo_box())
	plt.show()
	plt.savefig("fired_over_lumin.pdf")
	


graph_eff_lumin()
#graph_fired_over_eff_lumin()

