# This script is run in day 2 recognition run, pick up a dicom in realtime folder
# in Milgram. And choose that as the day2 functional template volume.

import os
import sys
import argparse
import numpy as np
import nibabel as nib
import scipy.io as sio
from subprocess import call
from nibabel.nicom import dicomreaders
import pydicom as dicom  # type: ignore
import time
import glob
import shutil
from nilearn.image import new_img_like
import joblib

os.chdir('/gpfs/milgram/project/turk-browne/users/kp578/realtime/rt-cloud/')

# import project modules from rt-cloud
import rtCommon.utils as utils
from rtCommon.utils import loadConfigFile
from rtCommon.fileClient import FileInterface
import rtCommon.projectUtils as projUtils
from rtCommon.imageHandling import readRetryDicomFromFileInterface, getDicomFileName, convertDicomImgToNifti

def dicom2nii(dicomObject, filename,templateFunctionalVolume):
	dicomObject = dicom.read_file(templateVolume)
    niftiObject = dicomreaders.mosaic_to_nii(dicomObject)
    # print(nib.aff2axcodes(niftiObject.affine))
    temp_data = niftiObject.get_data()
    output_image_correct = nib.orientations.apply_orientation(temp_data, ornt_transform)
    correct_object = new_img_like(templateFunctionalVolume, output_image_correct, copy_header=True)
    print(nib.aff2axcodes(correct_object.affine))
    splitList=filename.split('/')
    # fullNiftiFilename="/".join(splitList[0:-1])+'/'+splitList[-1].split('.')[0]+'.nii.gz'
    fullNiftiFilename=os.path.join(tmp_folder, splitList[-1].split('.')[0]+'.nii.gz')
    print('fullNiftiFilename=',fullNiftiFilename)
    correct_object.to_filename(fullNiftiFilename)
    return fullNiftiFilename


tomlFIle=f"/gpfs/milgram/project/turk-browne/users/kp578/realtime/rt-cloud/projects/tProject/conf/tProject.toml"
argParser = argparse.ArgumentParser()
argParser.add_argument('--config', '-c', default=tomlFIle, type=str,
                           help='experiment file (.json or .toml)')
args = argParser.parse_args()
cfg = utils.loadConfigFile(args.config)

# YYYYMMDD= '20201009' #'20201009' '20201015'
# LASTNAME='rtSynth_pilot001'
# PATIENTID='rtSynth_pilot001'
YYYYMMDD= cfg.YYYYMMDD #'20201009' '20201015'
LASTNAME=cfg.realtimeFolder_subjectName
PATIENTID=cfg.realtimeFolder_subjectName

subjectFolder=f"{Top_directory}/{YYYYMMDD}.{LASTNAME}.{PATIENTID}/" #20190820.RTtest001.RTtest001: the folder for current subject # For each patient, a new folder will be generated:

dicomFiles=glob(f"{subjectFolder}*")
templateVolume=dicomFiles[int(len(dicomFiles)/2)]
newDicomFile=dicom2nii(templateVolume, fileName,templateFunctionalVolume) # convert dicom to nifti
templateVolume=dicom2nii(templateVolume)

main_folder='/gpfs/milgram/project/turk-browne/projects/rtcloud_kp/'
day2functionalTemplate=f"{main_folder}subjects/{sub}/ses2_recognition/functionalTemplate.nii.gz"
call(f"cp {templateVolume} {day2functionalTemplate}")

command = f'flirt -in {day2functionalTemplate} \
-ref {day1functionalTemplate} \
-out {day2functionalTemplate_inDay1}' 




call(command,shell=True)