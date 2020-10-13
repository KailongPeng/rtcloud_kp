# preprocess code for neurosketch data for testing different filters
# There are six run for each subject recognition task
# I use 5 runs to train the model and 1 run to test the model and that testing accuracy 
# is used as the metric. comparing different filtering methods.

# How should the metrics be? Should it be model testing accuracy of training process 


def recognition_dataAnalysis_brain(sub='0110171_neurosketch',run=1): # normally sub should be sub001

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
	homeDir="/gpfs/milgram/project/turk-browne/jukebox/ntb/projects/sketchloop02/" 
	dataDir=f"{homeDir}subjects/{sub}/data/nifti/"

	# if the data have been analyzed, load the saved data.
	PreprocessedData=f'{dataDir}realtime_preprocessed/{sub}_recognition_run_{run}.nii.gz'
	if os.path.exists(PreprocessedData):
		return

	tmp_folder = "/gpfs/milgram/scratch60/turk-browne/kp578/sandbox/" + sub # tmp_folder='/tmp/kp578/'
	if os.path.isdir(tmp_folder):
		shutil.rmtree(tmp_folder)
	os.mkdir(tmp_folder) # the intermediate data are saved in scratch folder, only original data and final results are saved in project folder

	def printOrien(full_ref_BOLD):
		# input might be .nii.gz file
		ref_BOLD_obj = nib.load(full_ref_BOLD)
		ref_bold_ornt = nib.aff2axcodes(ref_BOLD_obj.affine)
		print('Ref BOLD orientation:') # day1functionalInAnatomicalSpace Ref BOLD orientation:('R', 'A', 'S') # What is the orientation of the realtime data? 
		print(ref_bold_ornt)
		return ref_bold_ornt

	functional=f'{dataDir}{sub}_recognition_run_{run}.nii.gz'

	# copy the functional data to tmp folder 
	call(f"cp {functional} {tmp_folder}/",shell=True)

	# split functional data to multiple volumes
	call(f"fslsplit {tmp_folder}/{functional.split('/')[-1]}  {tmp_folder}/",shell=True)
	functionalFiles=glob.glob(f'{tmp_folder}/*.nii.gz')
	functionalFiles.sort()

	# select the middle volume as the template functional volume
	templateFunctionalVolume=functionalFiles[int(len(functionalFiles)/2)]

	# align every other functional volume with templateFunctionalVolume
	outputFileNames=[]
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
		outputFileNames.append(TR_FunctionalTemplateSpace)

	# merge the aligned data to the PreprocessedData, finish preprocessing
	command=f"fslmerge -t {PreprocessedData} {file}"
	print('running',command)
	call(command, shell=True)

recognition_dataAnalysis_brain(sub='0110171_neurosketch',run=1)