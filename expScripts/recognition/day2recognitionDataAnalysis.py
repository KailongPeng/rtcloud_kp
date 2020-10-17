# This script is run in day 2 recognition run, pick up a dicom in realtime folder
# in Milgram. And choose that as the day2 functional template volume.
form glob import glob
YYYYMMDD= '20201009' #'20201009' '20201015'
LASTNAME='rtSynth_pilot001'
PATIENTID='rtSynth_pilot001'
subjectFolder=f"{Top_directory}/{YYYYMMDD}.{LASTNAME}.{PATIENTID}/" #20190820.RTtest001.RTtest001: the folder for current subject # For each patient, a new folder will be generated:

dicomFiles=glob(f"{subjectFolder}*")
templateVolume=dicomFiles[int(len(dicomFiles)/2)]
templateVolume=dicom2nii(templateVolume)

main_folder='/gpfs/milgram/project/turk-browne/projects/rtcloud_kp/'
day2functionalTemplate=f"{main_folder}subjects/{sub}/ses2_recognition/functionalTemplate.nii.gz"
call(f"cp {templateVolume} {day2functionalTemplate}")

command=f"flirt -in {day2functionalTemplate}\
- \
"

day2functionalTemplate_inDay1=
command = f'flirt -in {day2functionalTemplate} \
-ref {day1functionalTemplate} \
-out {day2functionalTemplate_inDay1}' 