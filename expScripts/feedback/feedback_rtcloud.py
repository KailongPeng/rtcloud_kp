
## - function defintiion and environment setting up
def dicom2nii(filename):
	dicomObject = dicom.read_file(filename)
	niftiObject = dicomreaders.mosaic_to_nii(dicomObject)
	print(nib.aff2axcodes(niftiObject.affine))
	splitList=filename.split('/')
	fullNiftiFilename='/'+os.path.join(*splitList[0:-1] , splitList[-1].split('.')[0]+'.nii.gz')
	print('fullNiftiFilename=',fullNiftiFilename)
	niftiObject.to_filename(fullNiftiFilename)
	return fullNiftiFilename

# def convertToNifti(tempNiftiDir,dicomObject,curr_dicom_name,ornt_transform,scratch_bold_ref):
#     nameToSaveNifti = curr_dicom_name.split('.')[0] + '.nii.gz'
#     fullNiftiFilename = os.path.join(tempNiftiDir, nameToSaveNifti)
#     niftiObject = dicomreaders.mosaic_to_nii(dicomObject)
#     print(nib.aff2axcodes(niftiObject.affine))
#     temp_data = niftiObject.get_data()
#     output_image_correct = nib.orientations.apply_orientation(temp_data, ornt_transform)
#     correct_object = new_img_like(scratch_bold_ref, output_image_correct, copy_header=True)
#     print(nib.aff2axcodes(correct_object.affine))
#     correct_object.to_filename(fullNiftiFilename)
#     print(fullNiftiFilename)
#     return fullNiftiFilename

def getDicomFileName(cfg, scanNum, fileNum):
    """
    This function takes in different variables (which are both specific to the specific
    scan and the general setup for the entire experiment) to produce the full filename
    for the dicom file of interest.
    Used externally.
    """
    if scanNum < 0:
        raise ValidationError("ScanNumber not supplied or invalid {}".format(scanNum))

    # the naming pattern is provided in the toml file
    if cfg.dicomNamePattern is None:
        raise InvocationError("Missing config settings dicomNamePattern")

    if '{run' in cfg.dicomNamePattern:
        fileName = cfg.dicomNamePattern.format(scan=scanNum, run=fileNum)
    else:
        scanNumStr = str(scanNum).zfill(2)
        fileNumStr = str(fileNum).zfill(3)
        fileName = cfg.dicomNamePattern.format(scanNumStr, fileNumStr)
    fullFileName = os.path.join(cfg.dicomDir, fileName)

    return fullFileName


tmp_folder='/tmp/kp578/'
if os.path.isdir(tmp_folder):
	shutil.rmtree(tmp_folder)
os.mkdir(tmp_folder)
Top_directory = '/gpfs/milgram/project/realtime/DICOM'
# Top_directory = '/gpfs/milgram/project/turk-browne/users/kp578/realtime/rt-cloud/projects/tProject/dicomDir/example/neurosketch/' # simulated folder for realtime folder where new incoming dicom files are pushed to

## - realtime feedback code
# subject folder
YYYYMMDD='20201009'
LASTNAME='rtSynth_pilot001'
PATIENTID='rtSynth_pilot001'
subjectFolder=f"{Top_directory}/{YYYYMMDD}.{LASTNAME}.{PATIENTID}/" #20190820.RTtest001.RTtest001: the folder for current subject # For each patient, a new folder will be generated:
cfg.dicomDir=subjectFolder

import random
randomlist = []
for i in range(0,50):
    n = random.randint(1,19)
    randomlist.append(n)
print(randomlist)


# current TR dicom file name
SCANNUMBER='000001'
TRNUMBER='000001'
dicomFileName = f"001_{SCANNUMBER}_{TRNUMBER}.dcm" # DICOM_file #SCANNUMBER might be run number; TRNUMBER might be which TR is this currently.

# this is the output of the recognition_dataAnalysis.py, meaning the day1 functional template volume in day1 anatomical space.
# day1functionalInAnatomicalSpace='/gpfs/milgram/project/turk-browne/projects/rtcloud_kp/recognition/dataAnalysis/rtSynth_pilot001/nifti/day1functionalInAnatomicalSpace.nii.gz'
templateFunctionalVolume=f'{dataDir}/templateFunctionalVolume.nii.gz'

num_total_TRs=1
for this_TR in np.arange(num_total_TRs):
	# fileName = getDicomFileName(cfg, scanNum, this_TR) # get the filename expected for the new DICOM file, might be f"{subjectFolder}{dicomFileName}"
	fileName="pwd/gpfs/milgram/project/realtime/DICOM/20201009.rtSynth_pilot001.rtSynth_pilot001/001_000005_000149.dcm"
	print('fileName=',fileName)
	print("• use 'readRetryDicomFromFileInterface' to read dicom file for",
	    "TR %d, %s" %(this_TR, fileName)) # fileName is a specific file name of the interested file
	newDicomFile =  readRetryDicomFromFileInterface(fileInterface, fileName,timeout_file) # wait till you find the next dicom is available

	newDicomFile=dicom2nii(newDicomFile) # convert dicom to nifti
	newDicomFile_aligned=tmp_folder+newDicomFile.split('/')[-1][0:-7]+'_aligned.nii.gz' #aligned to day1 functional template run volume in day1 anatomical space

	command = f"3dvolreg -verbose -zpad 1 -base {templateFunctionalVolume} -cubic -prefix {newDicomFile_aligned} \
	-1Dfile {newDicomFile_aligned[0:-7]}_motion.1D -1Dmatrix_save {newDicomFile_aligned[0:-7]}_mat.1D {newDicomFile}"
	print('Running ' + command)
	A = time.time()
	call(command, shell=True)
	B = time.time()
	print('3dvolreg time=',B-A) 

	newDicomFile_aligned = nib.load(newDicomFile_aligned)
	newDicomFile_aligned = newDicomFile_aligned.get_data()
	data.append(newDicomFile_aligned)

	## - load the saved model and apply it on the new coming dicom file.
	parameter = np.mean(data)
	
	## - send the output of the model to web.
	projUtils.sendResultToWeb(projectComm, runNum, int(this_TR), parameter)




