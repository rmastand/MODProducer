# -*- coding: utf-8 -*-
import numpy as np
import sys

parsed_by_event = sys.argv[1]

"""
to answer the question: look at events where lower fired, higher was present. what fraction of the time did higher fire?
for which 240 fired, ask for those events, when did 300 fire? that can’t be above 1
"""

lower_trig_name = "HLT_Jet240"
higher_trig_name = "HLT_Jet300"


# YIKES these names...sorry to whoeever who reads this next lol
num_lower_fired_and_higher_present = 0
num_higher_fired_given_lower_fired_and_higher_present = 0

with open(parsed_by_event,"r") as event_listing:
  for line in event_listing:
    if "EventNum" not in line.split(): #just ignores the top line
      print line.split()[3].split(",")
      print line.split()[5].split(",")
      

