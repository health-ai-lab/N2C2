import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib notebook
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



'''Prints who wins by the Borda count'''

def VoteBorda(lags):
    wind = 10
    NumOfCandidates = 25
    lngth = len(lags)

    results= [float('nan')] * lngth

    candidates = []
    for i in range(51):
        candidates.append(str(i))


    candidates.append(str(float('nan')))



    for ind in range(lngth):

        lft = ind - wind;
        if lft < 0:
            lft = 0

        rght = ind + wind;
        if rght >= lngth:
            rght = lngth-1

        prefs = []

        for i in range(lft,rght):
            idx = (-np.array(lags[i])).argsort()[:NumOfCandidates]
            VoteCount = []
            for el in idx:
                VoteCount.append(str(el))
            prefs.append(VoteCount)

        results[ind] = float(borda(candidates,prefs))
    return results

""" 

Cleans the data (gets rid of unnecessary columns dellabels)

"""
def clean(df,del_labels=[]):

    for label in del_labels:
    	try:
        	df = df.drop(labels=label, axis=1)
    	except:
        	continue
    return df

def borda(candidates,prefs):
        '''Prints who wins by the Borda count'''

        counts = {}
        for candidate in candidates:
            counts[candidate] = 0

        max_point = len(candidates)
        for pref in prefs:
            for i in range(len(pref)):
                counts[pref[i]] += max_point - i

        return find_winner(counts)
        

def find_winner(aggregated_result):
    max_point = 0
    for point in aggregated_result.values():
        if point > max_point:
            max_point = point

    winner = []  # winner can be many, so use a list here
    for candidate in aggregated_result.keys():
        if aggregated_result[candidate] == max_point:
            winner.append(candidate)

    return winner[0]


""" Calculates the tricube weights  """
def tricube_modified(windowsize):
    step = (2.0/windowsize)/4
    weights = np.arange(0,0.5 + step,step)
    for i in range(windowsize + 1):
        weights[i] = (70.0/81.0)*((1-abs(weights[i])**3)**3)
    return weights


""" Counts the NAN values """

def countNan(lst):
    count = 0
    for el in lst:
        if math.isnan(el):
            count = count + 1
    return count

def NCC_PAR(i,param1,param2,window = 100,maxlag = 100):
    VERI = []

    leftborder = i - (window / 2)
    if leftborder < 0:
        leftborder = 0
    
    rightborder = i + (window / 2)
    if rightborder > len(param1):
        rightborder = len(param1)
    
    first = param1[leftborder:rightborder]

    corres = []
    
    for j in range(0,maxlag + 1):
        indx = i+j
        
        left = indx - (window / 2)
        if left < 0:
            left = 0
            
        right = indx + (window / 2)
        if right > len(param1):
            right = len(param1)


        second = param2[left:right]
        try:
            
            lenOne = len(first)
            lenTwo = len(second)
            
            if lenOne > 0 and lenTwo > 0:


                nanOne = countNan(first)
                #If all of them are nan in first there is nothing to compare.
                if nanOne == lenOne:
                    return float('nan')
            
                nanTwo = countNan(second)
                
                if nanOne/float(lenOne) < 0.2 and nanTwo/float(lenTwo) < 0.2:
                    
                    corres.append(IsSignificant(first,second))

                else:

                    corres.append(float('nan'))
            else:
                print("second else")
                corres.append(float('nan'))
        except Exception,e:
            #print str(i) + "  " + str(j) + " :EXCEPTION: " + str(e)
            break

   
    count = countNan(corres)
    
    if count == len(corres):
        return float('nan')
    
    corres = [0.0 if math.isnan(x) else x for x in corres]
    

    kernel = tricube_modified(maxlag)
    corres = np.array(corres) * np.array(kernel)
    VERI = corres.tolist()


    for k in range(len(VERI)):
        if VERI[k] == 0.0:
            VERI[k] = float('nan')
    return VERI

def MakeLags(param1,param2,window = 200,maxlag = 100):
    lags = []
    lags = Parallel(n_jobs=100)(delayed(NCC_PAR)(i,param1,param2,window,maxlag) for i in range(len(param1)))
    return lags


if __name__ ==  '__main__':
    if len(sys.argv) not in [6,7]:
        print "python GenerateLags.py consciousnessfn inputdir outputdir window maxlag [hours]"
        print "consciousnessfn is the file with all the consciousness levels,inputdir is the directory of the input data," \
	      "outputdir is where you want to save it (file path, not file name!),window the the window size (in seconds), maxlag is the maximum lag(in seconds)" \
 	      "hours is the amount of hours before a consciousness assessment you would like to use data from (optional, default 0)"
        sys.exit(0)
    consciousnessfn = sys.argv[1]
    inputdir = sys.argv[2]
    outputdir = sys.argv[3]
    window = int(sys.argv[4])
    maxlag = int(sys.argv[5])
    hours=0
    if len(sys.argv)==7:
    	hours = int(sys.argv[6])
    DATA = None



    dfCon = pd.read_csv(consciousnessfn, sep=',')

    ConA = dfCon.loc[dfCon.consciousness== 0] #get all the people that had a consciousness level of 0
    for index, row in ConA.iterrows():
    	PID = int(row.PID)
    	filename = 'Patient_' + str(PID) + '_c.csv'
        df1 = None
        df2 = None
        den = None
        den2 = None
        # add an array del_labels here for the labels you would like to delete
        try:
                df2 = clean(pd.read_csv(inputdir+filename, sep=','))
        except Exception,e:
                #print str(PID) + "     EXCEPTION:     " + str(e)
                continue
        
        currtime = int(row.time)
        left  = currtime - (hours*60) - (((window / 2) + 25) * 60)
        right = currtime - (hours*60) + (((window / 2) + 25) * 60)
        
        variables = {}
        if df2 is not None:
            den2 = df2.loc[(df2['Unnamed: 0'] >= left) & (df2['Unnamed: 0'] <= right)]


            Columns = df2.columns
            for col in Columns[1:]:
                variables[col] = 1
        tCount = {}
        for variable in variables:
            
            for col in variables:
                if col != variable:
                    first = variable
                    second = col
                    
                    name = first + "_vs_" + second
     
                    if name in tCount:
                        continue
                    else:
                        tCount[name] = 1

                    if den2 is not None and len(den2) > 0:
                        try:
                            first_value = np.array(den2[first].iloc[:].values)
                            second_value = np.array(den2[second].iloc[:].values)
                        except Exception,e:
                            #print str(PID) + "     EXCEPTION:     " + str(e)
                            continue
                        lags = MakeLags(first_value,second_value,window = window,maxlag = maxlag)
                        for k in range(len(lags)):
                            s = pd.Series(lags[k])
                            try:
                                lags[k] = s.interpolate(method="quadratic").tolist()
                            except:
                                pass

                        votedLags = VoteBorda(lags)
                        data = {}
                        data["PID"] = PID
                        data["Var1"] = first
                        data["Var2"] = second
                        data["Name"] = name
                        data["Window"] = window
                        data["Lags"] = votedLags

                        if DATA is None:
                            DATA = pd.DataFrame.from_dict(data)
                        else:
                            DATA = DATA.append(pd.DataFrame.from_dict(data))

	if DATA is not None and len(DATA) > 0:
            DATA.to_csv(outputdir + str(PID) +"_" + str(window)+"_"+str(maxlag)+"_"+str(hours)+".csv", sep=',')
