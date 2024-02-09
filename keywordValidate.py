import xml.etree.ElementTree as ET

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

myFileList = []
with open("OCM_Metadata_For_Snippets.txt", "r", encoding="utf-8") as filesToValidate:
    Lines = filesToValidate.readlines()
for line in Lines:
    myFileList.append(line)
print("MY FILE LIST: " + str(myFileList))
for item in myFileList:
    with open(item, "r") as xmlFile:
            data = xmlFile.read()
    print(str(data))

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
    organizedDictionary = {}
    elementList = []
    elements = root.findall(xpath, namespaces)
    if elements is not None:
        if len(elements) > 0:
            for element in elements:
                tempKeywordList = []
                thesaurus = element.find("gmd:thesaurusName/gmd:CI_Citation/gmd:title/gco:CharacterString", namespaces)
                if thesaurus is not None and "coris" in thesaurus.text.lower():
                    print("THESAURUS FOUND: " + thesaurus.text)
                    keywords = element.findall("gmd:keyword/gco:CharacterString",namespaces)
                    for keyword in keywords:
                        print(keyword.text)
                        tempKeywordList.append(keyword.text)
                    tempDict = {thesaurus.text:tempKeywordList}
                    organizedDictionary.update(tempDict)
            return organizedDictionary

def createKeywordList(fileName):
    newKeywordList = []
    with open(fileName, "rb") as fp:
        for line in fp:
            line = line.strip()
            line = line.decode('utf-8', 'ignore')
            newKeywordList.append(str(line))
    return newKeywordList

def validate_keywords(myKeywordList, myThesaurus, myFile):
    for keyword in myKeywordList:
        #print("CHECKING THIS KEYWORD: " + str(keyword))
        keywordMatch = False
        if str(keyword) in myThesaurus:
            for corisKeyword in myThesaurus:
                if keyword == corisKeyword:
                    print("CoRIS KEYWORD FOUND: " + str(keyword))
                    keywordMatch = True
        else: 
            print("BAD KEYWORD FOUND: " + str(keyword))
        if keywordMatch == False:
            tempDict = {str(myFile):[str(keyword)]}
            if str(myFile) not in badKeywordDict.keys():
                badKeywordDict.update(tempDict)
            else:
                badKeywordDict[str(myFile)].append(str(keyword))      

placeKeywordFile = "corisPlace.txt"
placeKeywordList = createKeywordList(placeKeywordFile)

discoveryKeywordFile = "corisDiscovery.txt"
discoveryKeywordList = createKeywordList(discoveryKeywordFile)

themeKeywordFile = "corisTheme.txt"
themeKeywordList = createKeywordList(themeKeywordFile)

#keywordsLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/gco:CharacterString"
keywordsLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords"
keywordTypeLocation = ".//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:type"

badKeywordDict = {}

for myFile in myFileList:
    tempDict = {}
    xml_content = open(myFile, 'r')
    data = xml_content.read()
    root = ET.fromstring(data)
    myKeywordDict = searchXML(root, keywordsLocation)
    placeKeywordsFromFile = myKeywordDict.get("CoRIS Place Thesaurus")
    print("PLACE KEYWORDS: " + str(placeKeywordsFromFile))
    themeKeywordsFromFile = myKeywordDict.get("CoRIS Theme Thesaurus")
    print("THEME KEYWORDS: " + str(themeKeywordsFromFile))
    discoveryKeywordsFromFile = myKeywordDict.get("CoRIS Discovery Thesaurus")
    print("discovery KEYWORDS: " + str(discoveryKeywordsFromFile))
    validate_keywords(placeKeywordsFromFile, placeKeywordList, myFile)
    validate_keywords(themeKeywordsFromFile, placeKeywordList, myFile)
    validate_keywords(discoveryKeywordsFromFile, placeKeywordList, myFile)

    print("\n" + str(badKeywordDict))