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

i = 0
# YIKES these names...sorry to whoeever who reads this next lol
num_lower_fired_and_higher_present = 0
num_higher_fired_given_lower_fired_and_higher_present = 0

with open(parsed_by_event,"r") as event_listing:
  for line in event_listing:
    i += 1
    if i > 50000:
      break
    if i % 10000 == 0:
      print "on line "+ str(i)
    if "EventNum" not in line.split(): #just ignores the top line
      triggers_present = line.split()[3].split(",")
      # cuts the version numbers out
      triggers_present = [x[:-3] for x in triggers_present]
      
      triggers_fired = line.split()[5].split(",")
      
      triggers_fired = [x[:-3] for x in triggers_fired]
      if (lower_trig_name in triggers_fired) and (higher_trig_name in triggers_present):
        num_lower_fired_and_higher_present += 1
        if higher_trig_name in triggers_fired:
          num_higher_fired_given_lower_fired_and_higher_present += 1
     
print lower_trig_name+" fired and "+higher_trig_name+"present: "+str(num_lower_fired_and_higher_present)
print higher_trig_name+" fired given above criteria: "+str(num_higher_fired_given_lower_fired_and_higher_present)

      

