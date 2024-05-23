import os
import filecmp
import shutil
import xml.etree.ElementTree as ET


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

title_match_keywords = ['C-CAP','Land cover','lidar','ifsar', 'Scanned Imagery']
place_match_keywords_reg = ['American Samoa','Manua','Ofu','Olosega','Rose','Swains','Tutuila','St. Croix','St. John','St. Thomas','Florida','CNMI','Puerto Rico','Guam','Hawaii','Oahu','Niihau','Kauai','Maui','Molokai','Lanai','St Thomas','St Croix','St John','Keys','U.S. Virgin Islands','US Virgin Islands','Key West','Dry Torturgas']
place_match_keywords_county = ['American Samoa','Manua','Ofu','Olosega','Rose','Swains','Tutuila','St. Croix','St. John','St. Thomas','Broward County','Martin County','Palm Beach County','Miami-Dade County','Monroe County','Florida Keys','CNMI','Puerto Rico','Guam','Hawaii','Oahu','Niihau','Kauai','Maui','Molokai','Lanai']
searchTheseLocationsByCounty = ['florida']

inportIDLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code/gmx:Anchor"
orgNameLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString"
titleLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString"
placeKeywordsLocation1 = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString"
placeKeywordsLocation2 = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gmx:Anchor"
editDateLocation = ".//gmd:dateStamp/gco:DateTime"

namespaces = {
    'gco':'http://www.isotc211.org/2005/gco',
    'gmd':'http://www.isotc211.org/2005/gmd',
    'gmi':'http://www.isotc211.org/2005/gmi',
    'gml':'http://www.opengis.net/gml/3.2',
    'gmx':'http://www.isotc211.org/2005/gmx',
    'gsr':'http://www.isotc211.org/2005/gsr',
    'gss':'http://www.isotc211.org/2005/gss',
    'gts':'http://www.isotc211.org/2005/gts',
    'srv':'http://www.isotc211.org/2005/srv',
    'xlink':'http://www.w3.org/1999/xlink',
    'xs':'http://www.w3.org/2001/XMLSchema',
    'xsi':'http://www.w3.org/2001/XMLSchema-instance'
}


def searchXML(root, xpath):
    """
    Search XML element by XPath.

        Args:
            root (Element): Root element of XML tree.
            xpath (str): XPath expression to search for.

        Returns:
            str or List[str]: Text content of the found element(s).
    """
    elementList = []
    elements = root.findall(xpath, namespaces)
    if elements is not None:
        if len(elements) > 1:
            for element in elements:
                text_value = element.text
                if text_value is not None:
                    elementList.append(text_value)
            return elementList

        else:
            try:
                element = elements[0]
                text_value = element.text
            except:
                return None
            return text_value
    else:
        print("Could not find element")

