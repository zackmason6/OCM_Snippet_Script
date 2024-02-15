# OCM_Snippet_Script
This repository contains:
<ul>
  <li>Three python applications written to automatically update OCM metadata with keyword snippets</li>
  <li>Three .txt thesaurus files used to validate the keywords within the XML metadata files</li>
</ul>

## Dependencies
<ul>
  <li>shutil</li>
  <li>filecmp</li>
  <li>os</li>
  <li>datetime</li>
  <li>xml.etree.ElementTree</li>
</ul>

## Testing Instructions
### This may be a bit out of date
<ol>
  <li>Create your test environment</li>
  <ul>
    <li>Create a new directory and clone this repository</li>
    <li>pip install all dependencies</li>
    <li>Create a "latest" and "existing" directory within your working directory</li> 
    <li>Ensure that the keyword and ID snippets are located in corresponding keywords and identifier directories and follow the inport ID naming convention</li>
    <li>Make sure that there are metadata files in the latest and/or existing directory for the script to pick up</li>
    <li>Ensure that the necessary thesauri are in your working directory</li>
  </ul>
  <li>Run OCMHarvest.py</li>
    <ul>
      <li>This script produces a list of metadata files that need to be modified. It then copies these files 
      to the "existing" directory.</li>
    </ul>
  
  <li>Run xpathTest.py</li>
    <ul>
      <li>This script takes a list of files (produced by OCMHarvest.py) and inserts keyword
      and ID snippets into these files.</li>
    </ul>

  <li>Run keywordValidate.py</li>
    <ul>
      <li>This script validates keywords for every file within the list created by OCMHarvest.py</li>
    </ul>
</ol>

## To-Do List
<ul>
  <li>Discuss logic for location filtering!</li>
  <ul>
    <li>Right now this is the logic flow:</li>
    <ol>
      <li>Script goes keyword by keyword through this list: - - 'American Samoa','Manua','Ofu','Olosega','Rose','Swains','Tutuila','St. Croix','St. John','St. Thomas','Florida','CNMI','Puerto Rico','Guam','Hawaii','Oahu','Niihau','Kauai','Maui','Molokai','Lanai','St Thomas','St Croix','St John','Keys','U.S. Virgin Islands','US Virgin Islands','Key West','Dry Torturgas'  - - If it finds any of these keywords even as a substring in the metadata file's keywords it will trigger the next step. If none of these are found, the record is approved for further work.</li>
      <li>Search all metadata keywords for another list of keywords. Currently this list just contains "florida." If a metadata record contains anything in this list, it means that it will necessitate a county search of the metadata record, as shown in the next step. If none of these keywords turn up in the metadata record, it is approved for further work.</li>
      <li>Search through the metadata record for a list of counties. If any are found, the record is approved. Otherwise it is marked as being potentially out of scope</li>
    </ol>
  </ul>
  <li>The script needs to copy files from existing to no-harvest</li>
  <li>Add functionality to fix frequent keyword errors</li>
  <li>Implement configuration file to add keyword search parameters for locations like Florida counties</li>
  <ul>
    <li>Add to the list of locations to search by county</li>
  </ul>
  <li>Check old scripts for other search parameters. Special operation for LIDAR or IFSAR records?</li>
  <li>Need to implement functionality to check for deleted files</li>
    <ul>
      <li>Compare records found in latest/existing to records in the WAF. If something is missing from existing/latest do we pull it from the WAF or just send an alert?</li>
    </ul>
  <li>Implement email functionality (through cronjob?)</li>
  <li>Test on coris.ams</li>
  <li>Remove old metadata files from the latest directory?? Or update them with the snippets as well? Currently only updating the existing directory</li>
</ul>

