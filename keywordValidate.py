import xml.etree.ElementTree as ET
import os

"""
Version1.1 of keywordValidate.py
Written by Zack Mason on 10/31/2023

This application is part of a larger project to automate updates to XML metadata files. Other python files
needed for the entire range of functionality include xpathTest.py and OCMHarvest.py.

This application (keywordValidate.py) ingests xml metadata and validates CoRIS keywords that it finds therein.
Specifically, the applications uses the xml.etree library to parse these files and look for a repeated keyword
tag. This tag contains a thesaurus and a list of keywords that are relevant to that thesaurus. The application
evaluates whether or not the thesaurus used is a CoRIS thesaurus first. If so, it grabs the keywords listed as
child tags of the overall keyword tag, adds them to a list, and moves on to the next keyword tag. Once it has
assembled a list of all CoRIS keywords in the file, it will then proceed to validate them by type. It will
compare each keyword to the relevant thesaurus. If the keyword doesn't match any thesaurus entry it will add
it (and the filename of the file that contains the bad keyword) to a dictionary. This dictionary uses file names
as keys and lists of bad keywords as values. Once all keywords have been validated, the dictionary will be sent
as the output to the CoRIS team so that they have a list of affected files and the corresponding bad keywords 
that need to be updated.

This is file number 3 of 3 for this workflow. 
1. OCMHarvest.py
    - Runs and produces a list of files that need to be modified. Copies these files 
      to the existing directory.
2. xpathTest.py
    - Takes a list of files (eventually the list created in step 1) and inserts keyword
      and ID snippets.
3. keywordValidate.py
    - Validates keywords for every file within a list (again, this will eventually be the list
      from step 1)

"""
rawBadFileList = []
badFileList = []

checkTheseManually = []

with open("badFileList.txt", "r", encoding="utf-8") as badFiles:
    rawBadFileList = badFiles.readlines()
    for badFile in rawBadFileList:
        badFile = badFile.strip()
        badFileList.append(str(badFile))
#for badFile in badFileList:
    #print("Found this bad xml file: " + str(badFile))

myFileList = [] # Set up data structure to hold list of files that need to be operated on
with open("OCM_Metadata_For_Snippets.txt", "r", encoding="utf-8") as filesToValidate:   # Open file that contains filenames that need to be checked
    Lines = filesToValidate.readlines() # read each line of the file
for line in Lines:
    line = line.strip()

    myFile = "\\existing\\" + str(line)
    myFile = os.path.join(os.getcwd()+str(myFile))
    if str(myFile) not in badFileList:
        myFileList.append(myFile) # Create list. Each list item is one line from the above file

# The block below is commented out as unnecessary. It just prints the list of files and the contents of each
# This was really just for testing the output of a single xml file.
#print("MY FILE LIST: " + str(myFileList))
#for item in myFileList:
#    with open(item, "r") as xmlFile:
#            data = xmlFile.read()
#    print(str(data))