def initialFilter(listOfFiles):
###############################################################################################################
# JUST MOVED THIS FROM xpathTest.py. Definitely needs to be tested!
###############################################################################################################
    moveTheseFiles = []
    for myFile in listOfFiles:
        myFile = myFile.strip()
        myFilePath = "\\initial\\" + str(myFile)
        myFile = os.path.join(os.getcwd()+str(myFilePath))
        
        titleFlag = 0
        keywordFlag = 0
        xml_content = open(myFile, 'r', encoding="utf-8")
        data = xml_content.read()
        data = data.replace('<?xml version="1.0" encoding="UTF-8"?>','')
        data = data.strip()
        root = ET.fromstring(data)
        # Search XML for a few things
        # Get Inport ID
        inportID = searchXML(root, inportIDLocation)
        
        #print("HERE IS YOUR INPORT ID: " + str(inportID))
        # Get Organization Name
        orgName = searchXML(root, orgNameLocation)
        #print("HERE IS YOUR ORGANIZATION NAME: " + str(orgName))
        # Get Title
        title = searchXML(root, titleLocation)
        #print("HERE IS YOUR TITLE: " + str(title))
        # Get Place Keywords
        placeKeywords = searchXML(root, placeKeywordsLocation1)
        if placeKeywords is None:
            placeKeywords = searchXML(root, placeKeywordsLocation2)
        #print("HERE ARE YOUR KEYWORDS: ")
        #for keyword in placeKeywords:
            #print(" " + str(keyword))

        #Standardize input and output
        standardizedPlaceKeywords = []
        standardizedTitleKeywords = []
        standardizedPlaceMatch = []
        standardizedPlaceMatchCounty = []

        for item in placeKeywords:
            item = item.lower()
            standardizedPlaceKeywords.append(item)
        for item in title_match_keywords:
            item = item.lower()
            standardizedTitleKeywords.append(item)
        for item in place_match_keywords_reg:
            item = item.lower()
            standardizedPlaceMatch.append(item)
        for item in place_match_keywords_county:
            item = item.lower()
            standardizedPlaceMatchCounty.append(item)

        # Title Filter
        for keyword in standardizedTitleKeywords:
            #print("LOOKING FOR THIS KEYWORD IN THE TITLE: " + keyword)
            if keyword in title.lower():
                #print("FOUND IT!\n")
                titleFlag = 1
                moveTheseFiles.append(myFile)
                break
        if titleFlag == 1:
            if "c-cap" in title.lower():
                if "forest fragmentation" in title.lower():
                    print("EXCLUDE THIS RECORD")
                    titleFlag = 0
                    moveTheseFiles.remove(myFile)
            #if "lidar" in title.lower() or "ifsar" in title.lower():
            #    print("LIDAR OR IFSAR RECORD FOUND - TRIGGER DIFFERENT KEYWORD SEARCH?")

        # Keyword Search
        if titleFlag == 1:
            for keyword in standardizedPlaceMatch: #These are a list of locations and each record needs at least one of these keywords.
                #print("LOOKING FOR THIS KEYWORD IN PLACE KEYWORDS: " + keyword)
                if keyword in standardizedPlaceKeywords: # These are the keywords from the record
                    #print("FOUND IT!")
                    keywordFlag = 1
                    break
            if keywordFlag == 0:
                moveTheseFiles.remove(myFile)

        #print("LOOKING FOR COUNTY STUFF NOW")
        if titleFlag == 1 and keywordFlag == 1:
            for location in searchTheseLocationsByCounty:
                #print("Looking for this location: " + location)
                if location in standardizedPlaceKeywords:
                    #print("COUNTY SEARCH NECESSARY\n")
                    keywordFlag = 0
                    for keyword in standardizedPlaceMatchCounty:
                        #print("Looking for this county keyword: " + keyword)
                        if keyword in standardizedPlaceKeywords:
                            #print("FOUND THIS ONE: " + keyword)
                            keywordFlag = 1
                            break
                    if keywordFlag == 1:
                        #print("COUNTY RECORD APPROVED")
                        if myFile not in moveTheseFiles:
                            moveTheseFiles.append(myFile)
                    elif keywordFlag == 0:
                        #print("BAD COUNTY RECORD")
                        if myFile in moveTheseFiles:
                            moveTheseFiles.remove(myFile)
    #for myFile in moveTheseFiles:
    #    print(str(myFile))
    return moveTheseFiles
# move files that meet filtering criteria
# to /nodc/projects/coris/Metadata/OCMharvest/existing - for first run
# to /nodc/projects/coris/Metadata/OCMharvest/latest - for weekly runs 

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


#existing = "/nodc/projects/coris/Metadata/OCMharvest/existing"
#latest = "/nodc/projects/coris/Metadata/OCMharvest/latest"
existing = os.path.join(os.getcwd()+"\\existing\\")
latest = os.path.join(os.getcwd()+"\\latest\\")

# THIS WILL NEED TO BE CHANGED WHEN TESTING IN ACTUAL ENVIRONMENT
initial = os.path.join(os.getcwd()+"\\initial\\")

initialList = getFileList(initial)
filteredList = initialFilter(initialList)
for file in filteredList:
    shutil.copy2(file, latest)

existingList = getFileList(existing)
print("EXISTING LIST: "+str(existingList))
latestList = getFileList(latest)
print("LATEST LIST: "+str(latestList))

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
        outputFile.write(str(record)+"\n")