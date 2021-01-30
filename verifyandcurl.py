import re
import requests # pip install requests
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

barcode = Path.cwd().stem # used to name the zip archive
url = 'https://babel.hathitrust.org/cgi/singleimage_validator' # HathiTrust validator
imageFilePath = './bitonals/' # path to where the combined files (.tif and .jp2) exist
errorLogPath = './errors/' # path to any error results from HathiTrust validator
skippedPath = './skipped/' # extra files found will be moved here
numFiles = [] # number of files in './bitonals/'
projNum = [] # projected number of files that should be in './bitonals/ based off of last file number'
dupe = [] # files that have name issues
validatedFiles = [] # list of files that succeeded
failedFiles = [] # list of files that failed
skippedFiles = [] # list of files that were skipped

def log(files, outputString): # log() writes to log.txt and keeps track of what files succeeded, failed, and skipped
    validatedLog.write(f'\n{outputString}\n')
    if files:
        for entry in files:
            validatedLog.write(entry)
            validatedLog.write('\n')
    else:
        validatedLog.write('none\n')

for imageFile in Path(imageFilePath).iterdir():
    if imageFile.is_file() and imageFile.suffix == '.tif' or imageFile.suffix == '.jp2':
        numFiles.append(imageFile.stem)
r = re.compile('^\d\d\d\d\d\d\d\d$')
check = list(filter(r.match, numFiles))

errorCount = 0
for filename in numFiles: # iterates through all tif and jp2 files, checks naming convention
    if filename not in check:
        print(f'{filename} is improperly named')
        dupe.append(filename.lstrip('0').zfill(8))
        errorCount = 1
print('')

# strip, sort, and repad zeros
numFilesStripped = [s.lstrip('0') for s in numFiles]
numFilesStripped.sort()
repadded = [str(s).zfill(8) for s in numFilesStripped] # add correct amount of zeros back in

counter = 1
for imageFile in range(int(repadded[-1])): # iterates based on 
    projNum.append(f'{counter:08}')
    counter = counter + 1
for filename in projNum:
    if filename not in dupe and filename not in repadded:
        print(f'{filename} is missing')
        errorCount = 1

if errorCount == 1: # exits out if there is an error
    print('\nRemidate and try again')
    exit()

print(f'Validating files in {barcode}\n') # starting validation process

if Path(errorLogPath).exists(): # checks if a previous ./errors/ exists and deletes it
    shutil.rmtree(errorLogPath)

Path('./log.txt').unlink(missing_ok = True) # checks if a previous log.txt exists and deletes it

for imageFile in Path(imageFilePath).iterdir(): # iterates on each .tif or jp2 in ./bitonals/
    if imageFile.is_file() and imageFile.suffix == '.tif' or imageFile.suffix == '.jp2':
        with open(imageFile, 'rb') as uploads:
            print(f'Validating {imageFile.name}...')
            result = requests.post(url, files = {'file': uploads}) # uploads to HathiTrust validator
            
            if 'File validation succeeded!' in result.text: # looks for specific success string
                    print(f'{imageFile.name} was a success!\n')
                    validatedFiles.append(imageFile.name) # adds succeeded files to a list
            else:                                           # success string not found means validation failed
                    print(f'{imageFile.name} was a failure...\n')
                    (Path.cwd() / errorLogPath).mkdir(exist_ok = True) # makes ./errors/ for failed results
                    with open(f'{errorLogPath}{imageFile.stem}.html', 'w') as errorLog: # saves failed results as html file
                        errorLog.write(result.text)
                    failedFiles.append(imageFile.name) # adds failed files to a list
    else:
        skippedFiles.append(imageFile.name) # adds skipped files to a list
        (Path.cwd() / skippedPath).mkdir(exist_ok = True)

if Path(skippedPath).exists(): # prints if there were skipped files
    print(f'Any extra file(s) were moved to {skippedPath}...\n')

with open('log.txt', 'a+') as validatedLog: # adds list of successes, failures, and skips to text file
    validatedLog.write(f'Log generated on: {datetime.now()}\n')
    log(validatedFiles, 'Succeeded:') # log()
    log(failedFiles, 'Failed:')
    log(skippedFiles, 'Skipped:')
    for skippedEntry in skippedFiles:
        shutil.move(imageFilePath + skippedEntry, skippedPath + skippedEntry) # moves skipped files to ./skipped/
    validatedLog.write(f'\n{len(validatedFiles)} files succeeded. | {len(failedFiles)} files failed. | {len(skippedFiles)} files skipped.')

if Path(errorLogPath).exists(): # prints if there were failures
    print(f'Error(s) found, check {errorLogPath} and remediate.\n')
else:
    print(f'{barcode} validated, creating zip...\n') # zips ./bitonals/
    shutil.make_archive(barcode, 'zip', imageFilePath)