# This script is in the environment of '/gpfs/milgram/project/turk-browne/projects/rtcloud_kp/expScripts/recognition/' 
# and activate_rt
# The purpose of this script is to analyze the data from recognition run

# import and set up environment
from subprocess import call
import nibabel as nib
from nibabel.nicom import dicomreaders
import pydicom as dicom  # type: ignore
import numpy as np
import time
import os
import glob
import shutil

sub="pilot_sub001" ; 
homeDir="/gpfs/milgram/project/turk-browne/projects/rtcloud_kp/" ; 
dataDir=homeDir+"subjects/"+sub+"/ses1_recognition/nifti/"

tmp_folder = "/gpfs/milgram/scratch60/turk-browne/kp578/sandbox/" + sub # tmp_folder='/tmp/kp578/'
if os.path.isdir(tmp_folder):
	shutil.rmtree(tmp_folder)
os.mkdir(tmp_folder)

def printOrien(full_ref_BOLD):
	# input might be .nii.gz file
	ref_BOLD_obj = nib.load(full_ref_BOLD)
	ref_bold_ornt = nib.aff2axcodes(ref_BOLD_obj.affine)
	print('Ref BOLD orientation:') # day1functionalInAnatomicalSpace Ref BOLD orientation:('R', 'A', 'S') # What is the orientation of the realtime data? 
	print(ref_bold_ornt)
	return ref_bold_ornt

# # fetch data from XNAT
subjectID="rtSynth_pilot001"
# call(f"sbatch fetchXNAT.sh {subjectID}",shell=True) # fetch data from XNAT
# call(f"upzip {subjectID}.zip")
# call(f"sbatch change2nifti.sh {subjectID}",shell=True) # convert dicom to nifti files

# paths of anatomical data and functional data
anatomical=dataDir+'rtSynth_pilot001_20201009165148_8.nii'
functional=dataDir+'rtSynth_pilot001_20201009165148_13.nii'


# this is commented because this is data analysis of the recognition run, so that data 
# should have the same orientation with the function template volume
# # Determine the orientation of ref BOLD 
# print('Ref BOLD orientation:')
# ref_bold_ornt = printOrien(functional)
# # Generate the transformation needed
# target_orientation = nib.orientations.axcodes2ornt(ref_bold_ornt)
# dicom_orientation = nib.orientations.axcodes2ornt(('P', 'L', 'S'))
# ornt_transform = nib.orientations.ornt_transform(dicom_orientation,target_orientation)
# output_image_correct = nib.orientations.apply_orientation(temp_data, ornt_transform)


# copy the functional data to tmp folder 
os.mkdir(tmp_folder+subjectID) # the intermediate data are saved in scratch folder, only original data and final results are saved in project folder
call(f"cp {functional} {tmp_folder}{subjectID}/",shell=True)

# split functional data to multiple volumes
call(f"fslsplit {tmp_folder}{subjectID}/{functional.split('/')[-1]}  {tmp_folder}{subjectID}/",shell=True) ## os.chdir(f"{tmp_folder}{subjectID}/")
functionalFiles=glob.glob(f'{tmp_folder}{subjectID}/*.nii.gz')
functionalFiles.sort()

# select the middle volume as the template functional volume
templateFunctionalVolume=functionalFiles[int(len(functionalFiles)/2)]

# this is commented because I don't do alignment between anatomical and functional anymore, the data is trained in function space.
# # align the middle volume to the anatomical data and visually check the result # save the middle volume as day1functionalInAnatomicalSpace_betonalInAnatomicalSpace.nii.gz
# day1functionalInAnatomicalSpace_bet=dataDir+"day1functionalInAnatomicalSpace_bet.nii.gz"
# templateFunctionalVolume_bet=f"{templateFunctionalVolume[0:-7]}_bet.nii.gz"
# call(f"bet {templateFunctionalVolume} {templateFunctionalVolume_bet}",shell=True)
# anatomical_bet=f"{anatomical[0:-4]}_bet.nii.gz"
# call(f"bet {anatomical} {anatomical_bet}",shell=True)
# functional2anatomical=dataDir+'functional2anatomical'
# call(f"flirt -in {templateFunctionalVolume_bet} -ref {anatomical_bet} \
# 	-omat {functional2anatomical} \
# 	-out {day1functionalInAnatomicalSpace_bet}",shell=True)
# # transform templateFunctionalVolume with skull to anatomical space using saved transformation
# day1functionalInAnatomicalSpace=dataDir+"day1functionalInAnatomicalSpace.nii.gz"
# call(f"flirt -in {templateFunctionalVolume} -ref {anatomical} -out {day1functionalInAnatomicalSpace} \
# -init {functional2anatomical} -applyxfm",shell=True) # the result of this looks fine, although not perfect.

# align every other functional volume with templateFunctionalVolume
data=[]
for curr_TR in functionalFiles:
	print('curr_TR=',curr_TR)
	TR_FunctionalTemplateSpace=f"{curr_TR[0:-7]}_FunctionalTemplateSpace.nii.gz"
	command = f"3dvolreg \
	-base {templateFunctionalVolume} \
	-prefix  {TR_FunctionalTemplateSpace} \
	-1Dfile {curr_TR[0:-7]}_motion.1D -1Dmatrix_save {curr_TR[0:-7]}_mat.1D {curr_TR}"
	print(command)
	A=time.time()
	call(command,shell=True)
	B=time.time()
	print(f"{B-A}s passed")
	TR_FunctionalTemplateSpace = nib.load(TR_FunctionalTemplateSpace)
	TR_FunctionalTemplateSpace = TR_FunctionalTemplateSpace.get_data()
	data.append(TR_FunctionalTemplateSpace)

# note that this is not masked for now, so skull is included.
# save all the functional data in day1 anatomical space, as M x N matrix. M TR, N voxels 
recognitionData=np.asarray(data)
recognitionData=recognitionData.reshape(recognitionData.shape[0],-1)
print("shape of recognitionData=",recognitionData.shape)
np.save(dataDir+'recognitionData',recognitionData)