# Set up a dictionary of namespaces
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
    This function searches an xml file (that has been read as data) for a specific xpath

    root = xml string data created by reading in xml files as a string and then using element tree to create a tree
    xpath = xpath location to search

    This function will find thesauruses used and all associated keywords and return both in a dictionary format
    """
    organizedDictionary = {}
    elementList = []
    elements = root.findall(xpath, namespaces) # finds a list of elements that have the indicated xpath
    if elements is not None: # if there are any results of the above search:
        if len(elements) > 0:
            for element in elements:
                tempKeywordList = [] # create a temporary list to hold the search results
                thesaurus = element.find("gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString", namespaces) # find the appropriate thesaurus
                if thesaurus is not None and "coris" in thesaurus.text.lower(): # If there is a coris thesaurus indicated:
                    #print("THESAURUS FOUND: " + thesaurus.text)
                    keywords = element.findall("gmd:keyword/gco:CharacterString",namespaces) # Find the keywords
                    for keyword in keywords:
                        #print(keyword.text)
                        tempKeywordList.append(keyword.text)
                    tempDict = {thesaurus.text:tempKeywordList} 
                    organizedDictionary.update(tempDict)
            return organizedDictionary  # Returns the type of keyword and then list of associated keywords

def createKeywordList(fileName):
    """
    This function reads through a given filename and creates a list of keywords from each line in the file.
    """
    newKeywordList = []
    with open(fileName, "rb") as fp:
        for line in fp:
            line = line.strip()
            line = line.decode('utf-8', 'ignore')
            newKeywordList.append(str(line))
    return newKeywordList

def validate_keywords(myKeywordList, myThesaurus, myFile):
    """
    This function cross-references keywords in the list of keywords found in each file with the
    appropriate keyword thesaurus.

    If a bad keyword is found, the function will create a dictionary of the file that contains the
    bad keyword, and then a list of the bad keywords themselves. RIGHT NOW THIS IS JUST PRINTED TO
    THE SCREEN. THIS OUTPUT SHOULD LIKELY BE SENT AS AN EMAIL. IF RAN ON A CRON JOB ALL OUTPUT CAN 
    EASILY BE REDIRECTED. HOWEVER, THIS SHOULD BE DECIDED SOONER RATHER THAN LATER.

    myKeywordList: list of keywords found in the metadata file

    myThesaurus: thesaurus text file determined by scanning the metadata file for thesaurus type. This can be
      discovery, theme, or place.

    
    """
    if myKeywordList is not None:
        for keyword in myKeywordList:
            #print("CHECKING THIS KEYWORD: " + str(keyword))
            keywordMatch = False
            if str(keyword) in myThesaurus:
                for corisKeyword in myThesaurus:
                    if keyword == corisKeyword:
                        #print("CoRIS KEYWORD FOUND: " + str(keyword))
                        keywordMatch = True
        #else: 
        #    print("BAD KEYWORD FOUND: " + str(keyword))
            if keywordMatch == False:
                tempDict = {str(myFile):[str(keyword)]}
                if str(myFile) not in badKeywordDict.keys():
                    badKeywordDict.update(tempDict)
                else:
                    badKeywordDict[str(myFile)].append(str(keyword))      
    else:
        print("No CoRIS keywords found for this file: " + str(myFile))

# The block below takes the text file thesauruses and turns them into lists by reading them one line at a time.
placeKeywordFile = "corisPlace.txt"
placeKeywordList = createKeywordList(placeKeywordFile)

discoveryKeywordFile = "corisDiscovery.txt"
discoveryKeywordList = createKeywordList(discoveryKeywordFile)

themeKeywordFile = "corisTheme.txt"
themeKeywordList = createKeywordList(themeKeywordFile)

#keywordsLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString"
keywordsLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords"
keywordTypeLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:type"

badKeywordDict = {} # Set up blank dictionary to house the bad keyword dictionary that is generated by the validate_keywords function

for myFile in myFileList: # Iterate over each file in the file list and validate their keywords.
    #print("Processing this file: " + str(myFile))
    tempDict = {} # Set up a temporary dictionary for some reason? THIS SHOULD LIKELY BE REMOVED! ARTIFACT OF A PREVIOUS BUILD OR SOMETHING
    xml_content = open(myFile, 'r')
    try:
        data = xml_content.read() # Read in xml data as a string
        root = ET.fromstring(data) # Use element tree to get a tree from the string data
    except:
        print("Couldn't read this xml file: " + str(myFile))
        checkTheseManually.append(str(myFile))
    myKeywordDict = searchXML(root, keywordsLocation) # get a dictionary of thesaurus type and keywords found in the xml data
    placeKeywordsFromFile = myKeywordDict.get("CoRIS Place Thesaurus") # Grab all place keywords from the keyword dictionary
    #print("\nPLACE KEYWORDS: " + str(placeKeywordsFromFile))
    themeKeywordsFromFile = myKeywordDict.get("CoRIS Theme Thesaurus") # Grab all the theme keywords from the keyword dictionary
    #print("\nTHEME KEYWORDS: " + str(themeKeywordsFromFile))
    discoveryKeywordsFromFile = myKeywordDict.get("CoRIS Discovery Thesaurus") # Grab all the discovery keywords from the keyword dictionary
    #print("\nDISCOVERY KEYWORDS: " + str(discoveryKeywordsFromFile)+"\n")
    validate_keywords(placeKeywordsFromFile, placeKeywordList, myFile) # Validate place keywords against place keyword dictionary
    validate_keywords(themeKeywordsFromFile, themeKeywordList, myFile) # Validate theme keywords against theme keyword dictionary
    validate_keywords(discoveryKeywordsFromFile, discoveryKeywordList, myFile) # Validate discovery keywords against discovery keyword dictionary
    
if len(badKeywordDict) >0:
    for key in badKeywordDict:
        print("Bad keywords for " + str(key) + ": " +str(badKeywordDict[key])+"\n")
    # MAYBE ADD A MORE DETAILED PRINT OUTPUT WITH SOME EXPLANATION? 
    # printing the bad keywords is important - if we run on a cronjob just redirect it to email output.
    # Should this be sent to a spreadsheet or text file somewhere instead?

if len(checkTheseManually)>0:
    print(str(len(checkTheseManually))+" bad XML file(s) found: " + str(checkTheseManually))
