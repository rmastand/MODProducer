import sys


def runs_to_lumi(input,output):
    """makes nicer file linking runs to lumi from file"""
    runalumi_data = open(input)
    output_data = open(output,"w")
    lines =  runalumi_data.readlines()
    split_lines = [line.split(",") for line in lines][2:]

    char = ""
    run_lumi_dict = {}
    i = 0
    while char !="#":
    	run = split_lines[i][0].strip().split(":")[0]
        lumi = split_lines[i][1].strip().split(":")[0]
    	rlumi_delivered = float(split_lines[i][5])
    	rlumi_recorded = float(split_lines[i][6])

        output_data.write(str(run)+"_"+str(lumi)+" "+str(rlumi_delivered)+" "+str(rlumi_recorded)+"\n")


    	i += 1
    	try:
    		char = split_lines[i][0][0]
    	except: pass
    return run_lumi_dict



