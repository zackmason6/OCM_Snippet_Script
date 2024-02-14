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

## Instructions
<ol>
  <li>Create your test environment</li>
  <ul>
    <li>Create a new directory and clone this repository</li>
    <li>pip install all dependencies</li>
    <li>Create a "latest" and "existing" directory</li> 
    <li>Replace the paths to latest and existing in the code with the paths to your directories</li>
    <li>Ensure that the keyword and ID snippets are located in corresponding keywords and identifier directories and follow the inport ID naming convention</li>
    <li>Make sure that there are metadata files in your latest directory for the script to pick up</li>
    <li>You might also want to add some metadata files to the existing directory to test functionality</li>
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
  <li>The script needs to copy files from existing to no-harvest</li>
  <li>Add functionality to fix frequent keyword errors</li>
  <li>Implement configuration file to add keyword search parameters for locations like Florida counties</li>
  <ul>
    <li>Add to the list of locations to search by county</li>
  </ul>
  <li>Check old scripts for other search parameters. Special operation for LIDAR or IFSAR records?</li>
  <li>Need to implement functionality to check for deleted files</li>
  <li>Implement email functionality (through cronjob?)</li>
  <li>Test on coris.ams</li>
  <li>Remove old metadata files from the latest directory?? Or update them with the snippets as well? Currently only updating the existing directory</li>
</ul>

