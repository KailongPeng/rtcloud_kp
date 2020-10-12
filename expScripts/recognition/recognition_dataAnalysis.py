## - recognition data analysis for behavior data and brain data

# parameters of this code:
subjectID='pilot_sub001' # normally it should be sub001
run=1

# loading packages and general paths
import pandas as pd
import numpy as np
import os
if 'milgram' in os.getcwd():
	main_dir='/gpfs/milgram/project/turk-browne/projects/rtcloud_kp/'
else:
	main_dir='/Volumes/GoogleDrive/My Drive/Turk_Browne_Lab/rtcloud_kp/'
datapath=main_dir+f'subjects/{subjectID}/ses1_recognition/{subjectID}_{run}.csv'
behav_data=pd.read_csv(datapath)

# the item(imcode) colume of the data represent each image in the following correspondence
imcodeDict={
'A': 'bed',
'B': 'Chair',
'C': 'table',
'D': 'bench'}

# When the imcode code is "A", the correct response should be '1', "B" should be '2'
correctResponseDict={
'A': 1,
'B': 2,
'C': 1,
'D': 2}

# extract the labels which is selected by the subject and coresponding TR and time
behav_data = behav_data[['TR', 'image_on', 'Resp',  'Item']] # the TR, the real time it was presented, 
behav_data=behav_data.dropna(subset=['Item'])

# check if the subject's response is correct. When Item is A,bed, response should be 1, or it is wrong
isCorrect=[]
for curr_trial in range(behav_data.shape[0]):
    isCorrect.append(correctResponseDict[behav_data['Item'].iloc[curr_trial]]==behav_data['Resp'].iloc[curr_trial])

behav_data['isCorrect']=isCorrect # merge the isCorrect clumne with the data dataframe
behav_data=behav_data[behav_data['isCorrect']] # discard the trials where the subject made wrong selection

labels=[]
# get the labels I need for the output of this function
for curr_trial in range(behav_data.shape[0]):
    labels.append(imcodeDict[behav_data['Item'].iloc[curr_trial]])

## - brain data analysis
from recognition_dataAnalysis_brain import get_brain_data_recognition
brain_data = get_brain_data_recognition(sub='pilot_sub001',run='01') # corresponding brain_data which is M TR x N voxels

# brain data is first aligned by pushed back 2TR(4s)
Brain_TR=np.arange(brain_data.shape[0])
Brain_TR = Brain_TR+2

# select volumes of brain_data by counting which TR is left in behav_data
Brain_TR=Brain_TR[list(behav_data['TR'])]
brain_data=brain_data[Brain_TR]

# This M x N brain_data and M labels

return brain_data, labels












