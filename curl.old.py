import requests # pip install requests
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from datetime import date

barcode = Path.cwd().stem # used to name the zip archive
url = 'https://babel.hathitrust.org/cgi/singleimage_validator' # HathiTrust validator
imageFilePath = './bitonals/' # path to where the combined files (.tif and .jp2) exist
errorLogPath = './errors/' # path to any error results from HathiTrust validator
skippedPath = './skipped/' # extra files found will be moved here
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

print(f'Validating files in {barcode}\n')

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