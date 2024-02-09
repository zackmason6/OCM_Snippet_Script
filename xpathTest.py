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
    namespaces = dict([node for _, node in ET.iterparse(filename, events=['start-ns'])])
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])

def insertSnippet(data,spl_word,snippetData):
    # Split xml file and append keywords snippet
    firstPart = data.split(spl_word,1)[0]
    secondPart = "         " + spl_word + data.split(spl_word,1)[1]
    fullXML = firstPart + "\n" + snippetData + "\n" + secondPart
    print(secondPart)
    return fullXML

def updateEditDate(myXML):
    register_all_namespaces(myXML) # Keeps namespaces from being modified
    tree = ET.parse(myXML)
    myRoot = tree.getroot()
        
    currentTime = datetime.now() # Get current datetime
    currentTime = str(currentTime).replace(" ","T") #Add T separator as required by ISO standard
    currentTime = currentTime.split(".")[0] #Remove microseconds as per ISO standard
    #print("CURRENT TIME IS: " + str(currentTime))

    for editDate in myRoot.findall(editDateLocation, namespaces):
        print("FOUND AN EDIT DATE")
        editDate.text = (str(currentTime))
        tree.write(myXML)

        #2023-07-03T17:07:52
        #2024-01-05T15:18:05
        
        # Here is the xpath: /gmi:MI_Metadata/gmd:dateStamp/gco:DateTime
        ############################################################################

for myFile in myFileList:
    # Check to see if snippet exists. If not, don't add it. Write that check here.
    keyWordSnippetFile = str(myFile).replace(".xml","") + "_keywords.xml"
    idSnippetFile = str(myFile).replace(".xml","") + "_identifier.xml"

    print("Looking for this keyword snippet file: " + str(keyWordSnippetFile))
    print("Looking for this ID snippet file: " + str(idSnippetFile))

    doTheSnippetsExist = True

    if os.path.exists(keyWordSnippetFile) == True:
        keywordSnippet = open(keyWordSnippetFile, 'r')
        keywordSnippetData = keywordSnippet.read()
    else:
        print("Couldn't find keyword snippet for this record: " + str(myFile))
        doTheSnippetsExist = False
   
    if os.path.exists(idSnippetFile) == True:
        idSnippet = open(idSnippetFile, "r")
        idSnippetData = idSnippet.read()
    else:
        print("Couldn't find ID snippet for this record: " + str(myFile))
        doTheSnippetsExist = False

    if doTheSnippetsExist == True:
        titleFlag = 0
        keywordFlag = 0

        xml_content = open(myFile, 'r')
        data = xml_content.read()
        root = ET.fromstring(data)

        updateEditDate(myFile)

        keywordSplitString = "<gmd:descriptiveKeywords>"
        xmlStringWithKeywords = insertSnippet(data,keywordSplitString,keywordSnippetData)

        idSplitString = "<gmd:identifier>"
        xmlStringWithID = insertSnippet(xmlStringWithKeywords,idSplitString,idSnippetData)

        with open(myFile, "w", encoding="utf-8") as xml_file:
        # Write the XML content to the file
            xml_file.write(xmlStringWithID)

        xml_content = open("combined.xml", 'r')
        data = xml_content.read()
        root = ET.fromstring(data)
        # Search XML for a few things
        # Get Inport ID
        inportID = searchXML(root, inportIDLocation)
        
        print("HERE IS YOUR INPORT ID: " + str(inportID))
        # Get Organization Name
        orgName = searchXML(root, orgNameLocation)
        print("HERE IS YOUR ORGANIZATION NAME: " + str(orgName))
        # Get Title
        title = searchXML(root, titleLocation)
        print("HERE IS YOUR TITLE: " + str(title))
        # Get Place Keywords
        placeKeywords = searchXML(root, placeKeywordsLocation1)
        if placeKeywords is None:
            placeKeywords = searchXML(root, placeKeywordsLocation2)
        print("HERE ARE YOUR KEYWORDS: ")
        for keyword in placeKeywords:
            print(" " + str(keyword))


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
            print("LOOKING FOR THIS KEYWORD IN THE TITLE: " + keyword)
            if keyword in title.lower():
                print("FOUND IT!\n")
                titleFlag = 1
                break
        if titleFlag == 1:
            if "c-cap" in title.lower():
                if "forest fragmentation" in title.lower():
                    print("EXCLUDE THIS RECORD")
                    titleFlag = 0
            if "lidar" in title.lower() or "ifsar" in title.lower():
                print("LIDAR OR IFSAR RECORD FOUND - TRIGGER DIFFERENT KEYWORD SEARCH?")

        # Keyword Search
        for keyword in standardizedPlaceMatch:
            print("LOOKING FOR THIS KEYWORD IN PLACE KEYWORDS: " + keyword)
            if keyword in standardizedPlaceKeywords:
                print("FOUND IT!")
                if keyword.lower() not in searchTheseLocationsByCounty:
                    keywordFlag = 1
                break

        print("LOOKING FOR COUNTY STUFF NOW")
        for location in searchTheseLocationsByCounty:
            print("Looking for this location: " + location)
            if location in standardizedPlaceKeywords:
                print("COUNTY SEARCH NECESSARY\n")
                for keyword in standardizedPlaceMatchCounty:
                    print("Looking for this county keyword: " + keyword)
                    if keyword in standardizedPlaceKeywords:
                        print("FOUND THIS ONE: " + keyword)
                        keywordFlag = 1
                        break
                if keywordFlag == 1:
                    print("COUNTY RECORD APPROVED")
                elif keywordFlag == 0:
                    print("BAD COUNTY RECORD")

# move files that meet filtering criteria
# to /nodc/projects/coris/Metadata/OCMharvest/existing - for first run
# to /nodc/projects/coris/Metadata/OCMharvest/latest - for weekly runs 








