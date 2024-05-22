import xml.etree.ElementTree as ET
import os
from datetime import datetime

"""
This application takes a list of xml metadata files and inserts keyword and ID snippets into them.

Some records will already have coris keywords and not need that snippet added. All records will have some form of snippet, however,
as they will at least need the coris ID added.

This is file number 2 of 3 for this workflow. 
1. OCMHarvest.py
    - Runs and produces a list of files that need to be modified. Copies these files 
      to the existing directory.
      - NEED TO GO TO LATEST NO HARVEST DIRECTORY

2. xpathTest.py
    - Takes a list of files (eventually the list created in step 1) and inserts keyword
      and ID snippets.

3. keywordValidate.py
    - Validates keywords for every file within a list (again, this will eventually be the list
      from step 1)

"""

myFileList = []

with open("OCM_Metadata_For_Snippets.txt", "r", encoding="utf-8") as filesToEdit:
    Lines = filesToEdit.readlines()

for line in Lines:
    #print("Got this line: " + str(line))
    myFileList.append(line)

###### ADD IN CONFIGURATION FILE FOR THE FOLLOWING KEYWORDS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
###### IF FILE MARKED AS NOT APPROPRIATE, DON'T COPY IT OVER

title_match_keywords = ['C-CAP','Land cover','lidar','ifsar', 'Scanned Imagery']
place_match_keywords_reg = ['American Samoa','Manua','Ofu','Olosega','Rose','Swains','Tutuila','St. Croix','St. John','St. Thomas','Florida','CNMI','Puerto Rico','Guam','Hawaii','Oahu','Niihau','Kauai','Maui','Molokai','Lanai','St Thomas','St Croix','St John','Keys','U.S. Virgin Islands','US Virgin Islands','Key West','Dry Torturgas']
place_match_keywords_county = ['American Samoa','Manua','Ofu','Olosega','Rose','Swains','Tutuila','St. Croix','St. John','St. Thomas','Broward County','Martin County','Palm Beach County','Miami-Dade County','Monroe County','Florida Keys','CNMI','Puerto Rico','Guam','Hawaii','Oahu','Niihau','Kauai','Maui','Molokai','Lanai']
searchTheseLocationsByCounty = ['florida']

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

inportIDLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code/gmx:Anchor"
orgNameLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString"
titleLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString"
placeKeywordsLocation1 = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString"
placeKeywordsLocation2 = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gmx:Anchor"
editDateLocation = ".//gmd:dateStamp/gco:DateTime"

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

def register_all_namespaces(filename):
    """
        Register namespaces from XML file.

        Args:
            filename (str): Path to the XML file.
    """
    namespaces = dict([node for _, node in ET.iterparse(filename, events=['start-ns'])])
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])

def insertSnippet(data,spl_word,snippetData):
    """
        Insert snippet into XML data.

        Args:
            data (str): Original XML data.
            spl_word (str): Split word to insert snippet.
            snippet_data (str): Snippet data to insert.

        Returns:
            str: XML data with inserted snippet.
    """
    # Split xml file and append keywords snippet
    firstPart = data.split(spl_word,1)[0]
    secondPart = "         " + spl_word + data.split(spl_word,1)[1]
    fullXML = firstPart + "\n" + snippetData + "\n" + secondPart
    #print(secondPart)
    return fullXML

def updateEditDate(myXML):
    """
        Update edit date in the XML file.

        Args:
            my_xml (str): Path to the XML file.
    """
    register_all_namespaces(myXML) # Keeps namespaces from being modified
    tree = ET.parse(myXML)
    myRoot = tree.getroot()
        
    currentTime = datetime.now() # Get current datetime
    currentTime = str(currentTime).replace(" ","T") #Add T separator as required by ISO standard
    currentTime = currentTime.split(".")[0] #Remove microseconds as per ISO standard
    #print("CURRENT TIME IS: " + str(currentTime))

    for editDate in myRoot.findall(editDateLocation, namespaces):
        #print("FOUND AN EDIT DATE")
        editDate.text = (str(currentTime))
        tree.write(myXML)

existing = os.path.join(os.getcwd()+"\\existing\\")
latest = os.path.join(os.getcwd()+"\\latest\\")
for myFile in myFileList:
    
####################################################################################
# NEED TO CHECK IF RECORDS ALREADY HAVE CORIS KEYWORDS! DONT WANT TO ADD THEM TWICE.
# This is currently not implemented.
# If the snippet exists you could likely just read it as a string and compare it to
# the xml file's string data as a substring. If snippet is in file data: do nothing
# THIS IS ACTUALLY LOW PRIORITY - shouldn't actually be anything in LATEST with the
# CoRIS keywords already. Not positive but this might be a very unlikely edge case.
####################################################################################

    myFile = myFile.strip()
    print(str(myFile)+"\n")
    myKeywordFile = "\\keywords\\" + str(myFile)
    myIDFile = "\\identifier\\" + str(myFile)
    keyWordSnippetFile = os.path.join(os.getcwd()+myKeywordFile)
    idSnippetFile = os.path.join(os.getcwd()+ str(myIDFile))

    #print("Looking for this keyword snippet file: " + str(keyWordSnippetFile))
    #print("Looking for this ID snippet file: " + str(idSnippetFile))

    doTheSnippetsExist = True

    if os.path.exists(keyWordSnippetFile) == True:
        keywordSnippet = open(keyWordSnippetFile, 'r')
        garbageLine = keywordSnippet.readline()
        keywordSnippetData = keywordSnippet.read()

    else:
        print("Couldn't find keyword snippet for this record: " + str(myFile))
        doTheSnippetsExist = False

    if os.path.exists(idSnippetFile) == True:
        idSnippet = open(idSnippetFile, "r")
        garbageLine = idSnippet.readline()
        idSnippetData = idSnippet.read()
    else:
        print("Couldn't find ID snippet for this record: " + str(myFile))
        doTheSnippetsExist = False

    if doTheSnippetsExist == True:
        myFile = "\\existing\\" + str(myFile)
        myFile = os.path.join(os.getcwd()+str(myFile))
        print("TRYING TO READ FROM THIS FILE: " + str(myFile))
        xml_content = open(myFile, 'r')
        data = xml_content.read()
        #data = data.replace('<?xml version="1.0" encoding="UTF-8"?>','')
        data = data.strip()
        #print(str(data))
        root = ET.fromstring(data)

        updateEditDate(myFile)

        keywordSplitString = "<gmd:descriptiveKeywords>"
        xmlStringWithKeywords = insertSnippet(data,keywordSplitString,keywordSnippetData)

        idSplitString = "<gmd:identifier>"
        xmlStringWithID = insertSnippet(xmlStringWithKeywords,idSplitString,idSnippetData)
    
        with open(myFile, "w", encoding="utf-8") as xml_file:
        # Write the XML content to the file
            xml_file.write(xmlStringWithID)
    else:
        removeThisRecord = existing + "/" + str(myFile)
        os.remove(removeThisRecord)


