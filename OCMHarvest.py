import os
import filecmp
import shutil

"""
This gets a list of xml files from the latest directory and compares it with 
a list from the existing directory. If new files or revised files are found,
the new/revised files are copied to the existing directory.

We need to check for deletions.
- Compare records found in latest/existing to records in the WAF.
- If something is missing we should send an alert.
- Also pull from the WAF and put back in existing/latest

This is file number 1 of 3 for this workflow. 
1. OCMHarvest.py
    - Runs and produces a list of files that need to be modified. Copies these files 
      to the existing directory.
2. xpathTest.py
    - Takes a list of files (eventually the list created in step 1?) and inserts keyword
      and ID snippets.
3. keywordValidate.py
    - Validates keywords for every file within a list (again, this will eventually be the list
      from step 1)

"""

def getFileList(myDirectory):
    """This function gets a list of xml files from the myDirectory variable.
    Specifically, the os.listdir command gets a list of everything in the directory
    and then this function iterates over that list and grabs everything where the
    filename ends with .xml. These are then added to another list.

    Args:
        myDirectory (string): This directory is specified by the user.

    Returns:
        list: This is a list of xml files in the user's current directory.
    """
    dataFiles = []
    myFiles = os.listdir(myDirectory)
    for file in myFiles:
        if file.endswith(".xml"):
            dataFiles.append(file)
    return dataFiles


# THIS SHOULD BE REVERTED PRIOR TO ANY ACTUAL TESTING!!!!!!!!!!

#existing = "/nodc/projects/coris/Metadata/OCMharvest/existing"
existing = "C:\\Users\\Zachary.T.Mason\\Desktop\\Coding\\CodingProjects\\OCMHarvest\\existing\\"
#latest = "/nodc/projects/coris/Metadata/OCMharvest/latest"
latest = "C:\\Users\\Zachary.T.Mason\\Desktop\\Coding\\CodingProjects\\OCMHarvest\\latest\\"

existingList = getFileList(existing)
latestList = getFileList(latest)

newFileList = []
revisedFileList = []

# If anything in latest is new or different from existing, this mandates a reaction

for metadataRecord in latestList:
    if metadataRecord in existingList:
        #print("old record found: " + str(metadataRecord))
        # Compare metadataRecord with item in existingList. 
        file1 = latest + "/" + str(metadataRecord)
        file2 = existing + "/"+ str(metadataRecord)
        comparison = filecmp.cmp(file1, file2, shallow = False)
        #print("Files are the same:", comparison)

        if comparison == False:
            revisedFileList.append(metadataRecord)

    else:
        print("New Record found")
        # metadataRecord must be a new file? I guess for now at least add it to the list
        newFileList.append(metadataRecord)

print("List of new files: \n")
for record in newFileList:
    print(str(record))
    originFilePath = latest + "/" + str(record)
    targetFilePath = existing + "/" + str(record)
    shutil.copy2(originFilePath, targetFilePath)

print("\nList of revised files: \n")
for record in revisedFileList:
    print(str(record))
    originFilePath = latest + "/" + str(record)
    targetFilePath = existing + "/" + str(record)
    shutil.copy2(originFilePath, targetFilePath)

listOfFilesToEdit = []
for record in newFileList:
    listOfFilesToEdit.append(record)
for record in revisedFileList:
    listOfFilesToEdit.append(record)

listOutputFile = "OCM_Metadata_For_Snippets.txt"

with open(listOutputFile, "w", encoding="utf-8") as outputFile:
    for record in listOfFilesToEdit:
        outputFile.write(str(record))


