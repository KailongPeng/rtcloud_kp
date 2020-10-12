# This script is in the environment of '/gpfs/milgram/project/turk-browne/projects/rtcloud_kp/expScripts/recognition/' 
# and activate_rt
# The purpose of this script is to analyze the data from recognition run

def get_brain_data_recognition(sub='pilot_sub001',run='01'):

	# import and set up environment
	from subprocess import call
	import nibabel as nib
	from nibabel.nicom import dicomreaders
	import pydicom as dicom
	import numpy as np
	import time
	import os
	import glob
	import shutil

	# sub="pilot_sub001" ; 
	homeDir="/gpfs/milgram/project/turk-browne/projects/rtcloud_kp/" 
	dataDir=f"{homeDir}subjects/{sub}/ses1_recognition/run{run}/nifti/"

	# if the data have been analyzed, load the saved data.
	if os.path.exists(dataDir+'recognitionData.npy'):
		recognitionData=np.load(dataDir+'recognitionData.npy')
		return recognitionData

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
	if sub==pilot_sub001:
		subjectID="rtSynth_pilot001"
		anatomical=dataDir+'rtSynth_pilot001_20201009165148_8.nii'
		functional=dataDir+'rtSynth_pilot001_20201009165148_13.nii'
	else:
		subjectID=f"rtSynth_{sub}"
		anatomical=dataDir+'rtSynth_{sub}_20201009165148_8.nii'
		functional=dataDir+'rtSynth_{sub}_20201009165148_13.nii'

	# call(f"sbatch fetchXNAT.sh {subjectID}",shell=True) # fetch data from XNAT
	# call(f"upzip {subjectID}.zip")
	# call(f"sbatch change2nifti.sh {subjectID}",shell=True) # convert dicom to nifti files

	# copy the functional data to tmp folder 
	os.mkdir(tmp_folder+subjectID) # the intermediate data are saved in scratch folder, only original data and final results are saved in project folder
	call(f"cp {functional} {tmp_folder}{subjectID}/",shell=True)

	# split functional data to multiple volumes
	call(f"fslsplit {tmp_folder}{subjectID}/{functional.split('/')[-1]}  {tmp_folder}{subjectID}/",shell=True) ## os.chdir(f"{tmp_folder}{subjectID}/")
	functionalFiles=glob.glob(f'{tmp_folder}{subjectID}/*.nii.gz')
	functionalFiles.sort()

	# select the middle volume as the template functional volume
	templateFunctionalVolume=functionalFiles[int(len(functionalFiles)/2)]

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
	np.save(dataDir+'recognitionData.npy',recognitionData)


	return recognitionData