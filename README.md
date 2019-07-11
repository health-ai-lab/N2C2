# Implementation of Nonstationary normalized Cross-correlation (N2C2)

## How to cite

T. T. Yavuz, J. Claassen, and S. Kleinberg. Lagged Correlations among Physiological Variables as Indicators of Consciousness in Stroke Patients. In: *AMIA Annual Symposium Proceedings*, 2019.

## Using the code

### Preparation: 

1. Outcome data format: ensure outcome data is a single CSV file with each row being an instance (such as a patient) of the format: ID, time, outcome. Time is when the outcome was measured. The outcome variable is expected to be discrete and categorial.  
2. Predictive data format: this is the data whose lags are being used to predict the outcome. Data should have one CSV file per instance (such as a patient), with one row per measurement time and columns being variables. See below for an example.
3. Create a directory (inputdir) for the predictive data files using the naming convention Patient_PID_c.csv, where PID is the Patient ID.
4. Create two output directories, one for output lags (outputdir-lag) and one for the results of statical testing (outputdir-stat).
5. Choose a parameter setting for window size in the same time unit as your input data (window), and maximum number of lags to search over (maxlag). We used window=300, and maxlag=50, but values will depend on your outcome variable and data granularity.
  The amount of hours before an outcome assessment you would like to use data from (hours=12; optional, default 0)

### To run the code:

1. python GenerateLags.py outcomes inputdir outputdir-lag window maxlag [hours] (hours being optional)
2. python ResultGeneration.py outcomes outputdir-lag outputdir-stat window maxlag [hours] (hours being optional)

### File format examples

outcomes.csv example

ID,time,outcome
0,60,5
0,120,4
0,180,0
1,240,2
1,300,2
1,360,3

inputdir: has files Patient_ID_c.csv with all the patients' measurements:

Patient_ID_c.csv example:

time, A, B, C, D, E, F, G, H
0,100,10,100,100,100,10,10,100
60,101,11,101,101,101,11,11,101

