import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from joblib import Parallel, delayed
import multiprocessing
import math
from os import walk
from IPython.core.debugger import set_trace
from mpl_toolkits.mplot3d import Axes3D
import random
from scipy import signal
from scipy import interpolate
from scipy import stats
import sys




""" 

Function generate_manu will output the results of the MannWhitneyU test on the 'criterias' array.

Input:
consciousnessfn: the file with all the consciousness levels
inputdir: the directory of the input data, outputfn is where you want to save it
window: the window size (in seconds)
maxlag: the maximum lag (in seconds)
hours: the amount of hours before a consciousness assessment you would like to use data from (optional, default 0)

Output:
Results for MannWhitneyU in csv format


"""

def generate_manwu(consciousnessfn,inputdir,outputfn,window,maxlag,hours=0):
	
    dfCon = pd.read_csv(consciousnessfn, sep=',')

    ConA = dfCon.loc[dfCon.consciousness == 0] #get all the people that had a consciousness level of 0
    for index, row in ConA.iterrows():
        PID = int(row.PID)
        filename = str(PID) + "_" + str(window) + "_" + str(maxlag)+"_"+str(hours)+'.csv'
	try:
    		df = pd.read_csv(inputdir+filename, sep=',')
        except Exception,e:
        	#print str(PID) + "     EXCEPTION:     " + str(e)
                continue

    	DATA1 = None
    	variables = df["Name"].unique()
	
    	for var in variables:
        	aName = df.loc[(df['Name'] == var)]
        	PIDs = aName["PID"].unique()
        	for PID in PIDs:
            		den = aName.loc[(aName['PID'] == PID)]
            	
            		lags = den["Lags"]
            	
	            	dummydata = {}
	            	dummydata["PID"] = [PID]
	            	dummydata["Name"] = var
        	    	dummydata["Window"] = window
	            	dummydata["Mean"] = np.nanmean(lags)
	            	dummydata["Var"] = np.nanvar(lags)
	            	dummydata["Median"] = np.nanmedian(lags)
	            	dummydata["Max"] = np.nanmax(lags)
	            	dummydata["Min"] = np.nanmin(lags)
            		dummydata["Range"] = dummydata["Max"] - dummydata["Min"]
            	
                	
            	
            	
	            	if DATA1 is None:
	                	DATA1 = pd.DataFrame.from_dict(dummydata, orient='columns')
	            	else:
	                	DATA1 = DATA1.append(pd.DataFrame.from_dict(dummydata))
	DATA2=DATA1
	
    	criterias = ["Mean"]
    	for criteria in criterias:
        	print criteria
        	RESULTS = None
        	variables = DATA2["Name"].unique()
		
        	for var in variables:
            		varden1 = DATA1.loc[(DATA1['Name'] == var)]
            		varden2 = DATA2.loc[(DATA2['Name'] == var)]
	
            		second = []
            		for index, row in varden2.iterrows():
                		if math.isnan(row[criteria]) != True:
                    			second.append(row[criteria])
	
            		first = []
            		for index, row in varden1.iterrows():
                		if math.isnan(row[criteria]) != True:
                    			first.append(row[criteria])
	
	
            		if(len(first)>0 and len(second)>0):
                		minesfirst = 0
                		minessecond = 0
	
                		if len(first) == 1:
                    			first.append(first[0])
                    			minesfirst = 1
	
	                	if len(second) == 1:
	                    		second.append(second[0])
	                    		minessecond = 1
	
	
	                	test = stats.ttest_ind(first,second,equal_var=False)
	                	test2 = stats.ttest_ind(first,second,equal_var=True)
	                	dummydata = {}
	                	dummydata["Comparison"] = [var]
	                	dummydata["T-Score"] = test.statistic
	                	dummydata["T-TEST p-value ( EqualVar=True )"] = test2.pvalue
	                	dummydata["T-TEST p-value ( EqualVar=False )"] = test.pvalue
	                	dummydata["n(0)"] = len(first) - minesfirst
	                	dummydata["n=(4,5)"] = len(second) - minessecond
	                	dummydata["Mean(0)"] = np.nanmean(first)
	                	dummydata["Mean(4,5)"] = np.nanmean(second)
	                	try:  
		                    	dummydata["MannWhitneyU p-value"] = stats.mannwhitneyu(first, second)[1]
	                	except Exception,e:
	  	                  	dummydata["MannWhitneyU p-value"] = float('nan')
		                    	print "     EXCEPTION:     " + str(e)
                    	
	
	                	if RESULTS is None:
		                    	RESULTS = pd.DataFrame.from_dict(dummydata, orient='columns')
                		else:
                    			RESULTS = RESULTS.append(pd.DataFrame.from_dict(dummydata))
	
		
        	RESULTS.to_csv(outputfn, sep=',')


if __name__ == '__main__':
    if len(sys.argv) not in [6,7]:
        print "python ResultGeneration.py consciousnessfn inputdir outputfn window maxlag"
        print "consciousnessfn is the file with all the consciousness levels,inputdir is the directory of the input data, outputfn is where you want to save it," \
	      "window the the window size(in seconds), maxlag is the maximum lag(in seconds)" \
	      "hours is the amount of hours before a consciousness assessment you would like to use data from (optional, default 0)"
        sys.exit(0)
    consciousnessfn = sys.argv[1]
    inputdir = sys.argv[2]
    outputfn = sys.argv[3]
    window = sys.argv[4]
    maxlag = sys.argv[5]
    hours=0
    if len(sys.argv)==7:
        hours = int(sys.argv[6])
    generate_manwu(consciousnessfn,inputdir,outputfn,window,maxlag,hours)

